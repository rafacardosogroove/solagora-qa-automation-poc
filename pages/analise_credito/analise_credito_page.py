import allure
import pytest  # <--- IMPORTANTE: Adicionado para o fail funcionar
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

        # Botão final
        self.btn_enviar_analise = page.get_by_role("button", name="Enviar para análise de crédito")

    @allure.step("Clicar em iniciar proposta")
    def iniciar_proposta(self):
        self.btn_quero_proposta.click()

    @allure.step("Tratar modal de seguro: {escolha}")
    def tratar_modal_seguro(self, escolha):
        try:
            self.page.wait_for_timeout(1500)
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

        # Localizador de CEP por ID com escape para o ponto
        self.page.locator("#addressInstallation\\.zipCode").fill(cep)
        self.page.locator("#addressInstallation\\.zipCode").press("Tab")
        self.page.wait_for_timeout(2000)

        # Clique no botão de enviar
        self.btn_enviar_analise.click()
        # Espera o sistema processar a análise
        self.page.wait_for_timeout(3000)

    @allure.step("Validar resultado da análise de crédito")
    def validar_resultado_analise(self):
        # Verifica se a tela de reprovação apareceu (image_160fa6.png)
        reprovado = self.page.get_by_text("Não será possível continuar com sua proposta").is_visible()

        if reprovado:
            allure.attach(self.page.screenshot(), name="Analise_Reprovada", attachment_type=allure.attachment_type.PNG)
            pytest.fail("O teste parou: Cliente reprovado na Análise de Crédito.")

        # Se não reprovou, espera o modal de sucesso (image_160842.png)
        expect(self.page.get_by_text("Seu cliente passou com sucesso")).to_be_visible(timeout=20000)

    @allure.step("Macro: Realizar fluxo completo de análise de crédito")
    def realizar_analise_credito_completa(self, nome, email, celular, cep, opcao_seguro="SEM SEGURO"):
        self.iniciar_proposta()
        self.tratar_modal_seguro(opcao_seguro)
        self.preencher_dados_cadastrais(nome, email, celular, cep)

        # Validamos se aprovou antes de tentar clicar no botão de continuar
        self.validar_resultado_analise()

        # Clica para avançar para documentação (image_160842.png)
        btn_continuar = self.page.get_by_role("button", name="Continuar para documentação")
        btn_continuar.click()