import pytest
import allure
from pytest_bdd import scenario, when, then
import data.customer_data as customer_data_module
from data.customer_data import INVALID_DATA
from pages.admin.customers.customers_list_page import CustomersListPage
from pages.admin.customers.customer_edit_page import CustomerEditPage


# ==============================================================================
# C01 — Editar só e-mail → status "Aguardando Aprovação"
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_edicao
@pytest.mark.fluxo_aprovacao
@pytest.mark.smoke_test
@allure.epic("Portal Admin — Gestão Cadastral")
@allure.feature("Clientes")
@allure.story("Edição de E-mail")
@allure.severity(allure.severity_level.CRITICAL)
@scenario('../../../features/admin/customers/edit_email.feature',
          'C01 - Submeter alteração exclusiva de e-mail para aprovação')
def test_c01_editar_email():
    pass


@when('busco o cliente pelo CPF para edição de e-mail')
def step_buscar_cliente_email(customers_list_page: CustomersListPage):
    from tests.admin.customers.conftest import _definir_cliente_sem_status
    with allure.step("Encontrar cliente sem status e buscar na lista"):
        cpf = _definir_cliente_sem_status(customers_list_page)
        customers_list_page.buscar_por_cpf(cpf)
        customers_list_page.verificar_badge_ausente(cpf)


@when('acesso a opção "Editar" do menu de ações')
def step_abrir_edicao_email(customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_editar()


@when('altero o campo "Email" para um novo endereço válido')
def step_preencher_email_valido(customer_edit_page: CustomerEditPage):
    customer_edit_page.limpar_e_preencher_email(customer_data_module.next_email())


@when('submeto o formulário de edição')
def step_submeter_form_email(customer_edit_page: CustomerEditPage):
    customer_edit_page.clicar_salvar()


@then('o modal de confirmação de solicitação deve ser exibido')
def step_verificar_modal_email(customer_edit_page: CustomerEditPage):
    customer_edit_page.verificar_modal_confirmacao()


@then('ao fechar o modal o cliente deve ter o badge de aguardando aprovação')
def step_fechar_e_verificar_badge_email(customer_edit_page: CustomerEditPage,
                                        customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customer_edit_page.fechar_modal()
    customers_list_page.page.wait_for_timeout(2000)
    customers_list_page.navegar_para_clientes()
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.verificar_badge_presente(cpf)
    allure.attach(
        customers_list_page.page.screenshot(),
        name="Badge_Aguardando_Email",
        attachment_type=allure.attachment_type.PNG
    )


# ==============================================================================
# C06 — E-mail inválido → erro de validação, sem badge
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_edicao
@pytest.mark.validacao_de_dados
@allure.epic("Portal Admin — Gestão Cadastral")
@allure.feature("Clientes")
@allure.story("Edição de E-mail")
@allure.severity(allure.severity_level.MINOR)
@scenario('../../../features/admin/customers/edit_email.feature',
          'C06 - Tentar submeter alteração com formato de e-mail inválido')
def test_c06_email_invalido():
    pass


@when('altero o campo "Email" para um formato inválido')
def step_preencher_email_invalido(customer_edit_page: CustomerEditPage):
    customer_edit_page.limpar_e_preencher_email(INVALID_DATA['email_sem_dominio'])


@then('o formulário não deve ser enviado')
def step_form_nao_enviado(customer_edit_page: CustomerEditPage):
    customer_edit_page.verificar_modal_nao_aparece()


@then('uma mensagem de erro de validação deve ser exibida no campo Email')
def step_erro_campo_email(customer_edit_page: CustomerEditPage):
    customer_edit_page.verificar_erro_validacao_visivel()


@then('o badge de aguardando aprovação não deve aparecer para o cliente')
def step_sem_badge_email_invalido(customers_list_page: CustomersListPage,
                                   customer_edit_page: CustomerEditPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customer_edit_page.clicar_voltar()
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.verificar_badge_ausente(cpf)
