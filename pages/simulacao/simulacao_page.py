import re
import allure
from playwright.sync_api import Page, expect
from utils.Generators import Generators

class SimulacaoPage:
    def __init__(self, page: Page):
        self.page = page
        self.link_projetos = page.get_by_role("link", name="Projetos")
        self.btn_novo_projeto = page.get_by_role("button", name=re.compile("Criar um novo projeto", re.IGNORECASE))
        self.btn_proximo = page.get_by_role("button", name="Próximo")
        self.btn_fechar_tour = page.get_by_role("button", name="Fechar")
        self.input_cpf = page.get_by_test_id("document-field")
        self.input_income = page.get_by_test_id("income-field")
        self.input_value = page.get_by_test_id("value-field")
        self.input_energia = page.locator("input[name=\"values.electricalEnergy\"]")
        self.input_vencimento = page.get_by_role("combobox", name="/00/0000")
        self.btn_iniciar = page.get_by_role("button", name="Iniciar Simulação")
        self.btn_quero_continuar = page.get_by_role("button", name="Quero continuar")

    @allure.step("Navegar até o simulador e lidar com o Tour")
    def acessar_nova_simulacao(self):
        self.link_projetos.click()
        self.btn_novo_projeto.click()
        try:
            self.btn_proximo.first.wait_for(state="visible", timeout=4000)
            for _ in range(2):
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
        if cpf.upper() == "GERAR":
            cpf = Generators.cpf()
        self.input_cpf.fill(cpf)
        self.input_income.fill(renda)
        self.input_value.fill(valor)
        self.page.locator("span").filter(has_text=re.compile(r"^Selecione$")).click()
        opcao = self.page.get_by_role("option", name=distribuidor, exact=False)
        if not opcao.is_visible():
            opcao = self.page.locator(".p-dropdown-item").get_by_text(distribuidor, exact=False)
        opcao.click()
        self.input_energia.fill(energia)
        self.input_vencimento.click()
        self.selecionar_data_vencimento_disponivel(dia_vencimento)
        self.btn_iniciar.click()
        self.tratar_modal_entrada_se_visivel()

    @allure.step("Selecionar data de vencimento disponível a partir do dia {dia_base}")
    def selecionar_data_vencimento_disponivel(self, dia_base: str):
        dia_atual = int(dia_base)
        max_tentativas = 31
        while dia_atual <= max_tentativas:
            seletor_dia = self.page.get_by_text(str(dia_atual), exact=True)
            try:
                seletor_dia.click(timeout=2000)
                print(f"Sucesso: Data {dia_atual} selecionada.")
                return
            except Exception:
                print(f"Dia {dia_atual} desabilitado. Tentando o próximo...")
                dia_atual += 1
        if dia_atual > max_tentativas:
            raise Exception("Não foi possível encontrar uma data disponível.")

    @allure.step("Lidar com modal de entrada necessária se aparecer")
    def tratar_modal_entrada_se_visivel(self):
        try:
            self.btn_quero_continuar.wait_for(state="visible", timeout=5000)
            self.btn_quero_continuar.click()
        except Exception:
            print("Modal de entrada não apareceu, seguindo fluxo.")