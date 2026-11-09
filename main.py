# main.py (A.T.L.A.S. - Operação Hands-Free + Modo Debug 3A)
import traceback
from router import processar_comando_atlas
from voice_engine import falar_texto, escutar_sempre_ativo

print("\n" + "="*60)
print("   A.T.L.A.S. — AGENTE DE TECNOLOGIA, LÓGICA E AUTOMAÇÃO")
print("="*60)

falar_texto("Sistemas do Atlas online. Escuta contínua ativada, senhor.")

while True:
    try:
        comando = escutar_sempre_ativo()
        
        if not comando:
            continue

        if any(p in comando.lower() for p in ("desligar sistema", "encerrar protocolo", "pode descansar")):
            falar_texto("Encerrando protocolos do Atlas. Até logo, senhor.")
            break

        resposta = processar_comando_atlas(comando)

        if resposta:
            falar_texto(resposta)

    except KeyboardInterrupt:
        print("\n[ATLAS] Encerrado manualmente pelo usuário.")
        break
    except Exception as e:
        print("\n" + "!"*60)
        print(f"[ATLAS DEBUG - ERRO DETALHADO]: {e}")
        traceback.print_exc()
        print("!"*60 + "\n")
        falar_texto("Ocorreu uma falha técnica. Os detalhes estão no terminal, senhor.")