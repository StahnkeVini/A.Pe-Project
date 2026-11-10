# voice_engine.py — interface compatível com main.py, usando a arquitetura modular v2.
import os
import re
import time
import asyncio

import edge_tts
import pygame

from voice_v2.pipeline import VoicePipeline

pygame.mixer.init()
_pipeline: VoicePipeline | None = None


def limpar_texto_para_fala(texto: str) -> str:
    texto_limpo = re.sub(r"[\*\#\`\_\~]", "", texto)
    return re.sub(r"\s+", " ", texto_limpo).strip()


def falar_texto(texto: str) -> None:
    if not texto:
        return

    texto_limpo = limpar_texto_para_fala(texto)
    print(f"\n[ATLAS]: {texto_limpo}")
    arquivo_audio = f"atlas_tts_{int(time.time() * 1000)}.mp3"

    async def gerar_tts() -> None:
        communicate = edge_tts.Communicate(texto_limpo, "pt-BR-AntonioNeural", rate="+12%")
        await communicate.save(arquivo_audio)

    try:
        asyncio.run(gerar_tts())
        pygame.mixer.music.load(arquivo_audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        pygame.mixer.music.unload()
    finally:
        if os.path.exists(arquivo_audio):
            try:
                os.remove(arquivo_audio)
            except OSError:
                pass
        time.sleep(0.3)


def escutar_sempre_ativo() -> str:
    """Mantém a mesma assinatura usada por main.py e delega ao pipeline v2."""
    global _pipeline
    if _pipeline is None:
        _pipeline = VoicePipeline()
    return _pipeline.listen_once()
