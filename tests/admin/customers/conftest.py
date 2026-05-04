import re
import pytest
import allure
from pathlib import Path
from playwright.sync_api import Page
from pytest_bdd import given

from pages.admin.customers.customers_list_page import CustomersListPage
from pages.admin.customers.customer_edit_page import CustomerEditPage
from pages.admin.customers.customer_details_page import CustomerDetailsPage
from data.customer_data import CUSTOMER, VALID_DATA, INVALID_DATA
from utils.hml_client import hml


# ==============================================================================
# FIXTURES DE INFRAESTRUTURA
# ==============================================================================

@pytest.fixture(scope="session")
def admin_portal():
    root_path = Path(__file__).parent.parent.parent.parent
    env_path = root_path / ".env"
    hml.configure(env_file=str(env_path))
    return hml


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
    return {"customer": CUSTOMER, "valid": VALID_DATA, "invalid": INVALID_DATA}


# ==============================================================================
# STEPS DADOS — CONTEXTO BASE
# ==============================================================================

@given("que o administrador está devidamente autenticado no portal")
def step_login_admin_portal(page: Page):
    with allure.step("Acessar portal admin e autenticar como superadmin"):
        page.goto("https://admin.hom.solagora.com.br/")
        page.wait_for_load_state("networkidle")

        # Se redirecionou para tela de login, preencher credenciais
        if "login" in page.url or "auth" in page.url:
            page.get_by_label("E-mail").fill("superadmin")
            senha_field = page.get_by_label("Senha")
            senha_field.press_sequentially("SuperAdmin@123", delay=50)
            page.wait_for_timeout(2000)
            senha_field.blur()
            page.get_by_role("button", name="Entrar").click(force=True)

            # Aguardar saída da tela de login
            page.wait_for_url(re.compile(r"(?!.*login)(?!.*auth).*"), timeout=20000)
            page.wait_for_load_state("networkidle")

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
