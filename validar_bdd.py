import os
import sys

def validar_bdd():
    erros = []
    pasta_features = 'features'

    if not os.path.exists(pasta_features):
        sys.exit(0)

    for root, _, files in os.walk(pasta_features):
        for file in files:
            if file.endswith(".feature"):
                caminho = os.path.join(root, file)
                with open(caminho, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()

                tem_autor = any("Autor:" in l for l in linhas[:15])
                if not tem_autor:
                    erros.append(f"❌ [{file}] Falta 'Autor:' no início do arquivo.")

                passos_cenario = 0
                variacoes_cenario = ('Cenário:', 'Cenario:', 'Esquema do Cenário:', 'Scenario:')
                variacoes_passos = ('Dado ', 'Quando ', 'Então ', 'Entao ', 'E ', 'Mas ')
                linha_anterior = ""

                for num_linha, linha in enumerate(linhas, 1):
                    l_strip = linha.strip()
                    if not l_strip: continue

                    if l_strip.startswith(variacoes_cenario):
                        passos_cenario = 0
                        if not linha_anterior.startswith('@'):
                            erros.append(f"❌ [{file} | Linha {num_linha}] Cenário sem Tag (@).")

                    elif l_strip.startswith(variacoes_passos):
                        passos_cenario += 1
                        if passos_cenario > 8:
                            erros.append(f"❌ [{file} | Linha {num_linha}] Mais de 8 passos.")

                    linha_anterior = l_strip

    if erros:
        for erro in erros: print(erro)
        sys.exit(1)
    else:
        print("✅ BDDs Validados!")
        sys.exit(0)

if __name__ == '__main__':
    validar_bdd()