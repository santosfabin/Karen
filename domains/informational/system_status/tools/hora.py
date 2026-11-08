import sys
from datetime import datetime

sys.dont_write_bytecode = True


def executar(frase: str = "") -> str:
    agora = datetime.now()
    hora = agora.hour
    minuto = agora.minute

    # Formatação natural para o Kokoro sintetizar de forma perfeita
    if hora == 0:
        texto_hora = "meia-noite"
    elif hora == 1:
        texto_hora = "uma hora"
    elif hora == 12:
        texto_hora = "meio-dia"
    else:
        texto_hora = f"{hora} horas"

    if minuto == 0:
        resposta = f"Agora é {texto_hora} em ponto." if hora in (0, 1, 12) else f"Agora são {texto_hora} em ponto."
    elif minuto == 1:
        resposta = f"Agora é {texto_hora} e um minuto." if hora in (0, 1, 12) else f"Agora são {texto_hora} e um minuto."
    else:
        resposta = f"Agora é {texto_hora} e {minuto} minutos." if hora in (0, 1, 12) else f"Agora são {texto_hora} e {minuto} minutos."

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta