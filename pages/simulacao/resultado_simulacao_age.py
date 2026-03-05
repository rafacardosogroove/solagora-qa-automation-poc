import allure
from playwright.sync_api import Page, expect


class ResultadoSimulacaoPage:
    def __init__(self, page: Page):
        self.page = page
        # Texto principal de sucesso que vimos no seu print
        self.msg_sucesso = page.get_by_text("Boas notícias! As condições foram aceitas")
        self.btn_criar_proposta = page.get_by_role("button", name="Quero criar uma proposta")

    @allure.step("Validar que a tela de resultados de financiamento carregou")
    def validar_tela_resultados(self, mensagem):
        # Aguarda a mensagem de sucesso com um timeout generoso (o cálculo pode demorar)
        expect(self.page.get_by_text(mensagem)).to_be_visible(timeout=15000)

        # Tira um screenshot para o Allure provar que as taxas apareceram
        allure.attach(
            self.page.screenshot(full_page=True),
            name="Resultado_Simulacao_Sucesso",
            attachment_type=allure.attachment_type.PNG
        )