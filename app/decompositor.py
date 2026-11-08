import sys
from pathlib import Path
import re
import unicodedata
import torch
import torch.nn as nn

sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "models" / "decomposer" / "modelo_karen.pt"

UNK_TOKEN = "<UNK>"

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

def tags_para_json(tokens: list[str], tags: list[str]) -> list[dict]:
    comandos = []
    comando_atual = None
    buffer_item = []
    depois_de_id = None
    modo_global = None
    substituir_antigo = None  # texto que o usuario quer trocar ("pao" em "pao nao troca por torrada")

    def aplicar_substituicao(novo: str) -> bool:
        """Troca a palavra antiga pela nova no item mais recente que a contem."""
        nonlocal substituir_antigo
        antigo, substituir_antigo = substituir_antigo, None
        padrao = re.compile(rf"\b{re.escape(antigo)}\b")
        for cmd in reversed(comandos):
            for it in reversed(cmd["itens"]):
                if padrao.search(it["nome"]):
                    it["nome"] = padrao.sub(novo, it["nome"], count=1)
                    return True
        return False

    def descarregar_item():
        nonlocal buffer_item
        if buffer_item and comando_atual:
            nome_item = " ".join(buffer_item).strip()
            if nome_item:
                if substituir_antigo is not None:
                    if not aplicar_substituicao(nome_item):
                        comando_atual["incerto"] = True  # nao achou o que trocar
                else:
                    comando_atual["itens"].append({
                        "nome": nome_item,
                        "qtd": None,
                        "quando": None
                    })
        buffer_item = []

    for token, tag in zip(tokens, tags):
        if tag == "B-DEP":
            descarregar_item()
            if comando_atual:
                depois_de_id = comando_atual["id"]
            continue

        if "MODO_SEPARADO" in tag:
            descarregar_item()
            modo_global = "separado"
            if comando_atual:
                comando_atual["modo"] = "separado"
            continue
        if "MODO_JUNTO" in tag:
            descarregar_item()
            modo_global = "junto"
            if comando_atual:
                comando_atual["modo"] = "junto"
            continue

        # "na verdade nao abre o chrome": descarta o comando anterior
        if tag == "B-CORRECAO":
            descarregar_item()
            if comandos:
                removido = comandos.pop()
                depois_de_id = removido["depois_de"]  # o proximo comando herda a dependencia
            comando_atual = comandos[-1] if comandos else None
            continue
        if tag == "I-CORRECAO":
            continue

        # "ah pao nao troca por torrada": item antes da tag = antigo, item depois = novo
        if tag == "B-SUBSTITUIR":
            descarregar_item()
            if comando_atual and comando_atual["itens"]:
                substituir_antigo = comando_atual["itens"].pop()["nome"]
            continue

        if tag.startswith("B-") and tag not in ("B-ITEM", "B-DEP"):
            acao = tag.split("-")[1].lower()
            descarregar_item()
            novo_id = len(comandos) + 1
            comando_atual = {
                "id": novo_id,
                "acao": acao,
                "modo": modo_global if modo_global else "junto",
                "depois_de": depois_de_id,
                "itens": []
            }
            comandos.append(comando_atual)
            depois_de_id = None
            modo_global = None
            continue

        if tag == "B-ITEM":
            descarregar_item()
            if comando_atual:
                buffer_item.append(token)
        elif tag == "I-ITEM":
            if comando_atual:
                buffer_item.append(token)
        else:
            descarregar_item()

    descarregar_item()
    return comandos

class DecompositorKaren:
    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Modelo não encontrado em: {MODEL_PATH}. Execute o treino primeiro!")

        checkpoint = torch.load(MODEL_PATH, map_location="cpu")
        self.vocab = checkpoint["vocab"]
        self.id2tag = checkpoint["id2tag"]
        tag2id = checkpoint["tag2id"]

        self.modelo = ModeloKaren(
            tam_vocab=len(self.vocab),
            tam_emb=64,
            tam_oculto=64,
            num_tags=len(tag2id)
        )
        self.modelo.load_state_dict(checkpoint["model_state"])
        self.modelo.eval()

    def processar(self, frase: str) -> list[dict]:
        tokens = tokenizar(frase)
        if not tokens:
            return []

        ids = [self.vocab.get(t, self.vocab[UNK_TOKEN]) for t in tokens]
        tensor_x = torch.tensor([ids], dtype=torch.long)

        with torch.no_grad():
            logits = self.modelo(tensor_x)
            predicoes = torch.argmax(logits, dim=-1)[0].tolist()

        tags = [self.id2tag[p] for p in predicoes]
        return tags_para_json(tokens, tags)

def remontar(comandos_json: list[dict]) -> list[dict]:
    tarefas = []
    for cmd in comandos_json:
        itens = [it["nome"] for it in cmd["itens"] if it.get("nome")]
        if not itens:
            continue

        if cmd.get("modo") == "junto":
            texto_itens = " ".join(itens)
            tarefas.append({
                "id": cmd["id"],
                "frase": f"{cmd['acao']} {texto_itens}",
                "conteudo": texto_itens,
                "depois_de": cmd["depois_de"],
                "modo": "junto"
            })
        else:
            for it_nome in itens:
                tarefas.append({
                    "id": cmd["id"],
                    "frase": f"{cmd['acao']} {it_nome}",
                    "conteudo": it_nome,
                    "depois_de": cmd["depois_de"],
                    "modo": "separado"
                })
    return tarefas