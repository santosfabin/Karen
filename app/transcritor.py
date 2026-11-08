import time

from faster_whisper import WhisperModel


class Transcritor:
    def __init__(self, modelo="small", compute_type="int8"):
        # modelo: "tiny", "base", "small", "medium"... (maior = mais certo e mais lento)
        inicio = time.time()
        self.modelo = WhisperModel(modelo, device="cpu", compute_type=compute_type)
        self.tempo_carga = time.time() - inicio

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
