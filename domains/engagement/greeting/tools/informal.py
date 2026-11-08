import sys
import random

sys.dont_write_bytecode = True


def executar(frase: str = ""):
    opcoes = [
        "Olá! Como posso ajudar?",
        "Oi! Em que posso ser útil?",
        "Olá. À disposição.",
        "Oi! Tudo bem? Como posso ajudar?",
        "Olá! O que deseja fazer hoje?",
        "Oi! Pronto para ajudar.",
        "Olá. No que posso ser útil agora?",
        "Oi! Diga o que você precisa.",
        "Olá. O que posso fazer por você?",
        "Oi, tudo certo? Em que posso ajudar?",
        "Olá! Sistemas prontos para você.",
        "Oi! Pode falar, estou ouvindo.",
        "Olá. Como posso te ajudar agora?",
        "Oi! Em que posso colaborar hoje?",
        "Olá! Pode dizer o seu comando.",
        "Oi. Estou pronto para ajudar.",
        "Olá! O que temos para hoje?",
        "Oi! Diga o que deseja fazer.",
        "Olá. Às suas ordens.",
        "Oi! Pronto para o próximo comando.",
    ]
    resposta = random.choice(opcoes)

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)