from __future__ import annotations

import numpy as np
import torch
from silero_vad import load_silero_vad

from .config import SAMPLE_RATE, VAD_THRESHOLD


class SileroVAD:
    """Streaming Silero VAD wrapper for 16 kHz audio."""

    def __init__(self, threshold: float = VAD_THRESHOLD) -> None:
        torch.set_num_threads(1)
        self.threshold = threshold
        self.model = load_silero_vad()
        self.pending = np.empty(0, dtype=np.float32)

    def reset(self) -> None:
        self.pending = np.empty(0, dtype=np.float32)
        if hasattr(self.model, "reset_states"):
            self.model.reset_states()

    def probability(self, frame: np.ndarray) -> float:
        samples = np.asarray(frame, dtype=np.float32).reshape(-1)
        if self.pending.size:
            samples = np.concatenate((self.pending, samples))

        scores: list[float] = []
        offset = 0
        while samples.size - offset >= 512:
            chunk = torch.from_numpy(samples[offset:offset + 512].copy())
            with torch.inference_mode():
                score = self.model(chunk, SAMPLE_RATE)
            scores.append(float(score.item()))
            offset += 512

        self.pending = samples[offset:].astype(np.float32, copy=True)
        return max(scores, default=0.0)

    def is_speech(self, frame: np.ndarray) -> tuple[bool, float]:
        score = self.probability(frame)
        return score >= self.threshold, score
