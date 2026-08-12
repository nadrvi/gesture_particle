"""
overlay_utils.py
3D Particle Engine dengan Dual-Hand Custom Gesture Combos (Clean Aesthetic - No Lightning).
"""

import math
import os
import time
from typing import List, Optional, Sequence, Tuple, Union

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class ParticleSystem:
    MODES = {"STARFIELD", "HEART", "BIG_HEART", "TEXT", "PLANET", "MARS", "SUPERNOVA", "BLACK_HOLE"}

    def __init__(self, width: int, height: int, count: int = 1400,
                 lerp_factor: float = 0.08, seed: int = 42,
                 stiffness: float = 0.42, damping: float = 0.86):
        self.width = max(width, 320)
        self.height = max(height, 240)
        self.count = count
        self.lerp_factor = lerp_factor
        self.rng = np.random.default_rng(seed)

        self.current_pos = self.rng.uniform(
            [-self.width/2, -self.height/2, -300], [self.width/2, self.height/2, 300], (count, 3)
        ).astype(np.float32)

        self.target_pos = self.current_pos.copy()
        self.velocity = np.zeros_like(self.current_pos, dtype=np.float32)
        self.mode = "STARFIELD"
        self.particle_phase = 0.0
        self._indices = np.arange(count, dtype=np.float32)

        count_surface = int(count * 0.80)
        self._mars_phi = self.rng.uniform(0, 2 * np.pi, count_surface).astype(np.float32)
        self._mars_theta = np.arccos(self.rng.uniform(-1, 1, count_surface)).astype(np.float32)

        self._base_text_targets: Optional[np.ndarray] = None

        self.stiffness = (stiffness * self.rng.uniform(0.9, 1.25, count)).astype(np.float32)
        self.damping = (damping * self.rng.uniform(0.88, 1.02, count)).astype(np.float32)
        self.mass = self.rng.uniform(0.7, 1.1, count).astype(np.float32)

        self._last_time = time.perf_counter()

        self._shockwave_active = False
        self._shockwave_radius = 0.0
        self._shockwave_origin = np.array([0.0, 0.0], dtype=np.float32)

        self.max_sparks = 350
        self.spark_pos = np.zeros((self.max_sparks, 3), dtype=np.float32)
        self.spark_vel = np.zeros((self.max_sparks, 3), dtype=np.float32)
        self.spark_life = np.zeros(self.max_sparks, dtype=np.float32)
        self.spark_color = np.zeros((self.max_sparks, 3), dtype=np.uint8)
        self._spark_cursor = 0

        self.set_mode(self.mode)

    def resize(self, new_w: int, new_h: int) -> None:
        new_w, new_h = max(new_w, 320), max(new_h, 240)
        if new_w == self.width and new_h == self.height:
            return

        scale_x = new_w / max(self.width, 1)
        scale_y = new_h / max(self.height, 1)

        self.width = new_w
        self.height = new_h

        self.current_pos[:, 0] *= scale_x
        self.current_pos[:, 1] *= scale_y

        if self.mode == "TEXT":
            self._base_text_targets = self._generate_base_text_targets("I LOVE YOU")

    def _sample_points_evenly(self, points: np.ndarray) -> np.ndarray:
        if len(points) == 0:
            return self.rng.uniform([-self.width/2, -self.height/2, 0], [self.width/2, self.height/2, 0], (self.count, 3)).astype(np.float32)

        indices = np.linspace(0, len(points) - 1, self.count).astype(np.int32)
        sampled_2d = points[indices].astype(np.float32)

        z_depth = self.rng.uniform(-25.0, 25.0, (self.count, 1)).astype(np.float32)
        sampled_3d = np.hstack((sampled_2d, z_depth))
        return sampled_3d

    def _generate_base_text_targets(self, text: str = "I LOVE YOU") -> np.ndarray:
        image = Image.new("L", (self.width, self.height), 0)
        draw = ImageDraw.Draw(image)

        font_size = int(self.width / (len(text) * 0.58))
        font_size = min(font_size, int(self.height * 0.25))

        font = None
        for font_path in ("C:/Windows/Fonts/arialbd.ttf", "arialbd.ttf", "C:/Windows/Fonts/arial.ttf", "arial.ttf"):
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except OSError:
                continue
        if font is None:
            font = ImageFont.load_default()

        box = draw.textbbox((0, 0), text, font=font, stroke_width=1)
        text_w, text_h = box[2] - box[0], box[3] - box[1]
        pos = ((self.width - text_w) // 2, (self.height - text_h) // 2)

        draw.text(pos, text, fill=255, font=font, stroke_width=1)

        mask = np.asarray(image)
        ys, xs = np.where(mask > 120)

        if len(xs) == 0:
            return self.rng.uniform([-self.width/2, -self.height/2, 0], [self.width/2, self.height/2, 0], (self.count, 3)).astype(np.float32)

        points_centered = np.column_stack((xs - self.width / 2.0, ys - self.height / 2.0))
        return self._sample_points_evenly(points_centered)

    def trigger_shockwave(self, hand_screen_pos: Optional[tuple[float, float]] = None) -> None:
        self._shockwave_active = True
        self._shockwave_radius = 10.0
        if hand_screen_pos is not None:
            self._shockwave_origin = np.array([hand_screen_pos[0] - self.width / 2.0, hand_screen_pos[1] - self.height / 2.0], dtype=np.float32)
        else:
            self._shockwave_origin = np.array([0.0, 0.0], dtype=np.float32)

    def emit_fingertip_sparks(self, origin_2d: np.ndarray, velocity_2d: np.ndarray, count_per_tip: int = 4):
        for _ in range(count_per_tip):
            idx = self._spark_cursor
            self._spark_cursor = (self._spark_cursor + 1) % self.max_sparks

            self.spark_pos[idx, 0] = origin_2d[0] - self.width / 2.0 + self.rng.uniform(-4, 4)
            self.spark_pos[idx, 1] = origin_2d[1] - self.height / 2.0 + self.rng.uniform(-4, 4)
            self.spark_pos[idx, 2] = self.rng.uniform(-20, 20)

            burst = self.rng.uniform(-180.0, 180.0, 3).astype(np.float32)
            self.spark_vel[idx, :2] = velocity_2d * 0.45 + burst[:2]
            self.spark_vel[idx, 2] = burst[2]

            self.spark_life[idx] = 1.0

            if self.rng.random() > 0.4:
                self.spark_color[idx] = [self.rng.integers(10, 80), self.rng.integers(180, 255), 255]
            else:
                self.spark_color[idx] = [255, self.rng.integers(120, 255), 50]

    def set_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode in self.MODES and (mode != self.mode or self._base_text_targets is None):
            self.mode = mode
            if mode == "TEXT":
                self._base_text_targets = self._generate_base_text_targets("I LOVE YOU")

            self.trigger_shockwave()

            if mode in ("STARFIELD", "SUPERNOVA"):
                self.velocity = self.rng.uniform(-15.0, 15.0, (self.count, 3)).astype(np.float32)

    def _update_dynamic_targets(self) -> None:
        if self.mode in ("HEART", "BIG_HEART"):
            heart_angles = self._indices * (2 * np.pi / self.count) + self.particle_phase * 1.2
            pulse = 1.0 + 0.08 * np.sin(self.particle_phase * 5.0)
            base_scale = (min(self.width, self.height) / 24) if self.mode == "BIG_HEART" else (min(self.width, self.height) / 34)
            scale = base_scale * pulse

            x = 16 * (np.sin(heart_angles) ** 3)
            y = -(13 * np.cos(heart_angles) - 5 * np.cos(2 * heart_angles) - 2 * np.cos(3 * heart_angles) - np.cos(4 * heart_angles))
            z = 40.0 * np.sin(heart_angles * 2.0 + self.particle_phase)
            self.target_pos = np.column_stack((x * scale, y * scale, z))

        elif self.mode == "SUPERNOVA":
            arm_index = self._indices % 5
            arm_angle = arm_index * (2 * np.pi / 5) + self.particle_phase * 1.5
            dist = (self._indices / self.count) * (min(self.width, self.height) * 0.52) + 20.0
            
            theta = arm_angle + np.log(dist * 0.05 + 1.0) * 4.0
            x = dist * np.cos(theta)
            y = dist * np.sin(theta)
            z = np.sin(theta * 3.0 + self._indices * 0.1) * 60.0
            self.target_pos = np.column_stack((x, y, z))

        elif self.mode == "BLACK_HOLE":
            bh_angles = self._indices * (2 * np.pi / self.count) - self.particle_phase * 3.0
            radius = 35.0 + 15.0 * np.sin(self._indices * 0.2)
            x = radius * np.cos(bh_angles)
            y = radius * np.sin(bh_angles)
            z = (self._indices - self.count / 2) * 0.4
            self.target_pos = np.column_stack((x, y, z))

        elif self.mode == "MARS":
            count_surface = int(self.count * 0.80)
            count_atmo = self.count - count_surface
            radius = min(self.width, self.height) * 0.22

            self._mars_phi += 0.015
            surf_x = radius * np.sin(self._mars_theta) * np.cos(self._mars_phi)
            surf_y = radius * np.cos(self._mars_theta)
            surf_z = radius * np.sin(self._mars_theta) * np.sin(self._mars_phi)
            surface_pts = np.column_stack((surf_x, surf_y, surf_z))

            atmo_angles = self._indices[:count_atmo] * (2 * np.pi / count_atmo) - self.particle_phase * 1.0
            atmo_r = radius * 1.24
            atmo_x = atmo_r * np.cos(atmo_angles)
            atmo_y = atmo_r * np.sin(atmo_angles) * 0.35
            atmo_z = atmo_r * np.sin(atmo_angles) * 0.85
            atmo_pts = np.column_stack((atmo_x, atmo_y, atmo_z))

            self.target_pos = np.vstack((surface_pts, atmo_pts))

        elif self.mode == "PLANET":
            count_ring = int(self.count * 0.40)
            count_body = self.count - count_ring
            radius = min(self.width, self.height) * 0.16

            body_phi = self._indices[:count_body] * (2 * np.pi / count_body) + self.particle_phase * 0.5
            body_r = radius + np.sin(self.particle_phase * 2.0 + self._indices[:count_body]) * 2.0
            planet_x = body_r * np.cos(body_phi)
            planet_y = body_r * np.sin(body_phi)
            planet_z = np.cos(body_phi * 2.0) * 20.0
            planet = np.column_stack((planet_x, planet_y, planet_z))

            ring_t = self._indices[:count_ring] * (2 * np.pi / count_ring) - self.particle_phase * 2.0
            rx, ry = radius * 2.1, radius * 0.5
            ring_x = rx * np.cos(ring_t)
            ring_y = ry * np.sin(ring_t)
            ring_z = rx * np.sin(ring_t) * 0.6
            ring = np.column_stack((ring_x, ring_y, ring_z))

            self.target_pos = np.vstack((planet, ring))

        elif self.mode == "TEXT":
            if self._base_text_targets is not None:
                wave_y = np.sin(self.particle_phase * 3.0 + self._base_text_targets[:, 0] * 0.02) * 3.0
                wave_z = np.cos(self.particle_phase * 2.0 + self._base_text_targets[:, 1] * 0.03) * 15.0
                animated_text = self._base_text_targets.copy()
                animated_text[:, 1] += wave_y
                animated_text[:, 2] = wave_z
                self.target_pos = animated_text

    def update(self, dt: float | None = None,
               hand_positions: Optional[List[Tuple[float, float]]] = None,
               fingertips: Optional[List[Tuple[float, float]]] = None) -> None:
        now = time.perf_counter()
        real_dt = now - self._last_time
        self._last_time = now

        real_dt = float(np.clip(real_dt, 0.001, 0.035))
        self.particle_phase += real_dt * 3.5

        self._update_dynamic_targets()

        if self.mode == "STARFIELD":
            arm_index = self._indices % 3
            arm_angle = arm_index * (2 * np.pi / 3) + self.particle_phase * 0.8
            dist = (self._indices / self.count) * (min(self.width, self.height) * 0.48) + 15.0

            theta = arm_angle + np.log(dist * 0.05 + 1.0) * 3.0
            galaxy_x = dist * np.cos(theta)
            galaxy_y = dist * np.sin(theta) * 0.4
            galaxy_z = np.sin(theta * 2.0 + self._indices * 0.1) * 40.0

            galaxy_targets = np.column_stack((galaxy_x, galaxy_y, galaxy_z))
            to_target = galaxy_targets - self.current_pos
            self.velocity += to_target * (12.0 * real_dt)
            self.velocity *= max(0.0, 1.0 - (1.2 * real_dt))
            self.current_pos += self.velocity * real_dt

        else:
            speed_k, damp_k = 26.0, 18.0
            to_target = self.target_pos - self.current_pos
            accel = to_target * (speed_k * self.stiffness[:, None] * 14.0) - self.velocity * (damp_k * self.damping[:, None])

            self.velocity += accel * real_dt
            self.current_pos += self.velocity * real_dt

            blend = 1.0 - np.exp(-speed_k * real_dt)
            self.current_pos += (self.target_pos - self.current_pos) * (blend * 0.45)

        active_sparks = self.spark_life > 0.0
        if np.any(active_sparks):
            self.spark_pos[active_sparks] += self.spark_vel[active_sparks] * real_dt
            self.spark_vel[active_sparks] *= (1.0 - 2.5 * real_dt)
            self.spark_vel[active_sparks, 1] += 120.0 * real_dt
            self.spark_life[active_sparks] -= 2.2 * real_dt

        if self._shockwave_active:
            self._shockwave_radius += 1200.0 * real_dt
            delta_sw = self.current_pos[:, :2] - self._shockwave_origin
            dist_sw = np.linalg.norm(delta_sw, axis=1, keepdims=True) + 1e-5

            ring_dist = np.abs(dist_sw - self._shockwave_radius)
            sw_mask = (ring_dist < 60.0).flatten()
            if np.any(sw_mask):
                push_dir = delta_sw[sw_mask] / dist_sw[sw_mask]
                force_mag = (1.0 - ring_dist[sw_mask] / 60.0) * 400.0
                self.velocity[sw_mask, :2] += push_dir * force_mag * real_dt

            if self._shockwave_radius > max(self.width, self.height) * 1.2:
                self._shockwave_active = False

        if fingertips is not None and len(fingertips) > 0:
            curr_tips = np.array(fingertips, dtype=np.float32)
            if self._prev_fingertips is not None and self._prev_fingertips.shape == curr_tips.shape:
                tip_vels = (curr_tips - self._prev_fingertips) / max(real_dt, 1e-3)
                tip_speeds = np.linalg.norm(tip_vels, axis=1)

                for tip_pos, tip_vel, speed in zip(curr_tips, tip_vels, tip_speeds):
                    if speed > 380.0:
                        self.emit_fingertip_sparks(tip_pos, tip_vel, count_per_tip=3)

            self._prev_fingertips = curr_tips.copy()
        else:
            self._prev_fingertips = None

        if hand_positions is not None and len(hand_positions) > 0:
            for hand_pt in hand_positions:
                raw_hand = np.array([hand_pt[0] - self.width / 2.0, hand_pt[1] - self.height / 2.0], dtype=np.float32)
                delta = self.current_pos[:, :2] - raw_hand
                distance = np.linalg.norm(delta, axis=1, keepdims=True)

                influence = np.clip((280 - distance) / 280, 0, 1) ** 2
                direction = delta / np.maximum(distance, 1e-3)

                tangent_hand = np.column_stack((-direction[:, 1], direction[:, 0]))
                force_2d = (direction * influence * 1100.0 + tangent_hand * influence * 500.0)
                self.velocity[:, :2] += force_2d * real_dt / self.mass[:, None]
                self.current_pos[:, :2] += force_2d * real_dt

    def draw(self, frame: np.ndarray, hand_positions: Optional[List[Tuple[float, float]]] = None,
             fingertips: Optional[List[Tuple[float, float]]] = None, color=(180, 80, 255),
             rainbow: bool = True, phase: float = 0.0, dt: float | None = None) -> None:
        self.update(dt=dt, hand_positions=hand_positions, fingertips=fingertips)

        h, w = frame.shape[:2]
        cx, cy = w / 2.0, h / 2.0
        focal_length = 600.0

        z_projected = self.current_pos[:, 2] + 600.0
        z_projected = np.maximum(z_projected, 50.0)

        scale_factors = focal_length / z_projected
        screen_x = (self.current_pos[:, 0] * scale_factors + cx).astype(np.int32)
        screen_y = (self.current_pos[:, 1] * scale_factors + cy).astype(np.int32)

        valid_mask = (screen_x >= 0) & (screen_x < w) & (screen_y >= 0) & (screen_y < h)

        if self.mode == "MARS":
            reds = self.rng.integers(215, 256, self.count, dtype=np.uint8)
            greens = self.rng.integers(50, 120, self.count, dtype=np.uint8)
            blues = self.rng.integers(10, 50, self.count, dtype=np.uint8)
            colors = np.column_stack((blues, greens, reds))
        elif rainbow:
            hues = (125 + self._indices * 0.22 + phase * 10) % 50 + 125
            hsv = np.zeros((self.count, 1, 3), dtype=np.uint8)
            hsv[:, 0, 0] = hues.astype(np.uint8)
            hsv[:, 0, 1] = 220
            hsv[:, 0, 2] = 250
            colors = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[:, 0]
        else:
            colors = np.tile(np.asarray(color, dtype=np.uint8), (self.count, 1))

        base_radii = np.where(self.mode == "TEXT", 1.0, 1.8)
        radii = np.clip(base_radii * scale_factors, 1.0, 4.5).astype(np.int32)

        valid_indices = np.where(valid_mask)[0]
        sorted_order = valid_indices[np.argsort(-z_projected[valid_indices])]

        for idx in sorted_order:
            px, py = screen_x[idx], screen_y[idx]
            r = radii[idx]
            p_color = tuple(map(int, colors[idx]))
            cv2.circle(frame, (px, py), r, p_color, -1, cv2.LINE_AA)

        if self.mode in ("TEXT", "STARFIELD", "MARS", "SUPERNOVA"):
            front_indices = valid_indices[z_projected[valid_indices] < 580.0]
            for idx in front_indices[::2]:
                cv2.circle(frame, (screen_x[idx], screen_y[idx]), 1, (255, 255, 255), -1, cv2.LINE_AA)

        active_sparks = np.where(self.spark_life > 0.0)[0]
        for idx in active_sparks:
            sp_z = max(self.spark_pos[idx, 2] + 600.0, 50.0)
            sp_scale = focal_length / sp_z
            sp_x = int(self.spark_pos[idx, 0] * sp_scale + cx)
            sp_y = int(self.spark_pos[idx, 1] * sp_scale + cy)

            if 0 <= sp_x < w and 0 <= sp_y < h:
                alpha = self.spark_life[idx]
                r_spark = max(1, int(3 * sp_scale * alpha))
                color_spark = tuple(map(int, (self.spark_color[idx] * alpha).astype(np.uint8)))
                cv2.circle(frame, (sp_x, sp_y), r_spark, color_spark, -1, cv2.LINE_AA)
                cv2.circle(frame, (sp_x, sp_y), 1, (255, 255, 255), -1, cv2.LINE_AA)