from __future__ import annotations

from collections import deque
import math

import numpy as np

from .config import FRAME_SECONDS, MAX_COMMAND_SECONDS, SILENCE_SECONDS, VAD_THRESHOLD


class UtteranceSegmenter:
    """Build complete speech segments with pre-roll and VAD-based endpointing."""

    def __init__(self) -> None:
        self.pre_roll: deque[np.ndarray] = deque(maxlen=6)
        self.frames: list[np.ndarray] = []
        self.active = False
        self.silence_frames = 0
        self.max_frames = int(MAX_COMMAND_SECONDS / FRAME_SECONDS)
        self.required_silence = max(1, math.ceil(SILENCE_SECONDS / FRAME_SECONDS))

    def reset(self) -> None:
        self.pre_roll.clear()
        self.frames.clear()
        self.active = False
        self.silence_frames = 0

    def push(self, frame: np.ndarray, probability: float) -> np.ndarray | None:
        current = np.asarray(frame, dtype=np.float32).copy()

        if not self.active:
            self.pre_roll.append(current)
            if probability >= VAD_THRESHOLD:
                self.active = True
                self.frames = list(self.pre_roll)
                self.silence_frames = 0
            return None

        self.frames.append(current)
        if probability >= VAD_THRESHOLD:
            self.silence_frames = 0
        else:
            self.silence_frames += 1

        if self.silence_frames >= self.required_silence or len(self.frames) >= self.max_frames:
            result = np.concatenate(self.frames).astype(np.float32, copy=False)
            self.reset()
            return result

        return None
