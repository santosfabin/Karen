import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parents[5]
STORAGE_DIR = ROOT_DIR / "storage" / "notes"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def criar_nota_simples(conteudo: str) -> Path:
    """Cria uma nota de texto simples (.txt) nomeada por timestamp."""
    agora = datetime.now()
    nome_arquivo = agora.strftime("%Y-%m-%d_%H-%M-%S.txt")
    caminho_arquivo = STORAGE_DIR / nome_arquivo

    texto_final = f"Criado em: {agora.strftime('%d/%m/%Y %H:%M:%S')}\n\n{conteudo}\n"

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(texto_final)

    return caminho_arquivo
