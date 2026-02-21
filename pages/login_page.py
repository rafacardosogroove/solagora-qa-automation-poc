import allure
from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.input_auth = page.get_by_role("textbox", name="CPF/CNPJ ou e-mail")
        self.input_senha = page.get_by_role("textbox", name="Senha")
        self.btn_entrar = page.get_by_role("button", name="Entrar")

    @allure.step("Realizar login com usuário {usuario}")
    def realizar_login_duplo(self, usuario, senha):
        self.input_auth.fill(usuario)
        self.input_senha.fill(senha)
        self.btn_entrar.click()