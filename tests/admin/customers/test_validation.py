import pytest
import allure
from pytest_bdd import scenario, when, then
import data.customer_data as customer_data_module
from data.customer_data import INVALID_DATA
from pages.admin.customers.customers_list_page import CustomersListPage
from pages.admin.customers.customer_edit_page import CustomerEditPage


# ==============================================================================
# C08 — Campos em branco → campos obrigatórios, sem badge
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_edicao
@pytest.mark.validacao_de_dados
@scenario('../../../features/admin/customers/validation.feature',
          'C08 - Tentar submeter formulário de edição limpando campos obrigatórios')
def test_c08_campos_obrigatorios():
    pass


@when('busco o cliente pelo CPF para validação de campos')
def step_buscar_cliente_validacao(customers_list_page: CustomersListPage):
    from tests.admin.customers.conftest import _definir_cliente_sem_status
    with allure.step("Encontrar cliente sem status e buscar na lista"):
        cpf = _definir_cliente_sem_status(customers_list_page)
        customers_list_page.buscar_por_cpf(cpf)
        customers_list_page.verificar_badge_ausente(cpf)


@when('acesso a opção "Editar" do menu de ações para validação')
def step_abrir_edicao_validacao(customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_editar()


@when('apago os dados dos campos "Email" e "Celular" deixando-os em branco')
def step_apagar_campos(customer_edit_page: CustomerEditPage):
    customer_edit_page.limpar_e_preencher_email(INVALID_DATA['vazio'])
    customer_edit_page.limpar_e_preencher_celular(INVALID_DATA['vazio'])


@when('submeto o formulário com campos em branco')
def step_submeter_form_vazio(customer_edit_page: CustomerEditPage):
    customer_edit_page.clicar_salvar()


@then('o formulário não deve ser enviado por campos obrigatórios')
def step_form_nao_enviado_vazio(customer_edit_page: CustomerEditPage):
    customer_edit_page.verificar_modal_nao_aparece()


@then('mensagens de campos obrigatórios devem ser exibidas')
def step_erros_obrigatorios(customer_edit_page: CustomerEditPage):
    customer_edit_page.verificar_erro_validacao_visivel()
    allure.attach(
        customer_edit_page.page.screenshot(),
        name="Erros_Campos_Obrigatorios",
        attachment_type=allure.attachment_type.PNG
    )


@then('o badge de aguardando aprovação não deve aparecer após submissão inválida')
def step_sem_badge_campos_vazios(customers_list_page: CustomersListPage,
                                  customer_edit_page: CustomerEditPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customer_edit_page.clicar_voltar()
    customers_list_page.navegar_para_clientes()
    customers_list_page.ir_para_pagina_cliente()
    customers_list_page.verificar_badge_ausente(cpf)
