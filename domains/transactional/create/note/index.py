import sys
from domains.transactional.create.note.catalogo import TipoNota
from domains.transactional.create.note.identificador import identificar_tipo_nota
from domains.transactional.create.note.extrator import extrair_conteudo_nota
from domains.transactional.create.note.tools.simples import criar_nota_simples
from domains.transactional.create.note.tools.markdown import criar_nota_markdown

sys.dont_write_bytecode = True


def processar(frase: str, conteudo: str = None):
    # 1. Identifica o formato da nota (Simples ou Markdown)
    tipo_nota = identificar_tipo_nota(frase)
    print(f"    -> Tipo de Nota    : {tipo_nota.value}")

    # 2. Se não veio pronto do Decompositor, tenta extrair com o modelo
    if not conteudo:
        conteudo = extrair_conteudo_nota(frase)

    # 3. Fluxo de Diálogo se o conteúdo for ausente
    if not conteudo:
        print("    -> Status          : Nenhum conteúdo detectado na frase.")
        print("    -> Aguardando      : Pronto para anotar...")
        try:
            conteudo = input("       Digite o que deseja anotar > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n    -> Cancelado pelo usuário.")
            return

        if not conteudo:
            print("    -> Erro            : Nota cancelada (conteúdo vazio).")
            return

    # 4. Executa a ferramenta correspondente para salvar o arquivo real
    if tipo_nota == TipoNota.MARKDOWN:
        arquivo_salvo = criar_nota_markdown(conteudo)
    else:
        arquivo_salvo = criar_nota_simples(conteudo)

    # 5. Exibição do feedback final
    print("      " + "-" * 48)
    print(f"      -> Sucesso       : Arquivo criado com êxito!")
    print(f"      -> Conteúdo      : \"{conteudo}\"")
    print(f"      -> Salvo em      : {arquivo_salvo.relative_to(arquivo_salvo.parents[2])}")
    print("      " + "-" * 48)