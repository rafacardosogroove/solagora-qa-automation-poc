import allure
from playwright.sync_api import Page


class AnaliseProcessamentoPage:
    def __init__(self, page: Page):
        self.page = page

        # Labels de Status e Títulos
        self.titulo_pagina = page.get_by_text("Estamos fazendo a análise")
        self.status_tag = page.locator("span.p-tag-value")  # Seletor para o status 'Aguardando avaliação externa'
        self.texto_informativo = page.get_by_text("Realizando a análise de crédito do seu cliente em nossos sistemas")

        # Label de Tempo Estimado
        self.tempo_estimado = page.get_by_text("Tempo estimado para conclusão: 2 horas")

    @allure.step("Validar que a página de processamento de análise foi carregada")
    def validar_pagina_processamento(self):
        """Verifica se os elementos principais de status estão visíveis na tela."""
        self.titulo_pagina.wait_for(state="visible", timeout=15000)

    @allure.step("Verificar o status atual da análise")
    def validar_status_analise(self, status_esperado="Aguardando avaliação externa"):
        """Valida se o texto da tag de status corresponde ao esperado."""
        actual_status = self.status_tag.inner_text()
        assert actual_status == status_esperado, f"Esperado: {status_esperado}, mas obteve: {actual_status}"

    @allure.step("Validar exibição do tempo estimado")
    def validar_tempo_estimado_visivel(self):
        """Garante que a label de tempo estimado de 2 horas está presente."""
        assert self.tempo_estimado.is_visible(), "A label de tempo estimado não está visível"