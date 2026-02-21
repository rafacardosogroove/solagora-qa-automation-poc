from playwright.sync_api import Page, expect
import allure

class NotasFiscaisPage:
    def __init__(self, page: Page):
        self.page = page
        # Locators baseados no texto da imagem
        self.titulo_modal = page.get_by_text("Tudo certo até agora!")
        self.btn_continuar = page.get_by_role("button", name="Continuar para notas fiscais")

    def validar_modal_sucesso(self):
        with allure.step("Validando modal de sucesso da documentação"):
            # Colocamos um timeout estendido caso a transição de tela demore
            expect(self.titulo_modal).to_be_visible(timeout=15000)

    def clicar_continuar_para_notas(self):
        with allure.step("Clicando em 'Continuar para notas fiscais'"):
            self.btn_continuar.click()