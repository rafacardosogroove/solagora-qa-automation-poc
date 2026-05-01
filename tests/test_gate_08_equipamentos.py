import time
import allure
from pytest_bdd import scenarios, when, then
from playwright.sync_api import Page, expect
from pages.admin.admin_page import AdminPage
from utils.hml_client import hml

scenarios('../features/admin/equipamentos.feature')


# ==============================================================================
# O MODO Admin - GATE 08 (EQUIPAMENTOS)
# ==============================================================================
@when('aciono os serviços de equipamentos e monitoração via Modo Admin')
def step_trigger_equipamentos_modo_admin(orquestrador, context_data: dict, page: Page):
    projeto_id = context_data.get('projeto_id')

    with allure.step(f"Orquestração Gate 08 (Equipamentos) - ID: {projeto_id}"):
        orquestrador.orquestrar_gate_08(projeto_id)

        # Atualiza a tela para gerar evidência
        page.reload()
        page.wait_for_load_state("networkidle")

        allure.attach(
            page.screenshot(full_page=True),
            name="Status_Pos_Servicos_Equipamentos",
            attachment_type=allure.attachment_type.PNG
        )


# ==============================================================================
# VALIDAÇÃO (ENTÃO) - LINHA DE CHEGADA!
# ==============================================================================
@then('o sistema deve exibir o status do projeto como "Dados para monitoração da usina"')
def step_validate_status_monitoracao(page: Page):
    with allure.step("Validando status FINAL: Dados para monitoração da usina"):
        status_locator = page.get_by_text("Dados para monitoração da usina", exact=False).first
        expect(status_locator).to_be_visible(timeout=30000)

        allure.attach(
            page.screenshot(full_page=True),
            name="Gate08_Sucesso_Absoluto_Monitoracao",
            attachment_type=allure.attachment_type.PNG
        )
