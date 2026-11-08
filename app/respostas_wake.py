import random
import sys

sys.dont_write_bytecode = True

RESPOSTAS = [
    "Sim?",
    "Pois não.",
    "Estou ouvindo.",
    "Pode falar.",
    "Diga.",
    "Aqui.",
    "Sim, estou aqui.",
    "Pode dizer.",
    "Na escuta.",
    "Pode mandar.",
    "Sim, pode falar.",
    "Estou aqui.",
    "Diga o que precisa.",
    "Fale.",
    "Pois não, pode falar.",
    "Às ordens.",
    "Estou te ouvindo.",
    "Oi. Pode falar.",
    "Sim, o que manda?",
    "Qual o comando?",
    "Aqui. Pode falar.",
    "Pode falar, estou ouvindo.",
    "Sim, senhor.",
    "Pois não. Estou ouvindo.",
]

_ultima = None


def escolher() -> str:
    """Sorteia uma resposta, sem repetir a anterior."""
    global _ultima
    opcoes = [r for r in RESPOSTAS if r != _ultima]
    _ultima = random.choice(opcoes)
    return _ultima