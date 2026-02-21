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
                if not linha:
                    break
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
                    total_features += 1
                    cenarios_f = 0
                    nome_f = file.replace('.feature', '')
                    autor_f = extrair_autor_do_bdd(caminho)

                    with open(caminho, 'r', encoding='utf-8') as f:
                        for linha in f:
                            l = linha.strip()
                            for p in l.split():
                                if p.startswith('@'): tags_contador[p] += 1
                            if l.startswith(('Funcionalidade:', 'Feature:')):
                                nome_f = l.split(':', 1)[1].strip()
                            if l.startswith(('Cenário:', 'Cenario:', 'Esquema do Cenário:', 'Scenario:')):
                                total_cenarios += 1
                                cenarios_f += 1
                    
                    dados_features.append({'nome': nome_f, 'qtd': cenarios_f, 'data': data_m, 'autor': autor_f})
    return total_features, total_cenarios, dados_features, tags_contador

def montar_relatorio(para_email=False):
    _, cenarios, lista_features, tags = gerar_metricas_bdd()
    pages = detalhar_arquivos('pages', '.py')
    testes = detalhar_arquivos('tests', '.py') 
    commits = get_git_commits()
    autor = get_last_committer()
    top_qas = get_top_contributors()
    
    linhas = []
    linhas.append("# 📊 Dashboard de Engenharia de Qualidade - SolAgora\n")
    linhas.append(f"> 👤 **Último Push:** {autor} | 🕒 **Atualizado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    
    linhas.append("## 🏆 Top QAs (Ranking de Commits)")
    linhas.append("") # <--- Linha em branco obrigatória para o e-mail não quebrar a tabela
    linhas.append("| QA | Total de Pushes (Commits) |")
    linhas.append("|:---|:---:|")
    for qa, qtd in top_qas:
        linhas.append(f"| 👨‍💻 **{qa}** | {qtd} |")
    
    linhas.append("\n## 🚀 Status da Automação")
    linhas.append("") # <--- Linha em branco
    linhas.append("| Categoria | Total |")
    linhas.append("| :--- | :---: |")
    linhas.append(f"| 📝 Cenários BDD | {cenarios} |")
    linhas.append(f"| 📄 Page Objects | {len(pages)} |")
    linhas.append(f"| 🧪 Scripts de Teste | {len(testes)} |")
    
    linhas.append("\n## 📂 Detalhamento de Negócio (Features)")
    linhas.append("") # <--- Linha em branco
    linhas.append("| Feature | Cenários | Autor Principal | Modificação |")
    linhas.append("|:---|:---:|:---|:---:|")
    for f in lista_features:
        linhas.append(f"| {f['nome']} | {f['qtd']} | {f['autor']} | {f['data']} |")

    linhas.append("\n### 📄 Page Objects Criados")
    linhas.append("") # <--- Linha em branco
    if pages:
        if para_email: 
            for p in pages: linhas.append(f"- `{p}`")
        else:          
            linhas.append("<details>")
            linhas.append(f"<summary><b>Clique para ver a lista de {len(pages)} pages</b></summary>\n\n<ul>")
            for p in pages: linhas.append(f"<li><code>{p}</code></li>")
            linhas.append("</ul>\n</details>")
    else:
        linhas.append("*Nenhuma page encontrada na pasta /pages*")

    linhas.append("\n### 🧪 Scripts de Teste Automatizados")
    linhas.append("") # <--- Linha em branco
    if testes:
        if para_email: 
            for t in testes: linhas.append(f"- `{t}`")
        else:          
            linhas.append("<details>")
            linhas.append(f"<summary><b>Clique para ver os {len(testes)} scripts de teste</b></summary>\n\n<ul>")
            for t in testes: linhas.append(f"<li><code>{t}</code></li>")
            linhas.append("</ul>\n</details>")
    else:
        linhas.append("*Nenhum script de teste encontrado na pasta /tests*")
        
    linhas.append("\n## 📜 Histórico Recente de Commits")
    linhas.append("") # <--- Linha em branco
    linhas.append("| Data | Autor | Mensagem |")
    linhas.append("|:---|:---|:---|")
    for c in commits:
        cols = c.split(" | ")
        if len(cols) == 3: linhas.append(f"| {cols[0]} | **{cols[1]}** | {cols[2]} |")

    linhas.append("\n## 🏷️ Cobertura de Tags")
    linhas.append("") # <--- Linha em branco
    linhas.append("| Tag | Usos |")
    linhas.append("|---|---|")
    for tag, qtd in tags.most_common():
        linhas.append(f"| `{tag}` | {qtd} |")
        
    return "\n".join(linhas)

if __name__ == '__main__':
    # 1. Salva a versão limpa especificamente para o envio de e-mail
    with open('email_dashboard.md', 'w', encoding='utf-8') as f:
        f.write(montar_relatorio(para_email=True))
        
    # 2. Imprime a versão com Sanfona (vai alimentar o README.md no GitHub Actions)
    print(montar_relatorio(para_email=False))