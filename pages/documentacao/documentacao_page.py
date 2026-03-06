import allure
from playwright.sync_api import Page, expect

class DocumentacaoPage:
    def __init__(self, page: Page):
        self.page = page
        # MANTIVE SEUS SELETORES ORIGINAIS AQUI:
        self.input_numero = page.locator("#addressInstallation\\.number")


        self.input_complemento = page.locator("#addressInstallation\\.complement")  # Mantive o seu NAME
        self.toggle_mesmo_endereco = page.locator("input[name='billingAddressInstallation.canUseAddressInstallation']")

        self.input_rg = page.locator("#clientInfo\\.rg")
        self.input_celular_1 = page.locator("#contact\\.secondaryPhone") # Mantive o seu NAME
        self.input_celular_2 = page.locator("contact\\.landlinePhone") # Mantive o seu NAME
        self.input_fixo = page.locator("input[name='customer.landlinePhone']") # Mantive o seu NAME

        self.btn_enviar = page.get_by_role("button", name="Enviar documentação")

    @allure.step("Preencher endereço")
    def preencher_endereco(self, numero, complemento):
        self.input_numero.fill(numero)
        self.input_complemento.fill(complemento)

    @allure.step("Informar documento de identidade RG: {rg}")
    def informar_rg(self, rg: str):
        self.input_rg.fill(rg)

    @allure.step("Preencher contatos")
    def preencher_contatos(self, email, c1, c2, fixo):
        #self.input_email.fill(email)
        self.input_celular_1.fill(c1)
      #  self.input_celular_2.fill(c2)
      # self.input_fixo.fill(fixo)


        # validar Aguardando avaliação da proposta assert ou expected verificar

    def validar_botao_ativo(self):
        expect(self.btn_enviar).to_be_enabled(timeout=10000)
        self.btn_enviar.click()
        self.btn_enviar.click()


    @allure.step("Definir se o endereço de cobrança é igual ao de instalação: {escolha}")
    def definir_cobranca_igual(self, escolha: str):
        # O toggle geralmente vem desativado por padrão.
        # Clicamos apenas se a escolha for "Sim"
        if escolha.upper() == "SIM":
            # Usando o seletor que você já validou como funcional
            self.toggle_mesmo_endereco.click()
            # Pequena pausa para o sistema processar a cópia dos dados entre os campos
            self.page.wait_for_timeout(500)

