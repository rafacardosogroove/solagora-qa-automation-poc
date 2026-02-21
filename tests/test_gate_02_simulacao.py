import pytest
import allure
import re
from pytest_bdd import scenario, given, when, then, parsers
from playwright.sync_api import expect

# Importações das suas Pages e Utilitários
from pages.login_page import LoginPage
from pages.simulador_page import SimuladorPage
from utils.Generators import Generators


@allure.feature("Pipeline Gates - PR Blockers")
@allure.story("Gate 02 - Motor de Simulação")
@scenario('../features/simulacao/02_simulacao.feature', 'Validar a geração de condições de financiamento com sucesso')
def test_gate_02_simulacao():
    """Teste crítico: Valida se o motor de cálculo da Aldo está operante."""
    pass


@given('que o sistema está autenticado e na tela de novo projeto')
def step_preparar_ambiente(page):
    # Instancia as páginas
    login_page = LoginPage(page)
    simulador_page = SimuladorPage(page)

    with allure.step("Fast-Track: Autenticação e Navegação"):
        # 1. Acesso e Login rápido
        page.goto("https://integrator.hom.solagora.com.br/")
        login_page.realizar_login_duplo("qaautomacao", "solagora")
        expect(page).to_have_url(re.compile(".*integrator.hom.solagora.com.br.*"), timeout=20000)

        # 2. Navega para Novo Projeto
        simulador_page.link_projetos.click()
        simulador_page.btn_novo_projeto.click()

        # O Juiz lida com o Tour se ele aparecer
        if simulador_page.btn_fechar_tour.is_visible():
            simulador_page.btn_fechar_tour.click()

        # Garante que chegou na tela certa
        expect(simulador_page.input_cpf).to_be_visible(timeout=10000)


@when(parsers.parse('os dados técnicos são preenchidos com distribuidor "{distribuidor}" e vencimento "{vencimento}"'))
def step_preencher_dados_tecnicos(page, distribuidor, vencimento):
    simulador_page = SimuladorPage(page)

    # Gera um CPF dinâmico válido usando o seu arquivo Generators.py!
    cpf_dinamico = Generators.cpf()

    with allure.step(f"Preenchendo CPF Dinâmico: {cpf_dinamico}"):
        simulador_page.input_cpf.fill(cpf_dinamico)
        # Clica fora ou dá Tab para o sistema validar o CPF (padrão em formulários)
        page.keyboard.press("Tab")

    with allure.step(f"Selecionando distribuidor: {distribuidor}"):
        # Abre o combo de distribuidor
        page.locator("span").filter(has_text=re.compile(r"^Selecione$")).click()
        page.get_by_text(distribuidor).click()

    with allure.step("Preenchendo valores de energia e entrada (Mock)"):
        # Clica nos campos para ativar as máscaras (como estava na sua gravação)
        simulador_page.input_energia.click()
        simulador_page.input_energia.fill("500")  # Exemplo de R$ 500,00 de energia

    with allure.step(f"Selecionando o dia de vencimento: {vencimento}"):
        simulador_page.input_vencimento.click()
        page.get_by_text(vencimento, exact=True).first.click()


@then('o motor de cálculo deve processar a simulação')
def step_processar_simulacao(page):
    simulador_page = SimuladorPage(page)
    with allure.step("Iniciando o motor de cálculo da Aldo"):
        simulador_page.btn_iniciar.click()
        # O Juiz garante que saiu da tela de formulário e foi para a de simulação
        expect(page).to_have_url(re.compile(".*simulation/new.*"), timeout=20000)


@then('o sistema deve apresentar as condições de financiamento com sucesso')
def step_validar_condicoes(page):
    with allure.step("O Juiz valida se a simulação retornou opções de parcelamento"):
        # Validação principal: A mensagem de boas notícias deve aparecer!
        msg_sucesso = page.locator("div").filter(has_text="Boas notícias! As condições")
        expect(msg_sucesso.first).to_be_visible(timeout=30000)  # Timeout maior pois o cálculo pode demorar

        # Evidência de Sucesso para o Allure
        allure.attach(
            page.screenshot(full_page=True),
            name="PR_Liberado_Gate02_Simulacao",
            attachment_type=allure.attachment_type.PNG
        )