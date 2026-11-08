import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parents[5]
STORAGE_DIR = ROOT_DIR / "storage" / "notes"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def criar_nota_markdown(conteudo: str) -> Path:
    """Cria uma nota formatada em Markdown (.md) nomeada por timestamp."""
    agora = datetime.now()
    nome_arquivo = agora.strftime("%Y-%m-%d_%H-%M-%S.md")
    caminho_arquivo = STORAGE_DIR / nome_arquivo

    conteudo_md = (
        f"# Nota - {agora.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        f"{conteudo}\n"
    )

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo_md)

    return caminho_arquivo