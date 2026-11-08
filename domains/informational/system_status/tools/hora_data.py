import sys
from domains.informational.system_status.tools import hora, data

sys.dont_write_bytecode = True


def executar(frase: str = "") -> str:
    resp_data = data.executar(frase)
    resp_hora = hora.executar(frase)
    resposta = f"{resp_data} E {resp_hora.lower()}"
    return resposta