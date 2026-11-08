import io
import os
from pathlib import Path
import queue
import random
import sys
import threading
import time

import numpy as np
import pygame
import soundfile as sf
from kokoro_onnx import Kokoro

sys.dont_write_bytecode = True

pygame.mixer.init()

_fila_eventos = queue.Queue()
_worker_iniciado = False
_interromper_atual = threading.Event()

ROOT_DIR = Path(__file__).resolve().parent.parent

# Kokoro voice files live in models/voice/kokoro
PASTA_KOKORO = ROOT_DIR / "models" / "voice" / "kokoro"

MODELO_PATH = PASTA_KOKORO / "kokoro-v1.0.onnx"
VOICES_PATH = PASTA_KOKORO / "voices-v1.0.bin"

_kokoro = None
_voz_blend = None

# =====================================================================
# CARREGAMENTO DO MODELO (Blend: Dora 60% + Emma 40%)
# =====================================================================

def _carregar_voz():
    global _kokoro, _voz_blend
    if _kokoro is None:
        if not MODELO_PATH.exists() or not VOICES_PATH.exists():
            print(f"⚠️ [VOZ] Arquivos do Kokoro não encontrados em {PASTA_KOKORO}.")
            return None

        _kokoro = Kokoro(str(MODELO_PATH), str(VOICES_PATH))

        # Pré-calcula a voz combinada uma única vez na memória RAM
        banco = np.load(str(VOICES_PATH))
        _voz_blend = (banco["pf_dora"] * 0.60) + (banco["bf_emma"] * 0.40)
        print("  🔊 [VOZ] Motor Kokoro carregado na RAM com Blend Emma (60/40)!")

    return _kokoro

def interromper_fala():
    """Corta o áudio imediatamente e esvazia a fila pendente."""
    _interromper_atual.set()
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    except Exception:
        pass

    while not _fila_eventos.empty():
        try:
            _fila_eventos.get_nowait()
            _fila_eventos.task_done()
        except queue.Empty:
            break

    _interromper_atual.clear()

def _falar_texto(texto: str):
    kokoro = _carregar_voz()
    if kokoro is None or _interromper_atual.is_set():
        return

    try:
        # 1. Gera o áudio direto como array na memória RAM usando o Blend
        samples, sr = kokoro.create(
            texto,
            voice=_voz_blend,
            speed=1.0,
            lang="pt-br"
        )

        if _interromper_atual.is_set():
            return

        # 2. Escreve direto na memória RAM (Zero arquivos salvos no disco)
        buffer_memoria = io.BytesIO()
        sf.write(buffer_memoria, samples, sr, format="WAV")
        buffer_memoria.seek(0)

        # 3. O Pygame reproduz direto do buffer de memória
        pygame.mixer.music.load(buffer_memoria)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if _interromper_atual.is_set():
                pygame.mixer.music.stop()
                break
            pygame.time.Clock().tick(30)

        pygame.mixer.music.unload()

    except Exception as e:
        print(f"      -> Erro na síntese de voz: {e}")

# =====================================================================
# TEMPLATES DE TEXTO
# =====================================================================

NOMES_ACOES = {
    "criar": "criação",
    "deletar": "exclusão",
    "atualizar": "atualização",
    "executar": "execução",
    "anotar": "anotação",
}

TEMPLATES_STATUS = {
    "INICIANDO": [
        "Iniciando {acao}...",
        "Executando {acao}...",
    ],
    "TERMINO": [
        "{acao_cap} finalizada com sucesso!",
        "Pronto, {acao} concluída.",
    ],
    "ERRO": [
        "Não foi possível concluir a {acao}.",
        "Ocorreu uma falha durante a {acao}.",
    ],
}

# =====================================================================
# WORKER DE ÁUDIO EM SEGUNDO PLANO
# =====================================================================

def aguardar_eventos():
    _fila_eventos.join()

def _worker_loop():
    _carregar_voz()

    while True:
        try:
            evento = _fila_eventos.get()
            if evento is None:
                break

            if _interromper_atual.is_set():
                _fila_eventos.task_done()
                continue

            mensagem = evento.get("mensagem", "")
            if mensagem:
                _falar_texto(mensagem)

            _fila_eventos.task_done()
        except Exception as e:
            print(f"      -> Erro no monitor: {e}")

def iniciar_monitor_eventos():
    global _worker_iniciado
    if not _worker_iniciado:
        t = threading.Thread(target=_worker_loop, daemon=True, name="WorkerStatusKaren")
        t.start()
        _worker_iniciado = True

# =====================================================================
# FUNÇÕES PÚBLICAS DE EMISSÃO
# =====================================================================

def emitir_evento(status: str, acao: str, motivo: str = ""):
    iniciar_monitor_eventos()

    status_upper = status.upper()
    subcat_crua = acao.lower() if acao else "tarefa"
    acao_limpa = NOMES_ACOES.get(subcat_crua, subcat_crua)

    frases = TEMPLATES_STATUS.get(status_upper, ["{acao_cap}: {status}."])
    template_escolhido = random.choice(frases)

    mensagem = template_escolhido.format(
        acao=acao_limpa,
        acao_cap=acao_limpa.capitalize(),
        status=status_upper,
    )

    if motivo and status_upper == "ERRO":
        mensagem += f" Motivo: {motivo}"

    print("\n      " + "-" * 48)
    print(f"      -> Status Karen : {mensagem}")
    print("      " + "-" * 48)

    _fila_eventos.put({
        "tipo": "STATUS",
        "mensagem": mensagem,
        "timestamp": time.time(),
    })

def emitir_lote_inicio(qtd: int):
    iniciar_monitor_eventos()
    mensagem = f"Iniciando execução em lote de {qtd} tarefas."
    print("\n      " + "-" * 48)
    print(f"      -> Status Karen : {mensagem}")
    print("      " + "-" * 48)

    _fila_eventos.put({"tipo": "LOTE_INICIO", "mensagem": mensagem, "timestamp": time.time()})

def emitir_lote_fim(sucessos: int, erros: int):
    iniciar_monitor_eventos()
    if erros == 0:
        mensagem = f"Todas as {sucessos} tarefas foram concluídas com êxito!"
    else:
        mensagem = f"Lote finalizado com {sucessos} tarefas concluídas e {erros} falhas."

    print("\n      " + "-" * 48)
    print(f"      -> Status Karen : {mensagem}")
    print("      " + "-" * 48)

    _fila_eventos.put({"tipo": "LOTE_FIM", "mensagem": mensagem, "timestamp": time.time()})

def falar(mensagem: str):
    iniciar_monitor_eventos()
    _fila_eventos.put({
        "tipo": "FALA",
        "mensagem": mensagem,
        "timestamp": time.time(),
    })