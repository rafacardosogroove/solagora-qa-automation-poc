import os
import subprocess
from collections import Counter
from datetime import datetime

# ==============================================================================
# MAPEAMENTO REAL DOS GATES (baseado nas tags reais do projeto)
# ==============================================================================
GATES = [
    {"numero": "01", "nome": "Login",             "tag": "@gate01"},
    {"numero": "02", "nome": "Simulação",          "tag": "@gate02"},
    {"numero": "03", "nome": "Análise de Crédito", "tag": "@gate03"},
    {"numero": "04", "nome": "Documentação",       "tag": "@gate04"},
    {"numero": "05", "nome": "Mesa Interna",       "tag": "@gate05"},
    {"numero": "06", "nome": "Assinatura",         "tag": "@gate06"},
    {"numero": "07", "nome": "Notas Fiscais",      "tag": "@gate07"},
    {"numero": "08", "nome": "Equipamentos",       "tag": "@gate08"},
]

# Bots que poluem o ranking — ignorados
BOTS = {"robô da qualidade (qa bot)", "qa bot", "github-actions", "github actions"}

# URL do Allure Report publicado no GitHub Pages
ALLURE_REPORT_URL = "https://rafacardosogroove.github.io/solagora-qa-automation-poc/"


# ==============================================================================
# GIT HELPERS
# ==============================================================================

def _git(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode(errors="ignore").strip()
    except Exception:
        return ""


def get_last_committer():
    return _git("git log -1 --format=%an") or "QA Bot"


def get_git_commits(limit=7):
    raw = _git(f'git log -{limit} --format=%ad|||%an|||%s --date=format:"%d/%m %H:%M"')
    linhas = [l for l in raw.split("\n") if l.strip()]
    resultado = []
    for linha in linhas:
        partes = linha.split("|||")
        if len(partes) == 3:
            resultado.append({"data": partes[0].strip('"'), "autor": partes[1], "msg": partes[2]})
    return resultado


def get_top_contributors(top=5):
    raw = _git("git log --format=%an")
    autores = [a for a in raw.split("\n") if a.strip() and a.strip().lower() not in BOTS]
    return Counter(autores).most_common(top)


def get_total_commits():
    raw = _git("git log --format=%an")
    return len([a for a in raw.split("\n") if a.strip() and a.strip().lower() not in BOTS])


# ==============================================================================
# ANÁLISE DAS FEATURES
# ==============================================================================

def extrair_autor_do_bdd(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            for _ in range(15):
                linha = f.readline()
                if not linha:
                    break
                if "Autor:" in linha:
                    return linha.split("Autor:")[1].strip()
    except Exception:
        pass
    return "—"


def gerar_metricas_bdd(diretorio="features"):
    total_features = 0
    total_cenarios = 0
    tags_contador = Counter()
    dados_features = []

    if not os.path.exists(diretorio):
        return 0, 0, [], Counter()

    for root, _, files in os.walk(diretorio):
        for file in files:
            if not file.endswith(".feature"):
                continue

            caminho = os.path.join(root, file)
            data_m = datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%d/%m/%Y")
            autor_f = extrair_autor_do_bdd(caminho)
            nome_f = file.replace(".feature", "")
            cenarios_f = 0
            total_features += 1
            dentro_exemplos = False
            cabecalho_passado = False

            with open(caminho, "r", encoding="utf-8") as f:
                for linha in f:
                    l = linha.strip()
                    if not l:
                        continue

                    for token in l.split():
                        if token.startswith("@"):
                            tags_contador[token.lower()] += 1

                    if l.startswith(("Funcionalidade:", "Feature:")):
                        nome_f = l.split(":", 1)[1].strip()

                    if l.startswith(("Cenário:", "Cenario:", "Scenario:")) and not l.startswith(
                        ("Esquema do Cenário", "Scenario Outline")
                    ):
                        cenarios_f += 1
                        total_cenarios += 1
                        dentro_exemplos = False

                    if l.startswith(("Exemplos:", "Examples:")):
                        dentro_exemplos = True
                        cabecalho_passado = False
                        continue

                    if dentro_exemplos:
                        if l.startswith("|"):
                            if not cabecalho_passado:
                                cabecalho_passado = True
                            else:
                                cenarios_f += 1
                                total_cenarios += 1
                        elif l.startswith(("@", "Cenário", "Cenario", "Esquema")):
                            dentro_exemplos = False

            dados_features.append({"nome": nome_f, "qtd": cenarios_f, "data": data_m, "autor": autor_f})

    return total_features, total_cenarios, dados_features, tags_contador


def detalhar_arquivos(diretorio, extensao):
    lista = []
    if os.path.exists(diretorio):
        for root, _, files in os.walk(diretorio):
            for file in files:
                if file.lower().endswith(extensao) and "__init__" not in file.lower() and "__pycache__" not in root:
                    lista.append(file.replace(extensao, ""))
    return sorted(lista)


# ==============================================================================
# GERAÇÃO DO DASHBOARD
# ==============================================================================

def gerar_esteira(tags_encontradas, para_email=False):
    """Linha visual de progresso — baseada nas tags reais @gate01..@gate08"""
    tags = set(tags_encontradas.keys())
    gates_cobertos = sum(1 for g in GATES if g["tag"] in tags)
    pct = int((gates_cobertos / len(GATES)) * 100)

    partes = []
    ultimo_coberto = -1
    for i, gate in enumerate(GATES):
        coberto = gate["tag"] in tags
        if coberto:
            ultimo_coberto = i

    for i, gate in enumerate(GATES):
        coberto = gate["tag"] in tags
        if coberto:
            icone = "🔵"
        elif i == ultimo_coberto + 1:
            icone = "🟡"  # próximo a implementar
        else:
            icone = "⚪"
        partes.append(f"{icone} **Gate {gate['numero']}**<br/>{gate['nome']}")

    separador = " → "
    linha = separador.join(partes)
    cobertura_bar = gerar_barra_progresso(pct, para_email)

    return linha, pct, cobertura_bar, gates_cobertos


def gerar_barra_progresso(pct, para_email=False):
    if para_email:
        # Barra HTML pura para e-mail
        cor = "#2ecc71" if pct >= 75 else "#f39c12" if pct >= 40 else "#e74c3c"
        return f"""
        <div style="background:#eee;border-radius:8px;height:18px;width:100%;margin:8px 0;">
          <div style="background:{cor};width:{pct}%;height:18px;border-radius:8px;
               text-align:center;color:white;font-size:12px;line-height:18px;font-weight:bold;">
            {pct}%
          </div>
        </div>"""
    else:
        blocos = pct // 10
        barra = "█" * blocos + "░" * (10 - blocos)
        return f"`{barra}` **{pct}%**"


def health_badge(pct):
    if pct >= 75:
        return "🟢 **Saudável**"
    elif pct >= 40:
        return "🟡 **Em Progresso**"
    else:
        return "🔴 **Inicial**"


def montar_relatorio(para_email=False):
    total_features, total_cenarios, lista_features, tags = gerar_metricas_bdd()
    pages = detalhar_arquivos("pages", ".py")
    testes = detalhar_arquivos("tests", ".py")
    commits = get_git_commits()
    autor = get_last_committer()
    top_qas = get_top_contributors()
    total_commits = get_total_commits()

    esteira_linha, pct, barra_pct, gates_cobertos = gerar_esteira(tags, para_email)
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    if para_email:
        return montar_html_email(
            autor, agora, esteira_linha, pct, barra_pct, gates_cobertos,
            top_qas, total_commits, total_cenarios, pages, testes,
            lista_features, commits, tags, health_badge(pct)
        )
    else:
        return montar_markdown(
            autor, agora, esteira_linha, pct, barra_pct, gates_cobertos,
            top_qas, total_commits, total_cenarios, pages, testes,
            lista_features, commits, tags, health_badge(pct)
        )


def montar_markdown(autor, agora, esteira_linha, pct, barra_pct, gates_cobertos,
                    top_qas, total_commits, total_cenarios, pages, testes,
                    lista_features, commits, tags, badge):
    L = []
    L.append("# 📊 Dashboard de Engenharia de Qualidade — SolAgora\n")
    L.append(f"> 👤 **Último push:** {autor} &nbsp;|&nbsp; 🕒 **Atualizado:** {agora} &nbsp;|&nbsp; Status: {badge}\n")
    L.append("---\n")

    # Esteira
    L.append("## 🛤️ Esteira de Cobertura E2E\n")
    L.append(f"> Cobertura atual: {barra_pct} — **{gates_cobertos}/{len(GATES)} gates** automatizados\n")
    L.append(f"{esteira_linha}\n")
    L.append("> 🔵 Implementado &nbsp; 🟡 Próximo &nbsp; ⚪ Pendente\n")
    L.append("---\n")

    # Números
    L.append("## 🚀 Status da Automação\n")
    L.append("| Categoria | Total |")
    L.append("|:---|:---:|")
    L.append(f"| 📝 Cenários BDD (incl. Esquemas) | **{total_cenarios}** |")
    L.append(f"| 📄 Page Objects | **{len(pages)}** |")
    L.append(f"| 🧪 Scripts de Teste | **{len(testes)}** |")
    L.append(f"| 🔁 Commits (humanos) | **{total_commits}** |\n")

    # Top QAs
    L.append("## 🏆 Ranking de QAs\n")
    L.append("| # | QA | Commits |")
    L.append("|:---:|:---|:---:|")
    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, (qa, qtd) in enumerate(top_qas):
        L.append(f"| {medalhas[i] if i < len(medalhas) else i+1} | {qa} | {qtd} |")
    L.append("")

    # Features
    L.append("## 📂 Features por Domínio\n")
    L.append("| Feature | Cenários | Autor | Modificado |")
    L.append("|:---|:---:|:---|:---:|")
    for f in lista_features:
        barra = "🟦" * min(f["qtd"], 5) + ("🟧" * (f["qtd"] - 5) if f["qtd"] > 5 else "")
        L.append(f"| {f['nome']} | {f['qtd']} {barra} | {f['autor']} | {f['data']} |")
    L.append("")

    # Commits recentes
    L.append("## 📜 Últimos Commits\n")
    L.append("| Data | Autor | Mensagem |")
    L.append("|:---|:---|:---|")
    for c in commits:
        L.append(f"| {c['data']} | **{c['autor']}** | {c['msg']} |")
    L.append("")

    # Tags
    L.append("## 🏷️ Cobertura de Tags BDD\n")
    L.append("| Tag | Ocorrências |")
    L.append("|:---|:---:|")
    for tag, qtd in tags.most_common():
        L.append(f"| `{tag}` | {qtd} |")

    L.append("\n---")
    L.append(f"**[Ver Allure Report Completo]({ALLURE_REPORT_URL})** — evidências, screenshots e steps detalhados\n")
    L.append(f"*Gerado automaticamente pelo QA Bot — {agora}*")
    return "\n".join(L)


def montar_html_email(autor, agora, esteira_linha, pct, barra_pct_html, gates_cobertos,
                      top_qas, total_commits, total_cenarios, pages, testes,
                      lista_features, commits, tags, badge):
    cor_badge = "#2ecc71" if "Saudável" in badge else "#f39c12" if "Progresso" in badge else "#e74c3c"

    # Esteira HTML
    esteira_html = ""
    tags_set = set(tags.keys())
    ultimo_coberto = -1
    for i, g in enumerate(GATES):
        if g["tag"] in tags_set:
            ultimo_coberto = i

    for i, gate in enumerate(GATES):
        coberto = gate["tag"] in tags_set
        proximo = (i == ultimo_coberto + 1)
        if coberto:
            bg, cor_texto = "#2980b9", "white"
            icone = "✅"
        elif proximo:
            bg, cor_texto = "#f39c12", "white"
            icone = "▶️"
        else:
            bg, cor_texto = "#ecf0f1", "#999"
            icone = "○"
        seta = " → " if i < len(GATES) - 1 else ""
        esteira_html += f"""
        <span style="display:inline-block;background:{bg};color:{cor_texto};
             padding:6px 12px;border-radius:20px;font-size:12px;font-weight:bold;margin:3px;">
          {icone} G{gate['numero']} {gate['nome']}
        </span>{seta}"""

    # Top QAs HTML
    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    ranking_html = ""
    for i, (qa, qtd) in enumerate(top_qas):
        m = medalhas[i] if i < len(medalhas) else str(i + 1)
        ranking_html += f"<tr><td style='padding:6px 12px;'>{m}</td><td style='padding:6px 12px;font-weight:bold;'>{qa}</td><td style='padding:6px 12px;text-align:center;'>{qtd}</td></tr>"

    # Features HTML
    features_html = ""
    for f in lista_features:
        barra = "🟦" * min(f["qtd"], 5) + ("🟧" * (f["qtd"] - 5) if f["qtd"] > 5 else "")
        features_html += f"<tr><td style='padding:6px 12px;'>{f['nome']}</td><td style='padding:6px 12px;text-align:center;'>{f['qtd']} {barra}</td><td style='padding:6px 12px;'>{f['autor']}</td><td style='padding:6px 12px;text-align:center;'>{f['data']}</td></tr>"

    # Commits HTML
    commits_html = ""
    for c in commits:
        commits_html += f"<tr><td style='padding:6px 12px;color:#888;'>{c['data']}</td><td style='padding:6px 12px;font-weight:bold;'>{c['autor']}</td><td style='padding:6px 12px;'>{c['msg']}</td></tr>"

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;background:#f4f6f8;margin:0;padding:20px;">
<div style="max-width:860px;margin:auto;background:white;border-radius:12px;
     box-shadow:0 2px 12px rgba(0,0,0,0.1);overflow:hidden;">

  <!-- HEADER -->
  <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:28px 32px;color:white;">
    <h1 style="margin:0;font-size:22px;">📊 Dashboard de Qualidade — SolAgora</h1>
    <p style="margin:8px 0 0;opacity:0.75;font-size:13px;">
      👤 Último push: <b>{autor}</b> &nbsp;|&nbsp; 🕒 {agora}
      &nbsp;|&nbsp; <span style="background:{cor_badge};padding:2px 10px;border-radius:10px;font-size:12px;">{badge}</span>
    </p>
  </div>

  <div style="padding:28px 32px;">

    <!-- ESTEIRA -->
    <h2 style="color:#2c3e50;border-bottom:2px solid #eee;padding-bottom:8px;">🛤️ Esteira de Cobertura E2E</h2>
    <p style="color:#555;font-size:13px;">Cobertura atual: <b>{gates_cobertos}/{len(GATES)} gates</b> automatizados</p>
    {barra_pct_html}
    <div style="margin:16px 0;line-height:2.5;">{esteira_html}</div>
    <p style="font-size:12px;color:#888;">✅ Implementado &nbsp; ▶️ Próximo &nbsp; ○ Pendente</p>

    <!-- NÚMEROS -->
    <h2 style="color:#2c3e50;border-bottom:2px solid #eee;padding-bottom:8px;">🚀 Status da Automação</h2>
    <table style="width:100%;border-collapse:collapse;">
      <tr style="background:#f8f9fa;">
        <td style="padding:10px 16px;border-radius:8px;text-align:center;">
          <div style="font-size:28px;font-weight:bold;color:#2980b9;">{total_cenarios}</div>
          <div style="font-size:12px;color:#888;">Cenários BDD</div>
        </td>
        <td style="padding:10px 16px;border-radius:8px;text-align:center;">
          <div style="font-size:28px;font-weight:bold;color:#27ae60;">{len(pages)}</div>
          <div style="font-size:12px;color:#888;">Page Objects</div>
        </td>
        <td style="padding:10px 16px;border-radius:8px;text-align:center;">
          <div style="font-size:28px;font-weight:bold;color:#8e44ad;">{len(testes)}</div>
          <div style="font-size:12px;color:#888;">Scripts de Teste</div>
        </td>
        <td style="padding:10px 16px;border-radius:8px;text-align:center;">
          <div style="font-size:28px;font-weight:bold;color:#e67e22;">{total_commits}</div>
          <div style="font-size:12px;color:#888;">Commits (humanos)</div>
        </td>
      </tr>
    </table>

    <!-- RANKING -->
    <h2 style="color:#2c3e50;border-bottom:2px solid #eee;padding-bottom:8px;margin-top:28px;">🏆 Ranking de QAs</h2>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <tr style="background:#f8f9fa;font-weight:bold;">
        <th style="padding:8px 12px;text-align:left;">#</th>
        <th style="padding:8px 12px;text-align:left;">QA</th>
        <th style="padding:8px 12px;text-align:center;">Commits</th>
      </tr>
      {ranking_html}
    </table>

    <!-- FEATURES -->
    <h2 style="color:#2c3e50;border-bottom:2px solid #eee;padding-bottom:8px;margin-top:28px;">📂 Features por Domínio</h2>
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <tr style="background:#f8f9fa;font-weight:bold;">
        <th style="padding:8px 12px;text-align:left;">Feature</th>
        <th style="padding:8px 12px;text-align:center;">Cenários</th>
        <th style="padding:8px 12px;text-align:left;">Autor</th>
        <th style="padding:8px 12px;text-align:center;">Modificado</th>
      </tr>
      {features_html}
    </table>

    <!-- COMMITS -->
    <h2 style="color:#2c3e50;border-bottom:2px solid #eee;padding-bottom:8px;margin-top:28px;">📜 Últimos Commits</h2>
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <tr style="background:#f8f9fa;font-weight:bold;">
        <th style="padding:8px 12px;text-align:left;">Data</th>
        <th style="padding:8px 12px;text-align:left;">Autor</th>
        <th style="padding:8px 12px;text-align:left;">Mensagem</th>
      </tr>
      {commits_html}
    </table>

  </div>

  <!-- FOOTER -->
  <!-- BOTÃO ALLURE REPORT -->
  <div style="padding:20px 32px;text-align:center;border-top:1px solid #eee;">
    <a href="{ALLURE_REPORT_URL}"
       style="display:inline-block;background:linear-gradient(135deg,#e74c3c,#c0392b);
              color:white;padding:12px 32px;border-radius:8px;text-decoration:none;
              font-weight:bold;font-size:14px;letter-spacing:0.5px;">
      Ver Allure Report Completo →
    </a>
    <p style="margin:8px 0 0;font-size:11px;color:#aaa;">
      Evidências, screenshots e steps detalhados de cada execução
    </p>
  </div>

  <!-- FOOTER -->
  <div style="background:#f8f9fa;padding:16px 32px;text-align:center;
       font-size:12px;color:#aaa;border-top:1px solid #eee;">
    Gerado automaticamente pelo QA Bot — {agora}<br/>
    SolAgora Quality Engineering
  </div>

</div>
</body>
</html>"""


# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == "__main__":
    # Gera DASHBOARD.md (markdown para o repositório)
    with open("DASHBOARD.md", "w", encoding="utf-8") as f:
        f.write(montar_relatorio(para_email=False))

    # Gera email_dashboard.html (HTML rico para o e-mail)
    with open("email_dashboard.html", "w", encoding="utf-8") as f:
        f.write(montar_relatorio(para_email=True))

    print("DASHBOARD.md e email_dashboard.html gerados com sucesso.")
