from datetime import datetime



def formatar_hora() -> str:
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
        return f"Agora é {texto_hora} em ponto." if hora in (0, 1, 12) else f"Agora são {texto_hora} em ponto."
    if minuto == 1:
        return f"Agora é {texto_hora} e um minuto." if hora in (0, 1, 12) else f"Agora são {texto_hora} e um minuto."
    return f"Agora é {texto_hora} e {minuto} minutos." if hora in (0, 1, 12) else f"Agora são {texto_hora} e {minuto} minutos."


def executar(frase: str = "") -> str:
    resposta = formatar_hora()

    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta