import pytest
import allure
from pytest_bdd import scenario, when, then
import data.customer_data as customer_data_module
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
    from tests.admin.customers.conftest import _definir_cliente_sem_status
    with allure.step("Encontrar cliente sem status e buscar na lista"):
        cpf = _definir_cliente_sem_status(customers_list_page)
        customers_list_page.buscar_por_cpf(cpf)
        customers_list_page.verificar_badge_ausente(cpf)


@when('acesso a opção "Editar" do menu de ações para edição simultânea')
def step_abrir_edicao_ambos(customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_editar()


@when('altero o campo "Email" e o campo "Celular" com novos dados válidos')
def step_preencher_ambos(customer_edit_page: CustomerEditPage):
    customer_edit_page.limpar_e_preencher_email(customer_data_module.next_email())
    customer_edit_page.limpar_e_preencher_celular(customer_data_module.VALID_DATA['celular_alt'])


@when('submeto o formulário de edição simultânea')
def step_submeter_form_ambos(customer_edit_page: CustomerEditPage):
    customer_edit_page.clicar_salvar()


@then('o modal de confirmação de múltiplas alterações deve ser exibido')
def step_verificar_modal_ambos(customer_edit_page: CustomerEditPage):
    customer_edit_page.verificar_modal_confirmacao()


@then('ao fechar o modal o cliente deve ter o badge de aguardando aprovação simultânea')
def step_fechar_e_verificar_badge_ambos(customer_edit_page: CustomerEditPage,
                                         customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customer_edit_page.fechar_modal()
    customers_list_page.page.wait_for_timeout(2000)
    customers_list_page.navegar_para_clientes()
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.verificar_badge_presente(cpf)
    allure.attach(
        customers_list_page.page.screenshot(),
        name="Badge_Aguardando_Ambos",
        attachment_type=allure.attachment_type.PNG
    )
