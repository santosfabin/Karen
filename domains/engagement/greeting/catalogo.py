import sys
from enum import Enum

sys.dont_write_bytecode = True


class AlvoSaudacao(Enum):
    SAUDACAO_HORARIO = "saudacao_horario"
    SAUDACAO_INFORMAL = "saudacao_informal"
    SAUDACAO_CHAMANDO = "saudacao_chamando"
    COMO_VAI = "como_vai"
    AGRADECIMENTO = "agradecimento"
    DESPEDIDA = "despedida"
    DESCONHECIDO = "desconhecido"