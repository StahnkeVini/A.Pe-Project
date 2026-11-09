# voice_engine.py (Versão Otimizada: Áudio Direto na RAM sem depender do PyAV)
import os
import time
import asyncio
import numpy as np
import sounddevice as sd
import keyboard
import pygame
import edge_tts
from faster_whisper import WhisperModel

print("[ATLAS] Carregando modelo Whisper Offline (CPU)...")
modelo_stt = WhisperModel("base", device="cpu", compute_type="int8")
print("[ATLAS] Modelo STT carregado com sucesso.")

pygame.mixer.init()

def falar_texto(texto: str):
    """Converte texto em voz neural da Microsoft e reproduz no PC."""
    arquivo_audio = "resposta_atlas.mp3"
    
    async def gerar_tts():
        communicate = edge_tts.Communicate(texto, "pt-BR-AntonioNeural", rate="+10%")
        await communicate.save(arquivo_audio)
        
    asyncio.run(gerar_tts())
    
    pygame.mixer.music.load(arquivo_audio)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    pygame.mixer.music.unload()
    if os.path.exists(arquivo_audio):
        os.remove(arquivo_audio)

def escutar_comando_push_to_talk(tecla_gatilho="f8", taxa_amostragem=16000) -> str:
    """Grava o microfone na memória RAM e envia direto para o Whisper (Zero I/O de disco)."""
    print(f"\n[ATLAS] Segure a tecla '{tecla_gatilho.upper()}' para falar...")
    
    keyboard.wait(tecla_gatilho)
    print("[ATLAS] Gravando... (Solte para enviar)")
    
    audio_data = []
    def callback(indata, frames, time_info, status):
        audio_data.append(indata.copy())

    # Captura direto em float32 a 16kHz (formato nativo que o Whisper espera na RAM)
    stream = sd.InputStream(samplerate=taxa_amostragem, channels=1, dtype="float32", callback=callback)
    with stream:
        while keyboard.is_pressed(tecla_gatilho):
            time.sleep(0.05)
            
    print("[ATLAS] Processando áudio offline na RAM...")
    if not audio_data:
        return ""
        
    # Achata o vetor 2D para 1D (exigência do Whisper em memória) e passa direto!
    audio_np = np.concatenate(audio_data, axis=0).flatten()
    
    # Passando audio_np direto, o faster-whisper NÃO chama o av.open()!
    segmentos, _ = modelo_stt.transcribe(audio_np, language="pt")
    texto_transcrito = "".join([segmento.text for segmento in segmentos]).strip()
    
    print(f"[ATLAS] Você disse: '{texto_transcrito}'")
    return texto_transcrito

if __name__ == "__main__":
    falar_texto("Sistemas de comunicação online. Segure F8 para iniciar o teste.")
    while True:
        comando = escutar_comando_push_to_talk("f8")
        if not comando:
            continue
        if "desligar" in comando.lower():
            falar_texto("Encerrando módulo de voz.")
            break
    falar_texto(f"Entendido. Você disse: {comando}")