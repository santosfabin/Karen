import sys
import os
import time
import importlib
import json
import re
from pathlib import Path

sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.classificador import ClassificadorPai
from app.decompositor import DecompositorKaren, remontar
from app.eventos import (
    iniciar_monitor_eventos,
    emitir_evento,
    interromper_fala,
    emitir_lote_inicio,
    emitir_lote_fim,
    falar,
    aguardar_eventos,
)

PASTAS_CATEGORIA = {
    "engajamento": "engagement",
    "transacional": "transactional",
    "informacional": "informational",
}
PASTAS_SUBCATEGORIA = {
    "saudacao": "greeting",
    "criar": "create",
    "status_sistema": "system_status",
}


def despachar_dinamicamente(categoria: str, subcategoria: str, frase: str, conteudo: str = None):
    cat_limpa = categoria.lower()
    sub_limpa = subcategoria.lower()
    pasta_cat = PASTAS_CATEGORIA.get(cat_limpa, cat_limpa)
    pasta_sub = PASTAS_SUBCATEGORIA.get(sub_limpa, sub_limpa)
    caminho_modulo = f"domains.{pasta_cat}.{pasta_sub}.identificador"

    try:
        modulo = importlib.import_module(caminho_modulo)
        if hasattr(modulo, "processar"):
            try:
                return modulo.processar(frase, conteudo=conteudo)
            except TypeError:
                return modulo.processar(frase)
        else:
            print(f"  -> Erro         : Arquivo '{caminho_modulo}' não possui 'processar(frase)'")
            return {"sucesso": False, "motivo": "Função não encontrada"}
    except ModuleNotFoundError as e:
        if e.name == caminho_modulo:
            print(f"  -> Status       : Módulo '{caminho_modulo}' ainda não implementado")
        else:
            print(f"  -> Erro Import  : Dependência ausente ({e.name})")
            print(f"  -> Detalhe      : {e}")
        return {"sucesso": False, "motivo": str(e)}


def processar_frase(frase_crua: str, classificador, decompositor):
    """Recebe uma frase (digitada ou transcrita) e executa tudo."""
    print("-" * 55)
    inicio_total = time.perf_counter()

    comandos_json = decompositor.processar(frase_crua)
    tarefas = remontar(comandos_json)

    print("  [DEBUG DECOMPOSIÇÃO] JSON Estruturado:")
    print("  " + json.dumps(comandos_json, ensure_ascii=False, indent=4).replace("\n", "\n  "))

    print(f"\n  [DEBUG FILA] Total de Ações na Fila: {len(tarefas)}")
    for t in tarefas:
        print(f"    -> [ID {t['id']}] modo='{t.get('modo')}' | frase='{t['frase']}'")
    print("-" * 55)

    if not tarefas:
        tarefas = [{"id": 1, "frase": frase_crua, "depois_de": None}]

    total_tarefas = len(tarefas)
    eh_lote = total_tarefas > 1
    sucessos_lote = 0
    erros_lote = 0

    if eh_lote:
        emitir_lote_inicio(total_tarefas)

    for i, tarefa in enumerate(tarefas):
        frase_atomica = tarefa["frase"]
        print(f"\n[Fila {i+1}/{total_tarefas}] -> '{frase_atomica}'")
        inicio_tarefa = time.perf_counter()

        res = classificador.classificar(frase_atomica)

        if not res["sucesso"]:
            print(f"  -> Falha        : {res['motivo']}")
            erros_lote += 1
            continue

        print(f"  -> Categoria    : {res['categoria']} ({res['confianca_categoria']:.1%})")
        print(f"  -> Subcategoria : {res['subcategoria']} ({res['confianca_subcategoria']:.1%})")

        eh_comando = res["categoria"].upper() == "TRANSACIONAL"

        if eh_comando and not eh_lote:
            emitir_evento("INICIANDO", acao=res["subcategoria"])
            time.sleep(0.05)

        try:
            resultado = despachar_dinamicamente(
                res["categoria"],
                res["subcategoria"],
                frase_atomica,
                conteudo=tarefa.get("conteudo"),
            )

            if isinstance(resultado, dict) and resultado.get("sucesso") is False:
                erros_lote += 1
                if eh_comando and not eh_lote:
                    emitir_evento("ERRO", acao=res["subcategoria"], motivo=resultado.get("motivo", ""))
            else:
                sucessos_lote += 1
                if eh_comando and not eh_lote:
                    emitir_evento("TERMINO", acao=res["subcategoria"])

        except Exception as err:
            erros_lote += 1
            if eh_comando and not eh_lote:
                emitir_evento("ERRO", acao=res["subcategoria"], motivo=str(err))

        duracao_tarefa = (time.perf_counter() - inicio_tarefa) * 1000
        print(f"  -> Concluído em : {duracao_tarefa:.2f} ms")

        if not eh_lote and i < total_tarefas - 1:
            time.sleep(0.5)

    if eh_lote:
        emitir_lote_fim(sucessos_lote, erros_lote)

    duracao_total = (time.perf_counter() - inicio_total) * 1000
    print("\n" + "-" * 55)
    print(f"-> Fila finalizada com sucesso! Tempo total: {duracao_total:.2f} ms")
    print("-" * 55)


def modo_texto(classificador, decompositor):
    print("\n" + "=" * 55)
    print(" SISTEMA PRONTO - DIGITE UM COMANDO")
    print("=" * 55)

    while True:
        try:
            frase_crua = input("\nComando > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if frase_crua:
            interromper_fala()

        if frase_crua.lower() in ("sair", "exit", "q"):
            break

        if frase_crua.lower() in ("clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            continue

        if not frase_crua:
            continue

        processar_frase(frase_crua, classificador, decompositor)


def mostrar_palavras(resultado: dict):
    if not resultado["words"]:
        return
    print(f"\n  [whisper {resultado['seconds']:.1f}s | pausa {resultado['pause']:.1f}s]")
    print(f"  [OUVIU] \"{resultado['bruto']}\"")
    for w in resultado["words"]:
        pct = w["prob"] * 100
        aviso = "  <- duvida" if pct < 70 else ""
        print(f"    {w['palavra']:<15} {pct:5.1f}%{aviso}")

def modo_voz(classificador, decompositor):
    from livekit.wakeword import WakeWordModel
    from app import audio
    from app.respostas_wake import escolher
    from app.transcritor import Transcritor

    print("Carregando Whisper e wake word...")
    transcritor = Transcritor("small")
    wake = WakeWordModel(models=[str(audio.WAKE_MODEL)])

    with audio.Microphone() as mic:
        print("Calibrando ruído, fica quieto 1s...")
        ruido = audio.calibrate(mic)

        print("\n" + "=" * 55)
        print(" SISTEMA PRONTO - DIGA 'KAREN' (Ctrl+C pra sair)")
        print("=" * 55)

        try:
            while True:
                resultado = audio.ouvir_comando(
                    mic, wake, transcritor, ruido, ao_acordar=interromper_fala
                )
                mostrar_palavras(resultado)

                if not resultado["text"]:
                    # Só disse "Karen": responde e espera o comando
                    print("\n  [WAKE] Karen acordou")
                    falar(escolher())
                    aguardar_eventos()
                    print("  [OUVINDO] pode falar...")

                    resultado = audio.escutar_frase_avulsa(mic, transcritor, ruido)
                    if not resultado or not resultado["text"]:
                        print("  [OUVINDO] ninguém falou, voltando a esperar 'Karen'...")
                        continue
                    mostrar_palavras(resultado)

                comando = resultado["text"]
                print("\n" + "=" * 55)
                print(f"  [COMANDO] \"{comando}\"")
                print("=" * 55)
                processar_frase(comando, classificador, decompositor)
                aguardar_eventos()
        except KeyboardInterrupt:
            print("\nTchau.")

def main():
    print("Iniciando o Sistema Karen...")
    iniciar_monitor_eventos()
    classificador = ClassificadorPai()
    decompositor = DecompositorKaren()

    if "--voz" in sys.argv:
        modo_voz(classificador, decompositor)
    else:
        modo_texto(classificador, decompositor)


if __name__ == "__main__":
    main()