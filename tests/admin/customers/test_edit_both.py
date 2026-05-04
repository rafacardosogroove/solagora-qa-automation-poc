import pytest
import allure
from pytest_bdd import scenario, when, then
from data.customer_data import CUSTOMER, VALID_DATA
from pages.admin.customers.customers_list_page import CustomersListPage
from pages.admin.customers.customer_edit_page import CustomerEditPage


# ==============================================================================
# C03 — Editar e-mail + celular → status "Aguardando Aprovação"
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_edicao
@pytest.mark.fluxo_aprovacao
@scenario('../../../features/admin/customers/edit_both.feature',
          'C03 - Submeter alteração simultânea de e-mail e celular para aprovação')
def test_c03_editar_email_e_celular():
    pass


@when('busco o cliente pelo CPF para edição simultânea')
def step_buscar_cliente_ambos(customers_list_page: CustomersListPage):
    with allure.step(f"Buscar cliente CPF: {CUSTOMER['cpf']}"):
        customers_list_page.buscar_por_cpf(CUSTOMER['cpf'])
        customers_list_page.verificar_badge_ausente(CUSTOMER['cpf'])


@when('acesso a opção "Editar" do menu de ações para edição simultânea')
def step_abrir_edicao_ambos(customers_list_page: CustomersListPage):
    customers_list_page.abrir_menu_acoes(CUSTOMER['cpf'])
    customers_list_page.clicar_editar()


@when('altero o campo "Email" e o campo "Celular" com novos dados válidos')
def step_preencher_ambos(customer_edit_page: CustomerEditPage):
    customer_edit_page.limpar_e_preencher_email(VALID_DATA['email_alt'])
    customer_edit_page.limpar_e_preencher_celular(VALID_DATA['celular_alt'])


@when('submeto o formulário de edição simultânea')
def step_submeter_form_ambos(customer_edit_page: CustomerEditPage):
    customer_edit_page.clicar_salvar()


@then('o modal de confirmação de múltiplas alterações deve ser exibido')
def step_verificar_modal_ambos(customer_edit_page: CustomerEditPage):
    customer_edit_page.verificar_modal_confirmacao()


@then('ao fechar o modal o cliente deve ter o badge de aguardando aprovação simultânea')
def step_fechar_e_verificar_badge_ambos(customer_edit_page: CustomerEditPage,
                                         customers_list_page: CustomersListPage):
    customer_edit_page.fechar_modal()
    customers_list_page.buscar_por_cpf(CUSTOMER['cpf'])
    customers_list_page.verificar_badge_presente(CUSTOMER['cpf'])
    allure.attach(
        customers_list_page.page.screenshot(),
        name="Badge_Aguardando_Ambos",
        attachment_type=allure.attachment_type.PNG
    )
