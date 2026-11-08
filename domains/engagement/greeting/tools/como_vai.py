import sys
import random

sys.dont_write_bytecode = True


def executar(frase: str = ""):
    opcoes = [
        "Tudo bem por aqui, obrigado. E com você?",
        "Tudo certo! Como posso ajudar você hoje?",
        "Tudo em ordem e operacional. Como você está?",
        "Vou bem, obrigado por perguntar. E você?",
        "Tudo ótimo por aqui! No que posso ser útil?",
        "Tudo sob controle por aqui. Como vão as coisas com você?",
        "Tudo tranquilo! Pronto para te ajudar.",
        "Tudo em paz. E por aí, tudo bem?",
        "Por aqui está tudo funcionando perfeitamente. E você?",
        "Tudo certo por aqui. O que deseja fazer agora?",
        "Tudo bem, senhor. Como você está hoje?",
        "Tudo em ordem. O que temos para hoje?",
        "Estou ótimo, obrigado. Como posso ajudar agora?",
        "Tudo ótimo! Espero que seu dia esteja indo bem.",
        "Tudo tranquilo por aqui. Em que posso ser útil?",
        "Todos os sistemas operacionais e em ordem. Como vai você?",
        "Vou muito bem, pronto para trabalhar. E você?",
        "Tudo certo por aqui, pronto para o próximo comando.",
        "Tudo bem! Como posso te ajudar hoje?",
        "Tudo em ordem por aqui, senhor. Como estão as coisas?",
    ]
    resposta = random.choice(opcoes)

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)