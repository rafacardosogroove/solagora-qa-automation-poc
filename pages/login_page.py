import re
import allure
from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.input_auth = page.get_by_label("CPF/CNPJ ou e-mail")
        self.input_senha = page.get_by_label("Senha")
        self.btn_entrar = page.get_by_role("button", name="Entrar")

    @allure.step("Ação: Realizar preenchimento de login duplo para '{usuario}'")
    def realizar_login_duplo(self, usuario, senha):
        with allure.step("Preencher campo de autenticação (CPF/E-mail)"):
            self.input_auth.fill(usuario)

        with allure.step("Digitar senha de forma sequencial e remover foco"):
            self.input_senha.press_sequentially(senha, delay=50)
            self.page.wait_for_timeout(1500)
            self.input_senha.blur()

        with allure.step("Acionar botão 'Entrar'"):
            self.btn_entrar.click(force=True)

    @allure.step("Validação: Verificar exibição da mensagem de erro '{mensagem}'")
    def validar_mensagem_erro(self, mensagem):
        alerta_erro = self.page.get_by_text(mensagem, exact=True)

        with allure.step("Aguardar elemento de erro ficar visível na tela"):
            expect(alerta_erro).to_be_visible(timeout=5000)

        # Evidência visual do erro capturado para o relatório
        allure.attach(
            self.page.screenshot(),
            name="Evidencia_Mensagem_Erro",
            attachment_type=allure.attachment_type.PNG
        )

    @allure.step("Macro: Executar fluxo completo de login e aguardar Dashboard")
    def realizar_login_completo_e_aguardar_dashboard(self, usuario, senha):
        with allure.step("Navegar para a página inicial (Ambiente de Homologação)"):
            self.page.goto("https://integrator.hom.solagora.com.br/")

        # Chama a ação que já documentamos acima
        self.realizar_login_duplo(usuario, senha)

        with allure.step("Garantir saída da tela de autenticação (Redirecionamento)"):
            expect(self.page).not_to_have_url(re.compile(".*auth.*"), timeout=15000)

        with allure.step("Aguardar carregamento do texto de Boas-vindas na Dashboard"):
            expect(self.page.get_by_text("Boas-vindas ao seu espaço de trabalho")).to_be_visible(timeout=10000)

        # Tira print da página inteira como prova de que o Macro funcionou
        allure.attach(
            self.page.screenshot(full_page=True),
            name="Dashboard_Carregada_Com_Sucesso",
            attachment_type=allure.attachment_type.PNG
        )