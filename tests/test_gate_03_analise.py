import pytest
import allure
from pytest_bdd import scenarios, given, when, then, parsers
from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage
from pages.simulacao.analise_credito_page import AnaliseCreditoPage

scenarios('../features/proposta/03_analise_credito.feature')

@given('que o ambiente de homologação está respondendo na página de login')
def step_acessar_login(page):
    page.goto("https://integrator.hom.solagora.com.br/")

@given(parsers.parse('que executo o fluxo completo de login válido ("{usuario}", "{senha}")'))
def step_macro_login(page, usuario, senha):
    login_page = LoginPage(page)
    login_page.realizar_login_completo_e_aguardar_dashboard(usuario, senha)

@given(parsers.parse('que realizo uma simulação completa para o distribuidor "{distribuidor}" com vencimento "{dia}"'))
def step_macro_simulacao(page, distribuidor, dia):
    simulacao_page = SimulacaoPage(page)
    simulacao_page.acessar_nova_simulacao()
    # Macro preenchendo o necessário para chegar no resultado
    simulacao_page.preencher_dados_simulacao("GERAR", "8000", "50000", distribuidor, "1000", dia)

@when('decido seguir com a proposta clicando em "Quero criar uma proposta"')
def step_iniciar_proposta(page):
    analise_page = AnaliseCreditoPage(page)
    analise_page.iniciar_proposta()

@when(parsers.parse('seleciono a opção de seguro "{opcao_seguro}" se o modal for exibido'))
def step_tratar_seguro(page, opcao_seguro):
    analise_page = AnaliseCreditoPage(page)
    analise_page.tratar_modal_seguro(opcao_seguro)

@when(parsers.parse('preencho os dados do cliente com Nome "{nome}", Email "{email}", Celular "{celular}" e CEP "{cep}"'))
def step_preencher_cadastro(page, nome, email, celular, cep):
    analise_page = AnaliseCreditoPage(page)
    analise_page.preencher_dados_cadastrais(nome, email, celular, cep)

@then('o sistema deve habilitar o botão "Enviar para análise de crédito"')
def step_validar_botao_ativo(page):
    analise_page = AnaliseCreditoPage(page)
    analise_page.validar_botao_envio()