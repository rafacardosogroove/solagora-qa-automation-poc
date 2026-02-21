import allure
from playwright.sync_api import Page


class ResultadoSimulacaoPage:
    def __init__(self, page: Page):
        self.page = page

        # Elementos de Verificação
        self.label_sucesso = page.get_by_text("Boas notícias! As condições foram aceitas")
        self.valor_projeto = page.locator("text=/Projeto no valor de/")

        # Opções de Parcelamento (Cards)
        self.cards_parcelas = page.locator(".p-card")  # Localizador genérico dos cards de opção

        # Botões de Ação Final
        self.btn_criar_proposta = page.get_by_role("button", name="Quero criar uma proposta")
        self.btn_encerrar = page.get_by_role("button", name="Encerrar simulação")

    @allure.step("Validar que as condições de financiamento foram exibidas")
    def validar_exibicao_resultados(self):
        self.label_sucesso.wait_for(state="visible", timeout=15000)
        allure.attach(self.page.screenshot(), name="Resultado_Simulacao", attachment_type=allure.attachment_type.PNG)

    @allure.step("Selecionar a opção de parcelamento: {parcela}")
    def selecionar_parcelamento_por_texto(self, parcela):
        """
        Seleciona o card que contém o texto específico da parcela (ex: '25x')
        """
        card = self.page.locator("div").filter(has_text=parcela).locator("..").first
        card.click()

    @allure.step("Avançar para a criação da proposta")
    def criar_proposta(self):
        self.btn_criar_proposta.click()