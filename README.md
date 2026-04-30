# SolAgora QA Automation — E2E Tests

Framework de automação E2E para o portal do integrador SolAgora.
Cobre o fluxo completo de uma proposta do Gate 01 (login) ao Gate 08 (equipamentos).

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Como rodar os testes](#como-rodar-os-testes)
3. [Entendendo a estrutura do projeto](#entendendo-a-estrutura-do-projeto)
4. [Cadeia de Gates (herança de contexto)](#cadeia-de-gates)
5. [Como criar um novo Gate](#como-criar-um-novo-gate)

---

## Pré-requisitos

Antes de rodar qualquer teste, garanta que:

- **VPN está conectada** — obrigatório para acessar o ambiente HML
- Python 3.12+ instalado
- Dependências instaladas:

```bash
pip install -r requirements.txt
playwright install chromium
```

- Arquivo `.env` na raiz do projeto (peça ao tech lead — nunca commite este arquivo)

---

## Como rodar os testes

### Rodar um gate específico

```bash
# Gate 01 — Login
pytest tests/test_gate_01_auth.py -v

# Gate 03 — Análise de Crédito
pytest tests/test_gate_03_analise.py -v

# Gate 08 — Equipamentos (roda TODA a cadeia do zero)
pytest tests/test_gate_08_equipamentos.py -v
```

### Rodar por marcação

```bash
# Só testes rápidos (smoke)
pytest -m smoke -v

# Suite completa de regressão
pytest -m regression -v
```

### Ver relatório Allure após execução

```bash
allure serve allure-results
```

> **Dica:** Se o teste falhar, o Allure já captura screenshot automático da tela no momento do erro. Procure o anexo `SITUAÇÃO_NO_ERRO` no relatório.

---

## Entendendo a estrutura do projeto

```
solagora-qa-automation-poc/
│
├── features/           # Cenários de teste em linguagem natural (Gherkin)
│   ├── login/
│   ├── simulacao/
│   ├── analise_credito/
│   ├── documentacao/
│   └── admin/          # Gates 05 a 08
│
├── pages/              # Page Objects — locators e ações de cada tela
│   ├── login_page.py
│   ├── simulacao/
│   ├── analise_credito/
│   ├── documentacao/
│   └── admin/
│
├── tests/              # Arquivos de teste (um por Gate)
│   ├── conftest.py     # ⭐ Motor central — macros e fixtures compartilhadas
│   ├── test_gate_01_auth.py
│   ├── test_gate_02_simulacao.py
│   └── ...
│
├── utils/
│   ├── hml_client.py           # Cliente HTTP + DB para o ambiente HML
│   ├── backend_orchestrator.py # Orquestra aprovações via API (sem UI)
│   └── Generators.py           # Geração de CPF, email, telefone aleatórios
│
└── data/               # Arquivos usados nos uploads (ex: conta.jpg)
```

---

## Cadeia de Gates

Cada Gate herda automaticamente todos os anteriores via `conftest.py`.
Você **não precisa** preparar o ambiente manualmente — basta declarar o `Dado` correto na feature.

```
Gate 01 — Login
  └── Gate 02 — Simulação de Financiamento
        └── Gate 03 — Análise de Crédito
              └── Gate 04 — Documentação
                    └── Gate 05 — Aprovação Mesa Interna (via API)
                          └── Gate 06 — Assinatura Eletrônica (via API)
                                └── Gate 07 — Notas Fiscais (via API)
                                      └── Gate 08 — Equipamentos e Monitoração (via API)
```

### Como funciona na prática

No arquivo `.feature`, você declara apenas o ponto de partida:

```gherkin
# Para testar Gate 06, basta declarar:
Dado que o projeto foi aprovado pela mesa interna
# O framework já executa Gates 01 a 05 automaticamente por baixo
```

---

## Como criar um novo Gate

Siga estes 3 passos:

### 1. Crie o arquivo de feature

```
features/admin/gate_09_meu_gate.feature
```

```gherkin
# language: pt
@meu_gate
Funcionalidade: Gate 09 - Descrição do que este gate valida

  Contexto: Estado inicial necessário
    Dado que as notas fiscais do projeto foram enviadas e aprovadas  ← herda tudo até Gate 07

  @gate09
  Cenário: Descrição do cenário
    Quando faço alguma ação
    Então o sistema deve exibir o resultado esperado
```

### 2. Crie o arquivo de teste

```
tests/test_gate_09_meu_gate.py
```

```python
from pytest_bdd import scenarios, when, then
from playwright.sync_api import Page, expect

scenarios('../features/admin/gate_09_meu_gate.feature')

@when('faço alguma ação')
def step_minha_acao(page: Page):
    # seu código aqui
    pass

@then('o sistema deve exibir o resultado esperado')
def step_validacao(page: Page):
    # seu assert aqui
    pass
```

### 3. Registre a marca no `pytest.ini`

Abra `pytest.ini` e adicione na seção `markers`:

```ini
gate09: gate 9 - descrição
```

> **Regra de ouro:** Nunca coloque seletores (locators) dentro dos arquivos de teste.
> Seletores ficam **sempre** no Page Object (`pages/`).
> Testes só chamam métodos do Page Object.

---

## Dúvidas frequentes

**Q: O teste falhou com `403` ou `RuntimeError: Keycloak`**
A: VPN desconectou. Reconecte e rode novamente.

**Q: O teste demorou muito e deu timeout na análise de crédito**
A: Ambiente HML pode estar lento. Tente novamente em alguns minutos.

**Q: Como saber qual CPF foi usado no teste?**
A: Abra o Allure Report e procure o anexo `Massa_de_Dados` no step da simulação.

**Q: Posso commitar o arquivo `.env`?**
A: **Nunca.** Ele contém credenciais. Está no `.gitignore`.
