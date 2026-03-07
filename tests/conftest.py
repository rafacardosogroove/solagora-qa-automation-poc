import pytest
import re
import allure
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers

from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage
from pages.analise_credito.analise_credito_page import AnaliseCreditoPage
from utils.Generators import Generators

from pages.documentacao.documentacao_page import DocumentacaoPage
from pages.documentacao.modal_conta_energia_page import ModalContaEnergiaPage


# ==============================================================================
# 1. FIXTURES DAS PAGES
# ==============================================================================

@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def simulacao_page(page: Page) -> SimulacaoPage:
    return SimulacaoPage(page)


@pytest.fixture
def analise_page(page: Page) -> AnaliseCreditoPage:
    return AnaliseCreditoPage(page)


@pytest.fixture
def doc_page(page: Page) -> DocumentacaoPage:
    return DocumentacaoPage(page)


@pytest.fixture
def modal_energia(page: Page) -> ModalContaEnergiaPage:
    return ModalContaEnergiaPage(page)


# ==============================================================================
# 2. CONTEXTOS MACRO (GATES 01, 02 E 03)
# ==============================================================================

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page: Page):
    with allure.step("Acessando ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        # Em macros de setup, o expect é tolerável para garantir que o ambiente subiu
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)


# Olha a mágica: Injetamos a `login_page` direto aqui!
@given(parsers.parse('que executo o fluxo completo de login válido ("{usuario}", "{senha}")'))
def step_macro_login(login_page: LoginPage, usuario: str, senha: str):
    with allure.step(f"Macro: Realizando login completo para {usuario}"):
        login_page.realizar_login_completo_e_aguardar_dashboard(usuario, senha)


@given(parsers.parse('que realizo uma simulação completa para o distribuidor "{distribuidor}" com vencimento "{dia}"'))
def step_macro_simulacao(simulacao_page: SimulacaoPage, distribuidor: str, dia: str):
    with allure.step(f"Macro: Simulação para distribuidor {distribuidor} e dia {dia}"):
        simulacao_page.acessar_nova_simulacao()
        simulacao_page.preencher_dados_simulacao("GERAR", "8000", "50000", distribuidor, "1000", dia)


@given(parsers.parse('que realizo a análise de crédito completa para o cliente "{nome}" com CEP "{cep}"'))
def step_macro_analise(analise_page: AnaliseCreditoPage, nome: str, cep: str):
    with allure.step(f"Macro: Análise de Crédito para {nome} (CEP: {cep})"):
        analise_page.realizar_analise_credito_completa(nome, Generators.email(), Generators.telefone(), cep)


# ==============================================================================
# 3. CONTEXTO MACRO (GATE 04)
# ==============================================================================

@given(parsers.parse('que envio a documentação completa com origem "{origem}" e arquivo "{arquivo}"'))
def step_macro_documentacao(page: Page, doc_page: DocumentacaoPage, modal_energia: ModalContaEnergiaPage, origem: str,
                            arquivo: str):
    with allure.step(f"Macro: Envio de Documentação (Origem: {origem} | Arquivo: {arquivo})"):
        # 1. Upload
        modal_energia.realizar_upload_energia(origem, arquivo)

        # 2. Preenchimento de dados genéricos para aprovar e pular a fase
        doc_page.preencher_endereco("123", "Apto Macro")
        doc_page.definir_cobranca_igual("SIM")
        doc_page.informar_rg("223334445")

        e = Generators.email()
        c = Generators.telefone()
        doc_page.preencher_contatos(e, c, c, "1144445555")

        # 3. Valida e envia (Ajustado para o Padrão POM)
        botao_enviar = doc_page.obter_botao_enviar()
        botao_enviar.wait_for(state="visible", timeout=10000)

        # Usamos uma ação encapsulada na Page ao invés de dar .click() direto no elemento
        doc_page.acionar_envio_documentacao()

        # Hardcoded waits são perigosos, mas em macros às vezes nos salvam da lentidão de APIs
        with allure.step("Aguardar processamento sistêmico da documentação"):
            page.wait_for_timeout(5000)