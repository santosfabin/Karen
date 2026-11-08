import sys
import random
from datetime import datetime

sys.dont_write_bytecode = True


def executar(frase: str = ""):
    hora_atual = datetime.now().hour

    if 5 <= hora_atual < 12:
        opcoes = [
            "Bom dia.",
            "Bom dia.",
            "Bom dia.",
            "Bom dia, senhor.",
            "Bom dia. Como posso ajudar?",
            "Bom dia. Em que posso ser útil?",
            "Bom dia. O que temos para hoje?",
            "Bom dia. Pronto para começar quando quiser.",
            "Bom dia. Pode falar.",
            "Bom dia. À disposição.",
            "Bom dia. Por onde começamos?",
            "Bom dia. Qual é o plano de hoje?",
            "Bom dia. Estou ouvindo.",
            "Bom dia. Como foi a noite?",
            "Bom dia. Dormiu bem?",
            "Bom dia. Vamos ao trabalho?",
            "Bom dia. Pronto para o que precisar.",
            "Bom dia. O que vamos fazer primeiro?",
            "Bom dia. No que posso ajudar?",
            "Bom dia. Pode mandar.",
        ]
    elif 12 <= hora_atual < 18:
        opcoes = [
            "Boa tarde.",
            "Boa tarde.",
            "Boa tarde.",
            "Boa tarde, senhor.",
            "Boa tarde. Como posso ajudar?",
            "Boa tarde. Em que posso ser útil?",
            "Boa tarde. O que temos para agora?",
            "Boa tarde. Pronto para o próximo comando.",
            "Boa tarde. Pode falar.",
            "Boa tarde. À disposição.",
            "Boa tarde. Por onde seguimos?",
            "Boa tarde. Qual é o plano?",
            "Boa tarde. Estou ouvindo.",
            "Boa tarde. Como está sendo o dia?",
            "Boa tarde. Já almoçou?",
            "Boa tarde. Vamos continuar?",
            "Boa tarde. Pronto para o que precisar.",
            "Boa tarde. O que vamos fazer agora?",
            "Boa tarde. No que posso ajudar?",
            "Boa tarde. Pode mandar.",
        ]
    else:
        opcoes = [
            "Boa noite.",
            "Boa noite.",
            "Boa noite.",
            "Boa noite, senhor.",
            "Boa noite. Como posso ajudar?",
            "Boa noite. Em que posso ser útil?",
            "Boa noite. O que temos para hoje?",
            "Boa noite. Pronto para o próximo comando.",
            "Boa noite. Pode falar.",
            "Boa noite. À disposição.",
            "Boa noite. Por onde começamos?",
            "Boa noite. Qual é o plano?",
            "Boa noite. Estou ouvindo.",
            "Boa noite. Como foi o dia?",
            "Boa noite. Trabalhando até tarde?",
            "Boa noite. Vamos ao trabalho?",
            "Boa noite. Pronto para o que precisar.",
            "Boa noite. O que vamos fazer agora?",
            "Boa noite. No que posso ajudar?",
            "Boa noite. Pode mandar.",
        ]

    resposta = random.choice(opcoes)

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)