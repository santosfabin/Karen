# Karen (mark10)

Assistente de voz local em português. Você fala (ou digita), a Karen classifica a intenção e executa a ação — tudo no seu computador, sem API de LLM.

Dois modos:

- **texto** (padrão): loop no terminal
- **voz** (`--voz`): wake word **"Karen"** → transcrição Whisper → mesma fila de comandos, com fala via Kokoro

## Como funciona

```
frase
  → decompositor (comandos compostos + conteúdo)
  → classificador (categoria → subcategoria)
  → domínio / ferramenta
  → evento de voz (quando aplicável)
```

| Camada | O que decide | Onde vive |
| --- | --- | --- |
| Decompositor | Quebra falas compostas (`anota X e que horas são`) e extrai itens | `app/decompositor.py` |
| Classificador pai | Categoria: engajamento, transacional, informacional | `app/classificador.py` |
| Classificador filho | Subcategoria / ação | mesmos embeddings + um `.joblib` por categoria |
| Domínios | Identificam o alvo e chamam a tool | `domains/` |
| Eventos / TTS | Fala respostas e feedback de comando | `app/eventos.py` |

Categorias e o que já está ligado:

- **Engajamento → saudação** — bom dia/tarde/noite, informal, chamando, como vai, obrigado, tchau
- **Transacional → criar** — notas (txt/markdown). Agenda e devops estão no catálogo, ainda sem tool
- **Informacional → status do sistema** — hora, data, dia, mês, ano, dia da semana

O despacho é dinâmico: `domains.<categoria>.<subcategoria>.identificador.processar(...)`.

## Requisitos

- Python 3.11+ (desenvolvido com 3.13)
- Microfone e saída de áudio só para `--voz`
- PyTorch (`torch`) — usado pelo decompositor e pelo extrator de slots; **não está** no `requirements.txt`, instale à parte

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install torch
```

Na primeira execução o Hugging Face baixa o embedding `paraphrase-multilingual-MiniLM-L12-v2`. No modo voz o Faster-Whisper baixa o modelo `small`.

## Modelos (não vão pro git)

Pesos, ONNX e notas geradas ficam de fora do repositório de propósito. Sem eles o app não sobe.

O runtime espera **nomes em inglês**:

```
models/
  category/professor.joblib
  subcategory/informational/professor_sub_informacional.joblib
  subcategory/transactional/professor_sub_transacional.joblib
  subcategory/engagement/professor_sub_engajamento.joblib
  greeting/professor_saudacao.joblib
  decomposer/modelo_karen.pt
  slots/note/          # pasta Hugging Face (config, tokenizer, safetensors)
  wakeword/karen.onnx
  voice/kokoro/kokoro-v1.0.onnx
  voice/kokoro/voices-v1.0.bin
```

### Treinar os classificadores e o decompositor

Com o venv ativo, a partir da raiz do mark10:

```bash
python treinamento/treinar.py
```

Isso roda, nesta ordem: decompositor → categoria → subcategorias → saudação → slots de nota.

Alguns treinadores ainda gravam pastas em português (`decompositor/`, `slots/nota/`). Se o app não achar o arquivo, copie (ou crie um symlink) para o caminho em inglês da tabela acima.

Dados de treino: `dados/treinamento/`.

### Voz (Kokoro)

Coloque os arquivos oficiais do Kokoro ONNX em `models/voice/kokoro/`. Sem eles a Karen processa o comando mas não fala.

### Wake word

`models/wakeword/karen.onnx` é o detector da palavra **"Karen"** (LiveKit wakeword). Sem esse arquivo o modo `--voz` não inicia.

## Uso

```bash
# terminal
python -m app.main

# microfone
python -m app.main --voz
```

No modo texto: `sair` / `exit` / `q` encerra; `clear` limpa a tela.

No modo voz: diga **Karen** e o comando na sequência, ou só **Karen** e espere ela pedir pra falar. `Ctrl+C` sai.

Exemplos:

```
bom dia
que horas são
que dia é hoje
anota comprar pão
anota em markdown a ata da reunião
anota tomar água e que horas são
```

Notas vão para `storage/notes/` (timestamp no nome). Esse diretório não é versionado.

## Layout

```
app/            orquestração, classificação, decomposição, áudio, TTS
domains/        ferramentas por intenção (inglês no path)
dados/          CSVs de treino
treinamento/    pipeline de treino
models/         pesos locais (gitignored)
storage/notes/  notas criadas em runtime (gitignored)
```

## O que o Git não leva

O `.gitignore` deste mark (e o da raiz do monorepo Karen) bloqueia:

- `.venv/`, caches Python, IDEs
- `.env`, chaves, `credentials.json`
- qualquer peso: `.pt`, `.onnx`, `.safetensors`, `.bin`, `.joblib`
- a pasta `models/` inteira (incluindo leftovers em português e tokenizers)
- notas em `storage/notes/` e `storage/notas/`
- dumps (`contextogeral*.md`), logs e áudio capturado (`.wav`, `.mp3`, …)

Antes de um `git add`, vale conferir:

```bash
git status
git check-ignore -v models/wakeword/karen.onnx models/voice/kokoro/voices-v1.0.bin storage/notes/qualquer.md
```

Os três devem aparecer como ignorados.

## Dependências de runtime

| Peça | Pacote / artefato |
| --- | --- |
| Embeddings + SVM/logreg | `sentence-transformers`, `scikit-learn`, `joblib` |
| Decompositor | `torch` + `modelo_karen.pt` |
| Slots de nota | `transformers` + pasta `models/slots/note` |
| Wake word | `livekit-wakeword` + `karen.onnx` |
| STT | `faster-whisper` (modelo `small`) |
| TTS | `kokoro-onnx` + ONNX/voices do Kokoro |
| Áudio | `sounddevice`, `soundfile`, `pygame` |
