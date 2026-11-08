import sys
import warnings
import re
from pathlib import Path
import pandas as pd
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForTokenClassification, AutoTokenizer

warnings.filterwarnings("ignore")
sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT_DIR / "dados" / "treinamento" / "dados_slots_nota.csv"
OUTPUT_DIR = ROOT_DIR / "models" / "slots" / "nota"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODELO_BASE = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TAGS = ["O", "B-NOTE", "I-NOTE"]
TAG2ID = {tag: i for i, tag in enumerate(TAGS)}
ID2TAG = {i: tag for i, tag in enumerate(TAGS)}


def _normalizar(texto: str) -> str:
    """Remove pontuação redundante para casamento sem ruído."""
    return re.sub(r"[^\w\s]", " ", str(texto).lower()).strip()


def _encontrar_span_conteudo(frase: str, conteudo: str) -> tuple[int, int] | None:
    """Localiza as coordenadas exatas de caractere (início, fim) do conteúdo na frase."""
    if pd.isna(conteudo) or not str(conteudo).strip():
        return None

    c_limpo = str(conteudo).strip()
    f_lower = frase.lower()
    c_lower = c_limpo.lower()

    # 1. Tenta achar a correspondência exata vindo do final (rfind lida com autocorreções)
    pos = f_lower.rfind(c_lower)
    if pos != -1:
        return pos, pos + len(c_lower)

    # 2. Se falhar por pontuação, tenta pelas palavras extremas da direita para a esquerda
    palavras = [p for p in _normalizar(c_limpo).split() if p]
    if len(palavras) >= 2:
        p_inicio = palavras[0]
        p_fim = palavras[-1]

        pos_fim = f_lower.rfind(p_fim)
        if pos_fim != -1:
            # Procura a palavra inicial antes da palavra final
            pos_inicio = f_lower[:pos_fim].rfind(p_inicio)
            if pos_inicio != -1:
                return pos_inicio, pos_fim + len(p_fim)

    return None


def _alinhar_tokens(tokenizer, frase: str, conteudo: str):
    encoding = tokenizer(
        frase,
        return_offsets_mapping=True,
        padding="max_length",
        truncation=True,
        max_length=64,
        return_tensors="pt",
    )

    offset_mapping = encoding["offset_mapping"][0]
    labels = [TAG2ID["O"]] * len(offset_mapping)

    span = _encontrar_span_conteudo(frase, conteudo)
    if span:
        inicio_char, fim_char = span
        primeiro = True

        for idx, (t_start, t_end) in enumerate(offset_mapping):
            if t_start == t_end:
                continue
            if t_start >= inicio_char and t_end <= fim_char:
                labels[idx] = TAG2ID["B-NOTE"] if primeiro else TAG2ID["I-NOTE"]
                primeiro = False

    encoding["labels"] = torch.tensor([labels])
    return encoding


class DatasetSlots(Dataset):
    def __init__(self, df, tokenizer):
        self.exemplos = []
        for _, row in df.iterrows():
            enc = _alinhar_tokens(tokenizer, str(row["frase"]), str(row.get("conteudo", "")))
            self.exemplos.append({
                "input_ids": enc["input_ids"][0],
                "attention_mask": enc["attention_mask"][0],
                "labels": enc["labels"][0],
            })

    def __len__(self):
        return len(self.exemplos)

    def __getitem__(self, idx):
        return self.exemplos[idx]


def main():
    print("\n" + "=" * 55)
    print(" [TREINADOR SLOTS NOTA] Treinando Modelo de Autocorreção...")
    print("=" * 55)

    if not CSV_PATH.exists():
        print(f"Erro: Arquivo {CSV_PATH} não encontrado!")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    print(f"-> Total de exemplos para treino: {len(df)}")

    tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE)
    modelo = AutoModelForTokenClassification.from_pretrained(
        MODELO_BASE,
        num_labels=len(TAGS),
        id2label=ID2TAG,
        label2id=TAG2ID,
    )

    dataset = DatasetSlots(df, tokenizer)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)

    optimizer = AdamW(modelo.parameters(), lr=5e-5, weight_decay=0.01)
    modelo.train()

    epocas = 15
    print(f"-> Treinando por {epocas} épocas...")

    for epoca in range(epocas):
        perda_total = 0.0
        for batch in loader:
            optimizer.zero_grad()
            outputs = modelo(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
                labels=batch["labels"],
            )
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            perda_total += loss.item()

        if (epoca + 1) % 3 == 0 or epoca == epocas - 1:
            print(f"   Época {epoca + 1:02d}/{epocas} - Loss: {perda_total / len(loader):.4f}")

    print("\n-> Salvando modelo refinado...")
    modelo.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"-> Sucesso! Modelo de slots salvo em: {OUTPUT_DIR}")
    print("=" * 55)


if __name__ == "__main__":
    main()