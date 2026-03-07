import allure
from playwright.sync_api import Page


class ResultadoSimulacaoPage:
    def __init__(self, page: Page):
        self.page = page
        # Textos e botões mapeados
        self.msg_sucesso = page.get_by_text("Boas notícias! As condições foram aceitas")
        self.btn_criar_proposta = page.get_by_role("button", name="Quero criar uma proposta")

    @allure.step("Mapeamento: Obter elemento contendo a mensagem '{mensagem}'")
    def obter_mensagem_resultado(self, mensagem: str):
        """
        Apenas retorna o locator da mensagem dinâmica.
        A asserção (expect) e a evidência visual (print) ficam na camada de testes (steps).
        """
        return self.page.get_by_text(mensagem)

    @allure.step("Ação: Iniciar a criação da proposta de financiamento")
    def acionar_criacao_proposta(self):
        """
        Clica no botão para avançar de etapa no funil.
        """
        # Uma boa prática em botões que dependem de transição de tela é aguardá-los
        self.btn_criar_proposta.wait_for(state="visible", timeout=15000)
        self.btn_criar_proposta.click()