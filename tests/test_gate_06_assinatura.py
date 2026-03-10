import pytest
import time
import allure
from pytest_bdd import scenarios, when, then
from playwright.sync_api import Page, expect
from pages.admin.admin_page import AdminPage

# Aponta para o caminho da sua feature do Gate 06
# (Se estiver tudo no admin.feature, aponte para lá)
scenarios('../features/admin/admin.feature')


@pytest.fixture
def context_data():
    return {}


# ==============================================================================
# PASSOS AUXILIARES (Caso não estejam em um conftest global)
# ==============================================================================
@when('capturo o ID do projeto atual pela interface')
def step_capturar_id(admin_page: AdminPage, context_data: dict):
    context_data['projeto_id'] = admin_page.capturar_id_projeto_url()


@when('atualizo a página do portal do integrador')
def step_atualizar_pagina_integrador(page: Page):
    with allure.step("Atualizando a página do portal do integrador"):
        page.reload()
        page.wait_for_load_state("networkidle")


# ==============================================================================
# O MODO DEUS - GATE 06 (FINALIZAR ASSINATURA)
# ==============================================================================
@when('aciono o serviço de finalização de assinatura via Modo Admin')
def step_trigger_assinatura_modo_admin(admin, context_data: dict, page: Page):
    projeto_id = context_data.get('projeto_id')

    with allure.step(f"Orquestração Gate 06 (Assinatura) - ID: {projeto_id}"):

        # --- ETAPA ÚNICA: FINALIZAR ASSINATURA ---
        with allure.step("Fase 1: Acionar endpoint de finalização de assinatura"):
            try:
                # O admin é a sua fixture HmlClient
                admin.finalizar_assinatura(projeto_id)
                print("✅ Assinatura finalizada via API.")
            except Exception as e:
                print(f"⚠️ Aviso ao finalizar assinatura: {e}")

            # Tempo para o worker do backend processar a mudança de status
            time.sleep(3)

        # Atualiza a tela para gerar a evidência do passo
        page.reload()
        page.wait_for_load_state("networkidle")

        # 📸 Captura Allure Intermediária
        allure.attach(
            page.screenshot(full_page=True),
            name="Status_Pos_Servico_Assinatura",
            attachment_type=allure.attachment_type.PNG
        )


# ==============================================================================
# VALIDAÇÃO (ENTÃO)
# ==============================================================================
@then('o sistema deve exibir o status do projeto como "Faturamento Autorizado"')
def step_validate_status_faturamento(page: Page, admin_page: AdminPage):
    with allure.step("Validando transição de status para 'Faturamento Autorizado'"):
        # Aguarda a tela confirmar o avanço
        # OBS: Se você já tiver mapeado "label_faturamento_autorizado" na AdminPage,
        # troque o locator direto por expect(admin_page.label_faturamento_autorizado)
        status_locator = page.locator("text=Faturamento autorizado")
        expect(status_locator).to_be_visible(timeout=20000)

        # 📸 Captura Allure Final do Gate 06
        allure.attach(
            page.screenshot(full_page=True),
            name="Gate06_Sucesso_Assinado",
            attachment_type=allure.attachment_type.PNG
        )