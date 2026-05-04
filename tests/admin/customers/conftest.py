import re
import pytest
import allure
from playwright.sync_api import Page, expect
from pytest_bdd import given

from pages.admin.customers.customers_list_page import CustomersListPage
from pages.admin.customers.customer_edit_page import CustomerEditPage
from pages.admin.customers.customer_details_page import CustomerDetailsPage
import data.customer_data as customer_data_module


# ==============================================================================
# FIXTURES DAS PAGES
# ==============================================================================

@pytest.fixture
def customers_list_page(page: Page) -> CustomersListPage:
    return CustomersListPage(page)


@pytest.fixture
def customer_edit_page(page: Page) -> CustomerEditPage:
    return CustomerEditPage(page)


@pytest.fixture
def customer_details_page(page: Page) -> CustomerDetailsPage:
    return CustomerDetailsPage(page)


@pytest.fixture
def customer_data():
    return {
        "customer": customer_data_module.CUSTOMER,
        "valid": customer_data_module.VALID_DATA,
        "invalid": customer_data_module.INVALID_DATA,
    }


# ==============================================================================
# HELPER — LOGIN NO PORTAL ADMIN
# ==============================================================================

def _fazer_login_admin(page: Page):
    """
    Navega para /customers e aguarda: ou tabela aparece (já logado)
    ou SPA redireciona para Keycloak (precisa logar).
    """
    page.goto("https://admin.hom.solagora.com.br/customers")

    # Aguardar: tabela visível (logado) OU redirect para Keycloak (não logado)
    page.wait_for_function(
        "() => document.querySelector('table') !== null"
        " || location.href.includes('employee-auth')",
        timeout=20000
    )

    if "employee-auth" in page.url:
        with allure.step("Preencher credenciais superadmin no Keycloak"):
            page.fill("input[name='username']", "superadmin")
            page.fill("input[type='password']", "SuperAdmin@123")
            page.locator("input[type='submit']").click()

        with allure.step("Aguardar redirect de volta ao portal admin"):
            page.wait_for_url(re.compile(r"admin\.hom\.solagora\.com\.br"), timeout=25000)
            page.wait_for_function(
                "() => document.querySelector('table') !== null",
                timeout=30000
            )

    expect(page.locator("table").first).to_be_visible(timeout=5000)


# ==============================================================================
# HELPER — DEFINIR CLIENTE SEM STATUS (DINÂMICO)
# ==============================================================================

def _definir_cliente_sem_status(customers_list_page: CustomersListPage) -> str:
    """
    Varre a lista de clientes e define customer_data.CUSTOMER['cpf'] com o
    primeiro registro que não possui status 'AGUARDANDO'.
    Retorna o CPF encontrado.
    """
    with allure.step("Procurar cliente sem status na lista"):
        cpf = customers_list_page.encontrar_cliente_sem_status()
        customer_data_module.CUSTOMER['cpf'] = cpf
        allure.attach(
            customers_list_page.page.screenshot(),
            name=f"Cliente_Sem_Status_Encontrado_{cpf}",
            attachment_type=allure.attachment_type.PNG
        )
        return cpf


# ==============================================================================
# HELPER — LIMPAR STATUS PENDENTE DO CLIENTE
# ==============================================================================

def _limpar_status_pendente(page: Page, cpf: str):
    """
    Se o cliente tiver status 'AGUARDANDO', vai para Ver Detalhes,
    reprova a solicitação, e volta à listagem sem badge.
    """
    lista = CustomersListPage(page)
    detalhes = CustomerDetailsPage(page)

    lista.buscar_por_cpf(cpf)
    linha = page.locator("tr", has_text=cpf)
    badge = linha.get_by_text("AGUARDANDO", exact=False).first
    if badge.is_visible():
        with allure.step("Setup: limpar status pendente existente"):
            lista.abrir_menu_acoes(cpf)
            lista.clicar_ver_detalhes()
            detalhes.ir_para_secao_analise()
            detalhes.selecionar_reprovar()
            detalhes.clicar_salvar()
            page.wait_for_timeout(2000)
            lista.navegar_para_clientes()
            lista.buscar_por_cpf(cpf)

    allure.attach(
        page.screenshot(),
        name="Setup_Status_Limpo",
        attachment_type=allure.attachment_type.PNG
    )


# ==============================================================================
# STEPS DADOS — CONTEXTO BASE
# ==============================================================================

@given("que o administrador está devidamente autenticado no portal")
def step_login_admin_portal(page: Page):
    with allure.step("Autenticar no portal admin como superadmin"):
        _fazer_login_admin(page)
        allure.attach(
            page.screenshot(full_page=True),
            name="Admin_Portal_Autenticado",
            attachment_type=allure.attachment_type.PNG
        )


@given('o componente de navegação carrega a página de "Clientes"')
def step_navegar_clientes(customers_list_page: CustomersListPage):
    customers_list_page.navegar_para_clientes()
    allure.attach(
        customers_list_page.page.screenshot(),
        name="Pagina_Clientes_Carregada",
        attachment_type=allure.attachment_type.PNG
    )
