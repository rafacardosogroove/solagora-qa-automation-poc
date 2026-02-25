import re
import allure
from playwright.sync_api import Page
from utils.Generators import Generators


class SimuladorPage:
    def __init__(self, page: Page):
        self.page = page

        # Elementos de Navegação
        self.link_projetos = page.get_by_role("link", name="Projetos")
        self.btn_novo_projeto = page.get_by_role("button", name=" Criar um novo projeto")

        # Elementos do 'Tour' (Overlay)
        self.overlay_path = page.locator(".driver-overlay > path")
        self.btn_proximo = page.get_by_role("button", name="Próximo")
        self.btn_fechar_tour = page.get_by_role("button", name="Fechar")

        # Elementos do Formulário
        self.input_cpf = page.get_by_test_id("document-field")
        self.input_income = page.get_by_test_id("income-field")
        self.input_value = page.get_by_test_id("value-field")
        self.input_energia = page.locator("input[name=\"values.electricalEnergy\"]")
        self.input_vencimento = page.get_by_role("combobox", name="/00/0000")
        self.btn_iniciar = page.get_by_role("button", name="Iniciar Simulação")

    @allure.step("Navegar até o simulador e lidar com o Tour")
    def navegar_ate_o_simulador(self):
        self.page.goto("https://integrator.hom.solagora.com.br/")
        self.link_projetos.click()
        self.btn_novo_projeto.click()

        try:
            # Espera até 5 segundos para o botão 'Próximo' do tour aparecer
            self.btn_proximo.first.wait_for(state="visible", timeout=5000)

            # Clique 1
            self.btn_proximo.first.click()
            self.page.wait_for_timeout(500)

            # Clique 2
            self.btn_proximo.first.click()
            self.page.wait_for_timeout(500)

            # Clique 3
            self.btn_proximo.first.click()
            self.page.wait_for_timeout(500)

            # Espera o botão 'Fechar' aparecer e clica nele
            self.btn_fechar_tour.first.wait_for(state="visible", timeout=5000)
            self.btn_fechar_tour.first.click()

            # Pausa de ouro para o balão e a tela escura sumirem antes de preencher o CPF
            self.page.wait_for_timeout(1000)

        except Exception as e:
            # Se der erro de timeout, significa que o tour não apareceu na tela.
            # Imprimimos no console e o script segue normalmente.
            print("Tour não apareceu, seguindo fluxo normal.")

    @allure.step("Preencher dados da simulação: CPF {cpf}, Distribuidor {distribuidor}")
    def preencher_dados_simulacao(self, cpf, distribuidor, dia):

        cpf_gerado = Generators.cpf()

        self.input_cpf.wait_for(state="visible")
        self.input_cpf.fill(cpf_gerado)
        self.input_income.fill("5000")
        self.input_value.fill("50000")

        # 1. Abre o dropdown de distribuidor
        self.page.locator("span").filter(has_text=re.compile(r"^Selecione$")).click()

        # 2. Seleciona o distribuidor na LISTA de opções
        opcao = self.page.get_by_role("option", name=distribuidor, exact=False)

        # Caso o componente não use roles, usamos o localizador genérico de item da lista
        if not opcao.is_visible():
            opcao = self.page.locator(".p-dropdown-item").get_by_text(distribuidor, exact=False)

        opcao.click()

        # 3. Restante do formulário (Energia)
        self.input_energia.fill("1000")

        # 4. Seleção do Vencimento
        self.input_vencimento.click()
        self.page.get_by_text(dia, exact=True).click()

        # 5. Iniciar Simulação
        self.btn_iniciar.click()