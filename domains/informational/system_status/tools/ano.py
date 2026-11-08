import sys
from datetime import datetime

sys.dont_write_bytecode = True


def executar(frase: str = "") -> str:
    resposta = f"Estamos em {datetime.now().year}."

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta
