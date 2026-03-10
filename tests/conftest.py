import pytest
import re
import allure
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers

# Imports de Utilitários e API
from utils.Generators import Generators
from utils.hml_client import hml

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
    """Fixture que injeta o hml_client apontando para o .env na RAIZ do projeto."""
    from pathlib import Path

    # Se o conftest.py está em /tests, subimos um nível para chegar na raiz
    # onde o print mostra que o .env está localizado.
    root_path = Path(__file__).parent.parent
    env_path = root_path / ".env"

    with allure.step(f"Configurando HML Client com .env em: {env_path}"):
        # Configura o hml_client com o caminho real detectado
        hml.configure(env_file=str(env_path))

    return hml


@pytest.fixture
def context_data():
    """Dicionário para compartilhar dados (como o ID do Projeto) entre steps."""
    return {}


# ==============================================================================
# 2. FIXTURES DAS PAGES (PAGE OBJECT MODEL)
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


@pytest.fixture
def admin_page(page: Page) -> AdminPage:
    """Fixture para orquestração e aprovações administrativas."""
    return AdminPage(page)


# ==============================================================================
# 3. CONTEXTOS MACRO (GATES 01, 02 E 03)
# ==============================================================================

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page: Page):
    with allure.step("Acessando ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)


@given(parsers.parse('que executo o fluxo completo de login válido ("{usuario}", "{senha}")'))
def step_macro_login(login_page: LoginPage, usuario: str, senha: str):
    with allure.step(f"Macro: Realizando login completo para {usuario}"):
        login_page.realizar_login_completo_e_aguardar_dashboard(usuario, senha)


@given(parsers.parse('que realizo uma simulação completa para o distribuidor "{distribuidor}" com vencimento "{dia}"'))
def step_macro_simulacao(simulacao_page: SimulacaoPage, distribuidor: str, dia: str):
    with allure.step(f"Macro: Simulação para distribuidor {distribuidor} e dia {dia}"):
        simulacao_page.acessar_nova_simulacao()
        # INTEGRAÇÃO: CPF dinâmico para evitar bloqueio por duplicidade
        simulacao_page.preencher_dados_simulacao("GERAR", "8000", "50000", distribuidor, "1000", dia)


@given(parsers.parse('que realizo a análise de crédito completa para o cliente "{nome}" com CEP "{cep}"'))
def step_macro_analise(analise_page: AnaliseCreditoPage, nome: str, cep: str):
    with allure.step(f"Macro: Análise de Crédito para {nome} (CEP: {cep})"):
        # Generators garantindo e-mail e telefone únicos para cada teste
        analise_page.realizar_analise_credito_completa(nome, Generators.email(), Generators.telefone(), cep)


# ==============================================================================
# 4. CONTEXTO MACRO (GATE 04 - DOCUMENTAÇÃO)
# ==============================================================================

@given(parsers.parse('que envio a documentação completa com origem "{origem}" e arquivo "{arquivo}"'))
def step_macro_documentacao(page: Page, doc_page: DocumentacaoPage, modal_energia: ModalContaEnergiaPage, origem: str,
                            arquivo: str):
    with allure.step(f"Macro: Envio de Documentação (Origem: {origem} | Arquivo: {arquivo})"):
        modal_energia.realizar_upload_energia(origem, arquivo)
        doc_page.preencher_endereco("123", "Apto Macro")
        doc_page.definir_cobranca_igual("SIM")
        doc_page.informar_rg("223334445")
        doc_page.preencher_contatos(Generators.email(), Generators.telefone(), Generators.telefone(), "1144445555")

        # Validação de botão habilitado antes do clique para evitar flaky tests
        botao = doc_page.obter_botao_enviar()
        botao.wait_for(state="visible", timeout=10000)
        doc_page.acionar_envio_documentacao()

        # Pausa estratégica para o backend processar a criação definitiva do ID de projeto
        page.wait_for_timeout(5000)