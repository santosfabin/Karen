from datetime import datetime



def executar(frase: str = "") -> str:
    resposta = f"Estamos em {datetime.now().year}."

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta
