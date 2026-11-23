import random


OPCOES = [
    "De nada.",
    "Por nada.",
    "Disponha.",
    "Imagina, estou aqui para ajudar.",
    "Foi um prazer.",
    "Sempre às ordens.",
    "Que isso, sem problema.",
    "Estou à disposição.",
]


def executar(frase: str = "") -> str:
    resposta = random.choice(OPCOES)

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta
