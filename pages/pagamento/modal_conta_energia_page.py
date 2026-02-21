import allure
from playwright.sync_api import Page


class ModalContaEnergiaPage:
    def __init__(self, page: Page):
        self.page = page

        # --- UPLOAD ---
        # O input de arquivo real costuma estar escondido atrás do botão roxo '+'
        self.input_file = page.locator("input[type='file']")
        self.btn_selecionar_arquivo = page.get_by_text("Selecione o arquivo")

        # --- DROPDOWNS (Padrão PrimeVue) ---
        # Local, remoto ou compartilhado?
        self.combo_localidade = page.locator("div").filter(has_text="Local, remoto ou compartilhado?").locator("span")
        # Tipo de consumo
        self.combo_tipo_consumo = page.locator("div").filter(has_text="Tipo de consumo").locator("span")

        # --- INPUTS ---
        self.input_valor_gasto = page.get_by_placeholder("R$ 0,00")

        # --- SWITCHES (Regras de Negócio) ---
        self.switch_debitos = page.locator("div").filter(has_text="Existem débitos nesta conta de energia").locator(
            ".p-inputswitch")
        self.switch_titularidade = page.locator("div").filter(has_text="Meu cliente não é o titular da conta").locator(
            ".p-inputswitch")

        # --- BOTÕES ---
        self.btn_confirmar = page.get_by_role("button", name="Confirmar informações")
        self.btn_fechar = page.get_by_role("button", name="Fechar")

    @allure.step("Preencher detalhes da conta de energia")
    def preencher_detalhes_conta(self, arquivo_path, valor, localidade, consumo):
        # 1. Upload do arquivo
        self.input_file.set_input_files(arquivo_path)

        # 2. Seleção de Dropdowns (Clica para abrir, clica na opção)
        self.combo_localidade.click()
        self.page.get_by_role("option", name=localidade).click()

        self.input_valor_gasto.fill(valor)

        self.combo_tipo_consumo.click()
        self.page.get_by_role("option", name=consumo).click()

    @allure.step("Confirmar informações da conta")
    def confirmar(self):
        # O botão Confirmar só habilita após o upload e campos obrigatórios
        self.btn_confirmar.click()