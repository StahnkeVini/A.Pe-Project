from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "models"

SAMPLE_RATE = 16_000
FRAME_SECONDS = 0.08
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_SECONDS)

WAKEWORD_MODEL_PATH = Path(
    os.getenv("ATLAS_WAKEWORD_MODEL", str(MODEL_DIR / "atlas.onnx"))
)
WAKEWORD_THRESHOLD = float(os.getenv("ATLAS_WAKEWORD_THRESHOLD", "0.65"))
VAD_THRESHOLD = float(os.getenv("ATLAS_VAD_THRESHOLD", "0.52"))
SILENCE_SECONDS = float(os.getenv("ATLAS_SILENCE_SECONDS", "0.75"))
COMMAND_GRACE_SECONDS = float(os.getenv("ATLAS_COMMAND_GRACE_SECONDS", "1.5"))
MAX_COMMAND_SECONDS = float(os.getenv("ATLAS_MAX_COMMAND_SECONDS", "12"))
WHISPER_MODEL_SIZE = os.getenv("ATLAS_WHISPER_MODEL", "small")
WHISPER_CPU_THREADS = int(os.getenv("ATLAS_WHISPER_CPU_THREADS", "4"))
