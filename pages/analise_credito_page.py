import allure
from playwright.sync_api import Page
from utils.Generators import Generators


class AnaliseCreditoPage:
    def __init__(self, page: Page):
        self.page = page

        # Seção: Informações Pessoais tests disparo
        self.input_nome = page.get_by_placeholder("Nome e Sobrenome do cliente")
        self.input_cpf_readonly = page.locator("input[name='cpf']")  # Geralmente vem preenchido

        # Seção: Informações de Contato
        self.input_email = page.get_by_placeholder("Digite o melhor email do cliente")
        self.input_celular = page.get_by_placeholder("(00) 00000-0000")

        # Seção: Endereço de Instalação
        self.input_cep = page.get_by_placeholder("00000-000")

        # Botão de Ação
        self.btn_enviar_analise = page.get_by_role("button", name="Enviar para análise de crédito")

    @allure.step("Preencher formulário completo de análise de crédito")
    def preencher_formulario_cliente(self, nome, email, celular, cep):
        self.input_nome.fill(nome)
        self.input_email.fill(email)
        self.input_celular.fill(celular)
        self.input_cep.fill(cep)

        # Opcional: clicar fora para disparar busca de CEP se necessário
        self.page.keyboard.press("Tab")

    @allure.step("Submeter análise de crédito")
    def enviar_para_analise(self):
        self.btn_enviar_analise.wait_for(state="visible")
        self.btn_enviar_analise.click()