# pc_tools.py
import os 
import time
import pyautogui
import psutil

def abrir_programa_windows(nome_programa: str) -> str:
    """Abre qualquer aplicativo instalado no windows pelo nome (ex: Notepad, discord, chrome, steam)."""
    pyautogui.press("win")
    time.sleep(0.3)
    pyautogui.write(nome_programa, interval=0.05)
    time.sleep(0.2)
    pyautogui.press("enter")
    return f"Comando executado: aplicativo'{nome_programa}' iniciado no Windows"


def controlar_midia_e_volume(acao: str) -> str:
    """Controla o áudio do PC. Valores aceitos para acao: 'subir_volume', 'baixar_volume', 'mutar', 'play_pause'."""
    mapa_teclas = {
        "subir_volume": "volumeup",
        "baixar_volume": "volumedown",
        "mutar": "volumemute",
        "play_pause": "playpause"
    }
    tecla = mapa_teclas.get(acao.lower())
    if tecla:
        if "volume" in acao.lower() and acao.lower() != "mutar":
            # Pressiona 2 vezes para dar uma diferença perceptível no volume
            for _ in range(10):
                pyautogui.press(tecla)
        else:
            pyautogui.press(tecla)
        return f"Áudio ajustado com a ação: {acao}."
    return "Ação de áudio não reconhecida."

def diagnosticar_hardware() -> str:
    """Lê o uso real de CPU e Memória RAM do computador em tempo real."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    ram_usada_gb = round(ram.used / (1024**3), 1)
    ram_total_gb = round(ram.total / (1024**3), 1)
    return f"CPU em {cpu}% | RAM: {ram_usada_gb}GB de {ram_total_gb}GB ({ram.percent}%)."

def capturar_tela_para_visao() -> str:
    """Tira um print da tela atual e salva para inspeção multimodal."""
    caminho = "visao_atual.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(caminho)
    return caminho

# Lista de ferramentas exportadas para o Gemini enxergar automaticamente
LISTA_FERRAMENTAS_PC = [
    abrir_programa_windows,
    controlar_midia_e_volume,
    diagnosticar_hardware
]
