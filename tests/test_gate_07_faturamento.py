import pytest
import allure
from pytest_bdd import scenarios, when, then, parsers
from playwright.sync_api import Page, expect
from pages.notas_fiscais.faturamento_page import FaturamentoPage

# ==========================================
# CARREGAMENTO DA FEATURE
# ==========================================
scenarios('../features/admin/faturamento.feature')


# NOTA: O Contexto (@given 'que o contrato do projeto foi assinado eletronicamente')
# está centralizado e sendo injetado automaticamente pelo conftest.py!

# ==========================================
# PASSOS DE AÇÃO (QUANDO)
# ==========================================

@when('pesquiso o projeto pelo CPF do cliente na listagem')
def step_pesquisar_projeto(page: Page, context_data: dict):
    with allure.step("Ação: Pesquisar projeto pelo CPF do cliente"):
        # O CPF foi gerado no step_macro_simulacao do conftest
        cpf = context_data.get('cpf_utilizado', "249.622.403-66")  # Fallback de segurança
        faturamento_page = FaturamentoPage(page)
        faturamento_page.buscar_projeto_por_filtro(cpf)


@when('seleciono a opção de continuar o projeto faturamento na engrenagem')
def step_continuar_projeto(page: Page, context_data: dict):
    with allure.step("Ação: Acionar engrenagem e clicar em 'Continuar'"):
        cpf = context_data.get('cpf_utilizado', "249.622.403-66")
        faturamento_page = FaturamentoPage(page)
        faturamento_page.clicar_continuar_projeto(cpf)


@when('prossigo para o envio de notas no modal de sucesso')
def step_fechar_modal_sucesso(page: Page):
    with allure.step("Ação: Prosseguir no modal de documentação aprovada"):
        faturamento_page = FaturamentoPage(page)
        faturamento_page.btn_prosseguir_notas.click()


@when(parsers.parse('preencho os dados da Nota Fiscal de Equipamento com número "{numero}" e valor "{valor}"'))
def step_preencher_nf_equip(page: Page, numero, valor):
    with allure.step(f"Ação: Preencher dados da NF de Equipamento (Nº {numero} | R$ {valor})"):
        faturamento_page = FaturamentoPage(page)
        faturamento_page.preencher_nf_equipamento(numero, valor, "conta.jpg")


@when(parsers.parse('preencho os dados da Nota Fiscal de Serviço com número "{numero}" e valor "{valor}"'))
def step_preencher_nf_serv(page: Page, numero, valor):
    with allure.step(f"Ação: Preencher dados da NF de Serviço (Nº {numero} | R$ {valor})"):
        faturamento_page = FaturamentoPage(page)
        faturamento_page.preencher_nf_servico(numero, valor, "conta.jpg")


@when(parsers.parse('seleciono o fabricante do inversor "{fabricante}" e quantidade "{quantidade}"'))
def step_fabricante_inversor(page: Page, fabricante, quantidade):
    with allure.step(f"Ação: Selecionar inversor {fabricante} (qtd: {quantidade})"):
        faturamento_page = FaturamentoPage(page)
        faturamento_page.selecionar_fabricante_inversor(fabricante, quantidade)


@when(parsers.parse('seleciono o fabricante do módulo "{fabricante}" e quantidade "{quantidade}"'))
def step_fabricante_modulo(page: Page, fabricante, quantidade):
    with allure.step(f"Ação: Selecionar módulo {fabricante} (qtd: {quantidade})"):
        faturamento_page = FaturamentoPage(page)
        faturamento_page.selecionar_fabricante_modulo(fabricante, quantidade)


@when('finalizo o envio das notas e informações')
def step_finalizar_envio(page: Page):
    with allure.step("Ação: Finalizar envio das notas e informações"):
        faturamento_page = FaturamentoPage(page)
        faturamento_page.finalizar_envio_notas()


# ==========================================
# PASSOS DE VALIDAÇÃO (ENTÃO)
# ==========================================

@then('o sistema deve exibir a tela de análise de notas fiscais')
def step_validar_final_nf(page: Page):
    with allure.step("Validar transição para a tela de Verificação das Notas Fiscais"):
        expect(page.get_by_text("Verificando as notas fiscais")).to_be_visible(timeout=15000)

        allure.attach(
            page.screenshot(full_page=True),
            name="Gate07_Finalizado",
            attachment_type=allure.attachment_type.PNG
        )