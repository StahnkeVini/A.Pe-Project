# router.py (v2.0 - Com Chat AFC + gemini-3.5-flash-lite)
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from pc_tools import (
    abrir_programa_windows,
    controlar_midia_e_volume,
    diagnosticar_hardware,
    capturar_tela_para_visao,
    LISTA_FERRAMENTAS_PC
)

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = (
    "Você é ATLAS, um sistema operacional agêntico avançado. "
    "Responda em português de forma concisa, precisa, elegante e levemente sagaz. "
    "Sempre que o usuário pedir uma ação no computador (abrir apps, controlar música/volume, "
    "ou checar hardware), acione a função correspondente imediatamente."
)

# Criamos a sessão de Chat persistente para o TIER 1 (Resolve o aviso de AFC e mantém memória!)
sessao_chat_leve = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=LISTA_FERRAMENTAS_PC,
        temperature=0.3
    )
)

# Contador global para o MIT Maker Portfolio
metricas_sessao = {
    "comandos_totais": 0,
    "resolvidos_zero_token": 0,
    "tokens_poupados_estimados": 0
}

def processar_comando_atlas(texto_usuario: str) -> str:
    inicio = time.perf_counter()
    cmd = texto_usuario.lower().strip()
    metricas_sessao["comandos_totais"] += 1

    rota_usada = ""
    resposta_final = ""

    # =========================================================================
    # TIER 0: ROTEAMENTO DETERMINÍSTICO LOCAL (0 TOKENS | LATÊNCIA < 50ms)
    # =========================================================================
    if cmd.startswith(("abre o ", "abrir ", "inicia o ", "iniciar ")):
        for prefixo in ("abre o ", "abrir ", "inicia o ", "iniciar "):
            if cmd.startswith(prefixo):
                app = cmd.replace(prefixo, "").strip()
                break
        abrir_programa_windows(app)
        rota_usada = "TIER 0 (Local Determinístico - 0 Tokens)"
        metricas_sessao["resolvidos_zero_token"] += 1
        metricas_sessao["tokens_poupados_estimados"] += 350
        resposta_final = f"Iniciando {app} imediatamente, senhor."

    elif cmd in ("status do sistema", "diagnóstico", "uso do pc", "como está o hardware"):
        dados = diagnosticar_hardware()
        rota_usada = "TIER 0 (Telemetria Local Direta - 0 Tokens)"
        metricas_sessao["resolvidos_zero_token"] += 1
        metricas_sessao["tokens_poupados_estimados"] += 350
        resposta_final = f"Sistemas operando normalmente. {dados}"

    elif any(p in cmd for p in (
        "aumenta o volume", "subir volume", "abaixa o volume", "mutar som",
        "pausar musica", "pausar música", "pausa a musica", "continue a musica",
        "continuar musica", "continuar música", "tocar musica"
    )) and len(cmd.split()) <= 5:
        if "aumenta" in cmd or "subir" in cmd:
            controlar_midia_e_volume("subir_volume")
        elif "abaixa" in cmd:
            controlar_midia_e_volume("baixar_volume")
        elif "mutar" in cmd:
            controlar_midia_e_volume("mutar")
        else:
            controlar_midia_e_volume("play_pause")
            
        rota_usada = "TIER 0 (Controle de Mídia Local - 0 Tokens)"
        metricas_sessao["resolvidos_zero_token"] += 1
        metricas_sessao["tokens_poupados_estimados"] += 350
        resposta_final = "Comando de mídia executado, senhor."

    # =========================================================================
    # TIER 2: VISÃO MULTIMODAL + RACIOCÍNIO PROFUNDO (GEMINI 2.5 FLASH)
    # =========================================================================
    elif any(gatilho in cmd for gatilho in ("minha tela", "olhe isso", "analise a tela", "erro na tela")):
        rota_usada = "TIER 2 (Visão Multimodal - gemini-2.5-flash)"
        caminho_img = capturar_tela_para_visao()
        imagem = Image.open(caminho_img)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[imagem, texto_usuario],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3
            )
        )
        resposta_final = response.text

    # =========================================================================
    # TIER 1: AGENTE COM CHAT AFC E MEMÓRIA (GEMINI 3.5 FLASH-LITE)
    # =========================================================================
    else:
        rota_usada = "TIER 1 (Chat AFC + Tools - gemini-3.5-flash-lite)"
        # Usa send_message na sessão de chat conforme recomendado pelo SDK!
        response = sessao_chat_leve.send_message(texto_usuario)
        resposta_final = response.text

    # Cálculo de telemetria em milissegundos
    latencia_ms = round((time.perf_counter() - inicio) * 1000, 1)
    taxa_economia = round((metricas_sessao["resolvidos_zero_token"] / metricas_sessao["comandos_totais"]) * 100, 1)

    print("\n" + "="*65)
    print(f"[TELEMETRIA ATLAS] Rota: {rota_usada}")
    print(f"[LATÊNCIA] {latencia_ms} ms | [ECONOMIA DE API] {taxa_economia}% resolvidos localmente (~{metricas_sessao['tokens_poupados_estimados']} tokens poupados)")
    print("="*65)

    return resposta_final