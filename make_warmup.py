"""Gera assets/warmup.wav com a mesma voz do app (Kokoro blend Dora 60% + Emma 40%)."""

from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from scipy.signal import resample_poly


ROOT_DIR = Path(__file__).resolve().parent
PASTA_KOKORO = ROOT_DIR / "models" / "voice" / "kokoro"
MODELO_PATH = PASTA_KOKORO / "kokoro-v1.0.onnx"
VOICES_PATH = PASTA_KOKORO / "voices-v1.0.bin"
SAIDA = ROOT_DIR / "assets" / "warmup.wav"

FRASE = "que horas sao agora"
SR_ALVO = 16000
DURACAO_ALVO = 2.0


def main():
    kokoro = Kokoro(str(MODELO_PATH), str(VOICES_PATH))

    banco = np.load(str(VOICES_PATH))
    voz_blend = (banco["pf_dora"] * 0.60) + (banco["bf_emma"] * 0.40)

    samples, sr = kokoro.create(FRASE, voice=voz_blend, speed=1.0, lang="pt-br")
    samples = np.asarray(samples, dtype=np.float32).squeeze()

    if sr != SR_ALVO:
        samples = resample_poly(samples, SR_ALVO, sr).astype(np.float32)

    faltando = int(DURACAO_ALVO * SR_ALVO) - len(samples)
    if faltando > 0:
        samples = np.pad(samples, (0, faltando))

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    sf.write(SAIDA, samples, SR_ALVO, subtype="PCM_16")

    print(f"gerado : {SAIDA}")
    print(f"frase  : {FRASE!r}")
    print(f"origem : {sr} Hz -> {SR_ALVO} Hz")
    print(f"duracao: {len(samples) / SR_ALVO:.2f}s")


if __name__ == "__main__":
    main()
