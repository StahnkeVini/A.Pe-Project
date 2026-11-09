# main.py
from router import processar_comando_atlas

print("=== ATLAS (Cérebro & Roteador Inicializados) ===")
print("Digite seus comandos (ou 'sair' para encerrar):\n")

while True:
    entrada = input("Você: ")
    if entrada.lower().strip() in ("sair", "exit", "desligar"):
        print("Atlas: Desconectando sistemas, senhor.")
        break
    if not entrada.strip():
        continue

    resposta = processar_comando_atlas(entrada)
    print(f"\nAtlas: {resposta}\n")