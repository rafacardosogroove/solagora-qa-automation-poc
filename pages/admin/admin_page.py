import allure
from playwright.sync_api import Page

class AdminPage:
    def __init__(self, page: Page):
        self.page = page
        self.label_aguardando_assinatura = page.get_by_text("Aguardando Assinatura", exact=False)

    @allure.step("Capturar o ID do projeto através da URL")
    def capturar_id_projeto_url(self) -> str:
        import re
        url_atual = self.page.url
        # Ajustado para capturar o UUID após 'proposal/'
        match = re.search(r"proposal/([^/]+)", url_atual)
        if match:
            projeto_id = match.group(1)
            allure.attach(f"ID Capturado: {projeto_id}", name="Debug_ID")
            return projeto_id
        raise Exception(f"ID não encontrado na URL: {url_atual}")

    @allure.step("Recarregar o portal para atualizar status")
    def atualizar_pagina(self):
        self.page.reload()
        # Aguarda a rede ficar ociosa para garantir que o novo status carregou
        self.page.wait_for_load_state("networkidle")