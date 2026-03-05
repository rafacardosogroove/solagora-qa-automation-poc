import re  # <--- ESSA LINHA É A QUE FALTAVA!
import allure
from playwright.sync_api import Page, expect

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.input_auth = page.get_by_label("CPF/CNPJ ou e-mail")
        self.input_senha = page.get_by_label("Senha")
        self.btn_entrar = page.get_by_role("button", name="Entrar")

    @allure.step("Realizar login com usuário: {usuario}")
    def realizar_login_duplo(self, usuario, senha):
        self.input_auth.fill(usuario)
        self.input_senha.press_sequentially(senha, delay=50)
        self.page.wait_for_timeout(1000)
        self.input_senha.blur()
        self.btn_entrar.click(force=True)

    @allure.step("Validar exibição da mensagem de erro: '{mensagem}'")
    def validar_mensagem_erro(self, mensagem):
        alerta_erro = self.page.get_by_text(mensagem, exact=True)
        expect(alerta_erro).to_be_visible(timeout=5000)

    # ESTE MÉTODO PRECISA ESTAR NESTA IDENTAÇÃO (FORA DO ANTERIOR)
    @allure.step("Executar fluxo macro de login com sucesso")
    def realizar_login_completo_e_aguardar_dashboard(self, usuario, senha):
        # 1. Acessa a página
        self.page.goto("https://integrator.hom.solagora.com.br/")

        # 2. Realiza o preenchimento
        self.realizar_login_duplo(usuario, senha)

        # 3. Garante que saímos da tela de login (não tem mais /auth na URL)
        expect(self.page).not_to_have_url(re.compile(".*auth.*"), timeout=15000)

        # Opcional: Validar um elemento que só existe na home, como o texto de boas-vindas do print
        expect(self.page.get_by_text("Boas-vindas ao seu espaço de trabalho")).to_be_visible(timeout=10000)