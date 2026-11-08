import sys
from datetime import datetime

sys.dont_write_bytecode = True

DIAS_SEMANA = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


def executar(frase: str = "") -> str:
    agora = datetime.now()
    dia_semana = DIAS_SEMANA[agora.weekday()]
    dia = agora.day
    mes = MESES[agora.month - 1]
    ano = agora.year

    dia_texto = "primeiro" if dia == 1 else str(dia)
    resposta = f"Hoje é {dia_semana}, dia {dia_texto} de {mes} de {ano}."

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta