import sys
import unicodedata
from rapidfuzz import fuzz

from domains.transactional.create.note.catalogo import (
    CATALOGO_REGRAS_NOTA,
    TipoNota,
)

sys.dont_write_bytecode = True


def _remover_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()


def identificar_tipo_nota(frase: str) -> TipoNota:
    """Identifica o tipo exato da nota via fuzzy matching no catálogo.
    Caso nenhum padrão específico seja detectado, assume SIMPLES por padrão.
    """
    frase_limpa = _remover_acentos(frase)
    palavras = frase_limpa.split()

    melhor_score = 0.0
    tipo_encontrado = None

    # Busca Fuzzy de N-Grams contra os termos cadastrados no catálogo de notas
    for tamanho in range(3, 0, -1):
        for i in range(len(palavras) - tamanho + 1):
            trecho = " ".join(palavras[i : i + tamanho])
            for termo_catalogo, tipo in CATALOGO_REGRAS_NOTA.items():
                score = fuzz.ratio(trecho, _remover_acentos(termo_catalogo))
                if score > melhor_score and score >= 80.0:
                    melhor_score = score
                    tipo_encontrado = tipo

    # Se identificou um tipo explicitamente com confiança, retorna ele
    if tipo_encontrado:
        return tipo_encontrado

    # Fallback padrão: se não especificou, é nota SIMPLES
    return TipoNota.SIMPLES