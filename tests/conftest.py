import pytest
import re
import sys
import platform
import allure
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, expect
from pytest_bdd import given, when, then, parsers

# ==============================================================================
# BROWSER — janela maximizada para todos os gates
# ==============================================================================

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "args": ["--start-maximized"],
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }

# Imports de Utilitários e API
from utils.Generators import Generators
from utils.hml_client import hml
from utils.backend_orchestrator import OrquestradorBackend

# Imports das Page Objects
from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage
from pages.analise_credito.analise_credito_page import AnaliseCreditoPage
from pages.documentacao.documentacao_page import DocumentacaoPage
from pages.documentacao.modal_conta_energia_page import ModalContaEnergiaPage
from pages.admin.admin_page import AdminPage


# ==============================================================================
# CREDENCIAIS — altere aqui se precisar trocar o usuário de teste
# ==============================================================================

USUARIO_PADRAO = "qaautomacao"
SENHA_PADRAO   = "solagora"


# ==============================================================================
# 1. FIXTURES DE INFRAESTRUTURA E DADOS
# ==============================================================================

@pytest.fixture(scope="session")
def admin():
    root_path = Path(__file__).parent.parent
    env_path  = root_path / ".env"
    with allure.step(f"Configurando HML Client com .env em: {env_path}"):
        hml.configure(env_file=str(env_path))
    return hml


@pytest.fixture(scope="session")
def orquestrador(admin):
    return OrquestradorBackend(admin)


@pytest.fixture
def context_data():
    """Dicionário persistente para compartilhar dados entre steps do mesmo teste (CPF, ID, etc.)."""
    return {}


# ==============================================================================
# 2. FIXTURES DAS PAGES (PAGE OBJECT MODEL)
#    Mantidas individualmente — os arquivos de teste as usam diretamente.
# ==============================================================================

@pytest.fixture
def login_page(page: Page)      -> LoginPage:             return LoginPage(page)

@pytest.fixture
def simulacao_page(page: Page)  -> SimulacaoPage:         return SimulacaoPage(page)

@pytest.fixture
def analise_page(page: Page)    -> AnaliseCreditoPage:    return AnaliseCreditoPage(page)

@pytest.fixture
def doc_page(page: Page)        -> DocumentacaoPage:      return DocumentacaoPage(page)

@pytest.fixture
def modal_energia(page: Page)   -> ModalContaEnergiaPage: return ModalContaEnergiaPage(page)

@pytest.fixture
def admin_page(page: Page)      -> AdminPage:             return AdminPage(page)


# ==============================================================================
# 3. GATE CONTEXT — mochila única passada pela cadeia de macros
#
#    ctx.page          → Playwright Page
#    ctx.login_page    → LoginPage
#    ctx.simulacao_page → SimulacaoPage
#    ctx.analise_page  → AnaliseCreditoPage
#    ctx.doc_page      → DocumentacaoPage
#    ctx.modal_energia → ModalContaEnergiaPage
#    ctx.admin_page    → AdminPage
#    ctx.orquestrador  → OrquestradorBackend
#    ctx.data          → dict compartilhado (mesmo objeto que context_data)
#
# ==============================================================================

@dataclass
class GateContext:
    page:           Page
    login_page:     LoginPage
    simulacao_page: SimulacaoPage
    analise_page:   AnaliseCreditoPage
    doc_page:       DocumentacaoPage
    modal_energia:  ModalContaEnergiaPage
    admin_page:     AdminPage
    orquestrador:   OrquestradorBackend
    data:           dict = field(default_factory=dict)


@pytest.fixture
def ctx(page, login_page, simulacao_page, analise_page,
        doc_page, modal_energia, admin_page, orquestrador, context_data) -> GateContext:
    """
    Fixture central: monta o GateContext com todas as dependências.
    ctx.data aponta para o mesmo dict que context_data — alterações em um
    são visíveis no outro, então os arquivos de teste continuam funcionando.
    """
    return GateContext(
        page=page,
        login_page=login_page,
        simulacao_page=simulacao_page,
        analise_page=analise_page,
        doc_page=doc_page,
        modal_energia=modal_energia,
        admin_page=admin_page,
        orquestrador=orquestrador,
        data=context_data,
    )


# ==============================================================================
# 4. CADEIA DE MACROS PRIVADAS
#
#    Cada função _macro_gateXX recebe APENAS ctx: GateContext.
#    Cada função chama a anterior — cadeia automática e sem parâmetros extras.
#
#    Para adicionar Gate 09:
#      1. Crie _macro_gate09(ctx) chamando _macro_gate08(ctx) dentro
#      2. Adicione o @given correspondente abaixo
#      Pronto. Zero mudanças no resto do arquivo.
#
#    CADEIA:
#      _macro_gate01  ← Gate 01 (Login)
#        └── _macro_gate02  ← Gate 02 (Simulação)
#              └── _macro_gate03  ← Gate 03 (Análise de Crédito)
#                    └── _macro_gate04  ← Gate 04 (Documentação)
#                          └── _macro_gate05  ← Gate 05 (Mesa Interna — API)
#                                └── _macro_gate06  ← Gate 06 (Assinatura — API)
#                                      └── _macro_gate07  ← Gate 07 (Notas Fiscais — API)
#                                            └── _macro_gate08  ← Gate 08 (Equipamentos — API)
#
# ==============================================================================

def _macro_gate01(ctx: GateContext):
    """Gate 01 — Login."""
    ctx.login_page.realizar_login_completo_e_aguardar_dashboard(USUARIO_PADRAO, SENHA_PADRAO)


def _macro_gate02(ctx: GateContext):
    """Gate 02 — Simulação de Financiamento. Herda Gate 01."""
    _macro_gate01(ctx)
    with allure.step("MACRO Gate 02: Preparar Simulação Aprovada"):
        ctx.simulacao_page.acessar_nova_simulacao()
        cpf_gerado = Generators.cpf()
        ctx.data['cpf_utilizado'] = cpf_gerado
        allure.attach(f"CPF Gerado para o Fluxo: {cpf_gerado}", name="Massa_de_Dados")
        ctx.simulacao_page.preencher_dados_simulacao(cpf_gerado, "8000", "50000", "ALDO", "1000", "28")


def _macro_gate03(ctx: GateContext):
    """Gate 03 — Análise de Crédito. Herda Gates 01-02."""
    _macro_gate02(ctx)
    with allure.step("MACRO Gate 03: Preparar Análise de Crédito Aprovada"):
        ctx.analise_page.realizar_analise_credito_completa(
            "Rafael Automacao", Generators.email(), Generators.telefone(), "13282538"
        )


def _macro_gate04(ctx: GateContext):
    """Gate 04 — Documentação. Herda Gates 01-03."""
    _macro_gate03(ctx)
    with allure.step("MACRO Gate 04: Preparar Documentação Enviada"):
        ctx.modal_energia.realizar_upload_energia("Local", "conta.jpg")
        ctx.doc_page.preencher_endereco("123", "Apto Macro")
        ctx.doc_page.definir_cobranca_igual("SIM")
        ctx.doc_page.informar_rg("223334445")
        ctx.doc_page.preencher_contatos(
            Generators.email(), Generators.telefone(), Generators.telefone(), "1144445555"
        )
        ctx.doc_page.obter_botao_enviar().click()
        ctx.page.wait_for_timeout(5000)


def _macro_gate05(ctx: GateContext):
    """Gate 05 — Aprovação Mesa Interna via API. Herda Gates 01-04."""
    _macro_gate04(ctx)
    with allure.step("MACRO Gate 05: Orquestrar Aprovação da Mesa via API"):
        projeto_id = ctx.admin_page.capturar_id_projeto_url()
        ctx.data['projeto_id'] = projeto_id
        ctx.orquestrador.orquestrar_gate_05(projeto_id)


def _macro_gate06(ctx: GateContext):
    """Gate 06 — Assinatura Eletrônica via API. Herda Gates 01-05."""
    _macro_gate05(ctx)
    with allure.step("MACRO Gate 06: Forçar Assinatura de Contrato"):
        ctx.orquestrador.orquestrar_gate_06(ctx.data.get('projeto_id'))
        ctx.page.reload()
        ctx.page.wait_for_load_state("networkidle")


def _macro_gate07(ctx: GateContext):
    """Gate 07 — Notas Fiscais via API. Herda Gates 01-06."""
    _macro_gate06(ctx)
    with allure.step("MACRO Gate 07: Orquestrar Faturamento/Cessão via API"):
        ctx.orquestrador.orquestrar_gate_07(ctx.data.get('projeto_id'))
        ctx.page.reload()
        ctx.page.wait_for_load_state("networkidle")


def _macro_gate08(ctx: GateContext):
    """Gate 08 — Equipamentos e Monitoração via API. Herda Gates 01-07."""
    _macro_gate07(ctx)
    with allure.step("MACRO Gate 08: Orquestrar Equipamentos e Monitoração via API"):
        ctx.orquestrador.orquestrar_gate_08(ctx.data.get('projeto_id'))
        ctx.page.reload()
        ctx.page.wait_for_load_state("networkidle")


# ==============================================================================
# 5. PASSOS @given — wrappers finos que ativam a cadeia correta
#
#    O texto da .feature mapeia para o gate de entrada.
#    O framework executa tudo até aquele gate automaticamente.
# ==============================================================================

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page: Page):
    with allure.step("Acessando ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)


@given(parsers.parse('que o sistema está autenticado com credenciais válidas ("{usuario}" e "{senha}")'))
def step_login_explicito(ctx: GateContext, usuario: str, senha: str):
    """Usado em cenários de Gate 01 que especificam credenciais na feature."""
    ctx.login_page.realizar_login_completo_e_aguardar_dashboard(usuario, senha)


@given('que possuo uma simulação de financiamento aprovada')
def step_dado_gate02(ctx: GateContext):
    _macro_gate02(ctx)


@given('que o cliente foi aprovado na análise de crédito')
def step_dado_gate03(ctx: GateContext):
    _macro_gate03(ctx)


@given('que a documentação do projeto foi enviada com sucesso')
def step_dado_gate04(ctx: GateContext):
    _macro_gate04(ctx)


@given('que o projeto foi aprovado pela mesa interna')
def step_dado_gate05(ctx: GateContext):
    _macro_gate05(ctx)


@given('que o contrato do projeto foi assinado eletronicamente')
def step_dado_gate06(ctx: GateContext):
    _macro_gate06(ctx)


@given('que as notas fiscais do projeto foram enviadas e aprovadas')
def step_dado_gate07(ctx: GateContext):
    _macro_gate07(ctx)


@given('que os equipamentos foram entregues e o projeto está em monitoração')
def step_dado_gate08(ctx: GateContext):
    _macro_gate08(ctx)


# ==============================================================================
# 6. PASSOS @when GLOBAIS — reutilizados por múltiplos gates
# ==============================================================================

@when('capturo o ID do projeto atual pela interface')
def step_capturar_id_global(ctx: GateContext):
    ctx.data['projeto_id'] = ctx.admin_page.capturar_id_projeto_url()


@when('atualizo a página do portal do integrador')
def step_atualizar_pagina_integrador_global(page: Page):
    with allure.step("Atualizando portal"):
        page.reload()
        page.wait_for_load_state("networkidle")


# ==============================================================================
# HOOKS DE INFRAESTRUTURA — captura de evidência em falhas
# ==============================================================================

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Intercepta falhas e captura screenshot + detalhes no Allure."""
    outcome = yield
    report  = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get('page')
        if page:
            try:
                url_erro       = page.url
                screenshot     = page.screenshot(full_page=True)
                erro_original  = str(call.excinfo.value)

                allure.attach(screenshot, name="SITUAÇÃO_NO_ERRO",
                              attachment_type=allure.attachment_type.PNG)

                allure.attach(
                    (
                        f"🛑 FALHA DETECTADA\n"
                        f"--------------------------------------------------\n"
                        f"📍 URL DO ERRO: {url_erro}\n"
                        f"📝 STEP: {item.name}\n"
                        f"🔍 MENSAGEM: {erro_original}\n"
                        f"--------------------------------------------------"
                    ),
                    name="RELATÓRIO_DE_TIMEOUT_OU_FALHA",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as e:
                print(f"Erro ao capturar evidência de falha: {e}")


# ==============================================================================
# ALLURE — Informações de ambiente
# ==============================================================================

@pytest.fixture(scope="session", autouse=True)
def configure_allure_environment():
    """Escreve environment.properties em allure-results antes de qualquer teste."""
    props_path = Path(__file__).parent.parent / "allure-results" / "environment.properties"
    props_path.parent.mkdir(exist_ok=True)
    props_path.write_text(
        f"Browser=Chromium\n"
        f"Environment=Homologacao\n"
        f"Base.URL=https://integrator.hom.solagora.com.br\n"
        f"Admin.URL=https://admin.hom.solagora.com.br\n"
        f"Python={sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n"
        f"OS={platform.system()} {platform.release()}\n"
        f"Viewport=1920x1080\n"
        f"Execution.Start={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        encoding="utf-8"
    )
