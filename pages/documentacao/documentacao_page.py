import allure
from playwright.sync_api import Page


class DocumentacaoPage:
    def __init__(self, page: Page):
        self.page = page
        self.input_numero = page.locator("#addressInstallation\\.number")
        self.input_complemento = page.locator("#addressInstallation\\.complement")
        self.toggle_mesmo_endereco = page.locator("input[name='billingAddressInstallation.canUseAddressInstallation']")
        self.input_rg = page.locator("#clientInfo\\.rg")
        self.input_celular_1 = page.locator("#contact\\.secondaryPhone")

        # Mapeamento base para os métodos
        self.btn_enviar = page.get_by_role("button", name="Enviar documentação")

    @allure.step("Preenchimento: Endereço do cliente (Nº {numero})")
    def preencher_endereco(self, numero: str, complemento: str):
        self.input_numero.fill(numero)
        self.input_complemento.fill(complemento)

    @allure.step("Preenchimento: Documento de identidade RG ({rg})")
    def informar_rg(self, rg: str):
        self.input_rg.fill(rg)

    @allure.step("Preenchimento: Telefones de Contato Secundários")
    def preencher_contatos(self, email: str, c1: str, c2: str, fixo: str):
        # Apenas os campos que você desativou o comentário
        self.input_celular_1.fill(c1)

    @allure.step("Mapear elemento: Botão final para Enviar Documentação")
    def obter_botao_enviar(self):
        # O método que o teste estava procurando desesperadamente!
        return self.btn_enviar

    @allure.step("Ação: Submeter a documentação para o Backoffice")
    def acionar_envio_documentacao(self):
        # O método utilizado no fluxo Macro do conftest.py
        self.btn_enviar.click()

    @allure.step("Ação: Configurar endereço de cobrança: Igual à instalação? -> {escolha}")
    def definir_cobranca_igual(self, escolha: str):
        if escolha.upper() == "SIM":
            self.toggle_mesmo_endereco.click()
            self.page.wait_for_timeout(500)