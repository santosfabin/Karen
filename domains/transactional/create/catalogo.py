import sys
from enum import Enum

sys.dont_write_bytecode = True


class AlvoCriar(Enum):
    NOTA = {
        "alvo": "NOTA",
        "filhos": None
    }
    AGENDA = {
        "alvo": "AGENDA",
        "filhos": {
            "TEMPO": "TEMPO",
        }
    }
    DEVOPS = {
        "alvo": "DEVOPS",
        "filhos": {
            "NOME": "NOME"
        }
    }
    DESCONHECIDO = {
        "alvo": "DESCONHECIDO",
        "filhos": None
    }


# Termo -> Alvo direto OU Dicionário de Parâmetro -> Alvo
CATALOGO_REGRAS_CRIAR = {
    # --- Termos Diretos (Sem filhos/parâmetros necessários) ---
    "anotacao": AlvoCriar.NOTA,
    "anotação": AlvoCriar.NOTA,
    "anota": AlvoCriar.NOTA,
    "anote": AlvoCriar.NOTA,
    "anotar": AlvoCriar.NOTA,
    "nota": AlvoCriar.NOTA,
    "txt": AlvoCriar.NOTA,
    "markdown": AlvoCriar.NOTA,
    "md": AlvoCriar.NOTA,
    "bloco de notas": AlvoCriar.NOTA,
    "rascunho": AlvoCriar.NOTA,
    "ata": AlvoCriar.NOTA,
    "documento": AlvoCriar.NOTA,
    "resumo": AlvoCriar.NOTA,
    "memo": AlvoCriar.NOTA,
    "memorando": AlvoCriar.NOTA,
    "postit": AlvoCriar.NOTA,
    "post-it": AlvoCriar.NOTA,
    "texto": AlvoCriar.NOTA,

    "agenda": AlvoCriar.AGENDA,
    "agendamento": AlvoCriar.AGENDA,
    "reuniao": AlvoCriar.AGENDA,
    "reunião": AlvoCriar.AGENDA,
    "compromisso": AlvoCriar.AGENDA,
    "evento": AlvoCriar.AGENDA,
    "consulta": AlvoCriar.AGENDA,
    "jantar": AlvoCriar.AGENDA,
    "horario": AlvoCriar.AGENDA,
    "horário": AlvoCriar.AGENDA,

    "repositorio": AlvoCriar.DEVOPS,
    "repositório": AlvoCriar.DEVOPS,
    "repo": AlvoCriar.DEVOPS,
    "branch": AlvoCriar.DEVOPS,
    "pod": AlvoCriar.DEVOPS,
    "container": AlvoCriar.DEVOPS,
    "docker": AlvoCriar.DEVOPS,
    "kubernetes": AlvoCriar.DEVOPS,
    "servidor": AlvoCriar.DEVOPS,
    "lista": AlvoCriar.NOTA,
    "escrever": AlvoCriar.NOTA,

    # --- Termos Condicionais vinculados aos filhos do Enum ---
    "lembrete": {
        AlvoCriar.AGENDA.value["filhos"]["TEMPO"]: AlvoCriar.AGENDA,
        None: AlvoCriar.NOTA,
    },
    "aviso": {
        AlvoCriar.AGENDA.value["filhos"]["TEMPO"]: AlvoCriar.AGENDA,
        None: AlvoCriar.NOTA,
    },
    "tarefa": {
        AlvoCriar.AGENDA.value["filhos"]["TEMPO"]: AlvoCriar.AGENDA,
        None: AlvoCriar.NOTA,
    },
    "afazer": {
        AlvoCriar.AGENDA.value["filhos"]["TEMPO"]: AlvoCriar.AGENDA,
        None: AlvoCriar.NOTA,
    },
    "todo": {
        AlvoCriar.AGENDA.value["filhos"]["TEMPO"]: AlvoCriar.AGENDA,
        None: AlvoCriar.NOTA,
    },
}