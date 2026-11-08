import sys
import time
from pathlib import Path
import joblib
from sentence_transformers import SentenceTransformer

sys.dont_write_bytecode = True

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"


class ClassificadorPai:
    tradutor_compartilhado = None

    def __init__(self, limiar_confianca: float = 0.50):
        print("Carregando modelos do Classificador Pai...")

        if ClassificadorPai.tradutor_compartilhado is None:
            ClassificadorPai.tradutor_compartilhado = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        self.tradutor = ClassificadorPai.tradutor_compartilhado
        self.modelo_pai = joblib.load(MODELS_DIR / "category" / "professor.joblib")

        self.modelos_sub = {
            "INFORMACIONAL": joblib.load(
                MODELS_DIR / "subcategory" / "informational" / "professor_sub_informacional.joblib"
            ),
            "TRANSACIONAL": joblib.load(
                MODELS_DIR / "subcategory" / "transactional" / "professor_sub_transacional.joblib"
            ),
            "ENGAJAMENTO": joblib.load(
                MODELS_DIR / "subcategory" / "engagement" / "professor_sub_engajamento.joblib"
            ),
        }

        self.limiar = limiar_confianca

    def _prever(self, vetor, modelo):
        probs = modelo.predict_proba(vetor)[0]
        indice_max = probs.argmax()
        return str(modelo.classes_[indice_max]), float(probs[indice_max])

    def classificar(self, frase: str) -> dict:
        """Classifica Nível 1 (Categoria) e Nível 2 (Subcategoria/Ação)."""
        if not frase.strip():
            return {"sucesso": False, "motivo": "Frase vazia"}

        inicio = time.perf_counter()

        # 1. Vetorização
        vetor = self.tradutor.encode([frase])

        # 2. Categoria Macro (Nível 1)
        categoria, conf_cat = self._prever(vetor, self.modelo_pai)
        if conf_cat < self.limiar:
            duracao_ms = (time.perf_counter() - inicio) * 1000
            return {
                "sucesso": False,
                "motivo": f"Incerteza na categoria (Mais próximo: {categoria} com {conf_cat:.1%})",
                "duracao_ms": duracao_ms,
            }

        # 3. Subcategoria / Ação (Nível 2)
        modelo_filho = self.modelos_sub[categoria]
        subcategoria, conf_sub = self._prever(vetor, modelo_filho)
        if conf_sub < self.limiar:
            duracao_ms = (time.perf_counter() - inicio) * 1000
            return {
                "sucesso": False,
                "motivo": f"Incerteza na ação (Detectado {categoria}, mas subcategoria com {conf_sub:.1%})",
                "duracao_ms": duracao_ms,
            }

        duracao_ms = (time.perf_counter() - inicio) * 1000

        return {
            "sucesso": True,
            "frase": frase,
            "categoria": categoria,
            "confianca_categoria": conf_cat,
            "subcategoria": subcategoria,
            "confianca_subcategoria": conf_sub,
            "duracao_ms": duracao_ms,
        }


# ==========================================
# LOOP DE TESTES FORMATADO
# ==========================================
if __name__ == "__main__":
    classificador = ClassificadorPai()

    print("\n" + "=" * 50)
    print(" CLASSIFICADOR PAI (CATEGORIA + AÇÃO)")
    print("=" * 50)

    while True:
        try:
            frase = input("\nComando > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if frase.lower() in ("sair", "exit", "q"):
            break

        if not frase:
            continue

        res = classificador.classificar(frase)

        print("-" * 50)
        if res["sucesso"]:
            print(f"  Status       : SUCESSO")
            print(f"  Categoria    : {res['categoria']} ({res['confianca_categoria']:.1%})")
            print(f"  Ação         : {res['subcategoria']} ({res['confianca_subcategoria']:.1%})")
            print(f"  Latência     : {res['duracao_ms']:.2f} ms")
        else:
            print(f"  Status       : FALHA")
            print(f"  Motivo       : {res['motivo']}")
            if "duracao_ms" in res:
                print(f"  Latência     : {res['duracao_ms']:.2f} ms")
        print("-" * 50)