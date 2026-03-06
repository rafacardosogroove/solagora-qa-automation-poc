import os
import subprocess
from collections import Counter
from datetime import datetime


def get_last_committer():
    try:
        return subprocess.check_output(["git", "log", "-1", "--format=%an"]).decode(errors='ignore').strip()
    except:
        return "Robô de QA"


def get_git_commits(limit=5):
    try:
        output = subprocess.check_output(
            ["git", "log", f"-{limit}", "--format=%ad | %an | %s", "--date=format:%d/%m %H:%M"]
        ).decode(errors='ignore').strip()
        return output.split('\n')
    except:
        return ["Sem histórico de commits disponível"]


def get_top_contributors():
    try:
        output = subprocess.check_output(["git", "log", "--format=%an"]).decode(errors='ignore').strip()
        autores = output.split('\n')
        ranking = Counter(autores)
        return ranking.most_common(5)
    except:
        return []


def detalhar_arquivos(diretorio, extensao):
    lista_arquivos = []
    if os.path.exists(diretorio):
        for root, _, files in os.walk(diretorio):
            for file in files:
                if file.lower().endswith(extensao) and "__init__.py" not in file.lower():
                    nome_limpo = file.replace(extensao, "")
                    lista_arquivos.append(nome_limpo)
    return sorted(lista_arquivos)


def extrair_autor_do_bdd(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for _ in range(15):
                linha = f.readline()
                if not linha: break
                if "Autor:" in linha:
                    return linha.split("Autor:")[1].strip()
    except:
        pass
    return "Não identificado"


def gerar_metricas_bdd(diretorio='features'):
    total_features, total_cenarios = 0, 0
    tags_contador = Counter()
    dados_features = []

    if os.path.exists(diretorio):
        for root, _, files in os.walk(diretorio):
            for file in files:
                if file.endswith('.feature'):
                    caminho = os.path.join(root, file)
                    data_m = datetime.fromtimestamp(os.path.getmtime(caminho)).strftime('%d/%m/%Y')

                    nome_f = file.replace('.feature', '')
                    autor_f = extrair_autor_do_bdd(caminho)
                    cenarios_f = 0

                    total_features += 1
                    dentro_de_exemplos = False
                    cabecalho_passado = False

                    with open(caminho, 'r', encoding='utf-8') as f:
                        for linha in f:
                            l = linha.strip()
                            if not l: continue

                            for p in l.split():
                                if p.startswith('@'): tags_contador[p.lower()] += 1  # Garantimos minúsculo

                            if l.startswith(('Funcionalidade:', 'Feature:')):
                                nome_f = l.split(':', 1)[1].strip()

                            if l.startswith(('Cenário:', 'Cenario:', 'Scenario:')) and not l.startswith(
                                    ('Esquema do Cenário', 'Scenario Outline')):
                                cenarios_f += 1
                                total_cenarios += 1
                                dentro_de_exemplos = False

                            if l.startswith(('Exemplos:', 'Examples:')):
                                dentro_de_exemplos = True
                                cabecalho_passado = False
                                continue

                            if dentro_de_exemplos:
                                if l.startswith('|'):
                                    if not cabecalho_passado:
                                        cabecalho_passado = True
                                    else:
                                        cenarios_f += 1
                                        total_cenarios += 1
                                elif l.startswith(('@', 'Cenário', 'Cenario', 'Esquema')):
                                    dentro_de_exemplos = False

                    dados_features.append({'nome': nome_f, 'qtd': cenarios_f, 'data': data_m, 'autor': autor_f})
    return total_features, total_cenarios, dados_features, tags_contador


def gerar_esteira_progresso(tags_encontradas):
    """Gera o visual da esteira baseado em tags funcionais (@login, @simulacao, etc)"""
    etapas_obrigatorias = [
        {"nome": "Login", "tag": "@login"},
        {"nome": "Simulação", "tag": "@simulacao"},
        {"nome": "Análise de Crédito", "tag": "@analise_credito"},
        {"nome": "Documentação", "tag": "@documentacao"},
        {"nome": "Notas Fiscais", "tag": "@notas_fiscais"},
        {"nome": "Pagamento", "tag": "@pagamento"}
    ]

    esteira = []
    # Agora recebemos o dicionário corretamente
    lista_tags_projeto = list(tags_encontradas.keys())

    for etapa in etapas_obrigatorias:
        check = "🔵" if etapa['tag'] in lista_tags_projeto else "⚪"
        esteira.append(f"{check} **{etapa['nome']}**")

    return " --- ".join(esteira)


def montar_relatorio(para_email=False):
    # 'tags' aqui é o dicionário Counter retornado pela função
    _, total_cenarios, lista_features, tags = gerar_metricas_bdd()
    pages = detalhar_arquivos('pages', '.py')
    testes = detalhar_arquivos('tests', '.py')
    commits = get_git_commits()
    autor = get_last_committer()
    top_qas = get_top_contributors()

    linhas = []
    linhas.append("# 📊 Dashboard de Engenharia de Qualidade - SolAgora\n")

    # --- CHAMADA CORRIGIDA ---
    esteira_visual = gerar_esteira_progresso(tags)  # Mudamos de nomes_features para tags
    linhas.append("### 🛤️ Esteira de Cobertura (Gates)")
    linhas.append(f"{esteira_visual}\n")
    linhas.append("---\n")
    # -------------------------

    linhas.append(f"> 👤 **Último Push:** {autor} | 🕒 **Atualizado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    linhas.append("## 🏆 Top QAs (Ranking de Commits)")
    linhas.append("\n| QA | Total de Pushes (Commits) |")
    linhas.append("|:---|:---:|")
    for qa, qtd in top_qas:
        linhas.append(f"| 👨‍💻 **{qa}** | {qtd} |")

    linhas.append("\n## 🚀 Status da Automação")
    linhas.append("\n| Categoria | Total |")
    linhas.append("| :--- | :---: |")
    linhas.append(f"| 📝 Cenários Totais (incl. Esquemas) | {total_cenarios} |")
    linhas.append(f"| 📄 Page Objects | {len(pages)} |")
    linhas.append(f"| 🧪 Scripts de Teste | {len(testes)} |")

    linhas.append("\n## 📂 Detalhamento de Negócio (Features)")
    linhas.append("\n| Feature | Volume de Testes | Autor Principal | Modificação |")
    linhas.append("|:---|:---|:---|:---:|")
    for f in lista_features:
        barra = "🟦" * f['qtd'] if f['qtd'] <= 5 else "🟦" * 5 + "🟧" * (f['qtd'] - 5)
        linhas.append(f"| {f['nome']} | {f['qtd']} {barra} | {f['autor']} | {f['data']} |")

    linhas.append("\n### 📄 Page Objects Criados")
    if pages:
        if para_email:
            for p in pages: linhas.append(f"- `{p}`")
        else:
            linhas.append(
                f"\n<details>\n<summary><b>Clique para ver a lista de {len(pages)} pages</b></summary>\n\n<ul>")
            for p in pages: linhas.append(f"<li><code>{p}</code></li>")
            linhas.append("</ul>\n</details>")

    linhas.append("\n## 📜 Histórico Recente de Commits")
    linhas.append("\n| Data | Autor | Mensagem |")
    linhas.append("|:---|:---|:---|")
    for c in commits:
        cols = c.split(" | ")
        if len(cols) == 3: linhas.append(f"| {cols[0]} | **{cols[1]}** | {cols[2]} |")

    linhas.append("\n## 🏷️ Cobertura de Tags")
    linhas.append("\n| Tag | Usos |")
    linhas.append("|---|---|")
    for tag, qtd in tags.most_common():
        linhas.append(f"| `{tag}` | {qtd} |")

    return "\n".join(linhas)


if __name__ == '__main__':
    with open('email_dashboard.md', 'w', encoding='utf-8') as f:
        f.write(montar_relatorio(para_email=True))
    print(montar_relatorio(para_email=False))