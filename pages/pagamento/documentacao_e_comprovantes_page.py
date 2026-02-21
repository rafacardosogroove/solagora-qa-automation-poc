import allure
from playwright.sync_api import Page


class DocumentacaoEComprovantesPage:
    def __init__(self, page: Page):
        self.page = page

        # --- LISTA DE DOCUMENTOS ENVIADOS ---
        # Note que cada arquivo enviado vira uma linha com um ícone de lixeira ao lado
        self.lista_documentos = page.locator(".p-fileupload-row")
        self.doc_energia = page.get_by_text("contaDeEnergia.pdf")
        self.doc_pagamento = page.get_by_text("comprovantePgto.pdf")
        self.doc_rg = page.get_by_text("rg.pdf")

        # --- MAPA DE LOCALIZAÇÃO ---
        # Apareceu um mapa visual no meio da tela de instalação
        self.mapa_localizacao = page.locator("#map")

        # --- FORMULÁRIO DE ENDEREÇO (Atenção aos valores já preenchidos) ---
        self.input_cep = page.locator("input[name='cep']")
        self.input_numero = page.locator("input[name='numero']")
        self.input_complemento = page.locator("input[name='complemento']")

        # --- INFORMAÇÕES DO CLIENTE (Campos que parecem Read-Only) ---
        self.input_nome_readonly = page.get_by_label("Nome completo do cliente")  # Galileu Galilei
        self.input_rg = page.locator("input[name='rg']")  # 99.999.999-9

        # --- BOTÃO FINAL ---
        # Agora ele está Amarelo/Habilitado
        self.btn_enviar_documentacao = page.get_by_role("button", name="Enviar documentação")

    @allure.step("Validar se todos os documentos foram anexados com sucesso")
    def validar_documentos_anexados(self):
        # Garante que os 3 arquivos aparecem na lista antes de prosseguir
        assert self.doc_energia.is_visible()
        assert self.doc_pagamento.is_visible()
        assert self.doc_rg.is_visible()

    @allure.step("Finalizar a etapa de documentação")
    def finalizar_etapa(self):
        # O botão só deve ser clicado quando estiver habilitado
        self.btn_enviar_documentacao.wait_for(state="visible")
        self.btn_enviar_documentacao.click()