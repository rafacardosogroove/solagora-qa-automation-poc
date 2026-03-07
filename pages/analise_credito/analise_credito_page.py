import allure
import pytest
from playwright.sync_api import Page


class AnaliseCreditoPage:
    def __init__(self, page: Page):
        self.page = page
        self.btn_quero_proposta = page.get_by_role("button", name="Quero criar uma proposta")
        self.btn_com_seguro = page.get_by_role("button", name="Continuar com o seguro")
        self.btn_sem_seguro = page.get_by_role("button", name="Continuar sem o seguro")

        self.input_nome = page.get_by_placeholder("Nome e Sobrenome do cliente")
        self.input_email = page.get_by_placeholder("Digite o melhor email do cliente")
        self.input_celular = page.get_by_placeholder("(00) 00000-0000")

        self.btn_enviar_analise = page.get_by_role("button", name="Enviar para análise de crédito")
        self.btn_continuar = page.get_by_role("button", name="Continuar para documentação")

    @allure.step("Ação: Iniciar a criação da proposta no painel")
    def iniciar_proposta(self):
        self.btn_quero_proposta.click()

    @allure.step("Ação Intermediária: Tratar modal de escolha de seguro ({escolha})")
    def tratar_modal_seguro(self, escolha: str):
        try:
            if escolha.upper() == "COM SEGURO":
                self.btn_com_seguro.wait_for(state="visible", timeout=3000)
                self.btn_com_seguro.click()
            else:
                self.btn_sem_seguro.wait_for(state="visible", timeout=3000)
                self.btn_sem_seguro.click()
        except Exception:
            pass

    @allure.step("Preenchimento: Inserir dados do cliente ({nome})")
    def preencher_dados_cadastrais(self, nome: str, email: str, celular: str, cep: str):
        self.input_nome.fill(nome)
        self.input_email.fill(email)
        self.input_celular.fill(celular)

        self.page.locator("#addressInstallation\\.zipCode").fill(cep)
        self.page.locator("#addressInstallation\\.zipCode").press("Tab")
        # Dá o tempo para a API de CEP do SolAgora preencher o restante dos campos e habilitar o botão
        self.page.wait_for_timeout(2000)

        # 🚨 Removemos o 'self.btn_enviar_analise.click()' daqui!

    @allure.step("Mapear elemento: Botão de envio da análise de crédito")
    def obter_botao_envio(self):
        return self.btn_enviar_analise

    @allure.step("Macro: Realizar fluxo completo de análise de crédito e submeter")
    def realizar_analise_credito_completa(self, nome: str, email: str, celular: str, cep: str,
                                          opcao_seguro="SEM SEGURO"):
        self.iniciar_proposta()
        self.tratar_modal_seguro(opcao_seguro)
        self.preencher_dados_cadastrais(nome, email, celular, cep)

        # 🟢 O clique de envio veio para cá, onde ele realmente faz sentido (no Macro)!
        self.obter_botao_envio().click()

        self.btn_continuar.wait_for(state="visible", timeout=20000)
        self.btn_continuar.click()