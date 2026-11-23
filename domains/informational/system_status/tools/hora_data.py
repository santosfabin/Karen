from domains.informational.system_status.tools.data import formatar_data
from domains.informational.system_status.tools.hora import formatar_hora


def executar(frase: str = "") -> str:
    resposta = f"{formatar_data()} E {formatar_hora().lower()}"
    print("      " + "-" * 48)
    print(f"      -> Karen        : {resposta}")
    print("      " + "-" * 48)
    return resposta
