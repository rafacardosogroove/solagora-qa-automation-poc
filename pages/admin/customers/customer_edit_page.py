import allure
from playwright.sync_api import Page, expect


class CustomerEditPage:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Limpar e preencher campo Email com: {email}")
    def limpar_e_preencher_email(self, email: str):
        campo = self.page.get_by_label("Email")
        campo.clear()
        campo.fill(email)

    @allure.step("Limpar e preencher campo Celular com: {celular}")
    def limpar_e_preencher_celular(self, celular: str):
        campo = self.page.get_by_label("Celular")
        campo.clear()
        campo.fill(celular)

    @allure.step("Clicar em 'Salvar' no formulário de edição")
    def clicar_salvar(self):
        self.page.get_by_role("button", name="Salvar").click()
        self.page.wait_for_timeout(2000)

    @allure.step("Verificar modal de confirmação de solicitação")
    def verificar_modal_confirmacao(self):
        modal_texto = self.page.get_by_text("Solicitação de alteração enviada para aprovação", exact=False)
        expect(modal_texto).to_be_visible(timeout=10000)
        allure.attach(
            self.page.screenshot(),
            name="Modal_Confirmacao",
            attachment_type=allure.attachment_type.PNG
        )

    @allure.step("Fechar modal de confirmação")
    def fechar_modal(self):
        self.page.get_by_role("button", name="Fechar").click()
        self.page.wait_for_timeout(1000)

    @allure.step("Verificar que modal de confirmação NÃO apareceu")
    def verificar_modal_nao_aparece(self):
        modal_texto = self.page.get_by_text("Solicitação de alteração enviada para aprovação", exact=False)
        expect(modal_texto).not_to_be_visible(timeout=3000)

    @allure.step("Obter mensagem de erro do campo Email")
    def obter_erro_campo_email(self) -> str:
        erro = self.page.locator("[data-testid='email-error'], [id*='email'] ~ *[class*='error'], label:has-text('Email') ~ *[class*='error']").first
        expect(erro).to_be_visible(timeout=5000)
        return erro.inner_text()

    @allure.step("Obter mensagem de erro do campo Celular")
    def obter_erro_campo_celular(self) -> str:
        erro = self.page.locator("[data-testid='celular-error'], [id*='celular'] ~ *[class*='error'], label:has-text('Celular') ~ *[class*='error']").first
        expect(erro).to_be_visible(timeout=5000)
        return erro.inner_text()

    @allure.step("Verificar que há erro de validação visível na página")
    def verificar_erro_validacao_visivel(self):
        # Mensagem de erro usa texto direto (styled-components sem classe semântica)
        erro = self.page.get_by_text("inválido", exact=False).or_(
            self.page.get_by_text("obrigatório", exact=False)
        ).first
        expect(erro).to_be_visible(timeout=5000)
        allure.attach(
            self.page.screenshot(),
            name="Erro_Validacao",
            attachment_type=allure.attachment_type.PNG
        )

    @allure.step("Clicar em 'Voltar'")
    def clicar_voltar(self):
        self.page.get_by_role("button", name="Voltar").click()
        self.page.wait_for_load_state("networkidle")
