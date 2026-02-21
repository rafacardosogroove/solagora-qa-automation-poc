import allure
from playwright.sync_api import Page



class DocumentacaoPage:
    def __init__(self, page: Page):
        self.page = page

        # Títulos de Seção
        self.titulo_pagina = page.get_by_text("Documentação obrigatória")

        # Inputs de Arquivo (Upload)
        # No Playwright, focamos no input de sistema
        self.upload_doc_identificacao = page.locator("input[type='file']").first
        self.upload_comprovante_residencia = page.locator("input[type='file']").nth(1)

        # Botões Reais (Conforme o padrão visual das telas anteriores)
        self.btn_enviar_documentos = page.get_by_role("button", name="Enviar documentação")

    @allure.step("Realizar upload dos documentos")
    def realizar_upload_documentos(self, path_identidade, path_residencia):
        self.upload_doc_identificacao.set_input_files(path_identidade)
        self.upload_comprovante_residencia.set_input_files(path_residencia)
        self.btn_enviar_documentos.click()