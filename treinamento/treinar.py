import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def rodar_treino(script_nome: str):
    print(f"\n>>> Rodando: {script_nome}...")
    caminho = Path(__file__).resolve().parent / script_nome
    resultado = subprocess.run([sys.executable, str(caminho)])
    if resultado.returncode == 0:
        print(f">>> Sucesso: {script_nome}")
    else:
        print(f"!!! Erro no script: {script_nome}")
        sys.exit(1)


def main():
    print("=" * 55)
    print(" INICIANDO PIPELINE COMPLETO DE TREINAMENTO")
    print("=" * 55)

    # 0. Treina Decompositor de Fala Composta (Nível 0)
    rodar_treino("treinador_decompositor.py")

    # 1. Treina Categoria Pai (Nível 1)
    rodar_treino("treinador.py")

    # 2. Treina Subcategorias (Nível 2)
    rodar_treino("treinador_sub.py")

    # 3. Treina Especialista em Saudação (Nível 3)
    rodar_treino("treinador_saudacao.py")

    # 4. Treina Extrator de Slots de Notas (Nível 4)
    rodar_treino("treinador_slots_nota.py")

    print("\n" + "=" * 55)
    print(" PIPELINE DE TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 55)


if __name__ == "__main__":
    main()