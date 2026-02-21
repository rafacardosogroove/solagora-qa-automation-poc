import os
import sys

def validar_bdd():
    erros = []
    pasta_features = 'features'

    # Verifica se a pasta existe
    if not os.path.exists(pasta_features):
        print(f"⚠️ Pasta '{pasta_features}' não encontrada.")
        sys.exit(0)

    # Varre a pasta de features
    for root, dirs, files in os.walk(pasta_features):
        for file in files:
            if file.endswith(".feature"):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()

                # Regra 1: Cabeçalho (Autor) nas primeiras 15 linhas
                tem_autor = any("Autor:" in l for l in linhas[:15])
                if not tem_autor:
                    erros.append(f"❌ [{file}] Falta a tag '# Autor: Nome' no início do arquivo.")

                passos_cenario = 0
                nome_cenario = ""
                linha_anterior = ""

                # Variações aceitas para não quebrar por falta de acento ou idioma
                variacoes_cenario = ('Cenário:', 'Cenario:', 'Esquema do Cenário:', 'Esquema do Cenario:', 'Scenario:', 'Scenario Outline:')
                variacoes_passos = ('Dado ', 'Quando ', 'Então ', 'Entao ', 'E ', 'Mas ')

                for num_linha, linha in enumerate(linhas, 1):
                    l_strip = linha.strip()
                    
                    # Pula linhas em branco para não quebrar a lógica de validação da linha anterior
                    if not l_strip:
                        continue 

                    # Regra 2: Cenário precisa de Tag na linha de cima
                    if l_strip.startswith(variacoes_cenario):
                        nome_cenario = l_strip
                        passos_cenario = 0 # Zera a contagem para o novo cenário
                        
                        if not linha_anterior.startswith('@'):
                            erros.append(f"❌ [{file} | Linha {num_linha}] O cenário não possui uma Tag (@) na linha acima.")

                    # Regra 3: Máximo de 8 passos
                    elif l_strip.startswith(variacoes_passos):
                        passos_cenario += 1
                        if passos_cenario > 8:
                            erros.append(f"❌ [{file} | Linha {num_linha}] O '{nome_cenario}' tem mais de 8 passos (Total atual: {passos_cenario}).")

                    # Salva a linha atual para ser a "linha anterior" na próxima volta do loop
                    linha_anterior = l_strip

    # Veredito Final
    if erros:
        print("🚨 FALHA NO QUALITY GATE DOS BDDS 🚨\n")
        for erro in erros:
            print(erro)
        sys.exit(1) # Cancele o Pull Request!
    else:
        print("✅ SUCESSO! Todos os BDDs estão no padrão Ouro da SolAgora!")
        sys.exit(0) # Libera o Pull Request!

if __name__ == '__main__':
    validar_bdd()