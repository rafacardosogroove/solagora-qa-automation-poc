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

    @allure.step("Navegar até o simulador e fechar tour")
    @allure.step("Navegar até o simulador e fechar tour")
    def navegar_ate_o_simulador(self):
        self.page.goto("https://integrator.hom.solagora.com.br/")
        self.link_projetos.click()
        self.btn_novo_projeto.click()

        self.page.pause()
        try:
            # A SUA SEQUÊNCIA EXATA:
            self.overlay_path.wait_for(state="visible", timeout=5000)

            # force=True proíbe o Playwright de usar a barra de rolagem!
            self.overlay_path.click(force=True)
            self.page.wait_for_timeout(500)  # Meio segundo para o balão piscar

            self.btn_proximo.first.click(force=True)
            self.page.wait_for_timeout(500)

            self.btn_proximo.first.click(force=True)
            self.page.wait_for_timeout(500)

            self.btn_fechar_tour.first.click(force=True)

            # Pausa de ouro: 1 segundo para a tela preta sumir de vez antes de preencher o CPF
            self.page.wait_for_timeout(1000)

        except Exception as e:
            # Se o tour não aparecer hoje, o teste não quebra
            pass

    @allure.step("Preencher dados da simulação: CPF {cpf}, Distribuidor {distribuidor}")
    def preencher_dados_simulacao(self, cpf, distribuidor, dia):


        cpf_gerado = Generators.cpf();

        self.input_cpf.wait_for(state="visible")
        self.input_cpf.fill(cpf_gerado)
        self.input_income.fill("5000")
        self.input_value.fill("50000")

        # 1. Abre o dropdown
        self.page.locator("span").filter(has_text=re.compile(r"^Selecione$")).click()

        # 2. Seleciona o distribuidor na LISTA de opções (evita a ambiguidade)
        # Usamos o seletor de role "option" que é o padrão de dropdowns modernos (PrimeVue/Radix)
        opcao = self.page.get_by_role("option", name=distribuidor, exact=False)

        # Caso o componente não use roles, usamos o localizador de item da lista
        if not opcao.is_visible():
            opcao = self.page.locator(".p-dropdown-item").get_by_text(distribuidor, exact=False)

        opcao.click()

        # --- REMOVA A LINHA ABAIXO (ela estava causando o erro de texto duplicado) ---
        # self.page.get_by_text("ALDO COMPONENTES ELETRONICOS").click()

        # 3. Restante do formulário
        self.input_energia.fill("1000")
        self.input_vencimento.click()

        # Abre o campo de vencimento
        # self.input_vencimento.scroll_into_view_if_needed()
        # self.input_vencimento.click()

        # # 4. Seleção do Dia (Resolvendo a duplicidade)
        # # Procuramos o texto exato do dia, mas garantimos que ele NÃO seja o elemento desabilitado
        # # O seletor ':not(.p-disabled)' filtra apenas o dia ativo no calendário
        # dia_ativo = self.page.locator(".p-datepicker-calendar span").filter(
        #     has_text=re.compile(f"^{dia}$")
        # ).locator("xpath=self::*[not(contains(@class, 'p-disabled'))]")
        #
        # # Se o seletor acima for complexo demais, esta é a alternativa mais simples e eficaz:
        # # Pegamos todos os '29' e clicamos no que estiver visível e habilitado
        # dia_final = self.page.locator('span[data-pc-section="daylabel"]').get_by_text(dia, exact=True).filter(
        #     has_not=self.page.locator(".p-disabled")
        # )
        #
        # dia_final.first.click()

        # # Garante que o campo de vencimento está visível e clica uma única vez
        # self.input_vencimento.scroll_into_view_if_needed()
        # self.input_vencimento.click()
        #
        # # 3. Seleção do Dia (Tratando duplicidade de calendário)
        # # Procuramos o dia, mas filtramos para ignorar os que estão desabilitados (p-disabled)
        # dia_seletor = self.page.locator("span").filter(has_text=re.compile(f"^{dia}$")).filter(
        #     has_not=self.page.locator(".p-disabled")
        # ).first  # Pegamos o primeiro que estiver habilitado
        #
        # try:
        #     # Tenta clicar no elemento habilitado
        #     dia_seletor.wait_for(state="visible", timeout=5000)
        #     dia_seletor.click()
        # except:
        #     # Backup caso o seletor acima falhe: clica no que não tiver o atributo aria-disabled
        #     self.page.locator(f'span:has-text("{dia}"):not([aria-disabled="true"])').first.click()

        # 4. Iniciar

        self.input_vencimento.click()
        self.page.get_by_text(dia, exact=True).click()


        self.btn_iniciar.click()