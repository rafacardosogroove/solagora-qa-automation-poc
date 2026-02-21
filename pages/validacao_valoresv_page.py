import allure
from playwright.sync_api import Page


class ValidacaoValoresPage:
    def __init__(self, page: Page):
        self.page = page

        # Elementos Comuns aos Modais de Alerta
        self.icon_alerta = page.locator(".pi-exclamation-triangle")

        # Modal 1: Entrada necessária para continuar (image_c10b28.png)
        self.btn_quero_continuar = page.get_by_role("button", name="Quero continuar")

        # Modal 2: Valor da entrada mínimo (image_c1832a.png)
        self.btn_continuar_com_valor = page.get_by_role("button", name="Continuar com esse valor")

        # Opção comum para ambos
        self.btn_alterar_valores = page.get_by_role("button", name="Quero alterar os valores")

    @allure.step("Verificar se o modal de política de renda apareceu")
    def tratar_aviso_renda(self):
        """
        Aguarda o modal de compromisso de renda. Se aparecer, clica em continuar.
        """
        if self.btn_quero_continuar.is_visible(timeout=5000):
            self.btn_quero_continuar.click()

    @allure.step("Verificar se o modal de entrada mínima apareceu")
    def tratar_aviso_entrada_minima(self):
        """
        Aguarda o aviso de valor de entrada mínima sugerido.
        """
        if self.btn_continuar_com_valor.is_visible(timeout=5000):
            self.btn_continuar_com_valor.click()

    @allure.step("Clicar em alterar valores para ajustar a simulação")
    def ajustar_simulacao(self):
        self.btn_alterar_valores.click()