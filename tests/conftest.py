import pytest
import re
import allure
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers

from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage
from pages.analise_credito.analise_credito_page import AnaliseCreditoPage
from utils.Generators import Generators

# ==============================================================================
# 1. FIXTURES DAS PAGES
# ==============================================================================

@pytest.fixture
def login_page(page: Page):
    return LoginPage(page)

@pytest.fixture
def simulacao_page(page: Page):
    return SimulacaoPage(page)

@pytest.fixture
def analise_page(page: Page):
    return AnaliseCreditoPage(page)

# ==============================================================================
# 2. CONTEXTOS MACRO (GATES 01, 02 E 03)
# ==============================================================================

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page: Page):
    with allure.step("Acessando ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)

@given(parsers.parse('que executo o fluxo completo de login válido ("{usuario}", "{senha}")'))
def step_macro_login(page: Page, usuario, senha):
    with allure.step(f"Macro: Realizando login completo para {usuario}"):
        login_page = LoginPage(page)
        login_page.realizar_login_completo_e_aguardar_dashboard(usuario, senha)

@given(parsers.parse('que realizo uma simulação completa para o distribuidor "{distribuidor}" com vencimento "{dia}"'))
def step_macro_simulacao(page: Page, distribuidor, dia):
    with allure.step(f"Macro: Simulação para distribuidor {distribuidor} e dia {dia}"):
        simulacao = SimulacaoPage(page)
        simulacao.acessar_nova_simulacao()
        # Valores fixos ("8000", "50000", "1000") garantem que o macro passe rápido pelo formulário
        simulacao.preencher_dados_simulacao("GERAR", "8000", "50000", distribuidor, "1000", dia)

@given(parsers.parse('que realizo a análise de crédito completa para o cliente "{nome}" com CEP "{cep}"'))
def step_macro_analise(page: Page, nome, cep):
    with allure.step(f"Macro: Análise de Crédito para {nome} (CEP: {cep})"):
        analise_page = AnaliseCreditoPage(page)
        # O Generators é chamado no momento da execução para garantir e-mail e telefone únicos
        analise_page.realizar_analise_credito_completa(nome, Generators.email(), Generators.telefone(), cep)