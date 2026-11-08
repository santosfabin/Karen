import sys
from pathlib import Path
import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

sys.dont_write_bytecode = True

# Diretórios base
ROOT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT_DIR / "dados" / "treinamento" / "dados_saudacao.csv"
OUTPUT_DIR = ROOT_DIR / "models" / "greeting"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODELO_SAIDA = OUTPUT_DIR / "professor_saudacao.joblib"

print("\n" + "=" * 55)
print(" [TREINADOR SAUDAÇÃO] Iniciando Treinamento Especialista...")
print("=" * 55)

if not CSV_PATH.exists():
    print(f"Erro: Arquivo {CSV_PATH} não encontrado!")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)

print(f"Linhas carregadas: {len(df)}")
print("Distribuição das intenções:")
print(df["alvo"].value_counts())

print("\nCarregando o modelo de embeddings...")
tradutor = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

X = tradutor.encode(df["frase"].tolist(), show_progress_bar=True)
y = df["alvo"].tolist()

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

professor_saudacao = LogisticRegression(max_iter=1000)
professor_saudacao.fit(X_treino, y_treino)

pred = professor_saudacao.predict(X_teste)
joblib.dump(professor_saudacao, MODELO_SAIDA)

print(f"\n-> Sucesso! Modelo salvo em: {MODELO_SAIDA}")
print("-" * 55)
print(classification_report(y_teste, pred))
print(
    pd.DataFrame(
        confusion_matrix(y_teste, pred, labels=professor_saudacao.classes_),
        index=professor_saudacao.classes_,
        columns=professor_saudacao.classes_,
    )
)
print("=" * 55)