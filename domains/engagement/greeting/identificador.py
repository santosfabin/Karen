import importlib
import io
import re
import sys
from pathlib import Path
import joblib

from domains.engagement.greeting.catalogo import AlvoSaudacao
from app.classificador import ClassificadorPai
from app.eventos import falar

sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODELO_PATH = ROOT_DIR / "models" / "greeting" / "professor_saudacao.joblib"

MAPEAMENTO_TOOLS = {
    AlvoSaudacao.SAUDACAO_HORARIO: "domains.engagement.greeting.tools.horario",
    AlvoSaudacao.SAUDACAO_INFORMAL: "domains.engagement.greeting.tools.informal",
    AlvoSaudacao.SAUDACAO_CHAMANDO: "domains.engagement.greeting.tools.chamando",
    AlvoSaudacao.COMO_VAI: "domains.engagement.greeting.tools.como_vai",
    AlvoSaudacao.AGRADECIMENTO: "domains.engagement.greeting.tools.agradecimento",
    AlvoSaudacao.DESPEDIDA: "domains.engagement.greeting.tools.despedida",
}

# Carrega o modelo de classificação uma única vez (< 1MB, < 1ms)
_modelo = joblib.load(MODELO_PATH) if MODELO_PATH.exists() else None


def identificar_alvo(frase: str) -> tuple[AlvoSaudacao, float]:
    global _modelo
    if _modelo is None:
        _modelo = joblib.load(MODELO_PATH)

    tradutor = ClassificadorPai.tradutor_compartilhado
    if tradutor is None:
        from sentence_transformers import SentenceTransformer
        tradutor = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    vetor = tradutor.encode([frase], show_progress_bar=False)
    probs = _modelo.predict_proba(vetor)[0]
    indice_max = probs.argmax()

    alvo_str = _modelo.classes_[indice_max]
    confianca = float(probs[indice_max])

    for alvo in AlvoSaudacao:
        if alvo.value == alvo_str:
            return alvo, confianca

    return AlvoSaudacao.DESCONHECIDO, confianca


def processar(frase: str):
    alvo, confianca = identificar_alvo(frase)

    print(f"  -> Alvo Identificado : {alvo.name} ({confianca:.1%})")

    if alvo == AlvoSaudacao.DESCONHECIDO:
        print("  -> Status            : Intenção não reconhecida.")
        return

    modulo_nome = MAPEAMENTO_TOOLS.get(alvo)
    if not modulo_nome:
        print(f"  -> Status            : Nenhuma ferramenta vinculada a {alvo.name}")
        return

    try:
        modulo = importlib.import_module(modulo_nome)

        # Captura o que a ferramenta imprimir para falar automaticamente
        buffer = io.StringIO()
        stdout_antigo = sys.stdout
        resposta_retorno = None

        try:
            sys.stdout = buffer
            if hasattr(modulo, "executar"):
                resposta_retorno = modulo.executar(frase)
            elif hasattr(modulo, "processar"):
                resposta_retorno = modulo.processar(frase)
            else:
                print(f"  -> Erro              : '{modulo_nome}' não possui 'executar()' ou 'processar()'.")
        finally:
            sys.stdout = stdout_antigo

        # 1. Imprime na tela exatamente como antes
        saida = buffer.getvalue()
        print(saida, end="")

        # 2. O Karen SEMPRE fala a resposta em voz alta
        if isinstance(resposta_retorno, str) and resposta_retorno.strip():
            falar(resposta_retorno.strip())
        else:
            # Extrai o texto da linha "-> Karen : [resposta]"
            match = re.search(r"-> Karen\s*:\s*(.+)", saida)
            if match:
                texto_fala = match.group(1).strip()
                falar(texto_fala)

    except ModuleNotFoundError as e:
        print(f"  -> Tool Pendente     : Módulo '{modulo_nome}' ainda não implementado ({e.name}).")