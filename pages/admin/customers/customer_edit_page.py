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
        self.page.wait_for_timeout(3000)

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
        allure.attach(
            self.page.screenshot(),
            name="Erro_Validacao_Estado",
            attachment_type=allure.attachment_type.PNG
        )
        # Detectar qualquer mensagem de erro via JS (independente do texto exato)
        erro_encontrado = self.page.evaluate("""() => {
            const keywords = ['inválido', 'invalido', 'obrigatório', 'obrigatorio',
                              'formato', 'dígito', 'digito', 'mínimo', 'minimo',
                              'required', 'invalid', 'error', 'erro'];
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) continue;
                const txt = (el.textContent || '').trim().toLowerCase();
                const hasChild = el.children.length > 0;
                if (!hasChild && txt && keywords.some(k => txt.includes(k))) {
                    return txt.substring(0, 100);
                }
            }
            return null;
        }""")
        assert erro_encontrado, "Nenhuma mensagem de erro de validação encontrada na página"
        print(f"\n[DEBUG validacao] Erro encontrado: '{erro_encontrado}'")
        allure.attach(
            erro_encontrado,
            name="Erro_Validacao_Texto",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.step("Clicar em 'Voltar'")
    def clicar_voltar(self):
        # Fechar qualquer modal/overlay aberto antes de voltar
        overlay = self.page.locator("[data-pc-section='mask'], .p-dialog-mask")
        if overlay.count() > 0 and overlay.first.is_visible():
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        self.page.get_by_role("button", name="Voltar").click()
        self.page.wait_for_load_state("networkidle")
