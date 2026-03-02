import pytest
import allure
import re
from pytest_bdd import scenarios, scenario, given, when, then, parsers
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage  # <--- Adicione esta linha

# Isso faz o Pytest-BDD ler TODOS os cenários do arquivo .feature automaticamente
scenarios('../features/login/01_auth.feature')


# ==========================================
# PASSOS ORIGINAIS (GATE 01 - SUCESSO)
# ==========================================

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page):
    with allure.step("Verificando disponibilidade do ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)


@when(parsers.parse('o processo de autenticação é submetido com credenciais válidas ("{usuario}" e "{senha}")'))
def step_submeter_credenciais_validas(page, usuario, senha):
    login_page = LoginPage(page)
    with allure.step(f"Injetando credenciais de autorização para: {usuario}"):
        login_page.realizar_login_duplo(usuario, senha)


@then('o sistema deve autorizar o acesso e redirecionar para a dashboard')
def step_validar_autorizacao(page):
    with allure.step("Validando geração do token e redirecionamento seguro"):
        expect(page).to_have_url(re.compile(".*integrator.hom.solagora.com.br.*"), timeout=20000)


@then('o componente de navegação deve carregar o menu de "Projetos"')
def step_validar_componente(page):
    with allure.step("Validando carregamento do DOM - Menu Projetos"):
        menu_projetos = page.get_by_role("link", name="Projetos")
        expect(menu_projetos).to_be_visible(timeout=10000)

        allure.attach(
            page.screenshot(full_page=True),
            name="PR_Liberado_Gate01",
            attachment_type=allure.attachment_type.PNG
        )


# ==========================================
# NOVOS PASSOS: ITENS 2, 3, 4, 5 e 6 DO ROADMAP
# ==========================================

@when(parsers.parse('o processo de autenticação é submetido com usuario "{usuario}" e senha "{senha}"'))
def step_submeter_credenciais_invalidas(page, usuario, senha):
    login_page = LoginPage(page)
    with allure.step(f"Tentativa de login com dados incorretos: {usuario}"):
        login_page.realizar_login_duplo(usuario, senha)


@then('o sistema deve manter o usuário na tela de login')
def step_manter_na_tela_login(page):
    with allure.step("Validando que o usuário não foi redirecionado"):
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=10000)


@then(parsers.parse('exibir a mensagem de erro "{mensagem_erro}"'))
def step_validar_mensagem_erro(page, mensagem_erro):
    login_page = LoginPage(page)
    with allure.step(f"Validando mensagem de erro: {mensagem_erro}"):
        # Chamamos o método seguro que criamos lá na LoginPage
        login_page.validar_mensagem_erro(mensagem_erro)

@given(parsers.parse('que o sistema está autenticado com credenciais válidas ("{usuario}" e "{senha}")'))
def step_dado_usuario_autenticado(page, usuario, senha):
    # Reaproveita os passos que já criamos para logar rapidamente!
    step_ambiente_acessivel(page)
    step_submeter_credenciais_validas(page, usuario, senha)
    step_validar_autorizacao(page)


@when('aciono a opção de sair do sistema')
def step_acionar_logout(page):
    dashboard_page = DashboardPage(page)
    with allure.step("Clicando no botão de Logout através da Dashboard"):
        dashboard_page.realizar_logout()


@then('o sistema deve encerrar a sessão e redirecionar para a tela de login')
def step_validar_logout(page):
    with allure.step("Validando retorno para a tela de autenticação"):
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=10000)


@when('o token de sessão do navegador expira')
def step_simular_sessao_expirada(page):
    with allure.step("Simulando queda de token limpando os cookies do navegador"):
        # Truque de mestre do Playwright: limpa os cookies para matar a sessão na hora
        page.context.clear_cookies()


@when('e tento acessar a página interna de "Projetos"')
def step_tentar_acessar_projetos(page):
    with allure.step("Forçando recarregamento da página para validar a proteção de rota"):
        page.reload()


@when('tento acessar a URL restrita de administração diretamente')
def step_tentar_acessar_admin(page):
    with allure.step("Tentando acessar rota do admin pelo navegador (Força Bruta)"):
        page.goto("https://integrator.hom.solagora.com.br/admin")


@then('o sistema deve bloquear o acesso e exibir mensagem de permissão negada')
def step_validar_permissao_negada(page):
    with allure.step("Validando bloqueio de acesso 403 / Permissão Negada"):
        # Pode ser que redirecione ou mostre uma tela de erro, ajuste conforme a tela real
        msg_bloqueio = page.get_by_text(re.compile("acesso negado|sem permissão", re.IGNORECASE))
        expect(msg_bloqueio).to_be_visible(timeout=5000)