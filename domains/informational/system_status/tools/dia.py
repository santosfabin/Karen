from datetime import datetime



def executar(frase: str = "") -> str:
    dia = datetime.now().day
    dia_texto = "primeiro" if dia == 1 else str(dia)
    resposta = f"Hoje é dia {dia_texto}."

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta
