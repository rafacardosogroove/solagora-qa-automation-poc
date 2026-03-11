import pytest
import allure
from pytest_bdd import scenarios, when, then, parsers
from playwright.sync_api import Page, expect

# Imports apenas das Pages necessárias para tipagem
from pages.documentacao.modal_conta_energia_page import ModalContaEnergiaPage
from pages.documentacao.documentacao_page import DocumentacaoPage
from utils.Generators import Generators

# ==========================================
# CARREGAMENTO DA FEATURE
# ==========================================
scenarios('../features/documentacao/04_documentacao.feature')

# NOTA: O Contexto (@given 'que o cliente foi aprovado na análise de crédito')
# está centralizado e sendo injetado automaticamente pelo conftest.py!

# ==========================================
# PASSOS DE AÇÃO (QUANDO)
# ==========================================

@when(parsers.parse('realizo o upload da conta de energia "{origem}" com o arquivo "{arquivo}"'))
def step_upload_modal(modal_energia: ModalContaEnergiaPage, origem: str, arquivo: str):
    with allure.step(f"Ação: Upload da conta de energia ({origem})"):
        modal_energia.realizar_upload_energia(origem, arquivo)

@when(parsers.parse('preencho o endereço de instalação com Número "{numero}" e Complemento "{complemento}"'))
def step_endereco_doc(doc_page: DocumentacaoPage, numero: str, complemento: str):
    with allure.step(f"Ação: Preencher endereço de instalação"):
        doc_page.preencher_endereco(numero, complemento)

@when(parsers.parse('defino que o endereço de cobrança "{endereco_igual}" ao de instalação'))
def step_endereco_igual(doc_page: DocumentacaoPage, endereco_igual: str):
    with allure.step(f"Ação: Definir endereço de cobrança (Igual: {endereco_igual})"):
        doc_page.definir_cobranca_igual(endereco_igual)

@when(parsers.parse('informo o documento de identidade RG "{rg}"'))
def step_rg_doc(doc_page: DocumentacaoPage, rg: str):
    with allure.step(f"Ação: Preencher RG ({rg})"):
        doc_page.informar_rg(rg)

@when(parsers.parse('preencho os contatos com Email "{email}", Celular "{celular}", Segundo Celular "{celular_2}" e Fixo "{fixo}"'))
def step_contatos_doc(doc_page: DocumentacaoPage, email: str, celular: str, celular_2: str, fixo: str):
    with allure.step("Gerar massa de dados dinâmica para contatos se solicitado ('GERAR')"):
        e = Generators.email() if email.upper() == "GERAR" else email
        c1 = Generators.telefone() if celular.upper() == "GERAR" else celular
        c2 = Generators.telefone() if celular_2.upper() == "GERAR" else celular_2

    with allure.step("Ação: Preencher formulário de contatos"):
        doc_page.preencher_contatos(e, c1, c2, fixo)

# ==========================================
# PASSOS DE VALIDAÇÃO (ENTÃO)
# ==========================================

@then('o sistema deve habilitar o botão e concluir o envio da documentação')
def step_validar_final(page: Page, doc_page: DocumentacaoPage):
    with allure.step("Validar que o formulário foi preenchido e o botão foi habilitado"):
        # Seguindo nossa Regra de Ouro (POM não faz assert):
        botao_envio = doc_page.obter_botao_enviar()
        expect(botao_envio).to_be_enabled(timeout=10000)

        with allure.step("Ação: Clicar no botão para concluir o envio"):
            doc_page.acionar_envio_documentacao()

    with allure.step("Capturar evidência de documentação concluída"):
        allure.attach(
            page.screenshot(full_page=True),
            name="Evidencia_Documentacao_Aprovada",
            attachment_type=allure.attachment_type.PNG
        )