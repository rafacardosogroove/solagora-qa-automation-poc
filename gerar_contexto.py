import os

# 🚫 Pastas que NÃO queremos ler (para não travar a IA com lixo ou arquivos binários)
IGNORE_DIRS = {
    '.git', '.venv', 'venv', '__pycache__', '.pytest_cache',
    'allure-results', '.idea', '.vscode', 'node_modules'
}

# ✅ Extensões de arquivos que são código ou texto útil
ALLOWED_EXTENSIONS = {
    '.py', '.feature', '.md', '.txt', '.ini',
    '.json', '.yml', '.yaml', '.sql', '.env.example'
}


def gerar_txt_monstro(diretorio_raiz, arquivo_saida):
    print(f"🔍 Vasculhando o projeto em: {os.path.abspath(diretorio_raiz)}")

    with open(arquivo_saida, 'w', encoding='utf-8') as outfile:
        # Cabeçalho do arquivo
        outfile.write("CONTEXTO COMPLETO DO PROJETO DE AUTOMAÇÃO (SOLAGORA)\n")
        outfile.write("=" * 80 + "\n\n")

        arquivos_lidos = 0

        for root, dirs, files in os.walk(diretorio_raiz):
            # Remove diretórios ignorados para o os.walk não entrar neles
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()

                # Só lê se for uma extensão permitida e não for o próprio script gerador
                if ext in ALLOWED_EXTENSIONS and file != os.path.basename(__file__):
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, diretorio_raiz)

                    # Formatação visual para a IA entender onde começa e termina cada arquivo
                    outfile.write("-" * 80 + "\n")
                    outfile.write(f"📄 ARQUIVO: {caminho_relativo}\n")
                    outfile.write("-" * 80 + "\n")

                    try:
                        with open(caminho_completo, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                        arquivos_lidos += 1
                    except Exception as e:
                        outfile.write(f"[Erro ao ler o arquivo: {e}]\n")

                    outfile.write("\n\n")  # Espaço entre arquivos

    print(f"✅ Sucesso! {arquivos_lidos} arquivos consolidados.")
    print(f"📁 TXT Monstro gerado: {arquivo_saida}")


if __name__ == "__main__":
    # Define a pasta atual como raiz e o nome do arquivo que será gerado
    pasta_do_projeto = "."
    nome_do_txt = "contexto_monstro_projeto.txt"

    gerar_txt_monstro(pasta_do_projeto, nome_do_txt)