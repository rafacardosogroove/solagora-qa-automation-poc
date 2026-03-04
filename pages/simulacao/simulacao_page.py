import re
import allure
from playwright.sync_api import Page, expect
from utils.Generators import Generators  # Importando seu gerador!


class SimulacaoPage:
    def __init__(self, page: Page):
        self.page = page

        # Elementos de Navegação
        self.link_projetos = page.get_by_role("link", name="Projetos")
        # Usando regex no botão para evitar erro com aquele ícone estranho ""
        self.btn_novo_projeto = page.get_by_role("button", name=re.compile("Criar um novo projeto", re.IGNORECASE))

        # Elementos do 'Tour' (Overlay)
        self.btn_proximo = page.get_by_role("button", name="Próximo")
        self.btn_fechar_tour = page.get_by_role("button", name="Fechar")

        # Elementos do Formulário (Seus locators perfeitos!)
        self.input_cpf = page.get_by_test_id("document-field")
        self.input_income = page.get_by_test_id("income-field")
        self.input_value = page.get_by_test_id("value-field")
        self.input_energia = page.locator("input[name=\"values.electricalEnergy\"]")
        self.input_vencimento = page.get_by_role("combobox", name="/00/0000")
        self.btn_iniciar = page.get_by_role("button", name="Iniciar Simulação")

    @allure.step("Navegar até o simulador e lidar com o Tour")
    def acessar_nova_simulacao(self):
        # O goto() sumiu porque o Macro Login já nos deixou aqui!
        self.link_projetos.click()
        self.btn_novo_projeto.click()

        try:
            # Lógica excelente de fechar o tour que você criou
            self.btn_proximo.first.wait_for(state="visible", timeout=4000)
            for _ in range(3):
                self.btn_proximo.first.click()
                self.page.wait_for_timeout(500)

            self.btn_fechar_tour.first.wait_for(state="visible", timeout=3000)
            self.btn_fechar_tour.first.click()
            self.page.wait_for_timeout(1000)
        except Exception:
            print("Tour não apareceu, seguindo fluxo normal.")

    @allure.step("Preencher dados da simulação e iniciar")
    def preencher_dados_simulacao(self, cpf, renda, valor, distribuidor, energia, dia_vencimento):
        self.input_cpf.wait_for(state="visible")

        # Inteligência: Usa gerador se pedir, senão usa o que veio do BDD
        if cpf.upper() == "GERAR":
            cpf = Generators.cpf()

        self.input_cpf.fill(cpf)
        self.input_income.fill(renda)
        self.input_value.fill(valor)

        # Sua lógica impecável do Dropdown
        self.page.locator("span").filter(has_text=re.compile(r"^Selecione$")).click()
        opcao = self.page.get_by_role("option", name=distribuidor, exact=False)

        if not opcao.is_visible():
            opcao = self.page.locator(".p-dropdown-item").get_by_text(distribuidor, exact=False)
        opcao.click()

        # Restante do formulário
        self.input_energia.fill(energia)
        self.input_vencimento.click()
        self.page.get_by_text(dia_vencimento, exact=True).click()

        # Inicia
        self.btn_iniciar.click()