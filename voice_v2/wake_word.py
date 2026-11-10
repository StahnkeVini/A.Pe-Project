from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np

from .config import WAKEWORD_MODEL_PATH, WAKEWORD_THRESHOLD


class WakeWordDetector:
    """openWakeWord adapter for the custom ATLAS ONNX model."""

    def __init__(
        self,
        model_path: Path = WAKEWORD_MODEL_PATH,
        threshold: float = WAKEWORD_THRESHOLD,
    ) -> None:
        self.model_path = Path(model_path)
        self.threshold = threshold
        self.model = None
        self.recent_scores: deque[float] = deque(maxlen=3)
        self.unavailable_reason: str | None = None

        if not self.model_path.is_file():
            self.unavailable_reason = (
                f"Modelo personalizado ausente: {self.model_path}. "
                "O ATLAS usará o modo provisório VAD + Whisper."
            )
            return

        try:
            from openwakeword.model import Model

            self.model = Model(
                wakeword_models=[str(self.model_path)],
                inference_framework="onnx",
                vad_threshold=0.30,
                enable_speex_noise_suppression=False,
            )
        except Exception as exc:
            self.unavailable_reason = f"Falha ao carregar o modelo openWakeWord: {exc}"
            self.model = None

    @property
    def available(self) -> bool:
        return self.model is not None

    def predict(self, frame: np.ndarray) -> tuple[bool, float]:
        if self.model is None:
            return False, 0.0

        pcm16 = (np.clip(frame, -1.0, 1.0) * 32767.0).astype(np.int16)
        predictions = self.model.predict(pcm16)
        score = max((float(value) for value in predictions.values()), default=0.0)
        self.recent_scores.append(score)

        # Exige duas leituras positivas em até três quadros para reduzir disparos isolados.
        confirmed = sum(value >= self.threshold for value in self.recent_scores) >= 2
        return confirmed, score
