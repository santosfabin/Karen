import sys
import random

sys.dont_write_bytecode = True


def executar(frase: str = ""):
    opcoes = [
        "Até mais, senhor. Ficarei em espera se precisar.",
        "Até logo! Tenha um ótimo dia.",
        "Até mais. Qualquer coisa, é só chamar.",
        "Até logo! Bom descanso.",
        "Até a próxima, senhor. Estarei por aqui.",
        "Tchau! Tenha um excelente dia.",
        "Até mais! Se precisar de mim, estou aqui.",
        "Até logo, senhor. Sistemas em espera.",
        "Até a próxima! Qualquer coisa estou à disposição.",
        "Tchau! Fico no aguardo do próximo comando.",
        "Até mais. Tenha um bom descanso.",
        "Até logo. Estarei por aqui quando voltar.",
        "Até mais ver, senhor. Bom trabalho.",
        "Até a próxima. Tenha uma ótima semana.",
        "Tchau, senhor. Até breve.",
        "Até logo! Continue com um bom dia.",
        "Até mais. Encerrando por agora.",
        "Até a próxima, senhor. Estarei sempre por aqui.",
        "Tchau! Conte comigo quando precisar.",
        "Até logo! Ficarei de prontidão.",
    ]
    resposta = random.choice(opcoes)

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)