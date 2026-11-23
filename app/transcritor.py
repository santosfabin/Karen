import time
from pathlib import Path

import ctranslate2
import soundfile as sf
from faster_whisper import WhisperModel


ROOT_DIR = Path(__file__).resolve().parent.parent
WARMUP_PATH = ROOT_DIR / "assets" / "warmup.wav"


class Transcritor:
    def __init__(self, modelo="small", compute_type=None, device="auto"):
        # modelo: "tiny", "base", "small", "medium"... (maior = mais certo e mais lento)
        if device == "auto":
            device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        if compute_type is None:
            compute_type = "float16" if device == "cuda" else "int8"

        try:
            self._carregar_e_aquecer(modelo, device, compute_type)
        except (RuntimeError, Exception) as e:
            # RuntimeError cobre falhas de cuBLAS/cuDNN; Exception cobre o resto.
            if device != "cuda":
                raise
            motivo = str(e).splitlines()[0] if str(e) else type(e).__name__
            print(f"[Whisper] falha em CUDA ({motivo}); usando small em CPU/int8")
            self._carregar_e_aquecer("small", "cpu", "int8")

    def _carregar_e_aquecer(self, modelo, device, compute_type):
        inicio = time.perf_counter()
        self.modelo = WhisperModel(modelo, device=device, compute_type=compute_type)
        self.device = device
        self.compute_type = compute_type
        self.tempo_carga = time.perf_counter() - inicio
        print(
            f"[Whisper] modelo={modelo}, device={self.device}, "
            f"compute={self.compute_type}, carga={self.tempo_carga:.2f}s"
        )

        if not WARMUP_PATH.exists():
            print(f"[Whisper] aquecimento ignorado: {WARMUP_PATH} nao encontrado")
            return

        audio, sr = sf.read(str(WARMUP_PATH), dtype="float32")
        if sr != 16000:
            print(f"[Whisper] aquecimento ignorado: {WARMUP_PATH} tem {sr} Hz, esperado 16000")
            return
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        inicio_aquecimento = time.perf_counter()
        self.transcrever(audio, vad_filter=True)
        tempo_aquecimento = time.perf_counter() - inicio_aquecimento
        print(f"[Whisper] aquecimento={tempo_aquecimento:.2f}s")

    def transcrever(self, audio, **opcoes):
        """audio: numpy float32, 16 kHz, mono.
        opcoes: sobrescreve os parametros do transcribe (ex: hotwords="Karen", beam_size=1).
        Devolve (lista de palavras, segundos gastos).
        Cada palavra: {"palavra", "prob", "inicio", "fim"}"""
        parametros = dict(
            language="pt",
            beam_size=5,
            word_timestamps=True,
            vad_filter=False,  # o corte da fala fica pra depois
            condition_on_previous_text=False,
        )
        parametros.update(opcoes)

        inicio = time.time()
        segmentos, _ = self.modelo.transcribe(audio, **parametros)
        palavras = []
        for seg in segmentos:  # o decoding acontece aqui, enquanto itera
            for p in seg.words:
                palavras.append({
                    "palavra": p.word.strip(),
                    "prob": p.probability,
                    "inicio": p.start,
                    "fim": p.end,
                })
        return palavras, time.time() - inicio
