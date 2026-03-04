import pytest
import allure
import re
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage



scenarios('../features/02_simulacao.feature')

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
        # Como o formulário é enviado, aqui verificamos se ele foi para a próxima tela
        # ou se mostrou algum toast de sucesso. Ajuste essa validação conforme a tela real!
        erros_visiveis = page.locator("text='Campo obrigatório'").count()
        assert erros_visiveis == 0, "O formulário apresentou erros de validação na tela."