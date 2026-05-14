#!/usr/bin/env python3
"""
importar_bugs_azure_boards.py
─────────────────────────────
Lê todos os arquivos BUG-*.md em evidence/bugs/ e cria Work Items
do tipo "Bug" no Azure Boards via REST API.

USO:
    # Variáveis de ambiente obrigatórias:
    export AZURE_PAT="seu_personal_access_token"

    # Opcionalmente sobrescrever organização/projeto:
    export AZURE_ORG="credgrid"
    export AZURE_PROJECT="SolAgora"

    python scripts/importar_bugs_azure_boards.py

    # Dry-run (não cria, só mostra o que seria criado):
    python scripts/importar_bugs_azure_boards.py --dry-run

GERAR PAT:
    Azure DevOps → User Settings (ícone canto superior direito)
    → Personal Access Tokens → New Token
    Scopes necessários: Work Items → Read & Write
"""

import os
import re
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIGURAÇÃO
# ──────────────────────────────────────────────
AZURE_ORG     = os.environ.get("AZURE_ORG",     "credgrid")
AZURE_PROJECT = os.environ.get("AZURE_PROJECT", "SolAgora")
AZURE_PAT     = os.environ.get("AZURE_PAT",     "")

# Raiz do projeto (pasta pai de /scripts)
ROOT = Path(__file__).parent.parent
BUGS_DIR = ROOT / "evidence" / "bugs"

# Mapeamento de severidade do .md → valores do Azure Boards
SEVERIDADE_MAP = {
    "crítico":   "1 - Critical",
    "critico":   "1 - Critical",
    "critical":  "1 - Critical",
    "alto":      "2 - High",
    "high":      "2 - High",
    "médio":     "3 - Medium",
    "medio":     "3 - Medium",
    "medium":    "3 - Medium",
    "baixo":     "4 - Low",
    "low":       "4 - Low",
}


# ──────────────────────────────────────────────
# PARSER DOS .md
# ──────────────────────────────────────────────
def extrair_campo_tabela(conteudo: str, campo: str) -> str:
    """Extrai valor de uma linha de tabela markdown: | **Campo** | Valor |"""
    padrao = rf"\|\s*\*\*{re.escape(campo)}\*\*\s*\|\s*(.+?)\s*\|"
    m = re.search(padrao, conteudo, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extrair_secao(conteudo: str, titulo: str) -> str:
    """Extrai o conteúdo de uma seção ## Título até a próxima seção ##."""
    padrao = rf"##\s+{re.escape(titulo)}\s*\n(.*?)(?=\n##|\Z)"
    m = re.search(padrao, conteudo, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def mapear_severidade(texto: str) -> str:
    """Converte severidade do .md para valor aceito pelo Azure Boards."""
    texto_lower = texto.lower()
    for chave, valor in SEVERIDADE_MAP.items():
        if chave in texto_lower:
            return valor
    return "3 - Medium"  # padrão se não encontrar


def parse_bug_md(caminho: Path) -> dict:
    """Parseia um arquivo BUG-XX.md e retorna dict com campos do work item."""
    conteudo = caminho.read_text(encoding="utf-8")

    # Título: primeira linha # BUG-XX — Descrição
    titulo_match = re.match(r"#\s+(BUG-\d+\s+[—–-]+\s+.+)", conteudo)
    titulo = titulo_match.group(1).strip() if titulo_match else caminho.stem

    bug_id    = extrair_campo_tabela(conteudo, "ID")
    sev_raw   = extrair_campo_tabela(conteudo, "Severidade")
    tela      = extrair_campo_tabela(conteudo, "Tela")
    data      = extrair_campo_tabela(conteudo, "Data")
    autor     = extrair_campo_tabela(conteudo, "Autor")
    status_md = extrair_campo_tabela(conteudo, "Status")

    descricao  = extrair_secao(conteudo, "Descrição")
    reproducao = extrair_secao(conteudo, "Passo a Passo para Reprodução")
    esperado   = extrair_secao(conteudo, "Comportamento Esperado")
    impacto    = extrair_secao(conteudo, "Impacto")
    feature    = extrair_secao(conteudo, "Feature BDD Relacionada")

    # Monta campo "Repro Steps" em HTML (Azure Boards aceita HTML nos campos de texto)
    repro_html = _md_to_simple_html(reproducao) if reproducao else "<p>Ver arquivo .md para reprodução.</p>"
    desc_html  = _md_to_simple_html(
        f"**Tela:** {tela}\n\n"
        f"**Registrado em:** {data} por {autor}\n\n"
        f"**Status de confirmação:** {status_md}\n\n"
        + (f"### Descrição\n{descricao}\n\n" if descricao else "")
        + (f"### Impacto\n{impacto}\n\n" if impacto else "")
        + (f"### Comportamento Esperado\n{esperado}\n\n" if esperado else "")
        + (f"### Feature BDD\n{feature}" if feature else "")
    )

    return {
        "titulo":       titulo,
        "bug_id":       bug_id,
        "severidade":   mapear_severidade(sev_raw),
        "sev_raw":      sev_raw,
        "tela":         tela,
        "repro_html":   repro_html,
        "desc_html":    desc_html,
        "tags":         _extrair_tags(conteudo, bug_id),
        "arquivo":      str(caminho.relative_to(ROOT)),
    }


def _md_to_simple_html(texto: str) -> str:
    """Converte markdown básico para HTML simples aceito pelo Azure Boards."""
    if not texto:
        return ""
    linhas = texto.split("\n")
    html_parts = []
    for linha in linhas:
        if linha.startswith("### "):
            html_parts.append(f"<h3>{linha[4:]}</h3>")
        elif linha.startswith("## "):
            html_parts.append(f"<h2>{linha[3:]}</h2>")
        elif linha.startswith("# "):
            html_parts.append(f"<h1>{linha[2:]}</h1>")
        elif linha.startswith("- ") or linha.startswith("* "):
            html_parts.append(f"<li>{linha[2:]}</li>")
        elif linha.startswith("```"):
            html_parts.append("<pre><code>")
        elif linha == "```":
            html_parts.append("</code></pre>")
        elif linha.strip() == "":
            html_parts.append("<br>")
        else:
            # Bold inline
            linha = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", linha)
            linha = re.sub(r"`(.+?)`", r"<code>\1</code>", linha)
            html_parts.append(f"<p>{linha}</p>")
    return "\n".join(html_parts)


def _extrair_tags(conteudo: str, bug_id: str) -> str:
    """Gera tags para o work item baseado no conteúdo."""
    tags = [bug_id, "qa-automation"]
    if "playwright" in conteudo.lower():
        tags.append("playwright")
    if "react" in conteudo.lower() or "dom" in conteudo.lower():
        tags.append("frontend")
    if "api" in conteudo.lower():
        tags.append("api")
    if "admin" in conteudo.lower():
        tags.append("admin")
    if "integrador" in conteudo.lower():
        tags.append("integrador")
    return "; ".join(tags)


# ──────────────────────────────────────────────
# AZURE DEVOPS REST API
# ──────────────────────────────────────────────
def _auth_header(pat: str) -> str:
    token = base64.b64encode(f":{pat}".encode()).decode()
    return f"Basic {token}"


def criar_work_item(bug: dict, dry_run: bool = False) -> dict | None:
    """Cria um Work Item do tipo Bug no Azure Boards."""
    url = (
        f"https://dev.azure.com/{AZURE_ORG}/{AZURE_PROJECT}/_apis/wit/workitems"
        f"/$Bug?api-version=7.1"
    )

    payload = [
        {"op": "add", "path": "/fields/System.Title",              "value": bug["titulo"]},
        {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Severity", "value": bug["severidade"]},
        {"op": "add", "path": "/fields/Microsoft.VSTS.TCM.ReproSteps", "value": bug["repro_html"]},
        {"op": "add", "path": "/fields/System.Description",         "value": bug["desc_html"]},
        {"op": "add", "path": "/fields/System.Tags",                "value": bug["tags"]},
        {"op": "add", "path": "/fields/System.State",               "value": "New"},
        # Campo personalizado para ID original (opcional — comentar se der erro)
        # {"op": "add", "path": "/fields/Custom.OriginalBugID",      "value": bug["bug_id"]},
    ]

    print(f"\n  {'[DRY-RUN] ' if dry_run else ''}Criando: {bug['titulo']}")
    print(f"    Severidade : {bug['severidade']} (raw: {bug['sev_raw']})")
    print(f"    Tags       : {bug['tags']}")

    if dry_run:
        return {"id": "DRY-RUN", "titulo": bug["titulo"]}

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": _auth_header(AZURE_PAT),
            "Content-Type":  "application/json-patch+json",
            "Accept":        "application/json",
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resultado = json.loads(resp.read().decode())
            wi_id  = resultado.get("id")
            wi_url = resultado.get("_links", {}).get("html", {}).get("href", "")
            print(f"    ✅ Criado: Work Item #{wi_id} → {wi_url}")
            return resultado
    except urllib.error.HTTPError as e:
        corpo = e.read().decode()
        print(f"    ❌ Erro HTTP {e.code}: {corpo[:300]}")
        return None
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return None


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Importa bugs do /evidence/bugs para Azure Boards")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem criar work items")
    parser.add_argument("--bug",     type=str, default=None, help="Importar apenas BUG-XX específico (ex: BUG-01)")
    args = parser.parse_args()

    if not args.dry_run and not AZURE_PAT:
        print("❌ Variável AZURE_PAT não definida.")
        print("   export AZURE_PAT='seu_personal_access_token'")
        sys.exit(1)

    # Coleta todos os .md de bugs
    arquivos = sorted(BUGS_DIR.rglob("BUG-*.md"))
    # Ignora relatórios consolidados (CUSTOMERS-BUG-REPORT.md etc)
    arquivos = [f for f in arquivos if re.match(r"BUG-\d+", f.stem)]

    if args.bug:
        arquivos = [f for f in arquivos if args.bug.upper() in f.stem.upper()]

    if not arquivos:
        print("Nenhum arquivo BUG-*.md encontrado em evidence/bugs/")
        sys.exit(0)

    print(f"\n{'='*60}")
    print(f"  Azure Boards Bug Importer")
    print(f"  Org: {AZURE_ORG} | Projeto: {AZURE_PROJECT}")
    print(f"  Modo: {'DRY-RUN' if args.dry_run else 'REAL'}")
    print(f"  Bugs encontrados: {len(arquivos)}")
    print(f"{'='*60}")

    criados   = []
    com_erro  = []

    for arquivo in arquivos:
        try:
            bug = parse_bug_md(arquivo)
            resultado = criar_work_item(bug, dry_run=args.dry_run)
            if resultado:
                criados.append(bug["titulo"])
            else:
                com_erro.append(arquivo.stem)
        except Exception as e:
            print(f"\n  ❌ Erro ao processar {arquivo.name}: {e}")
            com_erro.append(arquivo.stem)

    print(f"\n{'='*60}")
    print(f"  RESUMO")
    print(f"  Criados com sucesso : {len(criados)}")
    print(f"  Com erro            : {len(com_erro)}")
    if com_erro:
        print(f"  Falharam            : {', '.join(com_erro)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
