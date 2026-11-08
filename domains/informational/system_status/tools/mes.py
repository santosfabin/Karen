import sys
from datetime import datetime

sys.dont_write_bytecode = True

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def executar(frase: str = "") -> str:
    mes = MESES[datetime.now().month - 1]
    resposta = f"Estamos em {mes}."

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta
