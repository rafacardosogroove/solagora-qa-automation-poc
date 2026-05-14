#!/usr/bin/env python3
"""
setup_azure_devops.py
─────────────────────
Script único que configura tudo no Azure DevOps com um PAT.

O QUE FAZ:
  1. Descobre o ID do repositório Git
  2. Registra os 3 pipelines (allure-report, dashboard-email, pr-quality-gate, auto-bug-on-failure)
  3. Cria Variable Groups: qa-emails (EMAIL_USER, EMAIL_PASS) e qa-boards (AZURE_PAT)
  4. Importa os 35 bugs de evidence/bugs/ como Work Items no Azure Boards
  5. Configura Branch Policy: PR para main exige quality gate passar

USO:
  python scripts/setup_azure_devops.py --pat SEU_PAT [--email-user GMAIL] [--email-pass SENHA_APP]

  Flags opcionais:
    --dry-run         Simula sem criar nada
    --skip-bugs       Pula importação de bugs
    --skip-pipelines  Pula registro de pipelines
    --skip-policy     Pula branch policy
    --skip-vargroups  Pula criação de variable groups

COMO GERAR O PAT:
  1. Acesse: https://dev.azure.com/credgrid/_usersSettings/tokens
  2. New Token → Name: "qa-automation-setup"
  3. Scopes (Custom):
     - Code: Read
     - Build: Read & Execute
     - Release: Read, Write & Execute
     - Variable Groups: Read, Create & Manage
     - Work Items: Read & Write
  4. Copie o token gerado
"""

import os
import re
import sys
import json
import base64
import argparse
import getpass
import urllib.request
import urllib.error
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
ORG          = "credgrid"
PROJECT      = "SolAgora"
REPO_NAME    = "Automation_e2e_testing"
API          = "7.1"
ROOT         = Path(__file__).parent.parent
BUGS_DIR     = ROOT / "evidence" / "bugs"

PIPELINES = [
    {"name": "QA — Allure Report",         "path": "/pipelines/allure-report.yml"},
    {"name": "QA — Dashboard e Email",     "path": "/pipelines/dashboard-email.yml"},
    {"name": "QA — PR Quality Gate",       "path": "/pipelines/pr-quality-gate.yml"},
    {"name": "QA — Auto Bug on Failure",   "path": "/pipelines/auto-bug-on-failure.yml"},
]

SEVERIDADE_MAP = {
    "crítico": "1 - Critical", "critico": "1 - Critical", "critical": "1 - Critical",
    "alto":    "2 - High",     "high":    "2 - High",
    "médio":   "3 - Medium",   "medio":   "3 - Medium",   "medium": "3 - Medium",
    "baixo":   "4 - Low",      "low":     "4 - Low",
}


# ──────────────────────────────────────────────
# HTTP HELPERS
# ──────────────────────────────────────────────
def _auth(pat: str) -> str:
    return "Basic " + base64.b64encode(f":{pat}".encode()).decode()


def _get(url: str, pat: str) -> dict:
    req = urllib.request.Request(url, headers={
        "Authorization": _auth(pat), "Accept": "application/json"
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _post(url: str, pat: str, payload: dict | list, content_type: str = "application/json") -> dict:
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, method="POST", headers={
        "Authorization": _auth(pat),
        "Content-Type":  content_type,
        "Accept":        "application/json",
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _patch(url: str, pat: str, payload: dict | list, content_type: str = "application/json") -> dict:
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, method="PATCH", headers={
        "Authorization": _auth(pat),
        "Content-Type":  content_type,
        "Accept":        "application/json",
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _safe(fn, desc: str):
    """Executa fn(), imprime resultado. Retorna valor ou None em erro."""
    try:
        result = fn()
        return result
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        print(f"    ❌ HTTP {e.code} — {desc}: {body}")
        return None
    except Exception as e:
        print(f"    ❌ Erro — {desc}: {e}")
        return None


# ──────────────────────────────────────────────
# STEP 1 — DESCOBRIR ID DO REPO
# ──────────────────────────────────────────────
def get_repo_id(pat: str, dry_run: bool) -> str | None:
    print("\n[1/5] Buscando ID do repositório Git...")
    if dry_run:
        print("    [DRY-RUN] repo_id = 'fake-repo-id'")
        return "fake-repo-id"

    url  = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/git/repositories?api-version={API}"
    data = _safe(lambda: _get(url, pat), "listar repositórios")
    if not data:
        return None

    repos = data.get("value", [])
    for r in repos:
        if r.get("name") == REPO_NAME:
            repo_id = r["id"]
            print(f"    ✅ Repo encontrado: {REPO_NAME} → ID: {repo_id}")
            return repo_id

    # Fallback: mostra repos disponíveis
    nomes = [r.get("name") for r in repos]
    print(f"    ⚠️  Repo '{REPO_NAME}' não encontrado. Disponíveis: {nomes}")
    if repos:
        repo_id = repos[0]["id"]
        print(f"    ↩️  Usando primeiro: {repos[0]['name']} → {repo_id}")
        return repo_id
    return None


# ──────────────────────────────────────────────
# STEP 2 — REGISTRAR PIPELINES
# ──────────────────────────────────────────────
def registrar_pipelines(pat: str, repo_id: str, dry_run: bool) -> dict[str, int]:
    """Retorna dict {nome_pipeline: definition_id} para uso na branch policy."""
    print("\n[2/5] Registrando pipelines...")
    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/pipelines?api-version={API}"

    ids = {}
    for p in PIPELINES:
        print(f"\n  → {p['name']} ({p['path']})")

        if dry_run:
            print(f"    [DRY-RUN] Pipeline seria criado.")
            ids[p["name"]] = 0
            continue

        payload = {
            "name": p["name"],
            "configuration": {
                "type": "yaml",
                "path": p["path"],
                "repository": {
                    "id":   repo_id,
                    "type": "azureReposGit",
                }
            }
        }

        result = _safe(lambda p=p, payload=payload: _post(url, pat, payload), f"criar pipeline {p['name']}")
        if result:
            pipe_id = result.get("id")
            print(f"    ✅ Pipeline criado: ID #{pipe_id}")
            ids[p["name"]] = pipe_id
        else:
            ids[p["name"]] = None

    return ids


# ──────────────────────────────────────────────
# STEP 3 — CRIAR VARIABLE GROUPS
# ──────────────────────────────────────────────
def criar_variable_groups(pat: str, email_user: str, email_pass: str, dry_run: bool):
    print("\n[3/5] Criando Variable Groups...")
    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/distributedtask/variablegroups?api-version={API}-preview.1"

    groups = [
        {
            "name":        "qa-emails",
            "description": "Credenciais Gmail para envio do dashboard QA",
            "type":        "Vsts",
            "variables": {
                "EMAIL_USER": {"value": email_user or "",  "isSecret": False},
                "EMAIL_PASS": {"value": email_pass or "",  "isSecret": True},
            }
        },
        {
            "name":        "qa-boards",
            "description": "PAT para criação automática de bugs no Azure Boards",
            "type":        "Vsts",
            "variables": {
                "AZURE_PAT": {"value": pat, "isSecret": True},
            }
        },
    ]

    for g in groups:
        print(f"\n  → Variable Group: {g['name']}")
        if dry_run:
            print("    [DRY-RUN] Seria criado.")
            continue
        result = _safe(lambda g=g: _post(url, pat, g), f"criar variable group {g['name']}")
        if result:
            print(f"    ✅ Criado: ID #{result.get('id')}")


# ──────────────────────────────────────────────
# STEP 4 — IMPORTAR BUGS NO AZURE BOARDS
# ──────────────────────────────────────────────
def _extrair_campo(conteudo: str, campo: str) -> str:
    m = re.search(rf"\|\s*\*\*{re.escape(campo)}\*\*\s*\|\s*(.+?)\s*\|", conteudo, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _extrair_secao(conteudo: str, titulo: str) -> str:
    m = re.search(rf"##\s+{re.escape(titulo)}\s*\n(.*?)(?=\n##|\Z)", conteudo, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def _md_para_html(texto: str) -> str:
    if not texto:
        return ""
    partes = []
    for linha in texto.split("\n"):
        if linha.startswith("### "):
            partes.append(f"<h3>{linha[4:]}</h3>")
        elif linha.startswith("## "):
            partes.append(f"<h2>{linha[3:]}</h2>")
        elif linha.startswith("- ") or linha.startswith("* "):
            partes.append(f"<li>{linha[2:]}</li>")
        elif linha.strip() == "":
            partes.append("<br>")
        else:
            linha = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", linha)
            linha = re.sub(r"`(.+?)`", r"<code>\1</code>", linha)
            partes.append(f"<p>{linha}</p>")
    return "\n".join(partes)


def _severidade(texto: str) -> str:
    t = texto.lower()
    for k, v in SEVERIDADE_MAP.items():
        if k in t:
            return v
    return "3 - Medium"


def _tags(conteudo: str, bug_id: str) -> str:
    tags = [bug_id, "qa-automation"]
    checks = {
        "playwright": "playwright", "react": "frontend", "dom": "frontend",
        "api": "api", "admin": "admin", "integrador": "integrador",
    }
    for kw, tag in checks.items():
        if kw in conteudo.lower() and tag not in tags:
            tags.append(tag)
    return "; ".join(tags)


def importar_bugs(pat: str, dry_run: bool):
    print("\n[4/5] Importando bugs para Azure Boards...")
    arquivos = sorted(BUGS_DIR.rglob("BUG-*.md"))
    arquivos = [f for f in arquivos if re.match(r"BUG-\d+", f.stem)]
    print(f"  Encontrados: {len(arquivos)} arquivos BUG-*.md")

    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/workitems/$Bug?api-version={API}"
    criados, erros = [], []

    for arq in arquivos:
        try:
            c     = arq.read_text(encoding="utf-8")
            m     = re.match(r"#\s+(BUG-\d+\s+[—–-]+\s+.+)", c)
            titulo = m.group(1).strip() if m else arq.stem

            bug_id  = _extrair_campo(c, "ID")
            sev_raw = _extrair_campo(c, "Severidade")
            tela    = _extrair_campo(c, "Tela")
            data    = _extrair_campo(c, "Data")
            autor   = _extrair_campo(c, "Autor")
            status  = _extrair_campo(c, "Status")

            desc   = _extrair_secao(c, "Descrição")
            repro  = _extrair_secao(c, "Passo a Passo para Reprodução")
            esp    = _extrair_secao(c, "Comportamento Esperado")
            imp    = _extrair_secao(c, "Impacto")
            feat   = _extrair_secao(c, "Feature BDD Relacionada")

            desc_html  = _md_para_html(
                f"**Tela:** {tela}\n**Data:** {data} | **Autor:** {autor}\n**Status:** {status}\n\n"
                + (f"### Descrição\n{desc}\n\n" if desc else "")
                + (f"### Impacto\n{imp}\n\n" if imp else "")
                + (f"### Comportamento Esperado\n{esp}\n\n" if esp else "")
                + (f"### Feature BDD\n{feat}" if feat else "")
            )
            repro_html = _md_para_html(repro) if repro else "<p>Ver arquivo .md para reprodução.</p>"

            print(f"\n  → {titulo[:80]}")
            print(f"    Severidade: {_severidade(sev_raw)}")

            if dry_run:
                print(f"    [DRY-RUN] Seria criado no Boards.")
                criados.append(titulo)
                continue

            payload = [
                {"op": "add", "path": "/fields/System.Title",                    "value": titulo},
                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Severity",  "value": _severidade(sev_raw)},
                {"op": "add", "path": "/fields/Microsoft.VSTS.TCM.ReproSteps",   "value": repro_html},
                {"op": "add", "path": "/fields/System.Description",              "value": desc_html},
                {"op": "add", "path": "/fields/System.Tags",                     "value": _tags(c, bug_id)},
                {"op": "add", "path": "/fields/System.State",                    "value": "New"},
            ]

            result = _safe(
                lambda payload=payload: _post(url, pat, payload, "application/json-patch+json"),
                f"criar work item {arq.stem}"
            )
            if result:
                wi_id  = result.get("id")
                wi_url = result.get("_links", {}).get("html", {}).get("href", "")
                print(f"    ✅ Work Item #{wi_id} → {wi_url}")
                criados.append(titulo)
            else:
                erros.append(arq.stem)

        except Exception as e:
            print(f"    ❌ {arq.stem}: {e}")
            erros.append(arq.stem)

    print(f"\n  Resultado: {len(criados)} criados | {len(erros)} erros")
    if erros:
        print(f"  Falharam: {', '.join(erros)}")


# ──────────────────────────────────────────────
# STEP 5 — BRANCH POLICY (PR Quality Gate)
# ──────────────────────────────────────────────
def configurar_branch_policy(pat: str, pipeline_ids: dict, dry_run: bool):
    print("\n[5/5] Configurando Branch Policy (Quality Gate em PRs)...")

    gate_id = pipeline_ids.get("QA — PR Quality Gate")
    if not gate_id:
        print("    ⚠️  Pipeline 'QA — PR Quality Gate' não encontrado. Pulando branch policy.")
        return

    if dry_run:
        print(f"    [DRY-RUN] Branch policy seria criada para pipeline #{gate_id}.")
        return

    # Primeiro: busca o project ID (necessário para branch policy)
    proj_url = f"https://dev.azure.com/{ORG}/_apis/projects/{PROJECT}?api-version={API}"
    proj     = _safe(lambda: _get(proj_url, pat), "buscar project ID")
    if not proj:
        return
    proj_id = proj.get("id")

    # Busca o repo ID novamente (necessário no scope da policy)
    repos_url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/git/repositories?api-version={API}"
    repos     = _safe(lambda: _get(repos_url, pat), "buscar repos")
    if not repos:
        return
    repo_id = next((r["id"] for r in repos.get("value", []) if r["name"] == REPO_NAME), None)
    if not repo_id:
        repo_id = repos["value"][0]["id"] if repos.get("value") else None

    # Tipo de policy: "Build" = fa73ebe7-1d9c-4da4-93cf-6a48ee23dab6 (fixed GUID no Azure)
    policy_url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/policy/configurations?api-version={API}"
    payload = {
        "isEnabled":  True,
        "isBlocking": True,
        "type": {"id": "fa73ebe7-1d9c-4da4-93cf-6a48ee23dab6"},
        "settings": {
            "buildDefinitionId":       gate_id,
            "queueOnSourceUpdateOnly": True,
            "manualQueueOnly":         False,
            "displayName":             "QA — PR Quality Gate (BDD Linter)",
            "validDuration":           720,
            "scope": [
                {
                    "repositoryId": repo_id,
                    "refName":      "refs/heads/main",
                    "matchKind":    "Exact",
                }
            ]
        }
    }

    result = _safe(lambda: _post(policy_url, pat, payload), "criar branch policy")
    if result:
        print(f"    ✅ Branch Policy criada: ID #{result.get('id')}")
        print(f"    PRs para main agora exigem quality gate passar.")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Setup completo Azure DevOps para QA SolAgora")
    parser.add_argument("--pat",            default="",  help="Azure DevOps Personal Access Token")
    parser.add_argument("--email-user",     default="",  help="Gmail remetente (ex: qa@gmail.com)")
    parser.add_argument("--email-pass",     default="",  help="Senha de app Gmail")
    parser.add_argument("--dry-run",        action="store_true", help="Simula sem criar nada")
    parser.add_argument("--skip-bugs",      action="store_true", help="Pula importação de bugs")
    parser.add_argument("--skip-pipelines", action="store_true", help="Pula registro de pipelines")
    parser.add_argument("--skip-policy",    action="store_true", help="Pula branch policy")
    parser.add_argument("--skip-vargroups", action="store_true", help="Pula criação de variable groups")
    args = parser.parse_args()

    pat = args.pat or os.environ.get("AZURE_PAT", "")
    if not pat and not args.dry_run:
        pat = getpass.getpass("Azure DevOps PAT: ")

    if not pat and not args.dry_run:
        print("❌ PAT obrigatório. Use --pat ou AZURE_PAT=...")
        sys.exit(1)

    email_user = args.email_user or os.environ.get("EMAIL_USER", "")
    email_pass = args.email_pass or os.environ.get("EMAIL_PASS", "")

    print(f"\n{'='*65}")
    print(f"  Azure DevOps Setup — QA SolAgora")
    print(f"  Org: {ORG} | Projeto: {PROJECT} | Repo: {REPO_NAME}")
    print(f"  Modo: {'DRY-RUN' if args.dry_run else 'REAL'}")
    print(f"{'='*65}")

    # 1. Repo ID
    repo_id = get_repo_id(pat, args.dry_run)

    # 2. Pipelines
    pipeline_ids = {}
    if not args.skip_pipelines:
        pipeline_ids = registrar_pipelines(pat, repo_id, args.dry_run)
    else:
        print("\n[2/5] Pipelines: PULADO")

    # 3. Variable Groups
    if not args.skip_vargroups:
        criar_variable_groups(pat, email_user, email_pass, args.dry_run)
    else:
        print("\n[3/5] Variable Groups: PULADO")

    # 4. Importar bugs
    if not args.skip_bugs:
        importar_bugs(pat, args.dry_run)
    else:
        print("\n[4/5] Bugs: PULADO")

    # 5. Branch Policy
    if not args.skip_policy:
        configurar_branch_policy(pat, pipeline_ids, args.dry_run)
    else:
        print("\n[5/5] Branch Policy: PULADO")

    print(f"\n{'='*65}")
    print(f"  Setup concluído!")
    print(f"  Portal: https://dev.azure.com/{ORG}/{PROJECT}")
    print(f"  Boards: https://dev.azure.com/{ORG}/{PROJECT}/_boards")
    print(f"  Pipes:  https://dev.azure.com/{ORG}/{PROJECT}/_build")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
