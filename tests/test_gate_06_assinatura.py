import allure
import time
from pytest_bdd import scenarios, when, then
from playwright.sync_api import Page, expect

# ==========================================
# CARREGAMENTO DA FEATURE
# ==========================================
scenarios('../features/admin/assinatura.feature')

# NOTA: O Contexto e os passos globais de atualizar a página
# estão centralizados e sendo injetados automaticamente pelo conftest.py!

# ==============================================================================
# O MODO ADMIN - GATE 06 (FINALIZAR ASSINATURA)
# ==============================================================================

@when('aciono o serviço de finalização de assinatura via Modo Admin')
def step_finalizar_assinatura_admin(admin, context_data: dict, page: Page):
    projeto_id = context_data.get('projeto_id')

    with allure.step(f"Finalizando Assinatura - Gate 06 - ID: {projeto_id}"):
        # 📸 Print inicial do Gate 06
        page.reload()
        page.wait_for_load_state("networkidle")
        allure.attach(page.screenshot(full_page=True), name="01_Inicio_Gate_06", attachment_type=allure.attachment_type.PNG)

        try:
            admin.finalizar_assinatura(projeto_id)
        except Exception as e:
            print(f"Tentando novamente finalizar assinatura após 3s... Erro: {e}")
            time.sleep(3)
            admin.finalizar_assinatura(projeto_id)

        # Espera o processamento para o print de sucesso ser real
        time.sleep(4)
        page.reload()
        page.wait_for_load_state("networkidle")
        allure.attach(page.screenshot(full_page=True), name="02_Status_Pos_Assinatura_Sucesso", attachment_type=allure.attachment_type.PNG)


# ==============================================================================
# VALIDAÇÃO (ENTÃO)
# ==============================================================================

@then('o sistema deve exibir o status do projeto como "Faturamento Autorizado"')
def step_validate_status_faturamento(page: Page):
    with allure.step("Validando transição final para 'Faturamento Autorizado'"):
        status_locator = page.locator("text=Faturamento autorizado")
        expect(status_locator).to_be_visible(timeout=20000)

        allure.attach(page.screenshot(full_page=True), name="03_Gate06_Concluido", attachment_type=allure.attachment_type.PNG)