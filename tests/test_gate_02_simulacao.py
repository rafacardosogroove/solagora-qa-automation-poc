import pytest
import allure
from pytest_bdd import scenarios, when, then, parsers
from playwright.sync_api import Page, expect

from pages.simulacao.simulacao_page import SimulacaoPage
from pages.simulacao.resultado_simulacao_page import ResultadoSimulacaoPage

# Carrega os cenários da feature
scenarios('../features/simulacao/simulacao.feature')


# Os passos @given estão centralizados no conftest.py, então não precisamos deles aqui!

@when('acesso a área de criação de um novo projeto')
def step_acessar_nova_simulacao(simulacao_page: SimulacaoPage):
    # A mágica da fixture do conftest: não precisamos mais fazer simulacao_page = SimulacaoPage(page)
    simulacao_page.acessar_nova_simulacao()


@when(parsers.parse(
    'preencho os dados com CPF "{cpf}", Renda "{renda}", Valor "{valor}", Distribuidor "{distribuidor}", Energia "{energia}" e Vencimento "{dia}"'))
def step_preencher_dados(simulacao_page: SimulacaoPage, cpf: str, renda: str, valor: str, distribuidor: str,
                         energia: str, dia: str):
    simulacao_page.preencher_dados_simulacao(cpf, renda, valor, distribuidor, energia, dia)


@then('o sistema deve avançar para a próxima etapa da simulação')
def step_validar_avanco(page: Page):
    with allure.step("Validar ausência de erros de formulário (Avanço de etapa)"):
        erros_visiveis = page.locator("text='Campo obrigatório'").count()
        assert erros_visiveis == 0, "O formulário apresentou erros de validação na tela."


@then(parsers.parse('deve exibir a tela de resultados com a mensagem "{mensagem}"'))
def step_validar_resultado_visual(page: Page, mensagem: str):
    resultado_page = ResultadoSimulacaoPage(page)

    with allure.step(f"Validar exibição da mensagem de sucesso: '{mensagem}'"):
        # REGRA DE OURO #3: A Page Object apenas mapeia o elemento. O expect fica aqui!
        elemento_mensagem = resultado_page.obter_mensagem_resultado(mensagem)
        expect(elemento_mensagem).to_be_visible(timeout=30000)  # Timeout generoso pois o cálculo pode demorar

    with allure.step("Capturar evidência da simulação concluída com sucesso"):
        allure.attach(
            page.screenshot(full_page=True),
            name="Evidencia_Simulacao_Concluida",
            attachment_type=allure.attachment_type.PNG
        )