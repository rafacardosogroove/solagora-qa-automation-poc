import pytest
import re
import allure
import time
from playwright.sync_api import Page, expect
from pytest_bdd import given, when, then, parsers

# Imports de Utilitários e API
from utils.Generators import Generators
from utils.hml_client import hml
from utils.backend_orchestrator import OrquestradorBackend  # <--- Nosso novo Garçom

# Imports das Page Objects
from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage
from pages.analise_credito.analise_credito_page import AnaliseCreditoPage
from pages.documentacao.documentacao_page import DocumentacaoPage
from pages.documentacao.modal_conta_energia_page import ModalContaEnergiaPage
from pages.admin.admin_page import AdminPage


# ==============================================================================
# 1. FIXTURES DE INFRAESTRUTURA E DADOS
# ==============================================================================

@pytest.fixture(scope="session")
def admin():
    from pathlib import Path
    root_path = Path(__file__).parent.parent
    env_path = root_path / ".env"
    with allure.step(f"Configurando HML Client com .env em: {env_path}"):
        hml.configure(env_file=str(env_path))
    return hml


@pytest.fixture(scope="session")
def orquestrador(admin):
    """Fixture que entrega o orquestrador já instanciado com o hml_client."""
    return OrquestradorBackend(admin)


@pytest.fixture
def context_data():
    """Dicionário persistente para compartilhar dados entre os Gates (ex: CPF, ID)."""
    return {}


# ==============================================================================
# 2. FIXTURES DAS PAGES (PAGE OBJECT MODEL)
# ==============================================================================

@pytest.fixture
def login_page(page: Page) -> LoginPage: return LoginPage(page)


@pytest.fixture
def simulacao_page(page: Page) -> SimulacaoPage: return SimulacaoPage(page)


@pytest.fixture
def analise_page(page: Page) -> AnaliseCreditoPage: return AnaliseCreditoPage(page)


@pytest.fixture
def doc_page(page: Page) -> DocumentacaoPage: return DocumentacaoPage(page)


@pytest.fixture
def modal_energia(page: Page) -> ModalContaEnergiaPage: return ModalContaEnergiaPage(page)


@pytest.fixture
def admin_page(page: Page) -> AdminPage: return AdminPage(page)


# ==============================================================================
# 3. CONTEXTOS MACRO PROGRESSIVOS (O MOTOR DO BDD)
# ==============================================================================

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page: Page):
    with allure.step("Acessando ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)


@given(parsers.parse('que o sistema está autenticado com credenciais válidas ("{usuario}" e "{senha}")'))
def macro_login(login_page: LoginPage, usuario: str, senha: str):
    login_page.realizar_login_completo_e_aguardar_dashboard(usuario, senha)


@given('que possuo uma simulação de financiamento aprovada')
def macro_simulacao_aprovada(page: Page, login_page: LoginPage, simulacao_page: SimulacaoPage, context_data: dict):
    # 1. Herda o Login
    macro_login(login_page, "qaautomacao", "solagora")

    with allure.step("MACRO: Preparar Simulação Aprovada"):
        simulacao_page.acessar_nova_simulacao()
        cpf_gerado = Generators.cpf()
        context_data['cpf_utilizado'] = cpf_gerado  # Fundamental para buscas futuras (ex: Gate 07)
        allure.attach(f"CPF Gerado para o Fluxo: {cpf_gerado}", name="Massa_de_Dados")
        simulacao_page.preencher_dados_simulacao(cpf_gerado, "8000", "50000", "ALDO", "1000", "10")


@given('que o cliente foi aprovado na análise de crédito')
def macro_analise_aprovada(page: Page, login_page: LoginPage, simulacao_page: SimulacaoPage,
                           analise_page: AnaliseCreditoPage, context_data: dict):
    # 2. Herda a Simulação
    macro_simulacao_aprovada(page, login_page, simulacao_page, context_data)

    with allure.step("MACRO: Preparar Análise de Crédito Aprovada"):
        analise_page.realizar_analise_credito_completa("Rafael Automacao", Generators.email(), Generators.telefone(),
                                                       "13282538")


@given('que a documentação do projeto foi enviada com sucesso')
def macro_documentacao_enviada(page: Page, login_page: LoginPage, simulacao_page: SimulacaoPage,
                               analise_page: AnaliseCreditoPage, doc_page: DocumentacaoPage,
                               modal_energia: ModalContaEnergiaPage, context_data: dict):
    # 3. Herda a Análise
    macro_analise_aprovada(page, login_page, simulacao_page, analise_page, context_data)

    with allure.step("MACRO: Preparar Documentação Enviada"):
        modal_energia.realizar_upload_energia("Local", "conta.jpg")
        doc_page.preencher_endereco("123", "Apto Macro")
        doc_page.definir_cobranca_igual("SIM")
        doc_page.informar_rg("223334445")
        doc_page.preencher_contatos(Generators.email(), Generators.telefone(), Generators.telefone(), "1144445555")
        doc_page.obter_botao_enviar().click()
        page.wait_for_timeout(5000)


@given('que o projeto foi aprovado pela mesa interna')
def macro_aprovado_mesa_interna(page: Page, login_page: LoginPage, simulacao_page: SimulacaoPage,
                                analise_page: AnaliseCreditoPage, doc_page: DocumentacaoPage,
                                modal_energia: ModalContaEnergiaPage, orquestrador: OrquestradorBackend,
                                admin_page: AdminPage, context_data: dict):
    # 4. Herda a Documentação
    macro_documentacao_enviada(page, login_page, simulacao_page, analise_page, doc_page, modal_energia, context_data)

    with allure.step("MACRO: Orquestrar Aprovação da Mesa via API"):
        projeto_id = admin_page.capturar_id_projeto_url()
        context_data['projeto_id'] = projeto_id

        # DELEGA TUDO PARA O ORQUESTRADOR!
        orquestrador.orquestrar_gate_05(projeto_id)


@given('que o contrato do projeto foi assinado eletronicamente')
def macro_contrato_assinado(page: Page, login_page: LoginPage, simulacao_page: SimulacaoPage,
                            analise_page: AnaliseCreditoPage, doc_page: DocumentacaoPage,
                            modal_energia: ModalContaEnergiaPage, orquestrador: OrquestradorBackend,
                            admin_page: AdminPage, context_data: dict):
    # 5. Herda a Aprovação da Mesa
    macro_aprovado_mesa_interna(page, login_page, simulacao_page, analise_page, doc_page, modal_energia, orquestrador,
                                admin_page, context_data)

    with allure.step("MACRO: Forçar Assinatura de Contrato"):
        projeto_id = context_data.get('projeto_id')

        # DELEGA TUDO PARA O ORQUESTRADOR!
        orquestrador.orquestrar_gate_06(projeto_id)
        page.reload()
        page.wait_for_load_state("networkidle")


@given('que as notas fiscais do projeto foram enviadas e aprovadas')
def macro_notas_enviadas(page: Page, login_page: LoginPage, simulacao_page: SimulacaoPage,
                         analise_page: AnaliseCreditoPage, doc_page: DocumentacaoPage,
                         modal_energia: ModalContaEnergiaPage, orquestrador: OrquestradorBackend, admin_page: AdminPage,
                         context_data: dict):
    # 6. Herda a Assinatura (Para uso no Gate 08)
    macro_contrato_assinado(page, login_page, simulacao_page, analise_page, doc_page, modal_energia, orquestrador,
                            admin_page, context_data)

    with allure.step("MACRO: Orquestrar Faturamento/Cessão via API"):
        projeto_id = context_data.get('projeto_id')

        # DELEGA TUDO PARA O ORQUESTRADOR!
        orquestrador.orquestrar_gate_07(projeto_id)
        page.reload()
        page.wait_for_load_state("networkidle")


# ==============================================================================
# 4. PASSOS AUXILIARES GLOBAIS REUTILIZADOS PELOS TESTS (WHENS)
# ==============================================================================

@when('capturo o ID do projeto atual pela interface')
def step_capturar_id_global(admin_page: AdminPage, context_data: dict):
    context_data['projeto_id'] = admin_page.capturar_id_projeto_url()


@when('atualizo a página do portal do integrador')
def step_atualizar_pagina_integrador_global(page: Page):
    with allure.step("Atualizando portal"):
        page.reload()
        page.wait_for_load_state("networkidle")


# ==============================================================================
# HOOKS DE INFRAESTRUTURA
# ==============================================================================

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook global que intercepta falhas em QUALQUER step do teste.
    Se houver erro, captura screenshot e detalhes do elemento/URL.
    """
    outcome = yield
    report = outcome.get_result()

    # Só agimos se o teste falhar (durante a execução do step)
    if report.when == "call" and report.failed:
        # Pegamos a fixture 'page' que está sendo usada no teste
        page = item.funcargs.get('page')

        if page:
            try:
                # 1. Captura a URL onde o erro ocorreu
                url_erro = page.url

                # 2. Tira um Screenshot da tela exata do erro
                screenshot = page.screenshot(full_page=True)
                allure.attach(screenshot, name="SITUAÇÃO_NO_ERRO", attachment_type=allure.attachment_type.PNG)

                # 3. Registra os detalhes técnicos no Allure
                erro_original = str(call.excinfo.value)

                detalhes_log = (
                    f"🛑 FALHA DETECTADA\n"
                    f"--------------------------------------------------\n"
                    f"📍 URL DO ERRO: {url_erro}\n"
                    f"📝 STEP: {item.name}\n"
                    f"🔍 MENSAGEM: {erro_original}\n"
                    f"--------------------------------------------------"
                )

                allure.attach(
                    detalhes_log,
                    name="RELATÓRIO_DE_TIMEOUT_OU_FALHA",
                    attachment_type=allure.attachment_type.TEXT
                )

            except Exception as e:
                print(f"Erro ao tentar capturar evidência de falha: {e}")