import allure
from playwright.sync_api import Page, expect


class CustomersListPage:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Navegar para listagem de clientes")
    def navegar_para_clientes(self):
        self.page.goto("https://admin.hom.solagora.com.br/customers")
        self.page.wait_for_load_state("networkidle")
        expect(self.page.get_by_role("table")).to_be_visible(timeout=15000)

    @allure.step("Buscar cliente por CPF: {cpf}")
    def buscar_por_cpf(self, cpf: str):
        campo_busca = self.page.get_by_placeholder("Pesquisar por...")
        campo_busca.fill(cpf)
        self.page.wait_for_timeout(1500)

    @allure.step("Verificar que badge 'AGUARDANDO' NÃO está presente para o cliente")
    def verificar_badge_ausente(self, cpf: str):
        linha = self.page.locator("tr", has_text=cpf)
        expect(linha.get_by_text("AGUARDANDO", exact=False)).not_to_be_visible(timeout=5000)

    @allure.step("Verificar que badge 'AGUARDANDO A...' está presente para o cliente")
    def verificar_badge_presente(self, cpf: str):
        linha = self.page.locator("tr", has_text=cpf)
        expect(linha.get_by_text("AGUARDANDO", exact=False)).to_be_visible(timeout=10000)

    @allure.step("Abrir menu de ações (3 pontinhos) do cliente")
    def abrir_menu_acoes(self, cpf: str):
        linha = self.page.locator("tr", has_text=cpf)
        linha.get_by_role("button").last.click()
        self.page.wait_for_timeout(500)

    @allure.step("Clicar em 'Editar' no menu de ações")
    def clicar_editar(self):
        self.page.get_by_role("menuitem", name="Editar").click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Clicar em 'Ver detalhes' no menu de ações")
    def clicar_ver_detalhes(self):
        self.page.get_by_role("menuitem", name="Ver detalhes").click()
        self.page.wait_for_load_state("networkidle")
