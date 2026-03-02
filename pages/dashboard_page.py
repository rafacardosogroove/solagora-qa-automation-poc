import allure
from playwright.sync_api import Page


class DashboardPage:
    def __init__(self, page: Page):
        self.page = page

        # ⚠️ ATENÇÃO AQUI: Ajuste o nome do botão conforme a sua tela real.
        # Às vezes pode ser "Logout", "Sair do sistema", etc.
        self.btn_sair = page.get_by_role("link", name="Sair")
        self.btn_avatar =  page.get_by_test_id("header.user-button")

    @allure.step("Acionar a opção de logout do sistema")
    def realizar_logout(self):
        self.btn_avatar.click()
        self.btn_sair.click()

