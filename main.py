"""
main.py
Real-Time Dual-Window System (Dual-Hand Custom Gestures Combo Engine + 120 FPS Async).
"""

import threading
import time
from pathlib import Path
from urllib.request import urlretrieve

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

import config
from gesture_detector import GestureClassifier, WRIST, FINGERTIP_INDICES, resolve_dual_hand_combo
from overlay_utils import ParticleSystem

HAND_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)


class AsyncCameraAndDetector:
    def __init__(self, src=0, width=1280, height=720, model_path=""):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=config.MAX_NUM_HANDS,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.classifier = GestureClassifier(
            buffer_size=config.GESTURE_BUFFER_SIZE,
            min_votes_ratio=config.MIN_VOTES_RATIO,
        )

        self.ok, self.raw_frame = self.cap.read()
        self.label = "UNKNOWN"
        self.active_combo_mode = "STARFIELD"
        self.norm_hand_positions = []
        self.norm_fingertips = []
        self.stopped = False
        self.lock = threading.Lock()
        self.last_timestamp_ms = 0

    def start(self):
        threading.Thread(target=self._worker, daemon=True).start()
        return self

    def _worker(self):
        while not self.stopped:
            ok, frame = self.cap.read()
            if not ok or frame is None:
                time.sleep(0.001)
                continue

            if config.MIRROR_CAMERA:
                frame = cv2.flip(frame, 1)

            curr_ms = int(time.time() * 1000)
            if curr_ms <= self.last_timestamp_ms:
                curr_ms = self.last_timestamp_ms + 1
            self.last_timestamp_ms = curr_ms

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = self.landmarker.detect_for_video(mp_image, curr_ms)

            label = "UNKNOWN"
            combo_mode = "STARFIELD"
            norm_hand_positions = []
            norm_fingertips = []

            if results.hand_landmarks:
                detected_gestures = []
                for hand_lms in results.hand_landmarks:
                    wrist = hand_lms[WRIST]
                    norm_hand_positions.append((wrist.x, wrist.y))

                    for tip_idx in FINGERTIP_INDICES:
                        norm_fingertips.append((hand_lms[tip_idx].x, hand_lms[tip_idx].y))

                    if config.DRAW_HAND_LANDMARKS:
                        draw_cyber_skeleton(frame, hand_lms)

                    g_label = self.classifier.classify(hand_lms)
                    detected_gestures.append(g_label)

                if len(detected_gestures) == 2:
                    g1, g2 = detected_gestures[0], detected_gestures[1]
                    combo_mode = resolve_dual_hand_combo(g1, g2)
                    label = f"{g1} + {g2} -> {combo_mode}"
                else:
                    g1 = detected_gestures[0]
                    combo_mode = {
                        "FIST_UP": "HEART",
                        "FIST_DOWN": "MARS",
                        "C_SHAPE": "PLANET",
                        "LOVE": "TEXT",
                        "OPEN_PALM": "STARFIELD",
                    }.get(g1, "STARFIELD")
                    label = f"{g1}"
            else:
                self.classifier.reset()

            with self.lock:
                self.raw_frame = frame
                self.label = label
                self.active_combo_mode = combo_mode
                self.norm_hand_positions = norm_hand_positions
                self.norm_fingertips = norm_fingertips

    def get_data(self):
        with self.lock:
            return (
                self.raw_frame.copy() if self.raw_frame is not None else None,
                self.label,
                self.active_combo_mode,
                self.norm_hand_positions,
                self.norm_fingertips,
            )

    def stop(self):
        self.stopped = True
        self.cap.release()


def ensure_hand_model() -> Path:
    model_path = Path(config.HAND_LANDMARKER_MODEL)
    if not model_path.is_absolute():
        model_path = Path(__file__).resolve().parent / model_path
    if not model_path.exists():
        model_path.parent.mkdir(parents=True, exist_ok=True)
        print("[INFO] Mengunduh model MediaPipe Hand Landmarker...")
        try:
            urlretrieve(HAND_LANDMARKER_URL, model_path)
            print("[INFO] Unduhan selesai.")
        except Exception as exc:
            model_path.unlink(missing_ok=True)
            raise RuntimeError(f"Gagal mengunduh model: {exc}") from exc
    return model_path


def fit_frame_letterbox(frame: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    target_w, target_h = target_size
    h, w = frame.shape[:2]

    scale = min(target_w / w, target_h / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)

    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2
    canvas[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized

    return canvas


def draw_cyber_skeleton(frame: np.ndarray, landmarks) -> None:
    h, w = frame.shape[:2]
    points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]

    glow_overlay = frame.copy()
    for conn in vision.HandLandmarksConnections.HAND_CONNECTIONS:
        p1, p2 = points[conn.start], points[conn.end]
        cv2.line(glow_overlay, p1, p2, (255, 0, 200), 6, cv2.LINE_AA)
    cv2.addWeighted(glow_overlay, 0.40, frame, 0.60, 0, frame)

    for conn in vision.HandLandmarksConnections.HAND_CONNECTIONS:
        p1, p2 = points[conn.start], points[conn.end]
        cv2.line(frame, p1, p2, (255, 235, 100), 2, cv2.LINE_AA)

    for idx, pt in enumerate(points):
        color = (0, 255, 255) if idx in (4, 8, 12, 16, 20) else (255, 100, 0)
        cv2.circle(frame, pt, 5, color, -1, cv2.LINE_AA)


def draw_hud(panel: np.ndarray, label: str, fps: float):
    badge_color = (255, 0, 220) if "+" in label else (50, 200, 255)

    cv2.rectangle(panel, (20, 20), (450, 75), (15, 15, 15), -1)
    cv2.rectangle(panel, (20, 20), (450, 75), badge_color, 2)

    cv2.putText(panel, f"COMBO: {label}", (35, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(
        panel, f"FPS: {fps:.1f}", (panel.shape[1] - 140, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 150), 2, cv2.LINE_AA
    )


def main() -> None:
    model_path = ensure_hand_model()

    part_w, part_h = config.FRAME_WIDTH, config.FRAME_HEIGHT
    cam_w, cam_h = config.FRAME_WIDTH, config.FRAME_HEIGHT

    async_engine = AsyncCameraAndDetector(
        src=config.CAMERA_INDEX, width=1280, height=720, model_path=model_path
    ).start()

    particles = ParticleSystem(part_w, part_h, count=config.PARTICLE_COUNT)
    particle_panel = np.zeros((part_h, part_w, 3), dtype=np.uint8)

    fps = 120.0
    win_cam = "Gesture Camera Tracker"
    win_part = "Particle Universe 3D [Dual-Hand Combo Engine]"

    cv2.namedWindow(win_cam, cv2.WINDOW_NORMAL)
    cv2.namedWindow(win_part, cv2.WINDOW_NORMAL)

    target_frame_time = 1.0 / 120.0
    prev_time = time.perf_counter()
    fullscreen = False

    while True:
        loop_start = time.perf_counter()

        try:
            rect_part = cv2.getWindowImageRect(win_part)
            if rect_part[2] > 100 and rect_part[3] > 100:
                cur_w, cur_h = rect_part[2], rect_part[3]
                if cur_w != part_w or cur_h != part_h:
                    part_w, part_h = cur_w, cur_h
                    particles.resize(part_w, part_h)
                    particle_panel = np.zeros((part_h, part_w, 3), dtype=np.uint8)

            rect_cam = cv2.getWindowImageRect(win_cam)
            if rect_cam[2] > 100 and rect_cam[3] > 100:
                cam_w, cam_h = rect_cam[2], rect_cam[3]
        except Exception:
            pass

        frame, label, combo_mode, norm_hand_positions, norm_fingertips = async_engine.get_data()

        if frame is None:
            time.sleep(0.001)
            continue

        hand_positions = []
        if norm_hand_positions:
            hand_positions = [(hx * part_w, hy * part_h) for hx, hy in norm_hand_positions]

        fingertips = None
        if norm_fingertips:
            fingertips = [(fx * part_w, fy * part_h) for fx, fy in norm_fingertips]

        # Set Mode Partikel Hasil Kombinasi Dua Tangan
        particles.set_mode(combo_mode)

        particle_panel.fill(0)
        particles.draw(particle_panel, hand_positions=hand_positions, fingertips=fingertips, rainbow=True, phase=time.time())

        camera_panel = fit_frame_letterbox(frame, (cam_w, cam_h))
        draw_hud(camera_panel, label, fps)

        cv2.putText(
            particle_panel,
            f"MODE: {combo_mode}",
            (30, 55),
            cv2.FONT_HERSHEY_DUPLEX,
            0.8,
            (240, 240, 240),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow(win_cam, camera_panel)
        cv2.imshow(win_part, particle_panel)

        elapsed = time.perf_counter() - loop_start
        sleep_time = target_frame_time - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

        curr_time = time.perf_counter()
        dt_loop = curr_time - prev_time
        prev_time = curr_time
        fps = 1.0 / max(dt_loop, 1e-5)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("1"):
            cv2.resizeWindow(win_part, 1280, 720)
            cv2.resizeWindow(win_cam, 1280, 720)
        elif key == ord("2"):
            cv2.resizeWindow(win_part, 1920, 1080)
            cv2.resizeWindow(win_cam, 1920, 1080)
        elif key == ord("f"):
            fullscreen = not fullscreen
            prop = cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL
            cv2.setWindowProperty(win_part, cv2.WND_PROP_FULLSCREEN, prop)

    async_engine.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()