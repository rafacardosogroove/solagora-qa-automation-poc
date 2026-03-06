import pytest
import re
import allure
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect

# Imports das suas Page Objects
from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage
from pages.analise_credito.analise_credito_page import AnaliseCreditoPage
from pages.documentacao.modal_conta_energia_page import ModalContaEnergiaPage
from pages.documentacao.documentacao_page import DocumentacaoPage
from utils.Generators import Generators

# Carregamento da Feature
scenarios('../features/documentacao/04_documentacao.feature')

# ==============================================================================
# 1. PASSOS DO CONTEXTO
# ==============================================================================

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page):
    with allure.step("Acessando ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)

@given(parsers.parse('que executo o fluxo completo de login válido ("{usuario}", "{senha}")'))
def step_macro_login(page, usuario, senha):
    with allure.step(f"Realizando login com {usuario}"):
        login_page = LoginPage(page)
        login_page.realizar_login_completo_e_aguardar_dashboard(usuario, senha)

@given(parsers.parse('que realizo uma simulação completa para o distribuidor "{distribuidor}" com vencimento "{dia}"'))
def step_macro_simulacao(page, distribuidor, dia):
    with allure.step(f"Executando simulação prévia para {distribuidor}"):
        simulacao = SimulacaoPage(page)
        simulacao.acessar_nova_simulacao()
        simulacao.preencher_dados_simulacao("GERAR", "8000", "50000", distribuidor, "1000", dia)

@given(parsers.parse('que realizo a análise de crédito completa para o cliente "{nome}" com CEP "{cep}"'))
def step_macro_analise(page, nome, cep):
    with allure.step(f"Executando análise de crédito para {nome}"):
        analise_page = AnaliseCreditoPage(page)
        analise_page.realizar_analise_credito_completa(nome, Generators.email(), Generators.telefone(), cep)

# ==============================================================================
# 2. PASSOS DE AÇÃO (QUANDO) - REFATORADOS
# ==============================================================================

@when(parsers.parse('realizo o upload da conta de energia "{origem}" com o arquivo "{arquivo}"'))
def step_upload_modal(page, origem, arquivo):
    # A lógica complexa de upload já está encapsulada na Page do Modal
    modal = ModalContaEnergiaPage(page)
    modal.realizar_upload_energia(origem, arquivo)

@when(parsers.parse('preencho o endereço de instalação com Número "{numero}" e Complemento "{complemento}"'))
def step_endereco_doc(page, numero, complemento):
    # Delega o preenchimento para a Page Object
    doc_page = DocumentacaoPage(page)
    doc_page.preencher_endereco(numero, complemento)

@when(parsers.parse('defino que o endereço de cobrança "{endereco_igual}" ao de instalação'))
def step_endereco_igual(page, endereco_igual):
    # Delega a lógica de clique no toggle para a Page Object
    doc_page = DocumentacaoPage(page)
    doc_page.definir_cobranca_igual(endereco_igual)

@when(parsers.parse('informo o documento de identidade RG "{rg}"'))
def step_rg_doc(page, rg):
    # Delega o preenchimento do RG para a Page Object
    doc_page = DocumentacaoPage(page)
    doc_page.informar_rg(rg)

@when(parsers.parse('preencho os contatos com Email "{email}", Celular "{celular}", Segundo Celular "{celular_2}" e Fixo "{fixo}"'))
def step_contatos_doc(page, email, celular, celular_2, fixo):
    doc_page = DocumentacaoPage(page)

    # A geração de dados dinâmicos (Generators) continua no Step
    e = Generators.email() if email.upper() == "GERAR" else email
    c1 = Generators.telefone() if celular.upper() == "GERAR" else celular
    c2 = Generators.telefone() if celular_2.upper() == "GERAR" else celular_2

    # Envia os dados processados para a Page Object
    doc_page.preencher_contatos(e, c1, c2, fixo)

# ==============================================================================
# 3. VALIDAÇÃO (ENTÃO)
# ==============================================================================

@then('o sistema deve habilitar o botão "Enviar documentação"')
def step_validar_final(page):
    DocumentacaoPage(page).validar_botao_ativo()