import allure
from playwright.sync_api import Page


class PoliticaRendaPage:
    def __init__(self, page: Page):
        self.page = page

        # Elementos do Modal de Aviso
        self.container_modal = page.locator("div.p-dialog")  # Seletor genérico PrimeVue para o modal
        self.titulo_aviso = page.get_by_text("Entrada necessária para continuar")

        # Botões de Ação
        self.btn_quero_continuar = page.get_by_role("button", name="Quero continuar")
        self.btn_alterar_valores = page.get_by_role("button", name="Quero alterar os valores")
        self.btn_encerrar = page.get_by_text("Encerrar simulação")

    @allure.step("Validar visibilidade do aviso de política de renda")
    def validar_exibicao_aviso(self):
        # Aguarda o texto principal do print aparecer
        self.titulo_aviso.wait_for(state="visible", timeout=10000)

    @allure.step("Clicar em 'Quero continuar' no modal de renda")
    def continuar_simulacao(self):
        self.btn_quero_continuar.click()

    @allure.step("Clicar em 'Quero alterar os valores'")
    def ajustar_valores(self):
        self.btn_alterar_valores.click()

    @allure.step("Encerrar a simulação pelo modal")
    def encerrar_fluxo(self):
        self.btn_encerrar.click()