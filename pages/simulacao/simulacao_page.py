import re
import allure
from playwright.sync_api import Page
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

    @allure.step("Navegação: Acessar a tela de nova simulação de projeto")
    def acessar_nova_simulacao(self):
        with allure.step("Acessar menu de 'Projetos' e iniciar novo projeto"):
            self.link_projetos.click()
            self.btn_novo_projeto.click()

        with allure.step("Lidar com o Tour (Overlay) de boas-vindas, caso seja exibido"):
            try:
                self.btn_proximo.first.wait_for(state="visible", timeout=4000)
                for _ in range(2):
                    self.btn_proximo.first.click()
                    self.page.wait_for_timeout(500)
                self.btn_fechar_tour.first.wait_for(state="visible", timeout=3000)
                self.btn_fechar_tour.first.click()
                self.page.wait_for_timeout(1000)
            except Exception:
                # Silencia propositalmente. Se não aparecer, o fluxo segue normalmente.
                pass

    @allure.step("Preenchimento: Inserir dados do cliente e iniciar simulação")
    def preencher_dados_simulacao(self, cpf: str, renda: str, valor: str, distribuidor: str, energia: str,
                                  dia_vencimento: str):
        with allure.step("Aguardar carregamento inicial do formulário"):
            self.input_cpf.wait_for(state="visible")

        with allure.step("Preencher o CPF do cliente"):
            if cpf.upper() == "GERAR":
                cpf = Generators.cpf()
            self.input_cpf.fill(cpf)

        with allure.step("Preencher os dados financeiros (Renda e Valor do Projeto)"):
            self.input_income.fill(renda)
            self.input_value.fill(valor)

        with allure.step(f"Abrir lista e selecionar o Distribuidor: '{distribuidor}'"):
            self.page.locator("span").filter(has_text=re.compile(r"^Selecione$")).click()
            opcao = self.page.get_by_role("option", name=distribuidor, exact=False)

            if not opcao.is_visible():
                opcao = self.page.locator(".p-dropdown-item").get_by_text(distribuidor, exact=False)
            opcao.click()

        with allure.step("Preencher consumo de Energia Elétrica (kWh)"):
            self.input_energia.fill(energia)

        with allure.step(f"Definir a data de vencimento (Dia base: {dia_vencimento})"):
            self.input_vencimento.click()
            self.selecionar_data_vencimento_disponivel(dia_vencimento)

        with allure.step("Acionar botão 'Iniciar Simulação'"):
            self.btn_iniciar.click()

        # O modal de entrada tem seu próprio step principal
        self.tratar_modal_entrada_se_visivel()

    @allure.step("Ação Oculta: Buscar e selecionar o próximo dia útil disponível no calendário")
    def selecionar_data_vencimento_disponivel(self, dia_base: str):
        dia_atual = int(dia_base)
        max_tentativas = 31

        while dia_atual <= max_tentativas:
            seletor_dia = self.page.get_by_text(str(dia_atual), exact=True)
            try:
                # Se o dia estiver desabilitado (disabled), o clique falha e cai no except
                seletor_dia.click(timeout=2000)
                return  # Sai da função assim que consegue clicar
            except Exception:
                dia_atual += 1

        if dia_atual > max_tentativas:
            raise Exception(
                f"Falha Crítica: Não foi possível encontrar uma data disponível a partir do dia {dia_base}.")

    @allure.step("Ação de Contorno: Aceitar modal de 'Entrada Necessária' (Regra de Risco)")
    def tratar_modal_entrada_se_visivel(self):
        try:
            self.btn_quero_continuar.wait_for(state="visible", timeout=5000)

            with allure.step("Modal detectado: Confirmando a continuidade da simulação"):
                self.btn_quero_continuar.click()
        except Exception:
            # Fluxo feliz, o modal não barrou a simulação
            pass