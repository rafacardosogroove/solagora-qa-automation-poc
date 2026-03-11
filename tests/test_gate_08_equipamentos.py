import pytest
import time
import allure
from pytest_bdd import scenarios, when, then
from playwright.sync_api import Page, expect
from pages.admin.admin_page import AdminPage

# Aponta para o caminho da sua feature do Gate 08
scenarios('../features/admin/admin.feature')


@pytest.fixture
def context_data():
    return {}


# ==============================================================================
# PASSOS AUXILIARES (Reaproveitados)
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
# O MODO Admin - GATE 08 (EQUIPAMENTOS)
# ==============================================================================
@when('aciono os serviços de equipamentos e monitoração via Modo Admin')
def step_trigger_equipamentos_modo_admin(admin, context_data: dict, page: Page):
    projeto_id = context_data.get('projeto_id')

    with allure.step(f"Orquestração Gate 08 (Equipamentos) - ID: {projeto_id}"):

        with allure.step("Fase 1: Confirmar documentação de equipamento e entrega do cliente"):
            try:
                # 1. Aguardar Doc
                admin.equip_aguardar_doc(projeto_id)
                time.sleep(2)

                # 2. Confirmar Cliente (Dispara a criação de equipamentos no RabbitMQ)
                admin.equip_confirmar_cliente(projeto_id)
                print("✅ Equipamento confirmado pelo cliente.")
            except Exception as e:
                print(f"⚠️ Aviso na confirmação de entrega: {e}")

            # Aguarda o worker RabbitMQ processar (crucial nessa etapa)
            print("⏳ Aguardando worker RabbitMQ (5s)...")
            time.sleep(5)

        with allure.step("Fase 2: Forçar avanço para Monitoração da Usina"):
            try:
                # 3. Forçar Monitoração (Fallback caso o projeto pare em Equipamento Entregue)
                admin.equip_forcar_monitoracao(projeto_id)
                print("✅ Status forçado para Monitoração da Usina.")
            except Exception as e:
                print(f"ℹ️ Fluxo automático já avançou para monitoração: {e}")

            time.sleep(3)

        # Atualiza a tela para gerar a evidência da etapa
        page.reload()
        page.wait_for_load_state("networkidle")

        # 📸 Captura Allure
        allure.attach(
            page.screenshot(full_page=True),
            name="Status_Pos_Servicos_Equipamentos",
            attachment_type=allure.attachment_type.PNG
        )


# ==============================================================================
# VALIDAÇÃO (ENTÃO) - LINHA DE CHEGADA!
# ==============================================================================
@then('o sistema deve exibir o status do projeto como "Dados para monitoração da usina"')
def step_validate_status_monitoracao(page: Page, admin_page: AdminPage):
    with allure.step("Validando o status FINAL do projeto: Dados para monitoração da usina"):
        # Substitua pelo locator correto mapeado na AdminPage amanhã
        status_locator = page.locator("text=Dados para monitoração da usina")
        expect(status_locator).to_be_visible(timeout=20000)

        # 📸 A FOTO DO PÓDIO! Captura Allure Final End-to-End
        allure.attach(
            page.screenshot(full_page=True),
            name="Gate08_Sucesso_Absoluto_Monitoracao",
            attachment_type=allure.attachment_type.PNG
        )