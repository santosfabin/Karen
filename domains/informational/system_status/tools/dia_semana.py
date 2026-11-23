from datetime import datetime

from domains.informational.system_status.tools.data import DIAS_SEMANA


def executar(frase: str = "") -> str:
    resposta = f"Hoje é {DIAS_SEMANA[datetime.now().weekday()]}."

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta
