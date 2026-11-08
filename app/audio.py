import math
import queue
import re
import sys
from collections import deque
from pathlib import Path

import numpy as np
import scipy.signal
import sounddevice as sd
import soundfile as sf

sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

WAKE_MODEL = ROOT_DIR / "models" / "wakeword" / "karen.onnx"

SR = 16000
BLOCK_S = 0.05
BLOCK_SAMPLES = int(SR * BLOCK_S)

BUFFER_BLOCOS = int(4.0 / BLOCK_S)   # 80 blocos (4 s) sempre guardados
WAKE_BLOCOS = int(2.0 / BLOCK_S)     # janela do modelo: 40 blocos (2 s)
WAKE_CADA = 2                        # roda o modelo a cada 2 blocos (0.1 s)
WAKE_THRESHOLD = 0.5
GATE_S = 1.5                         # so roda o modelo se teve voz nos ultimos 1.5 s

# Corte do "Karen"
CORTE_JANELA_BLOCOS = 12             # procura a pausa nos ultimos 0.6 s antes do disparo
CORTE_ATRAS_S = 0.25                 # sem pausa: volta isso antes do disparo (AJUSTE AQUI)
CORTE_ATRAS_BLOCOS = int(CORTE_ATRAS_S / BLOCK_S)
PAUSA_MINIMA_BLOCOS = 2              # 100 ms de silencio contam como pausa

PAUSE_MIN = 0.5                      # pausa que encerra o comando
SO_KAREN_S = 1.2                     # silencio depois do "Karen" = so chamou
MAX_SPEECH = 40.0
START_TIMEOUT = 5.0
PRE_BLOCOS = 3


class Microphone:
    """Um unico stream de mic de baixa latencia."""

    def __init__(self):
        device, rate, name = self._find_mic()
        self.name = name
        self.rate = rate
        g = math.gcd(SR, rate)
        self._up, self._down = SR // g, rate // g
        self._queue = queue.Queue()
        self._stream = sd.InputStream(
            samplerate=rate, channels=1, dtype="float32",
            blocksize=int(rate * BLOCK_S), device=device,
            callback=self._callback,
        )

    @staticmethod
    def _find_mic():
        for name in ("pipewire", "pulse", "default"):
            try:
                info = sd.query_devices(name, "input")
                return name, int(info["default_samplerate"]), info["name"]
            except Exception:
                continue
        info = sd.query_devices(kind="input")
        return None, int(info["default_samplerate"]), info["name"]

    def _callback(self, indata, frames, time_info, status):
        audio = indata[:, 0].astype(np.float32)
        if self.rate != SR:
            audio = scipy.signal.resample_poly(audio, self._up, self._down).astype(np.float32)
        self._queue.put(audio)

    def read(self):
        return self._queue.get()

    def flush(self):
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def __enter__(self):
        self._stream.start()
        return self

    def __exit__(self, *args):
        self._stream.stop()
        self._stream.close()


def rms(block):
    return float(np.sqrt(np.mean(block ** 2)))


def calibrate(mic, seconds=1.0):
    mic.flush()
    values = [rms(mic.read()) for _ in range(int(seconds / BLOCK_S))]
    return max(0.01, float(np.mean(values)) * 2.5)


def _ponto_de_corte(blocos, limiar):
    """Indice do buffer a partir do qual fica so o comando, sem o 'Karen'.
    O detector dispara um pouco depois do fim da palavra, entao o fim do buffer
    e logo apos o 'Karen'."""
    n = len(blocos)
    visto_fala = False
    silencio = 0
    for i in range(max(0, n - CORTE_JANELA_BLOCOS), n):
        if rms(blocos[i]) <= limiar:
            silencio += 1
        else:
            if visto_fala and silencio >= PAUSA_MINIMA_BLOCOS:
                return max(0, i - 1)  # fim da pausa: o comando comeca aqui
            visto_fala = True
            silencio = 0
    if silencio >= PAUSA_MINIMA_BLOCOS:
        return n  # terminou em silencio: o comando ainda nao comecou
    return max(0, n - CORTE_ATRAS_BLOCOS)  # sem pausa: volta um pouco


def _vazio():
    return {"text": "", "bruto": "", "words": [], "pause": 0.0, "seconds": 0.0}


def _transcrever(transcriber, blocos, pause):
    audio_completo = np.concatenate(blocos)
    sf.write("/tmp/karen_ultimo.wav", audio_completo, SR)  # DEBUG
    print(f"  [DEBUG] audio enviado ao Whisper: {len(audio_completo) / SR:.1f}s")
    words, seconds = transcriber.transcrever(audio_completo, vad_filter=True)
    bruto = " ".join(w["palavra"] for w in words).strip()
    texto = re.sub(r"^[^\w]+|[^\w]+$", "", bruto).strip()
    return {
        "text": texto,
        "bruto": bruto,   # o que o Whisper ouviu
        "words": words,
        "pause": pause,
        "seconds": seconds,
    }


def ouvir_comando(mic, wake_model, transcriber, noise_threshold, ao_acordar=None):
    """Fica ouvindo. Ao detectar 'Karen', corta o 'Karen' do audio, grava o que vem
    depois ate a pausa e transcreve so isso. 'text' vem vazio se a pessoa so chamou."""
    mic.flush()
    zero = np.zeros(BLOCK_SAMPLES, dtype=np.float32)
    buffer = deque([zero] * BUFFER_BLOCOS, maxlen=BUFFER_BLOCOS)
    gate_level = noise_threshold * 0.5
    desde_voz = 10 ** 6  # blocos desde a ultima voz
    n = 0

    while True:
        block = mic.read()
        buffer.append(block)
        n += 1
        desde_voz = 0 if rms(block) > gate_level else desde_voz + 1

        if n % WAKE_CADA or desde_voz * BLOCK_S > GATE_S:
            continue

        janela = np.concatenate(list(buffer)[-WAKE_BLOCOS:])
        scores = wake_model.predict(janela)
        if (max(scores.values()) if scores else 0.0) >= WAKE_THRESHOLD:
            break

    if ao_acordar:
        ao_acordar()

    blocos = list(buffer)
    gravado = blocos[_ponto_de_corte(blocos, noise_threshold):]

    falou = any(rms(b) > noise_threshold for b in gravado)
    silencio = 0
    for b in reversed(gravado):
        if rms(b) > noise_threshold:
            break
        silencio += 1
    total = len(gravado)

    while True:
        if total * BLOCK_S >= MAX_SPEECH:
            break
        if falou and silencio * BLOCK_S >= PAUSE_MIN:
            break
        if not falou and silencio * BLOCK_S >= SO_KAREN_S:
            return _vazio()  # so chamou "Karen": nao precisa do Whisper
        block = mic.read()
        gravado.append(block)
        total += 1
        if rms(block) > noise_threshold:
            falou = True
            silencio = 0
        else:
            silencio += 1

    if not falou:
        return _vazio()
    return _transcrever(transcriber, gravado, silencio * BLOCK_S)


def escutar_frase_avulsa(mic, transcriber, noise_threshold):
    """Escuta o comando depois que ela respondeu 'Pois nao'. None se ninguem falou."""
    mic.flush()
    pre = deque(maxlen=PRE_BLOCOS)
    gravado = []
    falando = False
    silencio = 0
    esperado = 0
    total = 0
    pico = 0.0

    while True:
        block = mic.read()
        nivel = rms(block)
        pico = max(pico, nivel)
        loud = nivel > noise_threshold

        if not falando:
            if loud:
                falando = True
                gravado = list(pre) + [block]
                total = len(gravado)
                silencio = 0
            else:
                pre.append(block)
                esperado += 1
                if esperado * BLOCK_S >= START_TIMEOUT:
                    print(f"  [DEBUG] ninguem passou do limiar: limiar {noise_threshold:.4f}, "
                          f"maior volume ouvido {pico:.4f}")
                    return None
            continue

        gravado.append(block)
        total += 1
        silencio = 0 if loud else silencio + 1
        if silencio * BLOCK_S >= PAUSE_MIN or total * BLOCK_S >= MAX_SPEECH:
            break

    resultado = _transcrever(transcriber, gravado, silencio * BLOCK_S)
    if not resultado["text"]:
        print(f"  [DEBUG] whisper devolveu vazio ({total * BLOCK_S:.1f}s de audio, "
              f"volume maximo {pico:.4f})")
    return resultado
    """Escuta o comando depois que ela respondeu 'Pois nao'. None se ninguem falou."""
    mic.flush()
    pre = deque(maxlen=PRE_BLOCOS)
    gravado = []
    falando = False
    silencio = 0
    esperado = 0
    total = 0

    while True:
        block = mic.read()
        loud = rms(block) > noise_threshold

        if not falando:
            if loud:
                falando = True
                gravado = list(pre) + [block]
                total = len(gravado)
                silencio = 0
            else:
                pre.append(block)
                esperado += 1
                if esperado * BLOCK_S >= START_TIMEOUT:
                    return None
            continue

        gravado.append(block)
        total += 1
        silencio = 0 if loud else silencio + 1
        if silencio * BLOCK_S >= PAUSE_MIN or total * BLOCK_S >= MAX_SPEECH:
            break

    return _transcrever(transcriber, gravado, silencio * BLOCK_S)