import allure
from playwright.sync_api import Page, expect


class CustomerDetailsPage:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Rolar até a seção '4 Análise'")
    def ir_para_secao_analise(self):
        secao = self.page.get_by_text("Análise", exact=False).last
        secao.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)

    @allure.step("Verificar texto de comparação de/para no bloco Análise")
    def verificar_texto_comparacao(self, de: str, para: str):
        bloco = self.page.locator("[class*='yellow'], [class*='warning'], [style*='yellow']").or_(
            self.page.get_by_text("alterado de", exact=False)
        )
        expect(bloco).to_be_visible(timeout=10000)
        conteudo = bloco.inner_text()
        assert de in conteudo, f"Valor anterior '{de}' não encontrado no texto: {conteudo}"
        assert para in conteudo, f"Novo valor '{para}' não encontrado no texto: {conteudo}"
        allure.attach(
            self.page.screenshot(),
            name="Bloco_Analise_Comparacao",
            attachment_type=allure.attachment_type.PNG
        )

    @allure.step("Selecionar radio 'Aprovar'")
    def selecionar_aprovar(self):
        self.page.get_by_label("Aprovar").check()

    @allure.step("Selecionar radio 'Reprovar'")
    def selecionar_reprovar(self):
        self.page.get_by_label("Reprovar").check()

    @allure.step("Clicar em 'Salvar' na seção Análise")
    def clicar_salvar(self):
        self.page.get_by_role("button", name="Salvar").last.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

    @allure.step("Obter dados da última linha do Histórico de Alterações")
    def obter_ultima_linha_historico(self) -> dict:
        tabela_historico = self.page.locator("table").filter(has_text="Valor Anterior")
        ultima_linha = tabela_historico.locator("tbody tr").last
        celulas = ultima_linha.locator("td").all()
        dados = [c.inner_text().strip() for c in celulas]
        return {
            "tipo": dados[0] if len(dados) > 0 else "",
            "valor_anterior": dados[1] if len(dados) > 1 else "",
            "novo_valor": dados[2] if len(dados) > 2 else "",
            "status": dados[3] if len(dados) > 3 else "",
            "solicitado_em": dados[4] if len(dados) > 4 else "",
            "processado_em": dados[5] if len(dados) > 5 else "",
            "por": dados[6] if len(dados) > 6 else "",
        }

    @allure.step("Verificar status no histórico: {status_esperado}")
    def verificar_status_historico(self, status_esperado: str):
        historico = self.obter_ultima_linha_historico()
        assert status_esperado.lower() in historico["status"].lower(), \
            f"Status esperado '{status_esperado}' não encontrado. Status atual: '{historico['status']}'"

    @allure.step("Navegar para aba 'Lista de Projetos' do cliente")
    def navegar_aba_projetos(self):
        self.page.get_by_role("tab", name="Lista de Projetos").click()
        self.page.wait_for_timeout(1000)

    @allure.step("Obter lista de emails na aba Projetos")
    def obter_emails_projetos(self) -> list:
        self.navegar_aba_projetos()
        linhas = self.page.locator("table tbody tr").all()
        emails = []
        for linha in linhas:
            celulas = linha.locator("td").all()
            for celula in celulas:
                texto = celula.inner_text().strip()
                if "@" in texto:
                    emails.append(texto)
        return emails
