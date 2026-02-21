import allure
from playwright.sync_api import Page


class DocumentacaoCompletaPage:
    def __init__(self, page: Page):
        self.page = page

        # --- SEÇÃO: DOCUMENTOS ---
        self.btn_upload_energia = page.locator("div").filter(has_text=re.compile(r"^Conta de energia$")).locator(
            "i")  # Botão '+' roxo

        # --- SEÇÃO: ENDEREÇO DE INSTALAÇÃO ---
        self.input_cep_inst = page.locator("input[name='cep_instalacao']")  # Campo '99999-999'
        self.input_logradouro_inst = page.get_by_placeholder("Rua, avenida, etc").first
        self.input_numero_inst = page.get_by_placeholder("000").first

        # --- SEÇÃO: ENDEREÇO DE COBRANÇA ---
        self.switch_mesmo_endereco = page.locator(".p-inputswitch")  # Switch 'O endereço de cobrança é o mesmo...'

        # --- SEÇÃO: INFORMAÇÕES DO CLIENTE ---
        self.input_rg = page.get_by_placeholder("00.000.000-0")  # Campo RG
        self.input_email = page.get_by_placeholder("email@email.com")
        self.input_tel_fixo = page.get_by_placeholder("(00) 0000-0000")

        # --- BOTÃO FINAL ---
        self.btn_enviar_doc = page.get_by_role("button", name="Enviar documentação")

    @allure.step("Preencher formulário completo de documentação")
    def preencher_documentacao(self, rg, cep, num):
        # Exemplo de interação com o switch de endereço
        if not self.switch_mesmo_endereco.is_checked():
            self.switch_mesmo_endereco.click()

        self.input_rg.fill(rg)
        self.input_cep_inst.fill(cep)
        self.input_numero_inst.fill(num)
        # O botão 'Enviar documentação' só habilita após todos os campos
        self.btn_enviar_doc.click()