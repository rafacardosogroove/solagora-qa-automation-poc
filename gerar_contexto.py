import os
import ast
import json

# 🚫 Pastas de sistema e binários que REALMENTE não queremos (o resto entra tudo)
IGNORE_DIRS = {
    '.git', '.venv', 'venv', '__pycache__', '.pytest_cache',
    'allure-results', 'allure-report', '.idea', '.vscode',
    'node_modules', 'build', 'dist'
}

# 🚫 Arquivos binários ou de mídia que corromperiam o TXT
IGNORE_FILES = {
    'contexto_monstro_projeto.txt', 'poetry.lock', 'package-lock.json'
}

# 🚫 Extensões que são lixo ou binários (Imagens, PDF, Executáveis)
IGNORE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.pyc', '.exe',
    '.dll', '.so', '.db', '.zip', '.tar', '.gz'
}

# 💻 Dicionário de Mapeamento (Função Python -> Comando Terminal)
TERMINAL_COMMANDS = {
    "aprovar_documentacao": "python hml_client.py --aprovar-doc <PID>",
    "aprovar_projeto": "python hml_client.py --analiseinterna <PID> aprovar",
    "reprovar_projeto": "python hml_client.py --analiseinterna <PID> reprovar",
    "finalizar_biometria": "python hml_client.py --biometria <PID>",
    "emitir_ccb": "python hml_client.py --emitir-ccb <PID>",
    "aguardar_assinatura": "python hml_client.py --aguardar-assinatura <PID>",
    "finalizar_assinatura": "python hml_client.py --finalizar-assinatura <PID>",
    "fluxo_cessao": "python hml_client.py --cessao <PID> [--tipo NFV|NFF]",
    "classificar_nota": "python hml_client.py --classificar-nota <PID> [--tipo NFV|NFF]",
    "aprovar_cessao": "python hml_client.py --aprovar-cessao <PID>",
    "callback_bmp": "python hml_client.py --callback-bmp <PID> <SITUACAO>",
    "enviar_callbacks_cessao": "python hml_client.py --callback <PID> [--intervalo 5]",
    "resolver_split_pagamento": "python hml_client.py --split <PID>",
    "equip_aguardar_doc": "python hml_client.py --equip-doc <PID>",
    "equip_confirmar_integrador": "python hml_client.py --equip-integrador <PID>",
    "equip_confirmar_cliente": "python hml_client.py --equip-cliente <PID>",
    "confirmar_equipamento_entregue": "python hml_client.py --equip-cliente <PID>",
    "equip_forcar_monitoracao": "python hml_client.py --equip-monitoracao <PID>",
    "fund_payment_started": "python hml_client.py --fund-started <PID>",
    "fund_payment_finished": "python hml_client.py --fund-finished <PID>",
    "ocr_toggle": "python hml_client.py --ocr on|off",
    "liberar_telefone": "python hml_client.py --liberar-telefone <TEL> --executar",
    "buscar_projetos_cpf": "python hml_client.py --projeto-cpf <CPF>",
    "_get_status_hml": "python hml_client.py --status <PID>",
    "_set_status_hml": "python hml_client.py --set-status <PID> <SID>"
}


def extrair_metadados_ast(conteudo_python):
    """Lê o código Python e extrai os parâmetros exatos das funções."""
    metadata = {}
    try:
        tree = ast.parse(conteudo_python)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                if func_name in TERMINAL_COMMANDS:
                    params_list = []

                    # Lógica para descobrir se o parâmetro é obrigatório ou tem valor default
                    num_args = len(node.args.args)
                    num_defaults = len(node.args.defaults)
                    default_offset = num_args - num_defaults

                    for i, arg in enumerate(node.args.args):
                        if arg.arg == 'self':
                            continue

                        is_optional = i >= default_offset
                        if is_optional:
                            def_node = node.args.defaults[i - default_offset]
                            try:
                                default_val = ast.literal_eval(def_node)
                            except Exception:
                                default_val = "..."  # Caso seja um default complexo

                            params_list.append(f"{arg.arg} (opcional, default: '{default_val}')")
                        else:
                            params_list.append(f"{arg.arg} (obrigatório)")

                    metadata[func_name] = {
                        "cli": TERMINAL_COMMANDS[func_name],
                        "params": params_list
                    }
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível fazer o parse AST: {e}")
    return metadata


def gerar_contexto_total(diretorio_raiz, arquivo_saida):
    print(f"📡 Iniciando varredura profunda em: {os.path.abspath(diretorio_raiz)}")

    total_arquivos = 0
    total_linhas = 0
    metadata_global = {}  # Guarda a inteligência artificial extraída

    with open(arquivo_saida, 'w', encoding='utf-8') as outfile:
        outfile.write("================================================================================\n")
        outfile.write("       CONTEXTO COMPLETO E EXAUSTIVO DO PROJETO SOLAGORA AUTOMATION             \n")
        outfile.write(f"       Gerado em: {os.path.abspath(diretorio_raiz)}\n")
        outfile.write("================================================================================\n\n")

        for root, dirs, files in os.walk(diretorio_raiz):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()

                if file in IGNORE_FILES: continue
                if ext in IGNORE_EXTENSIONS: continue
                if file.startswith('._'): continue

                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, diretorio_raiz)

                try:
                    with open(caminho_completo, 'r', encoding='utf-8', errors='replace') as infile:
                        conteudo = infile.read()
                        linhas_do_arquivo = len(conteudo.splitlines())

                        # Se for o hml_client, aplica a extração AST antes de escrever
                        if file == 'hml_client.py':
                            metadata_global = extrair_metadados_ast(conteudo)

                        outfile.write("+" * 80 + "\n")
                        outfile.write(f"📄 ARQUIVO: {caminho_relativo} ({linhas_do_arquivo} linhas)\n")
                        outfile.write("+" * 80 + "\n")
                        outfile.write(conteudo)
                        outfile.write("\n\n")

                        total_arquivos += 1
                        total_linhas += linhas_do_arquivo
                        print(f"✅ Incluído: {caminho_relativo} [{linhas_do_arquivo} linhas]")

                except Exception as e:
                    outfile.write(f"⚠️ [ERRO AO LER {caminho_relativo}]: {e}\n\n")

        # 👻 INJEÇÃO DO ARQUIVO FANTASMA (JSON) NO FINAL DO TXT
        if metadata_global:
            json_str = json.dumps(metadata_global, indent=4, ensure_ascii=False)
            linhas_json = len(json_str.splitlines())
            outfile.write("+" * 80 + "\n")
            outfile.write(f"📄 ARQUIVO: solagora_metadata.json ({linhas_json} linhas)\n")
            outfile.write("+" * 80 + "\n")
            outfile.write(json_str)
            outfile.write("\n\n")
            total_arquivos += 1
            total_linhas += linhas_json
            print(f"🧠✅ Injetado Arquivo Virtual: solagora_metadata.json [{linhas_json} linhas]")

        resumo = (
            f"\n\n{'=' * 80}\n"
            f"📊 RESUMO DA ENGENHARIA DE QUALIDADE:\n"
            f"Total de arquivos processados: {total_arquivos}\n"
            f"Total de linhas de inteligência: {total_linhas}\n"
            f"{'=' * 80}\n"
        )
        outfile.write(resumo)
        outfile.seek(0, 0)

    print(f"\n🚀 CONCLUÍDO!")
    print(f"📁 Arquivo gerado: {arquivo_saida}")
    print(f"📏 Volume total: {total_linhas} linhas de código e documentação.")


if __name__ == "__main__":
    gerar_contexto_total(".", "contexto_monstro_projeto.txt")