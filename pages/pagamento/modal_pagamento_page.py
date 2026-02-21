from playwright.sync_api import Page, expect
import allure

class PagamentoPage:
    def __init__(self, page: Page):
        self.page = page

        # --- Locators do Modal de Transição ---
        self.titulo_modal = page.get_by_text("Notas fiscais aprovadas!", exact=True)
        self.texto_explicativo = page.get_by_text("Agora seu projeto segue para a etapa de pagamento.")
        self.btn_continuar_pagamento = page.get_by_role("button", name="Continuar para pagamento")

    # --- MÉTODOS DE AÇÃO ---

    def validar_modal_aprovacao_nf(self):
        """
        Valida se o modal de sucesso apareceu após a aprovação das notas.
        """
        with allure.step("Validando modal de 'Notas fiscais aprovadas!'"):
            # Timeout estendido caso o carregamento do status dependa de alguma API lenta
            expect(self.titulo_modal).to_be_visible(timeout=15000)
            expect(self.texto_explicativo).to_be_visible()

    def clicar_continuar_para_pagamento(self):
        """
        Clica no botão amarelo para fechar o modal e acessar a tela de Pagamento.
        """
        with allure.step("Clicando no botão 'Continuar para pagamento'"):
            self.btn_continuar_pagamento.click()