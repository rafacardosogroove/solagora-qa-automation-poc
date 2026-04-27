import allure
import pytest
from playwright.sync_api import Page, expect


class AnaliseCreditoPage:
    def __init__(self, page: Page):
        self.page = page

        # --- Elementos Mapeados ---

        # O seletor de ouro capturado via codegen (A div que simula o checkbox)
        self.cbx_termos = page.locator(".min-w-\\[1\\.5rem\\]")
        self.btn_quero_proposta = page.get_by_role("button", name="Quero criar uma proposta")

        self.btn_com_seguro = page.get_by_role("button", name="Continuar com o seguro")
        self.btn_sem_seguro = page.get_by_role("button", name="Continuar sem o seguro")

        self.input_nome = page.get_by_placeholder("Nome e Sobrenome do cliente")
        self.input_email = page.get_by_placeholder("Digite o melhor email do cliente")
        self.input_celular = page.get_by_placeholder("(00) 00000-0000")

        self.btn_enviar_analise = page.get_by_role("button", name="Enviar para análise de crédito")
        self.btn_continuar = page.get_by_role("button", name="Continuar para documentação")

    @allure.step("Ação: Aceitar termos de uso e privacidade (se exibido)")
    def aceitar_termos(self):
        try:
            self.cbx_termos.wait_for(state="visible", timeout=5000)
            self.cbx_termos.scroll_into_view_if_needed()
            self.cbx_termos.click()
            self.page.wait_for_timeout(500)
        except Exception:
            # Checkbox removido da aplicação ou não exibido neste fluxo
            pass

    @allure.step("Ação: Iniciar a criação da proposta no painel")
    def iniciar_proposta(self):
        # Garante que o botão habilitou após o aceite dos termos
        expect(self.btn_quero_proposta).to_be_enabled(timeout=5000)
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
            # Se o modal não aparecer (regra de negócio ou cache), o teste segue
            print(f"Modal de seguro '{escolha}' não disparou, seguindo fluxo.")

    @allure.step("Preenchimento: Inserir dados do cliente ({nome})")
    def preencher_dados_cadastrais(self, nome: str, email: str, celular: str, cep: str):
        self.input_nome.fill(nome)
        self.input_email.fill(email)
        self.input_celular.fill(celular)

        self.page.locator("#addressInstallation\\.zipCode").fill(cep)
        self.page.locator("#addressInstallation\\.zipCode").press("Tab")

        # Tempo para a API de CEP carregar os campos de endereço
        self.page.wait_for_timeout(2000)

    @allure.step("Mapear elemento: Botão de envio da análise de crédito")
    def obter_botao_envio(self):
        return self.btn_enviar_analise

    @allure.step("Macro: Realizar fluxo completo de análise de crédito e submeter")
    def realizar_analise_credito_completa(self, nome: str, email: str, celular: str, cep: str,
                                          opcao_seguro="SEM SEGURO"):
        # 👇 Esta orquestração garante que o conftest.py (Macros E2E) continue funcionando! 👇

        # 1. Fluxo inicial
        self.aceitar_termos()
        self.iniciar_proposta()

        # 2. Preenchimento de dados
        self.tratar_modal_seguro(opcao_seguro)
        self.preencher_dados_cadastrais(nome, email, celular, cep)

        # 3. Submissão final
        self.obter_botao_envio().click()

        # 4. Aguarda a transição para a tela de documentação
        expect(self.btn_continuar).to_be_visible(timeout=20000)
        self.btn_continuar.click()
        self.page.wait_for_load_state("networkidle", timeout=15000)