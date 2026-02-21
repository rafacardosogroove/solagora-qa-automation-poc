import pytest
import allure
import re
from pytest_bdd import scenario, given, when, then, parsers
from playwright.sync_api import expect

# Importe a sua Page Object (ajuste o caminho 'pages' conforme a sua estrutura)
from pages.login_page import LoginPage


@allure.feature("Pipeline Gates - PR Blockers")
@allure.story("Gate 01 - Autenticação Core")
@scenario('../features/login/01_auth.feature', 'Validar a liberação de acesso ao portal do Integrador')
def test_gate_01_pr_blocker():
    """Teste crítico: Se falhar, o Pull Request será bloqueado."""
    pass


@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page):
    with allure.step("Verificando disponibilidade do ambiente de homologação"):
        # Acessa a raiz que redireciona para o Auth (Keycloak/Kong)
        page.goto("https://integrator.hom.solagora.com.br/")
        # O Juiz exige que a página de login tenha carregado de fato
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)


@when(parsers.parse('o processo de autenticação é submetido com credenciais válidas ("{usuario}" e "{senha}")'))
def step_submeter_credenciais(page, usuario, senha):
    login_page = LoginPage(page)
    with allure.step(f"Injetando credenciais de autorização para: {usuario}"):
        # Usa o seu método limpo da Page Object
        login_page.realizar_login_duplo(usuario, senha)


@then('o sistema deve autorizar o acesso e redirecionar para a dashboard')
def step_validar_autorizacao(page):
    with allure.step("Validando geração do token e redirecionamento seguro"):
        # O Juiz valida se o sistema saiu da tela de auth e voltou pro Integrator
        expect(page).to_have_url(re.compile(".*integrator.hom.solagora.com.br.*"), timeout=20000)


@then('o componente de navegação deve carregar o menu de "Projetos"')
def step_validar_componente(page):
    with allure.step("Validando carregamento do DOM - Menu Projetos"):
        # Mapeia o elemento e exige que ele esteja visível
        menu_projetos = page.get_by_role("link", name="Projetos")
        expect(menu_projetos).to_be_visible(timeout=10000)

        # O "carimbo" final do Juiz provando que o Gate passou para o Allure
        allure.attach(
            page.screenshot(full_page=True),
            name="PR_Liberado_Gate01",
            attachment_type=allure.attachment_type.PNG
        )