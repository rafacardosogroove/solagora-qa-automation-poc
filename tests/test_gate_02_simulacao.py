import pytest
import allure
import re
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage
# IMPORTAÇÃO DA NOVA PAGE
from pages.simulacao.resultado_simulacao_page import ResultadoSimulacaoPage

scenarios('../features/simulacao/simulacao.feature')

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page):
    with allure.step("Verificando disponibilidade do ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)

@given(parsers.parse('que executo o fluxo completo de login válido ("{usuario}", "{senha}")'))
def step_macro_login(page, usuario, senha):
    login_page = LoginPage(page)
    login_page.realizar_login_completo_e_aguardar_dashboard(usuario, senha)

@when('acesso a área de criação de um novo projeto')
def step_acessar_nova_simulacao(page):
    simulacao_page = SimulacaoPage(page)
    simulacao_page.acessar_nova_simulacao()

@when(parsers.parse('preencho os dados com CPF "{cpf}", Renda "{renda}", Valor "{valor}", Distribuidor "{distribuidor}", Energia "{energia}" e Vencimento "{dia}"'))
def step_preencher_dados(page, cpf, renda, valor, distribuidor, energia, dia):
    simulacao_page = SimulacaoPage(page)
    simulacao_page.preencher_dados_simulacao(cpf, renda, valor, distribuidor, energia, dia)

@then('o sistema deve avançar para a próxima etapa da simulação')
def step_validar_avanco(page):
    with allure.step("Validar que o sistema processou a simulação com sucesso"):
        erros_visiveis = page.locator("text='Campo obrigatório'").count()
        assert erros_visiveis == 0, "O formulário apresentou erros de validação na tela."

# NOVO PASSO ADICIONADO SEM ALTERAR OS ANTERIORES
@then(parsers.parse('deve exibir a tela de resultados com a mensagem "{mensagem}"'))
def step_validar_resultado_visual(page, mensagem):
    resultado_page = ResultadoSimulacaoPage(page)
    resultado_page.validar_tela_resultados(mensagem)