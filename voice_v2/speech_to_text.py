from __future__ import annotations

import numpy as np
from faster_whisper import WhisperModel

from .config import WHISPER_CPU_THREADS, WHISPER_MODEL_SIZE


class SpeechToText:
    """Portuguese transcription using Faster-Whisper on CPU INT8."""

    def __init__(self, model_size: str = WHISPER_MODEL_SIZE) -> None:
        self.model_size = model_size
        print(
            f"[ATLAS STT] Carregando Faster-Whisper '{model_size}' "
            f"em CPU INT8 ({WHISPER_CPU_THREADS} threads)..."
        )
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            cpu_threads=WHISPER_CPU_THREADS,
            num_workers=1,
        )
        print("[ATLAS STT] Modelo de transcrição pronto.")

    def transcribe(self, audio: np.ndarray) -> str:
        samples = np.asarray(audio, dtype=np.float32).reshape(-1)
        if samples.size < 4_000:
            return ""

        segments, _info = self.model.transcribe(
            samples,
            language="pt",
            beam_size=5,
            temperature=0.0,
            condition_on_previous_text=False,
            vad_filter=False,
            no_speech_threshold=0.6,
            log_prob_threshold=-1.0,
        )
        completed = list(segments)
        return " ".join(segment.text.strip() for segment in completed if segment.text.strip()).strip()
