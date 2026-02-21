import pytest
from pages.login_page import LoginPage
from pages.simulador_page import SimuladorPage

@pytest.fixture
def login_page(page):
    return LoginPage(page)

@pytest.fixture
def simulador_page(page):
    return SimuladorPage(page)