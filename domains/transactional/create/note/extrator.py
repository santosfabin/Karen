import re
import sys
import warnings
from pathlib import Path
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

warnings.filterwarnings("ignore")
sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parents[4]
MODEL_DIR = ROOT_DIR / "models" / "slots" / "note"

_TOKENIZER = None
_MODELO = None


def _carregar_modelo():
    global _TOKENIZER, _MODELO
    if _MODELO is None:
        _TOKENIZER = AutoTokenizer.from_pretrained(MODEL_DIR)
        _MODELO = AutoModelForTokenClassification.from_pretrained(MODEL_DIR)
        _MODELO.eval()
    return _TOKENIZER, _MODELO


def extrair_conteudo_nota(frase: str) -> str | None:
    """Extrai o conteúdo da nota usando o mini-transformer com fallback seguro."""
    if not frase or not frase.strip():
        return None

    tokenizer, modelo = _carregar_modelo()

    # Tokenização com mapeamento de caracteres originais
    encoding = tokenizer(
        frase,
        return_offsets_mapping=True,
        padding=True,
        truncation=True,
        max_length=64,
        return_tensors="pt",
    )

    offset_mapping = encoding["offset_mapping"][0]

    with torch.no_grad():
        outputs = modelo(
            input_ids=encoding["input_ids"],
            attention_mask=encoding["attention_mask"],
        )
        predicoes = torch.argmax(outputs.logits, dim=-1)[0].tolist()

    # Identifica os intervalos de caracteres marcados como B-NOTE (1) ou I-NOTE (2)
    spans_caracteres = []
    for idx, label_id in enumerate(predicoes):
        if label_id in (1, 2):  # B-NOTE ou I-NOTE
            start, end = offset_mapping[idx].tolist()
            if start != end:  # Ignora tokens especiais
                spans_caracteres.append((start, end))

    # 1. Se a IA achou as tags, pega do início detectado até o fim da frase (não come palavras no final)
    if spans_caracteres:
        inicio_corte = spans_caracteres[0][0]
        conteudo_ia = frase[inicio_corte:].strip()
        if conteudo_ia:
            return conteudo_ia

    # 2. FALLBACK SEGURO: Se a IA falhou (ex: frase curta como 'anotar vou comer'),
    # remove o comando do início e pega o restante da frase diretamente
    conteudo_fallback = re.sub(
        r"^(anot[ae]r?|cria[r]?\s+(uma?\s+)?nota|nota)\s+(que\s+|de\s+|pra\s+)?",
        "",
        frase,
        flags=re.IGNORECASE,
    ).strip()

    return conteudo_fallback if conteudo_fallback else None