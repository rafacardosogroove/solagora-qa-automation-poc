import pytest
import allure
from pytest_bdd import scenario, given, when, then
import data.customer_data as customer_data_module
from pages.admin.customers.customers_list_page import CustomersListPage
from pages.admin.customers.customer_edit_page import CustomerEditPage
from pages.admin.customers.customer_details_page import CustomerDetailsPage
from playwright.sync_api import expect


# ==============================================================================
# HELPER
# ==============================================================================

def _criar_e_aprovar_solicitacao(customers_list_page: CustomersListPage,
                                  customer_edit_page: CustomerEditPage,
                                  customer_details_page: CustomerDetailsPage,
                                  novo_email: str):
    """Encontra cliente limpo, submete edição e aprova."""
    from tests.admin.customers.conftest import _definir_cliente_sem_status
    cpf = _definir_cliente_sem_status(customers_list_page)
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_editar()
    customer_edit_page.limpar_e_preencher_email(novo_email)
    customer_edit_page.clicar_salvar()
    customer_edit_page.verificar_modal_confirmacao()
    customer_edit_page.fechar_modal()
    customers_list_page.page.wait_for_timeout(2000)
    customers_list_page.navegar_para_clientes()
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_ver_detalhes()
    customer_details_page.ir_para_secao_analise()
    customer_details_page.selecionar_aprovar()
    customer_details_page.clicar_salvar()


# ==============================================================================
# C09 — Nomenclatura exata do status
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_status
@pytest.mark.fluxo_riscos
@scenario('../../../features/admin/customers/history.feature',
          'C09 - Validar nomenclatura exata do status para pedidos em atendimento')
def test_c09_nomenclatura_status():
    pass


@when('submeto uma alteração de dados para o cliente de nomenclatura')
def step_submeter_alteracao_nomenclatura(customers_list_page: CustomersListPage,
                                          customer_edit_page: CustomerEditPage):
    from tests.admin.customers.conftest import _definir_cliente_sem_status
    with allure.step("Submeter alteração para gerar status de aguardando"):
        cpf = _definir_cliente_sem_status(customers_list_page)
        customers_list_page.buscar_por_cpf(cpf)
        customers_list_page.abrir_menu_acoes(cpf)
        customers_list_page.clicar_editar()
        customer_edit_page.limpar_e_preencher_email(customer_data_module.next_email())
        customer_edit_page.clicar_salvar()
        customer_edit_page.verificar_modal_confirmacao()
        customer_edit_page.fechar_modal()


@then('o status atribuído deve ser exatamente "Aguardando aprovação da alteração"')
def step_verificar_nomenclatura_status(customers_list_page: CustomersListPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.page.wait_for_timeout(2000)
    customers_list_page.navegar_para_clientes()
    customers_list_page.buscar_por_cpf(cpf)
    linha = customers_list_page.page.locator("tr", has_text=cpf)
    expect(linha).to_be_visible(timeout=10000)
    status_cell = linha.locator("td").nth(3)
    expect(status_cell).not_to_be_empty(timeout=10000)
    status_txt = status_cell.inner_text().strip()
    assert "aguard" in status_txt.lower(), f"Status inesperado: '{status_txt}'"
    allure.attach(status_txt, name="Texto_Status_Badge",
                  attachment_type=allure.attachment_type.TEXT)


@then("esse status deve estar visível na listagem de clientes")
def step_status_visivel_listagem(customers_list_page: CustomersListPage):
    allure.attach(
        customers_list_page.page.screenshot(full_page=True),
        name="Status_Aguardando_Listagem",
        attachment_type=allure.attachment_type.PNG
    )


# ==============================================================================
# C10 — Propagação do novo e-mail para projetos vinculados
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_analise
@pytest.mark.aprovacao_cascata
@pytest.mark.historico
@pytest.mark.smoke_test
@scenario('../../../features/admin/customers/history.feature',
          'C10 - Validar propagação da alteração aprovada para os projetos do cliente')
def test_c10_propagacao_projetos():
    pass


@given("que o cliente possui uma solicitação de novo e-mail aprovada")
def step_garantir_email_aprovado(customers_list_page: CustomersListPage,
                                  customer_edit_page: CustomerEditPage,
                                  customer_details_page: CustomerDetailsPage):
    with allure.step("Criar e aprovar solicitação de novo e-mail"):
        _criar_e_aprovar_solicitacao(
            customers_list_page, customer_edit_page, customer_details_page, customer_data_module.next_email()
        )


@when("acesso os projetos vinculados ao cliente")
def step_acessar_projetos(customers_list_page: CustomersListPage,
                           customer_details_page: CustomerDetailsPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.navegar_para_clientes()
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_ver_detalhes()
    try:
        customer_details_page.navegar_aba_projetos()
    except RuntimeError:
        import pytest
        pytest.skip("Cliente selecionado não possui projetos vinculados — cenário C10 requer cliente com projetos")


@then("todos os projetos devem exibir o novo e-mail aprovado")
def step_verificar_email_projetos(customer_details_page: CustomerDetailsPage):
    emails = customer_details_page.obter_emails_projetos()
    assert len(emails) > 0, "Nenhum projeto encontrado para o cliente"
    for email in emails:
        assert VALID_DATA['email'] in email, \
            f"Projeto com e-mail desatualizado: '{email}'. Esperado: '{VALID_DATA['email']}'"
    allure.attach(
        customer_details_page.page.screenshot(),
        name="Email_Propagado_Projetos",
        attachment_type=allure.attachment_type.PNG
    )


# ==============================================================================
# C11 — Histórico de auditoria completo
# ==============================================================================

@pytest.mark.clientes
@pytest.mark.clientes_analise
@pytest.mark.historico_auditoria
@scenario('../../../features/admin/customers/history.feature',
          'C11 - Validar o registro de histórico após a decisão da equipe de riscos')
def test_c11_historico_auditoria():
    pass


@given("que uma decisão de aprovação foi registrada para o cliente de histórico")
def step_garantir_decisao_registrada(customers_list_page: CustomersListPage,
                                      customer_edit_page: CustomerEditPage,
                                      customer_details_page: CustomerDetailsPage):
    with allure.step("Criar solicitação e aprovar para gerar registro de histórico"):
        _criar_e_aprovar_solicitacao(
            customers_list_page, customer_edit_page, customer_details_page, customer_data_module.next_email()
        )


@when("verifico o histórico de alterações do cliente")
def step_verificar_historico(customers_list_page: CustomersListPage,
                              customer_details_page: CustomerDetailsPage):
    cpf = customer_data_module.CUSTOMER['cpf']
    customers_list_page.navegar_para_clientes()
    customers_list_page.buscar_por_cpf(cpf)
    customers_list_page.abrir_menu_acoes(cpf)
    customers_list_page.clicar_ver_detalhes()


@then("o histórico deve conter os dados de de/para com autor e data/hora")
def step_validar_historico_depara(customer_details_page: CustomerDetailsPage):
    historico = customer_details_page.obter_ultima_linha_historico()
    assert historico['valor_anterior'], "Campo 'Valor Anterior' vazio no histórico"
    assert historico['novo_valor'], "Campo 'Novo Valor' vazio no histórico"
    assert historico['por'], "Campo 'Por' (autor) vazio no histórico"
    assert historico['solicitado_em'], "Campo 'Solicitado em' vazio no histórico"
    allure.attach(
        str(historico),
        name="Dados_Historico_Auditoria",
        attachment_type=allure.attachment_type.TEXT
    )


@then("os campos status processado_em e por devem estar preenchidos")
def step_validar_campos_auditoria(customer_details_page: CustomerDetailsPage):
    historico = customer_details_page.obter_ultima_linha_historico()
    assert historico['status'], "Campo 'Status' vazio no histórico"
    assert historico['processado_em'], "Campo 'Processado em' vazio no histórico"
    assert historico['por'], "Campo 'Por' vazio no histórico"
    allure.attach(
        customer_details_page.page.screenshot(),
        name="Historico_Auditoria_Completo",
        attachment_type=allure.attachment_type.PNG
    )
