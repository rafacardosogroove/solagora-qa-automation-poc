import allure
from playwright.sync_api import Page, expect

class DocumentacaoPage:
    def __init__(self, page: Page):
        self.page = page
        # MANTIVE SEUS SELETORES ORIGINAIS AQUI:
        self.input_numero = page.locator("#addressInstallation\\.number")


        self.input_complemento = page.locator("#addressInstallation\\.complement")  # Mantive o seu NAME
        self.toggle_mesmo_endereco = page.locator("span.switch-input__slider")

        self.input_rg = page.locator("input[name='customer.rg']") # Mantive o seu NAME
        self.input_email = page.locator("input[name='customer.email']") # Mantive o seu NAME
        self.input_celular_1 = page.locator("input[name='customer.primaryPhone']") # Mantive o seu NAME
        self.input_celular_2 = page.locator("input[name='customer.secondaryPhone']") # Mantive o seu NAME
        self.input_fixo = page.locator("input[name='customer.landlinePhone']") # Mantive o seu NAME

        self.btn_enviar = page.get_by_role("button", name="Enviar documentação")

    @allure.step("Preencher endereço")
    def preencher_endereco(self, numero, complemento):
        self.input_numero.fill(numero)
        self.input_complemento.fill(complemento)

    @allure.step("Preencher contatos")
    def preencher_contatos(self, email, c1, c2, fixo):
        self.input_email.fill(email)
        self.input_celular_1.fill(c1)
        self.input_celular_2.fill(c2)
        self.input_fixo.fill(fixo)

    def validar_botao_ativo(self):
        expect(self.btn_enviar).to_be_enabled(timeout=10000)

    @allure.step("Definir se o endereço de cobrança é igual ao de instalação: {escolha}")
    def definir_cobranca_igual(self, escolha: str):
        # O toggle geralmente vem desativado por padrão.
        # Clicamos apenas se a escolha for "Sim"
        if escolha.upper() == "SIM":
            # Usando o seletor que você já validou como funcional
            self.toggle_mesmo_endereco.click()
            # Pequena pausa para o sistema processar a cópia dos dados entre os campos
            self.page.wait_for_timeout(500)