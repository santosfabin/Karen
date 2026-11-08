import sys
from enum import Enum

sys.dont_write_bytecode = True


class AlvoStatus(Enum):
    HORA = "HORA"
    DATA = "DATA"              # data completa, por extenso
    DIA = "DIA"                # so o dia do mes
    MES = "MES"
    ANO = "ANO"
    DIA_SEMANA = "DIA_SEMANA"
    HORA_DATA = "HORA_DATA"
    DESCONHECIDO = "DESCONHECIDO"


# Termos -> Alvo Atomico
CATALOGO_REGRAS_STATUS = {
    # --- Hora ---
    "que horas sao": AlvoStatus.HORA,
    "que horas": AlvoStatus.HORA,
    "horas": AlvoStatus.HORA,
    "hora": AlvoStatus.HORA,
    "horario": AlvoStatus.HORA,
    "horario atual": AlvoStatus.HORA,
    "me da a hora": AlvoStatus.HORA,
    "sabe que horas sao": AlvoStatus.HORA,
    "hora agora": AlvoStatus.HORA,

    # --- Dia do mes (so o dia) ---
    "que dia e hoje": AlvoStatus.DIA,
    "que dia e": AlvoStatus.DIA,
    "hoje e dia quanto": AlvoStatus.DIA,
    "dia quanto e hoje": AlvoStatus.DIA,
    "a quantos estamos": AlvoStatus.DIA,
    "que dia do mes": AlvoStatus.DIA,
    "que dia do mes e hoje": AlvoStatus.DIA,
    "dia do mes": AlvoStatus.DIA,
    "em que dia estamos": AlvoStatus.DIA,

    # --- Data completa ---
    "data completa": AlvoStatus.DATA,
    "data por extenso": AlvoStatus.DATA,
    "dia completo": AlvoStatus.DATA,
    "dia por inteiro": AlvoStatus.DATA,
    "data de hoje": AlvoStatus.DATA,
    "qual e a data": AlvoStatus.DATA,
    "qual a data de hoje": AlvoStatus.DATA,
    "data atual": AlvoStatus.DATA,
    "data": AlvoStatus.DATA,

    # --- Mes ---
    "que mes e": AlvoStatus.MES,
    "que mes e hoje": AlvoStatus.MES,
    "que mes estamos": AlvoStatus.MES,
    "em que mes estamos": AlvoStatus.MES,
    "mes atual": AlvoStatus.MES,
    "qual e o mes": AlvoStatus.MES,
    "qual o mes atual": AlvoStatus.MES,

    # --- Ano ---
    "que ano e": AlvoStatus.ANO,
    "que ano e hoje": AlvoStatus.ANO,
    "que ano estamos": AlvoStatus.ANO,
    "em que ano estamos": AlvoStatus.ANO,
    "ano atual": AlvoStatus.ANO,
    "qual e o ano": AlvoStatus.ANO,
    "qual o ano atual": AlvoStatus.ANO,

    # --- Dia da Semana ---
    "que dia da semana": AlvoStatus.DIA_SEMANA,
    "que dia da semana e hoje": AlvoStatus.DIA_SEMANA,
    "dia da semana": AlvoStatus.DIA_SEMANA,
    "hoje e que dia da semana": AlvoStatus.DIA_SEMANA,
    "qual o dia da semana": AlvoStatus.DIA_SEMANA,

    # --- Hora + Data Juntos ---
    "que dia e que horas sao": AlvoStatus.HORA_DATA,
    "hora e data": AlvoStatus.HORA_DATA,
    "data e hora": AlvoStatus.HORA_DATA,
    "dia e horario": AlvoStatus.HORA_DATA,
}