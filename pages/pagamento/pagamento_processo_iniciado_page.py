from playwright.sync_api import Page, expect
import allure


class VerificacaoPagamentoPage:
    def __init__(self, page: Page):
        self.page = page

        # --- Locators da Tela de Verificação de Pagamento ---
        self.titulo_pagina = page.get_by_role("heading",
                                              name="Pagamento")  # Usando heading se for h1/h2, ou get_by_text
        self.subtitulo = page.get_by_text("Confira abaixo o passo a passo do que estamos fazendo.")

        # Mapeando o badge laranja
        self.badge_status = page.get_by_text("Status: Pagamento em andamento")

        # Mapeando os textos do processo
        self.passo_pagamento_iniciado = page.get_by_text("Processo de pagamento iniciado")
        self.texto_tempo_estimado = page.get_by_text("Tempo estimado para conclusão: 2 dias úteis")

    # --- MÉTODOS DE VALIDAÇÃO ---

    def validar_tela_pagamento_em_andamento(self):
        """
        Valida se o sistema exibe corretamente a tela de status do pagamento em processamento.
        """
        with allure.step("Validando tela de 'Pagamento' e status 'em andamento'"):
            # O timeout de 15s cobre eventuais demoras ao sair do modal anterior
            expect(self.titulo_pagina).to_be_visible(timeout=15000)
            expect(self.subtitulo).to_be_visible()
            expect(self.badge_status).to_be_visible()
            expect(self.passo_pagamento_iniciado).to_be_visible()

            # Garantindo que a expectativa de SLA está visível
            expect(self.texto_tempo_estimado).to_be_visible()

            login
            simulador
            valid