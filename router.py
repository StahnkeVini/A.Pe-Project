# router.py (v3.1 - gemini-3.8-flash na Visão + Limpeza de Pontuação)
import os
import re
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
from voice_engine import falar_texto

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# CONFIGURAÇÕES DE DESEMPENHO DA VISÃO

VISION_MODEL = "gemini-3.5-flash-lite"

VISION_RESOLUTION = types.MediaResolution.MEDIA_RESOLUTION_MEDIUM

VISION_THINKING_LEVEL = "low"


SYSTEM_PROMPT = (
    "Você é A.T.L.A.S. (Agente de Tecnologia, Lógica, Automação e Sistemas), "
    "um sistema operacional agêntico avançado. "
    "REGRAS DE RESPOSTA PARA VOZ: Responda SEMPRE em português, em no máximo 2 frases curtas, "
    "diretas, elegantes e sem usar asteriscos, listas ou formatação Markdown. "
    "Sempre que o usuário pedir uma ação no computador (abrir apps, música/volume, hardware), "
    "acione a ferramenta correspondente imediatamente."
)

sessao_chat_leve = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=LISTA_FERRAMENTAS_PC,
        temperature=0.3
    )
)

metricas_sessao = {
    "comandos_totais": 0,
    "resolvidos_zero_token": 0,
    "tokens_poupados_estimados": 0
}

def processar_comando_atlas(texto_usuario: str) -> str:
    inicio = time.perf_counter()
    # Limpa pontos finais e interrogações para facilitar o casamento exato no Tier 0
    cmd = re.sub(r"[\.\!\?]+$", "", texto_usuario.lower().strip()).strip()
    metricas_sessao["comandos_totais"] += 1

    rota_usada = ""
    resposta_final = ""

    # =========================================================================
    # TIER 0: ROTEAMENTO DETERMINÍSTICO LOCAL (0 TOKENS | LATÊNCIA < 50ms)
    # =========================================================================
    prefixos_abrir = ("abre o ", "abre a ", "abra o ", "abra a ", "abrir ", "inicia o ", "iniciar ")
    if cmd.startswith(prefixos_abrir):
        app = cmd
        for prefixo in prefixos_abrir:
            if cmd.startswith(prefixo):
                app = cmd[len(prefixo):].strip()
                break
        abrir_programa_windows(app)
        rota_usada = "TIER 0 (Local Determinístico - 0 Tokens)"
        metricas_sessao["resolvidos_zero_token"] += 1
        metricas_sessao["tokens_poupados_estimados"] += 350
        resposta_final = f"Iniciando {app} imediatamente, senhor."

    elif any(p in cmd for p in ("status do sistema", "diagnóstico", "uso do pc", "como está o hardware")):
        dados = diagnosticar_hardware()
        rota_usada = "TIER 0 (Telemetria Local Direta - 0 Tokens)"
        metricas_sessao["resolvidos_zero_token"] += 1
        metricas_sessao["tokens_poupados_estimados"] += 350
        resposta_final = f"Sistemas operando normalmente. {dados}"

    elif any(p in cmd for p in (
        "aumenta o volume", "subir volume", "abaixa o volume", "mutar som",
        "pausar musica", "pausar música", "pausa a musica", "pausa a música",
        "continue a musica", "continue a música", "continuar musica", "continuar música", "tocar musica"
    )) and len(cmd.split()) <= 6:
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
    # TIER 2: VISÃO MULTIMODAL + FEEDBACK SONORO 3B (GEMINI 3.8 FLASH)
    # =========================================================================
        # TIER 2: VISÃO MULTIMODAL OTIMIZADA
    elif any(gatilho in cmd for gatilho in (
        "minha tela",
        "olhe isso",
        "analise a tela",
        "erro na tela",
        "o que está na tela",
        "olhe minha tela"
    )):

        rota_usada = f"TIER 2 (Visão - {VISION_MODEL})"

        inicio_visao = time.perf_counter()

        # 1. Confirmação por voz
        inicio_ack = time.perf_counter()

        falar_texto("Analisando sua tela agora, senhor.")

        ack_ms = (time.perf_counter() - inicio_ack) * 1000

        # 2. Captura da tela
        inicio_captura = time.perf_counter()

        caminho_img = capturar_tela_para_visao()

        captura_ms = (time.perf_counter() - inicio_captura) * 1000

        tamanho_kb = os.path.getsize(caminho_img) / 1024

        # 3. Preparação da imagem
        inicio_abertura = time.perf_counter()

        with Image.open(caminho_img) as imagem_aberta:
            imagem = imagem_aberta.convert("RGB")

        abertura_ms = (time.perf_counter() - inicio_abertura) * 1000

        # 4. Ajuste de raciocínio
        termos_complexos = (
            "detalhadamente",
            "análise profunda",
            "debug",
            "depure",
            "investigue",
            "compare"
        )

        nivel_raciocinio = (
            "medium"
            if any(t in cmd for t in termos_complexos)
            else VISION_THINKING_LEVEL
        )

        # 5. Envio para Gemini
        inicio_api = time.perf_counter()

        response = client.models.generate_content(
            model=VISION_MODEL,
            contents=[imagem, texto_usuario],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                media_resolution=VISION_RESOLUTION,
                thinking_config=types.ThinkingConfig(
                    thinking_level=nivel_raciocinio
                )
            )
        )

        api_ms = (time.perf_counter() - inicio_api) * 1000

        resposta_final = (
            response.text
            or "Não consegui extrair uma resposta da análise visual."
        )

        # 6. Métricas
        total_ms = (time.perf_counter() - inicio_visao) * 1000

        usage = getattr(response, "usage_metadata", None)

        print("\n" + "=" * 65)
        print("[ATLAS VISÃO - TELEMETRIA]")
        print(f"Modelo: {VISION_MODEL}")
        print(f"Raciocínio: {nivel_raciocinio}")
        print(f"Confirmação por voz: {ack_ms:.1f} ms")
        print(f"Captura da tela: {captura_ms:.1f} ms")
        print(f"Preparação da imagem: {abertura_ms:.1f} ms")
        print(f"Tamanho da imagem: {tamanho_kb:.1f} KB")
        print(f"Tempo da API Gemini: {api_ms:.1f} ms")
        print(f"Tokens de pensamento: "
    f"{getattr(usage, 'thoughts_token_count', 'N/D')}")
        print(f"Tempo total: {total_ms:.1f} ms")

        if usage:
            print(
                f"Tokens de entrada: "
                f"{getattr(usage, 'prompt_token_count', 'N/D')}"
            )
            print(
                f"Tokens de saída: "
                f"{getattr(usage, 'candidates_token_count', 'N/D')}"
            )

        print("=" * 65)

    # =========================================================================
    # TIER 1: AGENTE COM CHAT AFC E MEMÓRIA (GEMINI 3.5 FLASH-LITE)
    # =========================================================================
    else:
        rota_usada = "TIER 1 (Chat AFC + Tools - gemini-3.5-flash-lite)"
        response = sessao_chat_leve.send_message(texto_usuario)
        resposta_final = response.text

    latencia_ms = round((time.perf_counter() - inicio) * 1000, 1)
    taxa_economia = round((metricas_sessao["resolvidos_zero_token"] / metricas_sessao["comandos_totais"]) * 100, 1)

    print("\n" + "="*68)
    print(f"[TELEMETRIA A.T.L.A.S.] Rota: {rota_usada}")
    print(f"[COMANDO PROCESSADO]: '{cmd}'")
    print(f"[LATÊNCIA] {latencia_ms} ms | [ECONOMIA DE API] {taxa_economia}% locais (~{metricas_sessao['tokens_poupados_estimados']} tokens poupados)")
    print("="*68)

    return resposta_final