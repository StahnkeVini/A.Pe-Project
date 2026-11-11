# pc_tools.py (v2.0 - Mapa de Execução Nativa + Limpeza de Pontuação)
import os
import re
import time
import subprocess
import pyautogui
import psutil

# Mapa de atalhos diretos do Windows (Execução instantânea sem usar teclado)
MAPA_APPS_NATIVOS = {
    "calculadora": "calc.exe",
    "calc": "calc.exe",
    "bloco de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "explorador de arquivos": "explorer.exe",
    "arquivos": "explorer.exe",
    "prompt de comando": "cmd.exe",
    "terminal": "wt.exe",
    "gerenciador de tarefas": "taskmgr.exe",
    "paint": "mspaint.exe",
    "configurações": "ms-settings:",
    "configuracoes": "ms-settings:",
    "navegador": "chrome",
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "vscode": "code",
    "vs code": "code",
    "spotify": "spotify",
    "steam": "steam://open/main",
    "discord": "discord://"
}

def abrir_programa_windows(nome_programa: str) -> str:
    """Abre qualquer aplicativo instalado no Windows pelo nome."""
    # Opção 2A: Limpa pontos finais, vírgulas e espaços extras
    nome_limpo = re.sub(r"[\.\,\!\?\;\:]", "", nome_programa).lower().strip()
    
    # Remove artigos soltos no início ("o ", "a ")
    nome_limpo = re.sub(r"^(o |a |os |as )", "", nome_limpo).strip()

    # 1. Tenta abrir instantaneamente via Mapa Nativo do Windows
    if nome_limpo in MAPA_APPS_NATIVOS:
        alvo = MAPA_APPS_NATIVOS[nome_limpo]
        try:
            os.startfile(alvo)
            return f"Aplicativo '{nome_limpo}' iniciado nativamente."
        except Exception:
            pass  # Se o atalho direto falhar, cai para o menu iniciar abaixo

    # 2. Fallback para qualquer outro programa via Menu Iniciar (sem pontuação)
    pyautogui.press("win")
    time.sleep(0.35)
    pyautogui.write(nome_limpo, interval=0.04)
    time.sleep(0.25)
    pyautogui.press("enter")
    return f"Comando executado: aplicativo '{nome_limpo}' iniciado via busca."

def controlar_midia_e_volume(acao: str) -> str:
    """Controla o áudio do PC. Valores aceitos: 'subir_volume', 'baixar_volume', 'mutar', 'play_pause'."""
    mapa_teclas = {
        "subir_volume": "volumeup",
        "baixar_volume": "volumedown",
        "mutar": "volumemute",
        "play_pause": "playpause"
    }
    tecla = mapa_teclas.get(acao.lower().strip())
    if tecla:
        if "volume" in acao.lower() and acao.lower() != "mutar":
            for _ in range(5):
                pyautogui.press(tecla)
        else:
            pyautogui.press(tecla)
        return f"Áudio ajustado com a ação: {acao}."
    return "Ação de áudio não reconhecida."

def diagnosticar_hardware() -> str:
    """Lê o uso real de CPU e Memória RAM do computador em tempo real."""
    cpu = psutil.cpu_percent(interval=0.4)
    ram = psutil.virtual_memory()
    ram_usada_gb = round(ram.used / (1024**3), 1)
    ram_total_gb = round(ram.total / (1024**3), 1)
    return f"CPU em {cpu} por cento. Memória RAM usando {ram_usada_gb} gigas de {ram_total_gb} gigas."

def capturar_tela_para_visao() -> str:
    """Captura a tela e salva uma versão JPEG otimizada."""
    caminho = "visao_atual.jpg"

    screenshot = pyautogui.screenshot()
    screenshot.thumbnail((1280, 720))

    if screenshot.mode != "RGB":
        screenshot = screenshot.convert("RGB")

    screenshot.save(
        caminho,
        format="JPEG",
        quality=88,
        optimize=False,
        progressive=False
    )

    return caminho

LISTA_FERRAMENTAS_PC = [
    abrir_programa_windows,
    controlar_midia_e_volume,
    diagnosticar_hardware
]