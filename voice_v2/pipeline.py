from __future__ import annotations

from collections import deque
import re
import time

import numpy as np

from .config import (
    COMMAND_GRACE_SECONDS,
    MAX_COMMAND_SECONDS,
    SILENCE_SECONDS,
)
from .microphone import MicrophoneStream
from .segmenter import UtteranceSegmenter
from .speech_to_text import SpeechToText
from .vad_engine import SileroVAD
from .wake_word import WakeWordDetector


class VoicePipeline:
    """Coordinates microphone capture, wake word, VAD and local transcription."""

    def __init__(self) -> None:
        self.wake_word = WakeWordDetector()
        self.vad = SileroVAD()
        self.segmenter = UtteranceSegmenter()
        self.stt: SpeechToText | None = None

        if self.wake_word.available:
            print("[ATLAS VOZ] Detector personalizado 'ATLAS' carregado.")
        else:
            print(f"[ATLAS VOZ] AVISO: {self.wake_word.unavailable_reason}")
            print("[ATLAS VOZ] Modo provisório: VAD + Whisper validando a palavra ATLAS.")

    def _transcriber(self) -> SpeechToText:
        if self.stt is None:
            self.stt = SpeechToText()
        return self.stt

    @staticmethod
    def _extract_command(text: str, trust_wakeword: bool = False) -> str | None:
        cleaned = text.strip()
        if not cleaned:
            return None

        match = re.match(
            r"^\s*(?:ei\s+)?(?:átlas|atlas)\b[\s,.:;!?-]*",
            cleaned,
            flags=re.IGNORECASE,
        )
        if match:
            return cleaned[match.end():].strip() or "olá, estou à disposição"

        # Com o modelo de palavra-chave ativo, a ativação já foi confirmada pelo detector.
        return cleaned if trust_wakeword else None

    def _listen_fallback(self, microphone: MicrophoneStream) -> str:
        while True:
            frame = microphone.read_frame()
            probability = self.vad.probability(frame)
            utterance = self.segmenter.push(frame, probability)
            if utterance is None:
                continue

            self.vad.reset()
            text = self._transcriber().transcribe(utterance)
            command = self._extract_command(text)
            if command is not None:
                print(f"[ATLAS VOZ - MODO PROVISÓRIO] '{text}'")
                return command

            if text:
                print(f"[ATLAS VOZ - IGNORADO, SEM 'ATLAS'] '{text}'")

    def _listen_with_wakeword(self, microphone: MicrophoneStream) -> str:
        pre_roll: deque[np.ndarray] = deque(maxlen=18)  # 1,44 s para preservar o início da chamada.

        while True:
            frame = microphone.read_frame()
            pre_roll.append(frame.copy())

            detected, score = self.wake_word.predict(frame)
            if not detected:
                continue

            print(f"[ATLAS WAKE WORD] Palavra-chave confirmada (score={score:.2f}).")
            audio_frames = list(pre_roll)
            self.vad.reset()

            started_at = time.monotonic()
            last_speech_at = started_at

            while True:
                next_frame = microphone.read_frame()
                audio_frames.append(next_frame)
                probability = self.vad.probability(next_frame)
                now = time.monotonic()

                if probability >= self.vad.threshold:
                    last_speech_at = now

                elapsed = now - started_at
                if elapsed >= COMMAND_GRACE_SECONDS and now - last_speech_at >= SILENCE_SECONDS:
                    break
                if elapsed >= MAX_COMMAND_SECONDS:
                    print("[ATLAS VOZ] Limite de duração do comando atingido.")
                    break

            audio = np.concatenate(audio_frames).astype(np.float32, copy=False)
            text = self._transcriber().transcribe(audio)
            command = self._extract_command(text, trust_wakeword=True)
            print(f"[ATLAS VOZ] Transcrição: '{text}'")
            return command or "olá, estou à disposição"

    def listen_once(self) -> str:
        self.segmenter.reset()
        self.vad.reset()

        with MicrophoneStream() as microphone:
            if self.wake_word.available:
                return self._listen_with_wakeword(microphone)
            return self._listen_fallback(microphone)
