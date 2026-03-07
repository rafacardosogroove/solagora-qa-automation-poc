import pytest
import re
import allure
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import Page, expect

# Imports apenas das Pages necessárias para tipagem
from pages.documentacao.modal_conta_energia_page import ModalContaEnergiaPage
from pages.documentacao.documentacao_page import DocumentacaoPage
from utils.Generators import Generators

# Carregamento da Feature
scenarios('../features/documentacao/04_documentacao.feature')

# ==============================================================================
# 1. PASSOS DO CONTEXTO
# ==============================================================================
# Dica de Sênior: Como você já tem esse @given no conftest.py, você poderia até
# apagá-lo daqui, mas vou mantê-lo conforme o seu original para não desestruturar.

@given('que o ambiente de homologação está respondendo na página de login')
def step_ambiente_acessivel(page: Page):
    with allure.step("Acessando ambiente de homologação"):
        page.goto("https://integrator.hom.solagora.com.br/")
        expect(page).to_have_url(re.compile(".*auth.*"), timeout=15000)

# ==============================================================================
# 2. PASSOS DE AÇÃO (QUANDO)
# ==============================================================================

@when(parsers.parse('realizo o upload da conta de energia "{origem}" com o arquivo "{arquivo}"'))
def step_upload_modal(modal_energia: ModalContaEnergiaPage, origem: str, arquivo: str):
    # A fixture modal_energia já foi injetada!
    modal_energia.realizar_upload_energia(origem, arquivo)

@when(parsers.parse('preencho o endereço de instalação com Número "{numero}" e Complemento "{complemento}"'))
def step_endereco_doc(doc_page: DocumentacaoPage, numero: str, complemento: str):
    # A fixture doc_page já foi injetada!
    doc_page.preencher_endereco(numero, complemento)

@when(parsers.parse('defino que o endereço de cobrança "{endereco_igual}" ao de instalação'))
def step_endereco_igual(doc_page: DocumentacaoPage, endereco_igual: str):
    doc_page.definir_cobranca_igual(endereco_igual)

@when(parsers.parse('informo o documento de identidade RG "{rg}"'))
def step_rg_doc(doc_page: DocumentacaoPage, rg: str):
    doc_page.informar_rg(rg)

@when(parsers.parse('preencho os contatos com Email "{email}", Celular "{celular}", Segundo Celular "{celular_2}" e Fixo "{fixo}"'))
def step_contatos_doc(doc_page: DocumentacaoPage, email: str, celular: str, celular_2: str, fixo: str):
    with allure.step("Gerar massa de dados dinâmica para contatos se solicitado ('GERAR')"):
        e = Generators.email() if email.upper() == "GERAR" else email
        c1 = Generators.telefone() if celular.upper() == "GERAR" else celular
        c2 = Generators.telefone() if celular_2.upper() == "GERAR" else celular_2

    # Envia os dados processados para a Page Object
    doc_page.preencher_contatos(e, c1, c2, fixo)

# ==============================================================================
# 3. VALIDAÇÃO (ENTÃO)
# ==============================================================================

@then('o sistema deve habilitar o botão "Enviar documentação"')
def step_validar_final(page: Page, doc_page: DocumentacaoPage):
    with allure.step("Validar que o formulário foi preenchido e o botão foi habilitado"):
        # Seguindo nossa Regra de Ouro (POM não faz assert):
        botao_envio = doc_page.obter_botao_enviar()
        expect(botao_envio).to_be_enabled(timeout=10000)

    with allure.step("Capturar evidência de documentação concluída"):
        allure.attach(
            page.screenshot(full_page=True),
            name="Evidencia_Documentacao_Aprovada",
            attachment_type=allure.attachment_type.PNG
        )