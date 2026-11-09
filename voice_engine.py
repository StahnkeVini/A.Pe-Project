# voice_engine.py (Versão Whisper Local Otimizado na RAM + Pre-Roll Buffer)
import os
import re
import time
import asyncio
from collections import deque
import numpy as np
import sounddevice as sd
import pygame
import edge_tts
from faster_whisper import WhisperModel

print("[ATLAS] Carregando motor Whisper Offline na RAM (CPU INT8)...")
# Usamos o modelo 'base' com computação int8 para máxima velocidade e leveza
modelo_stt = WhisperModel("base", device="cpu", compute_type="int8")
print("[ATLAS] Motor STT local pronto e ultra-rápido.")

pygame.mixer.init()

def limpar_texto_para_fala(texto: str) -> str:
    texto_limpo = re.sub(r"[\*\#\`\_\~]", "", texto)
    texto_limpo = re.sub(r"\s+", " ", texto_limpo).strip()
    return texto_limpo

def falar_texto(texto: str):
    if not texto:
        return
        
    texto_limpo = limpar_texto_para_fala(texto)
    print(f"\n[ATLAS]: {texto_limpo}")
    
    arquivo_audio = f"atlas_tts_{int(time.time() * 1000)}.mp3"
    
    async def gerar_tts():
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

def escutar_sempre_ativo(
    limiar_volume: float = 0.020,
    tempo_silencio_fim: float = 0.8,
    taxa_amostragem: int = 16000
) -> str:
    """Escuta contínua ultra-rápida processada inteiramente na RAM com Whisper local."""
    bloco_duracao = 0.1
    tamanho_bloco = int(taxa_amostragem * bloco_duracao)
    max_blocos_silencio = int(tempo_silencio_fim / bloco_duracao)

    pre_roll_buffer = deque(maxlen=5) # 0.5s de antecedência para não cortar o "At-" de Atlas
    audio_buffer = []
    gravando_fala = False
    blocos_silencio = 0

    print("\n[ATLAS] 🎙️ Escuta ativa local... (Diga 'Atlas' + seu comando)")

    with sd.InputStream(samplerate=taxa_amostragem, channels=1, dtype="float32") as stream:
        while True:
            bloco, _ = stream.read(tamanho_bloco)
            volume_rms = float(np.sqrt(np.mean(bloco**2)))

            if not gravando_fala:
                pre_roll_buffer.append(bloco.copy())
                if volume_rms > limiar_volume:
                    gravando_fala = True
                    audio_buffer.extend(pre_roll_buffer)
                    blocos_silencio = 0
            else:
                audio_buffer.append(bloco.copy())
                if volume_rms < limiar_volume:
                    blocos_silencio += 1
                    if blocos_silencio >= max_blocos_silencio:
                        break
                else:
                    blocos_silencio = 0

    if len(audio_buffer) < 6:
        return ""

    # Concatena direto na RAM (Zero-Copy)
    audio_np = np.concatenate(audio_buffer, axis=0).flatten()

    # Transcrição local instantânea com Whisper
    segmentos, _ = modelo_stt.transcribe(audio_np, language="pt", vad_filter=True)
    frase_completa = "".join([seg.text for seg in segmentos]).strip()

    if not frase_completa:
        return ""

    frase_lower = frase_completa.lower()
    gatilhos_atlas = ["atlas", "átlas", "atla", "atllas", "atras", "atrás"]

    if any(g in frase_lower for g in gatilhos_atlas):
        print(f"[VOZ RECONHECIDA LOCAL]: '{frase_completa}'")
        
        comando_limpo = re.sub(
            r"^.*?\b(atlas|átlas|atla|atllas|atras|atrás)\b[\,\.\!\?\:\s]*",
            "",
            frase_lower,
            flags=re.IGNORECASE
        ).strip()

        return comando_limpo if comando_limpo else "olá, estou à disposição"
    else:
        print(f"[Ignorado - Sem Wake Word]: '{frase_completa}'")
        return ""