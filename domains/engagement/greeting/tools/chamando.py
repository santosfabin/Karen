import sys
import random

sys.dont_write_bytecode = True


def executar(frase: str = ""):
    opcoes = [
        "Estou aqui. Como posso ajudar?",
        "Sim, senhor. À disposição.",
        "Na escuta. Pode falar.",
        "Estou por aqui. O que deseja?",
        "Presente. Em que posso ser útil?",
        "Sim? Pode falar.",
        "Estou ouvindo. Diga o que precisa.",
        "Às suas ordens, senhor.",
        "Aqui! Como posso ajudar agora?",
        "Estou online e pronto. Pode falar.",
        "Na escuta, senhor. O que precisa?",
        "Pronto para o comando. Pode falar.",
        "Estou aqui. O que deseja fazer?",
        "À disposição. Pode falar.",
        "Sim, estou na escuta.",
        "Ouvindo. Qual o comando?",
        "Aqui! No que posso ser útil hoje?",
        "Presente e operacional. Pode falar.",
        "Estou pronto. O que manda?",
        "Sim, senhor. Ouvindo perfeitamente.",
    ]
    resposta = random.choice(opcoes)

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)