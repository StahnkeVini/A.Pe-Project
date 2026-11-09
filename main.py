# main.py
from router import processar_comando_jarvis

print("=== A.Pe (Cérebro & Roteador Inicializados) ===")
print("Digite seus comandos (ou 'sair' para encerrar):\n")

while True:
    entrada = input("Você: ")
    if entrada.lower().strip() in ("sair", "exit", "desligar"):
        print("Âpe: Desconectando sistemas, senhor.")
        break
    if not entrada.strip():
        continue

    resposta = processar_comando_jarvis(entrada)
    print(f"\nJarvis: {resposta}\n")