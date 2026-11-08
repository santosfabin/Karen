import importlib
import io
import re
import sys
import unicodedata
from rapidfuzz import fuzz

from domains.informational.system_status.catalogo import CATALOGO_REGRAS_STATUS, AlvoStatus
from app.eventos import falar

sys.dont_write_bytecode = True

MAPEAMENTO_TOOLS = {
    AlvoStatus.HORA: "domains.informational.system_status.tools.hora",
    AlvoStatus.DATA: "domains.informational.system_status.tools.data",
    AlvoStatus.DIA: "domains.informational.system_status.tools.dia",
    AlvoStatus.MES: "domains.informational.system_status.tools.mes",
    AlvoStatus.ANO: "domains.informational.system_status.tools.ano",
    AlvoStatus.DIA_SEMANA: "domains.informational.system_status.tools.dia_semana",
    AlvoStatus.HORA_DATA: "domains.informational.system_status.tools.hora_data",
}


def _remover_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()


def identificar_alvo(frase: str) -> AlvoStatus:
    frase_limpa = _remover_acentos(frase)
    palavras = frase_limpa.split()

    melhor_score = 0.0
    alvo_encontrado = AlvoStatus.DESCONHECIDO

    # Busca N-Gram Fuzzy contra os termos cadastrados no catalogo
    for tamanho in range(len(palavras), 0, -1):
        for i in range(len(palavras) - tamanho + 1):
            trecho = " ".join(palavras[i : i + tamanho])
            for termo_catalogo, alvo in CATALOGO_REGRAS_STATUS.items():
                score = fuzz.ratio(trecho, _remover_acentos(termo_catalogo))
                if score >= 80.0 and score > melhor_score:
                    melhor_score = score
                    alvo_encontrado = alvo

    return alvo_encontrado


def _fallback_por_palavras(frase: str) -> AlvoStatus:
    """Se o catalogo nao achou nada, procura palavras-chave soltas.
    A ordem importa: 'semana' vem antes de 'dia', senao 'dia da semana' viraria so o dia."""
    palavras = set(re.findall(r"\w+", _remover_acentos(frase)))

    if "semana" in palavras:
        return AlvoStatus.DIA_SEMANA
    if palavras & {"hora", "horas", "horario"}:
        return AlvoStatus.HORA
    if "mes" in palavras:
        return AlvoStatus.MES
    if "ano" in palavras:
        return AlvoStatus.ANO
    if "data" in palavras:
        return AlvoStatus.DATA
    if "dia" in palavras:
        return AlvoStatus.DIA
    return AlvoStatus.DESCONHECIDO


def processar(frase: str, conteudo: str = None):
    alvo = identificar_alvo(frase)

    if alvo == AlvoStatus.DESCONHECIDO:
        alvo = _fallback_por_palavras(frase)
        if alvo != AlvoStatus.DESCONHECIDO:
            print("  -> Catalogo         : sem match, usei palavras-chave")

    print(f"  -> Alvo Identificado : {alvo.name}")

    if alvo == AlvoStatus.DESCONHECIDO:
        print("  -> Status            : Intencao de status nao reconhecida.")
        return

    modulo_nome = MAPEAMENTO_TOOLS.get(alvo)
    if not modulo_nome:
        print(f"  -> Status            : Nenhuma ferramenta vinculada a {alvo.name}")
        return

    try:
        modulo = importlib.import_module(modulo_nome)

        buffer = io.StringIO()
        stdout_antigo = sys.stdout
        resposta_retorno = None

        try:
            sys.stdout = buffer
            if hasattr(modulo, "executar"):
                resposta_retorno = modulo.executar(frase)
            elif hasattr(modulo, "processar"):
                resposta_retorno = modulo.processar(frase)
        finally:
            sys.stdout = stdout_antigo

        # 1. Imprime o output no terminal
        saida = buffer.getvalue()
        print(saida, end="")

        # 2. Karen fala o resultado diretamente
        if isinstance(resposta_retorno, str) and resposta_retorno.strip():
            falar(resposta_retorno.strip())
        else:
            match = re.search(r"-> Karen\s*:\s*(.+)", saida)
            if match:
                falar(match.group(1).strip())

    except ModuleNotFoundError as e:
        print(f"  -> Tool Pendente     : Modulo '{modulo_nome}' nao encontrado ({e.name}).")