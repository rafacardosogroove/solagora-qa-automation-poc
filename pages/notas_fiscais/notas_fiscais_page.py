from playwright.sync_api import Page, expect
import allure

class NotasFiscaisPage:
    def __init__(self, page: Page):
        self.page = page

        # --- Modal Anterior ---
        self.titulo_modal = page.get_by_text("Tudo certo até agora!")
        self.btn_continuar = page.get_by_role("button", name="Continuar para notas fiscais")

        # --- Tela de Notas Fiscais ---
        # Distribuidor
        self.drop_distribuidor = page.locator("text=Distribuidor atualizado").locator("..")

        # Uploads Equipamento e Serviço
        self.upload_nf_equipamento = page.locator("div").filter(has_text="Nota fiscal do equipamento").locator("input[type='file']")
        self.upload_nf_servico = page.locator("div").filter(has_text="Nota fiscal do serviço").locator("input[type='file']")

        # Campos Equipamento
        self.input_num_nf_equip = page.get_by_label("Número da nota fiscal do equipamento")
        self.input_valor_nf_equip = page.get_by_label("Valor da nota do equipamento")

        # Campos Serviço
        self.input_num_nf_servico = page.get_by_label("Número da nota fiscal do serviço")
        self.input_valor_nf_servico = page.get_by_label("Valor da nota do serviço")

        # ---> NOVO: Documentos Adicionais <---
        self.upload_carta_correcao = page.locator("div").filter(has_text="Carta de correção").locator("input[type='file']")
        self.upload_comprovante_pagto = page.locator("div").filter(has_text="Comprovante de pagamento").locator("input[type='file']")

        # ---> NOVO: Botões "Adicionar Outro" <---
        self.btn_add_inversor = page.locator("text=Dados dos inversores").locator("..").get_by_role("button", name="Adicionar outro")
        self.btn_add_modulo = page.locator("text=Dados dos módulos").locator("..").get_by_role("button", name="Adicionar outro")

        # Botão Final
        self.btn_enviar_informacoes = page.get_by_role("button", name="Enviar notas e informações")

    # --- MÉTODOS DE AÇÃO ---

    def validar_modal_sucesso(self):
        with allure.step("Validando modal de sucesso da documentação"):
            expect(self.titulo_modal).to_be_visible(timeout=15000)

    def clicar_continuar_para_notas(self):
        with allure.step("Clicando em 'Continuar para notas fiscais'"):
            self.btn_continuar.click()

    def preencher_nf_equipamento(self, numero: str, valor: str, caminho_arquivo: str):
        with allure.step(f"Preenchendo NF do Equipamento: {numero} - R$ {valor}"):
            self.upload_nf_equipamento.set_input_files(caminho_arquivo)
            self.input_num_nf_equip.fill(numero)
            self.input_valor_nf_equip.fill(valor)

    def preencher_nf_servico(self, numero: str, valor: str, caminho_arquivo: str):
        with allure.step(f"Preenchendo NF do Serviço: {numero} - R$ {valor}"):
            self.upload_nf_servico.set_input_files(caminho_arquivo)
            self.input_num_nf_servico.fill(numero)
            self.input_valor_nf_servico.fill(valor)

    # ---> NOVO MÉTODO: Upload de documentos extras <---
    def fazer_upload_documentos_adicionais(self, caminho_carta: str = None, caminho_comprovante: str = None):
        with allure.step("Fazendo upload de documentos adicionais (Opcionais)"):
            if caminho_carta:
                self.upload_carta_correcao.set_input_files(caminho_carta)
            if caminho_comprovante:
                self.upload_comprovante_pagto.set_input_files(caminho_comprovante)

    # ---> MÉTODO ATUALIZADO: Aceita 'index' para preencher múltiplos inversores <---
    def preencher_dados_inversor(self, fabricante: str, quantidade: str, index: int = 0):
        with allure.step(f"Preenchendo Inversor [{index}]: {fabricante} (Qtd: {quantidade})"):
            drop = self.page.get_by_label("Fabricante do inversor").nth(index)
            input_qtd = self.page.get_by_label("Quantidade").nth(index)
            drop.select_option(label=fabricante)
            input_qtd.fill(quantidade)

    # ---> MÉTODO ATUALIZADO: Aceita 'index' para preencher múltiplos módulos <---
    def preencher_dados_modulo(self, fabricante: str, quantidade: str, index: int = 0):
        with allure.step(f"Preenchendo Módulo [{index}]: {fabricante} (Qtd: {quantidade})"):
            drop = self.page.get_by_label("Fabricante do módulo").nth(index)
            input_qtd = self.page.locator("text=Dados dos módulos").locator("..").get_by_label("Quantidade").nth(index)
            drop.select_option(label=fabricante)
            input_qtd.fill(quantidade)

    # ---> NOVO MÉTODO: Clica para adicionar outro módulo/inversor <---
    def clicar_adicionar_novo_modulo(self):
        with allure.step("Clicando em 'Adicionar outro' módulo"):
            self.btn_add_modulo.click()

    def enviar_notas_fiscais(self):
        with allure.step("Enviando todas as notas fiscais e equipamentos"):
            self.btn_enviar_informacoes.click()