"""
gesture_detector.py
Gesture Classifier Presisi Tinggi untuk Single & Dual-Hand Combos.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Tuple

WRIST = 0
THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20

FINGERTIP_INDICES = [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]


@dataclass
class FingerState:
    thumb: bool
    index: bool
    middle: bool
    ring: bool
    pinky: bool


def _dist(a, b) -> float:
    dz = getattr(a, "z", 0.0) - getattr(b, "z", 0.0)
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + dz ** 2)


class GestureClassifier:
    def __init__(self, buffer_size: int = 5, min_votes_ratio: float = 0.5):
        self.buffer_size = buffer_size
        self.min_votes_ratio = min_votes_ratio
        self._history: Deque[str] = deque(maxlen=buffer_size)

    def _hand_scale(self, lm) -> float:
        return max(_dist(lm[WRIST], lm[MIDDLE_MCP]), 1e-5)

    def _finger_states(self, lm, handedness: str) -> FingerState:
        scale = self._hand_scale(lm)

        def is_extended(tip, mcp) -> bool:
            return (_dist(lm[WRIST], lm[tip]) / _dist(lm[WRIST], lm[mcp])) > 1.30

        index = is_extended(INDEX_TIP, INDEX_MCP)
        middle = is_extended(MIDDLE_TIP, MIDDLE_MCP)
        ring = is_extended(RING_TIP, RING_MCP)
        pinky = is_extended(PINKY_TIP, PINKY_MCP)

        d_thumb_pinky = _dist(lm[THUMB_TIP], lm[PINKY_MCP]) / scale
        d_thumb_index = _dist(lm[THUMB_TIP], lm[INDEX_MCP]) / scale
        thumb = d_thumb_pinky > 0.80 and d_thumb_index > 0.30

        return FingerState(thumb, index, middle, ring, pinky)

    def classify(self, landmarks, handedness: str = "Right") -> str:
        fingers = self._finger_states(landmarks, handedness)

        if fingers.thumb and fingers.index and fingers.pinky and not fingers.middle and not fingers.ring:
            raw_label = "LOVE"
        elif not any((fingers.thumb, fingers.index, fingers.middle, fingers.ring, fingers.pinky)):
            if landmarks[MIDDLE_MCP].y < landmarks[WRIST].y:
                raw_label = "FIST_UP"
            else:
                raw_label = "FIST_DOWN"
        elif self._is_c_shape(landmarks, fingers):
            raw_label = "C_SHAPE"
        elif all((fingers.thumb, fingers.index, fingers.middle, fingers.ring, fingers.pinky)):
            raw_label = "OPEN_PALM"
        else:
            raw_label = "UNKNOWN"

        self._history.append(raw_label)
        return self._stable_label()

    def _is_c_shape(self, lm, fingers: FingerState) -> bool:
        scale = self._hand_scale(lm)
        ratios = [
            _dist(lm[WRIST], lm[INDEX_TIP]) / scale,
            _dist(lm[WRIST], lm[MIDDLE_TIP]) / scale,
            _dist(lm[WRIST], lm[RING_TIP]) / scale,
            _dist(lm[WRIST], lm[PINKY_TIP]) / scale,
        ]
        is_semi_curled = all(0.80 <= r <= 1.45 for r in ratios)
        thumb_index_gap = _dist(lm[THUMB_TIP], lm[INDEX_TIP]) / scale
        return is_semi_curled and (0.35 <= thumb_index_gap <= 1.0)

    def _stable_label(self) -> str:
        if not self._history:
            return "UNKNOWN"
        counts = {}
        for label in self._history:
            counts[label] = counts.get(label, 0) + 1
        best_label, best_count = max(counts.items(), key=lambda x: x[1])
        if (best_count / len(self._history)) >= self.min_votes_ratio:
            return best_label
        return "UNKNOWN"

    def reset(self):
        self._history.clear()


def resolve_dual_hand_combo(g1: str, g2: str) -> str:
    """Pemetaan Kombinasi 2 Tangan ke Mode Partikel."""
    combo = tuple(sorted([g1, g2]))

    COMBO_MAP = {
        ("OPEN_PALM", "OPEN_PALM"): "SUPERNOVA",
        ("FIST_UP", "FIST_UP"): "BIG_HEART",
        ("FIST_DOWN", "FIST_DOWN"): "BLACK_HOLE",
        ("C_SHAPE", "C_SHAPE"): "MARS",
        ("LOVE", "LOVE"): "TEXT",
        ("FIST_UP", "OPEN_PALM"): "PLANET",
    }

    return COMBO_MAP.get(combo, "STARFIELD")