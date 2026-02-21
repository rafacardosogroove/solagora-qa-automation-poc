from playwright.sync_api import Page, expect
import allure


class VerificacaoNotasFiscaisPage:
    def __init__(self, page: Page):
        self.page = page

        # --- Locators da Tela de Verificação ---
        # Como não temos o HTML, get_by_text é a forma mais segura de mapear títulos visuais
        self.titulo_pagina = page.get_by_text("Verificando as notas fiscais", exact=True)

        # Mapeando o badge laranja de status
        self.badge_status = page.get_by_text("Status: Aguardando documentação de equipamento entregue")

        # Mapeando as informações de feedback
        self.texto_passo_analise = page.get_by_text("Análise do envio das notas fiscais")
        self.texto_tempo_estimado = page.get_by_text("Tempo estimado para conclusão: 2 dias úteis")

    # --- MÉTODOS DE AÇÃO / VALIDAÇÃO ---

    def validar_tela_verificacao_em_andamento(self):
        """
        Valida se o sistema carregou corretamente a tela de processamento
        após o envio das notas fiscais.
        """
        with allure.step("Validando tela de 'Verificando as notas fiscais' e status atual"):
            # Colocamos um timeout estendido pois o upload dos PDFs na tela anterior
            # pode fazer essa transição de tela demorar alguns segundos
            expect(self.titulo_pagina).to_be_visible(timeout=20000)
            expect(self.badge_status).to_be_visible()
            expect(self.texto_passo_analise).to_be_visible()

            # Validação opcional do SLA de atendimento
            expect(self.texto_tempo_estimado).to_be_visible()