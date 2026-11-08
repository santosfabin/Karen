import importlib
import sys
import unicodedata
import dateparser.search
from rapidfuzz import fuzz
from text_to_num import alpha2digit

from domains.transactional.create.catalogo import CATALOGO_REGRAS_CRIAR, AlvoCriar

sys.dont_write_bytecode = True


def _remover_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()


def _extrair_parametros(frase: str) -> set:
    """Extrai parâmetros de tempo usando dateparser."""
    parametros = set()

    try:
        frase_normalizada = alpha2digit(frase, "pt")
    except Exception:
        frase_normalizada = frase

    # Configuração livre para capturar qualquer menção temporal
    matches_tempo = dateparser.search.search_dates(
        frase_normalizada,
        languages=["pt"],
        settings={
            "PREFER_DATES_FROM": "future",
            "DATE_ORDER": "DMY",
        }
    )

    print(f"    [DEBUG] Matches de Tempo : {matches_tempo}")

    if matches_tempo:
        parametros.add("TEMPO")

    return parametros


PASTAS_ALVO = {"NOTA": "note", "AGENDA": "schedule", "DEVOPS": "devops"}


def identificar_alvo(frase: str) -> AlvoCriar:
    """Identifica o alvo resolvendo termos fuzzy + parâmetros contra o catálogo."""
    frase_limpa = _remover_acentos(frase)
    palavras = frase_limpa.split()
    parametros_presentes = _extrair_parametros(frase)

    print(f"    [DEBUG] Parâmetros       : {parametros_presentes}")

    melhor_score = 0.0
    regra_encontrada = None
    termo_vencedor = None

    # Busca Fuzzy de N-Grams contra os termos cadastrados no catálogo
    for tamanho in range(3, 0, -1):
        for i in range(len(palavras) - tamanho + 1):
            trecho = " ".join(palavras[i : i + tamanho])
            for termo_catalogo, regra in CATALOGO_REGRAS_CRIAR.items():
                score = fuzz.ratio(trecho, _remover_acentos(termo_catalogo))
                
                # Dá preferência para termos diretos ou scores maiores
                if score >= 80.0:
                    eh_termo_direto = isinstance(regra, AlvoCriar)
                    regra_atual_eh_direta = isinstance(regra_encontrada, AlvoCriar)

                    # Atualiza se tiver score maior OU se tiver o mesmo score mas for termo direto
                    if (score > melhor_score) or (score == melhor_score and eh_termo_direto and not regra_atual_eh_direta):
                        melhor_score = score
                        regra_encontrada = regra
                        termo_vencedor = termo_catalogo

    print(f"    [DEBUG] Termo Match      : '{termo_vencedor}' (Score: {melhor_score:.1f})")

    if not regra_encontrada:
        return AlvoCriar.DESCONHECIDO

    # Resolução de Mapeamento Direto
    if isinstance(regra_encontrada, AlvoCriar):
        return regra_encontrada

    # Resolução por Parâmetros Condicionais (ex: Lembrete com TEMPO -> AGENDA)
    if isinstance(regra_encontrada, dict):
        for param, alvo in regra_encontrada.items():
            if param in parametros_presentes:
                return alvo
        return regra_encontrada.get(None, AlvoCriar.DESCONHECIDO)

    return AlvoCriar.DESCONHECIDO


def processar(frase: str, conteudo: str = None):
    alvo = identificar_alvo(frase)

    print(f"  -> Alvo Identificado : {alvo.name}")

    if alvo == AlvoCriar.DESCONHECIDO or alvo.name == "DESCONHECIDO":
        print("  -> Status            : Falha ao determinar o módulo de criação.")
        return

    modulo_nome = f"domains.transactional.create.{PASTAS_ALVO.get(alvo.name, alvo.name.lower())}.index"

    try:
        modulo = importlib.import_module(modulo_nome)
        if hasattr(modulo, "processar"):
            try:
                modulo.processar(frase, conteudo=conteudo)
            except TypeError:
                modulo.processar(frase)
        else:
            print(f"  -> Erro              : {modulo_nome} não possui 'processar(frase)'.")
    except ModuleNotFoundError as e:
        print(f"  -> Modulo Pendente   : {modulo_nome} ainda não implementado ({e.name}).")