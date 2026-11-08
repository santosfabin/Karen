import sys
from pathlib import Path
import random
import re
import unicodedata
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT_DIR / "dados" / "treinamento" / "dados_decompositor.csv"
OUTPUT_DIR = ROOT_DIR / "models" / "decompositor"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_OUT = OUTPUT_DIR / "modelo_karen.pt"

PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"

# Mesmo mapa do app/decompositor.py: treino e uso precisam tokenizar igual
MAPA_ABREVIACOES = {
    "tbm": "tambem",
    "tb": "tambem",
    "q": "que",
    "vc": "voce",
    "ce": "voce",
    "pq": "porque",
    "eh": "e",
}


def normalizar_texto(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )


def tokenizar(texto: str) -> list[str]:
    palavras = re.findall(r"\w+", normalizar_texto(texto))
    return [MAPA_ABREVIACOES.get(p, p) for p in palavras]


class DatasetKaren(Dataset):
    def __init__(self, frases, tags_list, vocab, tag2id, treino=True):
        self.dados = []
        self.treino = treino
        pad_tag_id = tag2id["O"]
        id_item_b = tag2id.get("B-ITEM")
        id_item_i = tag2id.get("I-ITEM")

        for frase, tags_str in zip(frases, tags_list):
            tokens = tokenizar(frase)
            tags = tags_str.strip().split()

            if len(tokens) != len(tags):
                raise ValueError(
                    f"Desalinhado: '{frase}' ({len(tokens)} palavras, {len(tags)} tags)"
                )

            ids_tokens = [vocab.get(t, vocab[UNK_TOKEN]) for t in tokens]
            ids_tags = [tag2id.get(tg, pad_tag_id) for tg in tags]

            self.dados.append((ids_tokens, ids_tags))

        self.vocab_unk = vocab[UNK_TOKEN]
        self.id_item_b = id_item_b
        self.id_item_i = id_item_i

    def __len__(self):
        return len(self.dados)

    def __getitem__(self, idx):
        ids_tokens, ids_tags = self.dados[idx]
        tokens_out = list(ids_tokens)

        if self.treino:
            for i, tag_id in enumerate(ids_tags):
                if tag_id in (self.id_item_b, self.id_item_i):
                    if random.random() < 0.25:
                        tokens_out[i] = self.vocab_unk

        return torch.tensor(tokens_out, dtype=torch.long), torch.tensor(ids_tags, dtype=torch.long)


def collate_fn(batch):
    frases, tags = zip(*batch)
    max_len = max(len(f) for f in frases)

    frases_pad = torch.zeros((len(frases), max_len), dtype=torch.long)
    tags_pad = torch.full((len(tags), max_len), fill_value=-100, dtype=torch.long)

    for i, (f, t) in enumerate(zip(frases, tags)):
        frases_pad[i, :len(f)] = f
        tags_pad[i, :len(t)] = t

    return frases_pad, tags_pad


class ModeloKaren(nn.Module):
    def __init__(self, tam_vocab: int, tam_emb: int, tam_oculto: int, num_tags: int):
        super().__init__()
        self.embedding = nn.Embedding(tam_vocab, tam_emb, padding_idx=0)
        self.gru = nn.GRU(tam_emb, tam_oculto, batch_first=True, bidirectional=True)
        self.classificador = nn.Linear(tam_oculto * 2, num_tags)

    def forward(self, x):
        emb = self.embedding(x)
        saida_gru, _ = self.gru(emb)
        return self.classificador(saida_gru)


def main():
    print("\n" + "=" * 55)
    print(" [TREINADOR DECOMPOSITOR] Treinando BiGRU do Zero (Nível 0)...")
    print("=" * 55)

    if not CSV_PATH.exists():
        print(f"Erro: Arquivo {CSV_PATH} não encontrado!")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    print(f"-> Total de frases para treino: {len(df)}")

    vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
    for frase in df["frase"]:
        for t in tokenizar(frase):
            if t not in vocab:
                vocab[t] = len(vocab)

    tags_unicas = set()
    for row in df["tags"]:
        for tg in row.strip().split():
            tags_unicas.add(tg)

    tag2id = {tg: i for i, tg in enumerate(sorted(tags_unicas))}
    id2tag = {i: tg for tg, i in tag2id.items()}

    dataset = DatasetKaren(df["frase"].tolist(), df["tags"].tolist(), vocab, tag2id, treino=True)
    loader = DataLoader(dataset, batch_size=4, shuffle=True, collate_fn=collate_fn)

    modelo = ModeloKaren(
        tam_vocab=len(vocab),
        tam_emb=64,
        tam_oculto=64,
        num_tags=len(tag2id)
    )

    criterio = nn.CrossEntropyLoss(ignore_index=-100)
    otimizador = torch.optim.Adam(modelo.parameters(), lr=0.008)

    modelo.train()
    epocas = 55
    print(f"-> Treinando por {epocas} épocas na CPU...")

    for epoca in range(1, epocas + 1):
        perda_epoca = 0.0
        for x, y in loader:
            otimizador.zero_grad()
            logits = modelo(x)
            perda = criterio(logits.view(-1, len(tag2id)), y.view(-1))
            perda.backward()
            otimizador.step()
            perda_epoca += perda.item()

        if epoca % 15 == 0 or epoca == epocas:
            print(f"   Época {epoca:02d}/{epocas} - Perda: {perda_epoca:.4f}")

    checkpoint = {
        "model_state": modelo.state_dict(),
        "vocab": vocab,
        "tag2id": tag2id,
        "id2tag": id2tag,
    }
    torch.save(checkpoint, MODEL_OUT)
    print(f"\n-> Sucesso! Modelo decompositor salvo em: {MODEL_OUT}")
    print("=" * 55)


if __name__ == "__main__":
    main()