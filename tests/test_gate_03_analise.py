import pytest
import allure
import re
from pytest_bdd import scenarios, when, then, parsers
from playwright.sync_api import Page, expect

from pages.analise_credito.analise_credito_page import AnaliseCreditoPage
from utils.Generators import Generators

scenarios('../features/analise_credito/03_analise_credito.feature')

# --- PASSOS DE EXECUÇÃO ---

@when('aceito os termos de uso e privacidade para habilitar a proposta')
def step_aceitar_termos(analise_page: AnaliseCreditoPage):
    with allure.step("Ação: Marcar o checkbox de consentimento"):
        # Agora delegamos a ação inteira para a Page Object
        analise_page.aceitar_termos()

@when('decido seguir com a proposta clicando em "Quero criar uma proposta"')
def step_iniciar_proposta(analise_page: AnaliseCreditoPage):
    with allure.step("Ação: Iniciar criação da proposta"):
        # Apenas clica no botão, pois os termos já foram aceitos acima
        analise_page.iniciar_proposta()

@when(parsers.parse('seleciono a opção de seguro "{opcao_seguro}" se o modal for exibido'))
def step_tratar_seguro(analise_page: AnaliseCreditoPage, opcao_seguro: str):
    analise_page.tratar_modal_seguro(opcao_seguro)

@when(parsers.parse('preencho os dados do cliente com Nome "{nome}", Email "{email}", Celular "{celular}" e CEP "{cep}"'))
def step_preencher_cadastro(analise_page: AnaliseCreditoPage, nome: str, email: str, celular: str, cep: str):
    email_final = Generators.email() if email.upper() == "GERAR" else email
    celular_final = Generators.telefone() if celular.upper() == "GERAR" else celular
    analise_page.preencher_dados_cadastrais(nome, email_final, celular_final, cep)

# --- PASSOS DE VALIDAÇÃO ---

@then('o sistema deve habilitar o botão "Enviar para análise de crédito"')
def step_validar_botao_ativo(page: Page, analise_page: AnaliseCreditoPage):
    botao_envio = analise_page.obter_botao_envio()
    expect(botao_envio).to_be_enabled(timeout=15000)

    allure.attach(
        page.screenshot(full_page=True),
        name="Analise_Credito_Formulario_Pronto",
        attachment_type=allure.attachment_type.PNG
    )