"""Benchmark de configuracoes do Whisper para o fluxo da Karen."""

import csv
import gc
import re
import time
import unicodedata
from pathlib import Path

import soundfile as sf
from scipy.signal import resample_poly

from app.transcritor import Transcritor


ROOT_DIR = Path(__file__).resolve().parent
COCLEA_DIR = ROOT_DIR.parent.parent / "coclea" / "dados"
FRASES_CSV = COCLEA_DIR / "frases.csv"
WARMUP_PATH = ROOT_DIR / "assets" / "warmup.wav"
SR = 16000

CONFIGS = [
    ("small", "cpu", "int8"),
    ("medium", "cuda", "float16"),
    ("large-v3", "cuda", "float16"),
    ("large-v3-turbo", "cuda", "float16"),
]

TURBO_FALLBACK = "deepdml/faster-whisper-large-v3-turbo-ct2"


def normalizar(texto):
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    sem_pontuacao = re.sub(r"[^\w\s]", " ", sem_acento)
    return sem_pontuacao.lower().split()


def distancia_edicao(a, b):
    """Distancia de Levenshtein entre duas listas de palavras."""
    n, m = len(a), len(b)
    anterior = list(range(m + 1))
    for i in range(1, n + 1):
        atual = [i] + [0] * m
        for j in range(1, m + 1):
            custo = 0 if a[i - 1] == b[j - 1] else 1
            atual[j] = min(
                anterior[j] + 1,
                atual[j - 1] + 1,
                anterior[j - 1] + custo,
            )
        anterior = atual
    return anterior[m]


def wer(referencia, hipotese):
    ref = normalizar(referencia)
    hyp = normalizar(hipotese)
    if not ref:
        return 0.0 if not hyp else 1.0
    return distancia_edicao(ref, hyp) / len(ref)


def carregar_audio(caminho):
    audio, sr = sf.read(str(caminho), dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != SR:
        audio = resample_poly(audio, SR, sr).astype("float32")
    return audio


def carregar_dados():
    with open(FRASES_CSV, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    dados = []
    for linha in linhas:
        dados.append({
            "arquivo": linha["arquivo"],
            "texto": linha["texto"],
            "audio": carregar_audio(COCLEA_DIR / linha["arquivo"]),
        })
    return dados


def rodar_config(modelo, device, compute_type, dados, warmup):
    nomes = [modelo]
    if modelo == "large-v3-turbo":
        nomes.append(TURBO_FALLBACK)

    ultimo_erro = None
    for nome in nomes:
        try:
            transcritor = Transcritor(
                modelo=nome, device=device, compute_type=compute_type
            )
        except Exception as e:
            ultimo_erro = e
            continue

        if transcritor.device != device or transcritor.compute_type != compute_type:
            ultimo_erro = RuntimeError(
                f"pedido {device}/{compute_type}, mas carregou "
                f"{transcritor.device}/{transcritor.compute_type}"
            )
            del transcritor
            gc.collect()
            continue

        # Aquecimento descartado (o __init__ ja aqueceu com o mesmo audio).
        transcritor.transcrever(warmup, vad_filter=True)

        tempos = []
        wers = []
        for d in dados:
            inicio = time.perf_counter()
            palavras, _ = transcritor.transcrever(d["audio"], vad_filter=True)
            tempos.append(time.perf_counter() - inicio)

            ouvido = " ".join(p["palavra"] for p in palavras)
            wers.append(wer(d["texto"], ouvido))

        resultado = {
            "modelo": nome,
            "device": device,
            "carga": transcritor.tempo_carga,
            "tempo_medio": sum(tempos) / len(tempos),
            "tempo_max": max(tempos),
            "wer": sum(wers) / len(wers),
        }
        del transcritor
        gc.collect()
        return resultado, None

    return None, ultimo_erro


def imprimir_tabela(resultados, erros):
    cabecalho = (
        f"{'modelo':<16} {'device':<7} {'carga(s)':>9} "
        f"{'tempo medio(s)':>15} {'tempo maximo(s)':>15} {'WER medio':>10}"
    )
    print(cabecalho)
    print("-" * len(cabecalho))

    for modelo, device, compute_type in CONFIGS:
        chave = (modelo, device, compute_type)
        r = resultados.get(chave)
        if r is None:
            print(
                f"{modelo:<16} {device:<7} {'-':>9} {'-':>15} {'-':>15} {'ERRO':>10}"
            )
        else:
            print(
                f"{r['modelo']:<16} {r['device']:<7} {r['carga']:>9.2f} "
                f"{r['tempo_medio']:>15.3f} {r['tempo_max']:>15.3f} "
                f"{r['wer']:>9.1%}"
            )

    for (modelo, device, _), erro in erros.items():
        print(f"[ERRO] {modelo} / {device}: {erro}")


def main():
    if not FRASES_CSV.exists():
        raise SystemExit(f"nao encontrado: {FRASES_CSV}")
    if not WARMUP_PATH.exists():
        raise SystemExit(f"nao encontrado: {WARMUP_PATH}")

    dados = carregar_dados()
    warmup = carregar_audio(WARMUP_PATH)
    print(f"{len(dados)} audios | warmup={WARMUP_PATH}")

    resultados = {}
    erros = {}

    for modelo, device, compute_type in CONFIGS:
        chave = (modelo, device, compute_type)
        print(f"\n=== {modelo} | {device} | {compute_type} ===")
        try:
            resultado, erro = rodar_config(
                modelo, device, compute_type, dados, warmup
            )
        except Exception as e:
            resultado, erro = None, e

        if resultado is None:
            erros[chave] = erro
            print(f"[ERRO] {erro}")
        else:
            resultados[chave] = resultado
            print(
                f"carga={resultado['carga']:.2f}s | "
                f"medio={resultado['tempo_medio']:.3f}s | "
                f"max={resultado['tempo_max']:.3f}s | "
                f"WER={resultado['wer']:.1%}"
            )

    print("\nTABELA")
    imprimir_tabela(resultados, erros)


if __name__ == "__main__":
    main()
