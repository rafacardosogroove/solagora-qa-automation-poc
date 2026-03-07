import pytest
import allure
from pytest_bdd import scenarios, when, then, parsers
from playwright.sync_api import Page, expect

from pages.analise_credito.analise_credito_page import AnaliseCreditoPage
from utils.Generators import Generators

scenarios('../features/analise_credito/03_analise_credito.feature')


# Os @given foram mantidos comentados pois seu conftest.py já está
# cuidando deles brilhantemente de forma centralizada!
# @given('que o ambiente de homologação está respondendo na página de login')
# ...

@when('decido seguir com a proposta clicando em "Quero criar uma proposta"')
def step_iniciar_proposta(analise_page: AnaliseCreditoPage):
    # Passamos a usar a fixture 'analise_page' direto no parâmetro da função!
    analise_page.iniciar_proposta()


@when(parsers.parse('seleciono a opção de seguro "{opcao_seguro}" se o modal for exibido'))
def step_tratar_seguro(analise_page: AnaliseCreditoPage, opcao_seguro: str):
    analise_page.tratar_modal_seguro(opcao_seguro)


@when(
    parsers.parse('preencho os dados do cliente com Nome "{nome}", Email "{email}", Celular "{celular}" e CEP "{cep}"'))
def step_preencher_cadastro(analise_page: AnaliseCreditoPage, nome: str, email: str, celular: str, cep: str):
    with allure.step("Verificar e gerar massa de dados dinâmica caso solicitado ('GERAR')"):
        # Sua lógica impecável mantida exatamente como você fez:
        email_final = Generators.email() if email.upper() == "GERAR" else email
        celular_final = Generators.telefone() if celular.upper() == "GERAR" else celular

    # Manda tudo para a Page preencher
    analise_page.preencher_dados_cadastrais(nome, email_final, celular_final, cep)


@then('o sistema deve habilitar o botão "Enviar para análise de crédito"')
def step_validar_botao_ativo(page: Page, analise_page: AnaliseCreditoPage):
    with allure.step("Validar que o formulário foi preenchido e o botão de envio foi habilitado"):
        # REGRA DE OURO #3: A página apenas entrega o elemento. Quem valida é o teste.
        botao_envio = analise_page.obter_botao_envio()

        # Valida se o botão deixou de estar bloqueado (disabled)
        expect(botao_envio).to_be_enabled(timeout=10000)

    with allure.step("Capturar evidência da análise de crédito preenchida"):
        allure.attach(
            page.screenshot(full_page=True),
            name="Evidencia_Analise_Credito_Sucesso",
            attachment_type=allure.attachment_type.PNG
        )