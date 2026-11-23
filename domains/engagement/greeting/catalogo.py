from enum import Enum



class AlvoSaudacao(Enum):
    SAUDACAO_HORARIO = "saudacao_horario"
    SAUDACAO_INFORMAL = "saudacao_informal"
    SAUDACAO_CHAMANDO = "saudacao_chamando"
    COMO_VAI = "como_vai"
    AGRADECIMENTO = "agradecimento"
    DESPEDIDA = "despedida"
    DESCONHECIDO = "desconhecido"