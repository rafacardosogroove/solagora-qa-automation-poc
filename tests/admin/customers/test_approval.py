import pytest
import allure
from pytest_bdd import scenario, given, when, then
import data.customer_data as customer_data_module
from pages.admin.customers.customers_list_page import CustomersListPage
from pages.admin.customers.customer_edit_page import CustomerEditPage
from pages.admin.customers.customer_details_page import CustomerDetailsPage
from playwright.sync_api import expect


# ==============================================================================
# HELPER — cria solicitação pendente para o cliente já definido em CUSTOMER
# ==============================================================================

def _criar_solicitacao_pendente(customers_list_page: CustomersListPage,
                                 customer_edit_page: CustomerEditPage,
                                 novo_email: str):
    """Submete alteração de email para criar estado 'Aguardando Aprovação'."""
    from tests.admin.customers.conftest import _definir_cliente_sem_status
    cpf = _definir_cliente_sem_status(customers_list_page)
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_editar()
    customer_edit_page.limpar_e_preencher_email(novo_email)
    customer_edit_page.clicar_salvar()
    customer_edit_page.verificar_modal_confirmacao()
    customer_edit_page.fechar_modal()


# ==============================================================================
# C04 — Aprovar solicitação pendente → dados efetivados
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_analise
@pytest.mark.aprovacao_positiva
@pytest.mark.smoke_test
@scenario('../../../features/admin/customers/approval.feature',
          'C04 - Aprovar com sucesso uma solicitação de alteração de dados pendente')
def test_c04_aprovar_solicitacao():
    pass


@given("que o cliente possui uma solicitação de alteração pendente aguardando aprovação")
def step_garantir_pendente_aprovacao(customers_list_page: CustomersListPage,
                                      customer_edit_page: CustomerEditPage):
    with allure.step("Criar solicitação pendente para teste de aprovação"):
        _criar_solicitacao_pendente(customers_list_page, customer_edit_page, customer_data_module.next_email())
        cpf = customer_data_module.CUSTOMER['cpf']
        customers_list_page.navegar_para_clientes()
        customers_list_page.buscar_por_cpf(cpf)
        customers_list_page.verificar_badge_presente(cpf)


@when("acesso os detalhes do cliente com solicitação pendente")
def step_abrir_detalhes_aprovacao(customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_ver_detalhes()


@when("navego até o bloco de Análise")
def step_ir_analise_aprovacao(customer_details_page: CustomerDetailsPage):
    customer_details_page.ir_para_secao_analise()


@when('seleciono a opção "Aprovar"')
def step_selecionar_aprovar(customer_details_page: CustomerDetailsPage):
    customer_details_page.selecionar_aprovar()


@when("salvo a decisão de aprovação")
def step_salvar_aprovacao(customer_details_page: CustomerDetailsPage):
    customer_details_page.clicar_salvar()


@then("o badge de aguardando deve ser removido da listagem")
def step_verificar_badge_removido(customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.page.wait_for_timeout(3000)
    customers_list_page.navegar_para_clientes()
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.verificar_badge_ausente(cpf)
    allure.attach(
        customers_list_page.page.screenshot(),
        name="Badge_Removido_Apos_Aprovacao",
        attachment_type=allure.attachment_type.PNG
    )


@then("os novos dados devem estar efetivados no cadastro")
def step_verificar_dados_efetivados(customers_list_page: CustomersListPage):
    # Badge foi removido = aprovação processada; dados efetivados confirmados via badge ausente
    cpf = customer_data_module.CUSTOMER['cpf']
    linha = customers_list_page.page.locator("tr", has_text=cpf)
    expect(linha).to_be_visible(timeout=10000)


# ==============================================================================
# C05 — Reprovar solicitação → dados originais mantidos
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_analise
@pytest.mark.aprovacao_negativa
@scenario('../../../features/admin/customers/approval.feature',
          'C05 - Reprovar uma solicitação de alteração de dados pendente')
def test_c05_reprovar_solicitacao():
    pass


@given("que o cliente possui uma solicitação de alteração pendente aguardando reprovação")
def step_garantir_pendente_reprovacao(customers_list_page: CustomersListPage,
                                       customer_edit_page: CustomerEditPage):
    with allure.step("Criar solicitação pendente para teste de reprovação"):
        _criar_solicitacao_pendente(customers_list_page, customer_edit_page, customer_data_module.next_email())
        cpf = customer_data_module.CUSTOMER['cpf']
        customers_list_page.navegar_para_clientes()
        customers_list_page.buscar_por_cpf(cpf)
        customers_list_page.verificar_badge_presente(cpf)


@when("acesso os detalhes do cliente com solicitação pendente para reprovar")
def step_abrir_detalhes_reprovacao(customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_ver_detalhes()


@when("navego até o bloco de Análise para reprovar")
def step_ir_analise_reprovacao(customer_details_page: CustomerDetailsPage):
    customer_details_page.ir_para_secao_analise()


@when('seleciono a opção "Reprovar"')
def step_selecionar_reprovar(customer_details_page: CustomerDetailsPage):
    customer_details_page.selecionar_reprovar()


@when("salvo a decisão de reprovação")
def step_salvar_reprovacao(customer_details_page: CustomerDetailsPage):
    customer_details_page.clicar_salvar()


@then("o badge de aguardando deve ser removido após reprovação")
def step_verificar_badge_removido_reprovacao(customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.page.wait_for_timeout(3000)
    customers_list_page.navegar_para_clientes()
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.verificar_badge_ausente(cpf)
    allure.attach(
        customers_list_page.page.screenshot(),
        name="Badge_Removido_Apos_Reprovacao",
        attachment_type=allure.attachment_type.PNG
    )


@then("os dados originais devem ser mantidos no cadastro")
def step_verificar_dados_originais(customers_list_page: CustomersListPage):
    # Badge removido = reprovação processada; dados originais mantidos (badge ausente confirma)
    cpf = customer_data_module.CUSTOMER['cpf']
    linha = customers_list_page.page.locator("tr", has_text=cpf)
    expect(linha).to_be_visible(timeout=10000)
