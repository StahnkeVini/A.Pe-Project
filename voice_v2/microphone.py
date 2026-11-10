from __future__ import annotations

import os
import warnings

import numpy as np
import sounddevice as sd
import soxr

from .config import FRAME_SAMPLES, FRAME_SECONDS, SAMPLE_RATE


class MicrophoneStream:
    """Capture 80 ms mono frames and resample them to 16 kHz float32."""

    def __init__(self) -> None:
        configured = os.getenv("ATLAS_MIC_DEVICE", "").strip()
        if configured:
            try:
                self.device = int(configured)
            except ValueError:
                self.device = configured
        else:
            default_input = sd.default.device[0]
            self.device = None if default_input is None or int(default_input) < 0 else int(default_input)

        self.info = sd.query_devices(self.device, "input")
        if int(self.info.get("max_input_channels", 0)) < 1:
            raise RuntimeError("O dispositivo selecionado não possui entrada de microfone.")

        self.source_rate = int(round(float(self.info["default_samplerate"])))
        if self.source_rate <= 0:
            raise RuntimeError("Não foi possível determinar a frequência do microfone.")

        self.source_blocksize = max(1, int(round(self.source_rate * FRAME_SECONDS)))
        self.stream: sd.InputStream | None = None
        self._overflow_reported = False

    def __enter__(self) -> "MicrophoneStream":
        try:
            self.stream = sd.InputStream(
                device=self.device,
                samplerate=self.source_rate,
                channels=1,
                dtype="float32",
                blocksize=self.source_blocksize,
                latency="low",
            )
            self.stream.start()
        except Exception as exc:
            raise RuntimeError(
                f"Não foi possível abrir o microfone '{self.info.get('name', 'desconhecido')}'. "
                "Verifique a seleção do headset e as permissões do Windows."
            ) from exc

        print(
            f"[ATLAS ÁUDIO] Microfone: {self.info.get('name')} | "
            f"captura: {self.source_rate} Hz | processamento: {SAMPLE_RATE} Hz"
        )
        return self

    def read_frame(self) -> np.ndarray:
        if self.stream is None:
            raise RuntimeError("O microfone ainda não foi iniciado.")

        data, overflowed = self.stream.read(self.source_blocksize)
        if overflowed and not self._overflow_reported:
            warnings.warn(
                "O buffer do microfone sofreu overflow. Feche aplicações que disputem o dispositivo.",
                RuntimeWarning,
            )
            self._overflow_reported = True

        mono = np.asarray(data, dtype=np.float32).reshape(-1)
        if self.source_rate != SAMPLE_RATE:
            mono = soxr.resample(mono, self.source_rate, SAMPLE_RATE, quality="HQ")

        if mono.size < FRAME_SAMPLES:
            mono = np.pad(mono, (0, FRAME_SAMPLES - mono.size))
        elif mono.size > FRAME_SAMPLES:
            mono = mono[:FRAME_SAMPLES]

        return np.clip(mono, -1.0, 1.0).astype(np.float32, copy=False)

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
