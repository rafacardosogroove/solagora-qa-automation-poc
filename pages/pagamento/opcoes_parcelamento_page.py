import allure
from playwright.sync_api import Page


class OpcoesParcelamentoPage:
    def __init__(self, page: Page):
        self.page = page

        # Verificadores de Estado
        self.msg_sucesso = page.get_by_text("Boas notícias! As condições foram aceitas")
        self.container_parcelas = page.locator(".p-card")

        # Slider de Parcelas (Opcional, para simular movimento)
        self.slider_parcelas = page.locator(".p-slider-handle")

        # Botões Principais
        self.btn_criar_proposta = page.get_by_role("button", name="Quero criar uma proposta")
        self.btn_encerrar = page.get_by_role("button", name="Encerrar simulação")

    @allure.step("Validar exibição das opções de financiamento")
    def validar_resultados(self):
        self.msg_sucesso.wait_for(state="visible", timeout=20000)

    @allure.step("Selecionar a parcela de {texto_parcela}")
    def selecionar_parcela(self, texto_parcela):
        """
        Seleciona o card de parcelamento baseado no texto (ex: '25x de R$ 400,26')
        """
        # Filtra o card que contém o texto específico da parcela desejada
        card = self.page.locator(".p-card").filter(has_text=texto_parcela).first
        card.click()

    @allure.step("Avançar para criação da proposta")
    def avançar_para_proposta(self):
        self.btn_criar_proposta.click()