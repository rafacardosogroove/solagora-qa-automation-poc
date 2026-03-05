import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from pages.login_page import LoginPage
from pages.simulacao.simulacao_page import SimulacaoPage
from pages.analise_credito.analise_credito_page import AnaliseCreditoPage
from pages.documentacao.modal_conta_energia_page import ModalContaEnergiaPage
from pages.documentacao.documentacao_page import DocumentacaoPage
from utils.Generators import Generators

scenarios('../features/documentacao/04_documentacao.feature')


# --- CONTEXTO (MACROS) ---
@given(parsers.parse('que realizo a análise de crédito completa para o cliente "{nome}" com CEP "{cep}"'))
def step_macro_analise(page, nome, cep):
    analise_page = AnaliseCreditoPage(page)
    # A macro preenche tudo, valida aprovação e clica em 'Continuar para documentação'
    analise_page.realizar_analise_credito_completa(nome, Generators.email(), Generators.telefone(), cep)


# --- QUANDO (MODAL) ---
@when(parsers.parse('realizo o upload da conta de energia "{origem}" com o arquivo "{arquivo}"'))
def step_upload_modal(page, origem, arquivo):
    modal = ModalContaEnergiaPage(page)
    modal.realizar_upload_energia(origem, arquivo)


# --- QUANDO (ENDEREÇO) ---
@when(parsers.parse('preencho o endereço de instalação com Número "{numero}" e Complemento "{complemento}"'))
@when(parsers.parse('defino que o endereço de cobrança "{endereco_igual}" ao de instalação'))
def step_endereco_doc(page, numero=None, complemento=None, endereco_igual=None):
    doc_page = DocumentacaoPage(page)
    if numero:
        doc_page.input_numero.fill(numero)
        doc_page.input_complemento.fill(complemento)
    if endereco_igual:
        if endereco_igual.upper() == "SIM":
            doc_page.toggle_mesmo_endereco.click()


# --- QUANDO (DADOS E CONTATOS) ---
@when(parsers.parse('informo o documento de identidade RG "{rg}"'))
def step_rg_doc(page, rg):
    DocumentacaoPage(page).input_rg.fill(rg)


@when(parsers.parse(
    'preencho os contatos com Email "{email}", Celular "{celular}", Segundo Celular "{celular_2}" e Fixo "{fixo}"'))
def step_contatos_doc(page, email, celular, celular_2, fixo):
    doc_page = DocumentacaoPage(page)

    # Lógica GERAR
    e = Generators.email() if email == "GERAR" else email
    c1 = Generators.telefone() if celular == "GERAR" else celular
    c2 = Generators.telefone() if celular_2 == "GERAR" else celular_2

    doc_page.input_email.fill(e)
    doc_page.input_celular_1.fill(c1)
    doc_page.input_celular_2.fill(c2)
    doc_page.input_fixo.fill(fixo)


# --- ENTÃO ---
@then('o sistema deve habilitar o botão "Enviar documentação"')
def step_validar_final(page):
    DocumentacaoPage(page).validar_botao_ativo()