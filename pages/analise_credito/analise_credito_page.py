import allure
from playwright.sync_api import Page, expect


class AnaliseCreditoPage:
    def __init__(self, page: Page):
        self.page = page
        # Seletores baseados nos prints image_2f7870.png e image_2f74e8.png
        self.btn_quero_proposta = page.get_by_role("button", name="Quero criar uma proposta")
        self.btn_com_seguro = page.get_by_role("button", name="Continuar com o seguro")
        self.btn_sem_seguro = page.get_by_role("button", name="Continuar sem o seguro")

        # Campos de Informações Pessoais e Contato
        self.input_nome = page.get_by_placeholder("Nome e Sobrenome do cliente")
        self.input_email = page.get_by_placeholder("Digite o melhor email do cliente")
        self.input_celular = page.get_by_placeholder("(00) 00000-0000")
        self.input_cep = page.locator("input[name='address.postalCode']")  # Localizador comum para CEP

        # Botão final
        self.btn_enviar_analise = page.get_by_role("button", name="Enviar para análise de crédito")

    @allure.step("Clicar em iniciar proposta")
    def iniciar_proposta(self):
        self.btn_quero_proposta.click()

    @allure.step("Tratar modal de seguro: {escolha}")
    def tratar_modal_seguro(self, escolha):
        try:
            self.page.wait_for_timeout(1500)  # Pequena pausa para animação do modal
            if escolha.upper() == "COM SEGURO":
                self.btn_com_seguro.click(timeout=3000)
            else:
                self.btn_sem_seguro.click(timeout=3000)
        except Exception:
            print("Modal de seguro não interceptado.")

    @allure.step("Preencher formulário de análise: {nome}")
    def preencher_dados_cadastrais(self, nome, email, celular, cep):
        self.input_nome.fill(nome)
        self.input_email.fill(email)
        self.input_celular.fill(celular)
        self.input_cep.fill(cep)
        # Tab ou click fora para disparar a busca do CEP se necessário
        self.input_cep.press("Tab")

    @allure.step("Validar botão de envio habilitado")
    def validar_botao_envio(self):
        expect(self.btn_enviar_analise).to_be_enabled(timeout=5000)
        allure.attach(self.page.screenshot(), name="Formulario_Preenchido", attachment_type=allure.attachment_type.PNG)