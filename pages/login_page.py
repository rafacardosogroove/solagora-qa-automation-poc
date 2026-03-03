import allure
from playwright.sync_api import Page, expect

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        # Usando get_by_label para maior estabilidade
        self.input_auth = page.get_by_label("CPF/CNPJ ou e-mail")
        self.input_senha = page.get_by_label("Senha")
        self.btn_entrar = page.get_by_role("button", name="Entrar")

    @allure.step("Realizar login com usuário: {usuario}")
    def realizar_login_duplo(self, usuario, senha):
        self.input_auth.fill(usuario)
        self.input_senha.press_sequentially(senha, delay=50)

        # Workaround: O frontend (Solagora) possui um debounce de ~300ms na validação
        # do formulário. Sem essa pausa e o blur, o clique ocorre antes da liberação.
        self.page.wait_for_timeout(1000)
        self.input_senha.blur()

        self.btn_entrar.click(force=True)

    @allure.step("Validar exibição da mensagem de erro: '{mensagem}'")
    def validar_mensagem_erro(self, mensagem):
        # Mapeia dinamicamente o elemento que contém o texto exato do erro
        alerta_erro = self.page.get_by_text(mensagem, exact=True)
        # Faz a asserção garantindo que ele apareceu na tela
        expect(alerta_erro).to_be_visible(timeout=5000)

        @allure.step("Executar fluxo macro de login com sucesso")
        def realizar_login_completo_e_aguardar_dashboard(self, usuario, senha):
            # 1. Acessa a página
            self.page.goto("https://integrator.hom.solagora.com.br/")

            # 2. Chama o método que já faz a magia do preenchimento e clique!
            self.realizar_login_duplo(usuario, senha)

            # 3. Garante que a dashboard carregou para não quebrar o próximo teste
            expect(self.page).to_have_url(re.compile(".*dashboard.*"), timeout=15000)