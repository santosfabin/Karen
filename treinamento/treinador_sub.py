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
CSV_PATH = ROOT_DIR / "dados" / "treinamento" / "dados_exemplo.csv"
BASE_MODELS_SUB = ROOT_DIR / "models" / "subcategory"

print("\n" + "=" * 55)
print(" [TREINADOR SUB] Iniciando Treinamento de Subcategorias...")
print("=" * 55)

if not CSV_PATH.exists():
    print(f"Erro: Arquivo {CSV_PATH} não encontrado!")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)

# Carrega o modelo de embeddings uma única vez
print("Carregando o modelo de embeddings...")
tradutor = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Identifica todas as categorias presentes nos dados
categorias = [cat for cat in df["categoria"].dropna().unique()]

for cat in categorias:
    print("\n" + "-" * 50)
    print(f"-> Processando Categoria: {cat}")
    
    df_sub = df[(df["categoria"] == cat) & (df["subcategoria"].notna())]
    
    if len(df_sub) < 10:
        print(f"   [AVISO] Apenas {len(df_sub)} linhas com subcategoria para '{cat}'. Pulando...")
        continue
    
    # Cria a pasta de destino para a subcategoria específica
    pasta_destino = BASE_MODELS_SUB / {"engajamento": "engagement", "informacional": "informational", "transacional": "transactional"}.get(cat.lower(), cat.lower())
    pasta_destino.mkdir(parents=True, exist_ok=True)
    caminho_modelo = pasta_destino / f"professor_sub_{cat.lower()}.joblib"

    print(f"   Linhas válidas: {len(df_sub)}")
    print(f"   Distribuição:\n{df_sub['subcategoria'].value_counts()}")

    X = tradutor.encode(df_sub["frase"].tolist(), show_progress_bar=False)
    y = df_sub["subcategoria"].tolist()

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    professor_sub = LogisticRegression(max_iter=1000)
    professor_sub.fit(X_treino, y_treino)

    pred = professor_sub.predict(X_teste)
    joblib.dump(professor_sub, caminho_modelo)

    print(f"   -> Salvo em: {caminho_modelo}")
    print(classification_report(y_teste, pred))

print("\n" + "=" * 55)
print(" [TREINADOR SUB] Finalizado com sucesso!")
print("=" * 55)