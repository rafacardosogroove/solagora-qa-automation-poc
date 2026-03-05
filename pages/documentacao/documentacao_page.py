import allure
from playwright.sync_api import Page, expect


class DocumentacaoPage:
    def __init__(self, page: Page):
        self.page = page
        # Endereço (image_15edb7.png)
        self.input_numero = page.locator("input[name='address.number']")
        self.input_complemento = page.locator("input[name='address.complement']")
        self.toggle_mesmo_endereco = page.locator("span.switch-input__slider")

        # Dados e Contato (image_15ed97.png e image_15ed61.png)
        self.input_rg = page.locator("input[name='customer.rg']")
        self.input_email = page.locator("input[name='customer.email']")
        self.input_celular_1 = page.locator("input[name='customer.primaryPhone']")
        self.input_celular_2 = page.locator("input[name='customer.secondaryPhone']")
        self.input_fixo = page.locator("input[name='customer.landlinePhone']")

        self.btn_enviar = page.get_by_role("button", name="Enviar documentação")

    @allure.step("Preencher formulário de documentação")
    def preencher_dados_finais(self, numero, complemento, igual, rg, email, cel1, cel2, fixo):
        self.input_numero.fill(numero)
        self.input_complemento.fill(complemento)

        # Se for 'Sim', ativa o toggle para copiar endereço de instalação para cobrança
        if igual.upper() == "SIM":
            self.toggle_mesmo_endereco.click()

        self.input_rg.fill(rg)
        self.input_email.fill(email)
        self.input_celular_1.fill(cel1)
        self.input_celular_2.fill(cel2)
        self.input_fixo.fill(fixo)

    def validar_botao_ativo(self):
        expect(self.btn_enviar).to_be_enabled(timeout=10000)