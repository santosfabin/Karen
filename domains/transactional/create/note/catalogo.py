import sys
from enum import Enum

sys.dont_write_bytecode = True


class TipoNota(Enum):
    SIMPLES = "SIMPLES"      # Fallback padrão / TXT / Bloco de notas
    MARKDOWN = "MARKDOWN"    # Notas ricas / formatadas / .md


# Termo -> Tipo de Nota
CATALOGO_REGRAS_NOTA = {
    # --- Gatilhos Explícitos de Markdown ---
    "markdown": TipoNota.MARKDOWN,
    "md": TipoNota.MARKDOWN,
    "formatada": TipoNota.MARKDOWN,
    "formatado": TipoNota.MARKDOWN,
    "documento md": TipoNota.MARKDOWN,
    "texto formatado": TipoNota.MARKDOWN,
    "nota rica": TipoNota.MARKDOWN,

    # --- Gatilhos Explícitos de Simples / TXT ---
    "txt": TipoNota.SIMPLES,
    "simples": TipoNota.SIMPLES,
    "bloco de notas": TipoNota.SIMPLES,
    "rapida": TipoNota.SIMPLES,
    "rapido": TipoNota.SIMPLES,
    "rascunho": TipoNota.SIMPLES,
    "postit": TipoNota.SIMPLES,
    "post-it": TipoNota.SIMPLES,
}