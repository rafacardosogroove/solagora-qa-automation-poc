import pytest
import time
import allure
from pytest_bdd import scenarios, when, then
from playwright.sync_api import Page, expect
from pages.admin.admin_page import AdminPage

# Aponta para o caminho da sua feature do Gate 07
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
# INTERAÇÃO DE UI - PREENCHER AMANHÃ
# ==============================================================================
@when('realizo o upload da nota fiscal de venda pela interface')
def step_upload_nota_fiscal(page: Page, admin_page: AdminPage):
    with allure.step("Upload da Nota Fiscal via UI"):
        # TODO: Amanhã você vai criar esses métodos na AdminPage!
        # Exemplo do que faremos:
        # admin_page.clicar_aba_notas_fiscais()
        # admin_page.fazer_upload_arquivo_nota("caminho/do/arquivo/nf.pdf")
        # admin_page.preencher_dados_nota_fiscal(numero="12345", valor="50000")
        # admin_page.clicar_salvar_nota()

        print("Aguardando implementação da UI para upload da nota fiscal...")
        time.sleep(2)  # Placeholder

        # 📸 Evidência do upload na tela
        allure.attach(
            page.screenshot(full_page=True),
            name="UI_Upload_Nota_Fiscal",
            attachment_type=allure.attachment_type.PNG
        )


# ==============================================================================
# O MODO DEUS - GATE 07 (CESSÃO E CALLBACKS)
# ==============================================================================
@when('aciono os serviços de faturamento, cessão e callbacks via Modo Deus')
def step_trigger_faturamento_modo_deus(admin, context_data: dict, page: Page):
    projeto_id = context_data.get('projeto_id')

    with allure.step(f"Orquestração Gate 07 (Faturamento) - ID: {projeto_id}"):

        # --- ETAPA 1: FLUXO DE CESSÃO ---
        with allure.step("Fase 1: Classificar Nota e Aprovar Cessão"):
            try:
                # O método fluxo_cessao já faz a classificação (NFV) e a aprovação no seu hml_client
                resultado_cessao = admin.fluxo_cessao(projeto_id, tipo_nota="NFV")
                print(f"✅ Resultado da cessão: {resultado_cessao}")
            except Exception as e:
                print(f"⚠️ Aviso na aprovação da cessão: {e}")

            time.sleep(3)

        # --- ETAPA 2: CALLBACKS DO BMP (9 E 10) ---
        with allure.step("Fase 2: Enviar Callbacks do BMP"):
            try:
                # Dispara os callbacks 10 (Cessão Iniciada) e 9 (Cessão Finalizada)
                admin.enviar_callbacks_cessao(projeto_id, intervalo=5)
                print("✅ Callbacks BMP enviados com sucesso.")
            except Exception as e:
                print(f"⚠️ Aviso no envio dos callbacks BMP: {e}")

            time.sleep(3)

        # Atualiza a tela para gerar a evidência intermediária
        page.reload()
        page.wait_for_load_state("networkidle")

        # 📸 Captura Allure Intermediária
        allure.attach(
            page.screenshot(full_page=True),
            name="Status_Pos_Servicos_Cessao",
            attachment_type=allure.attachment_type.PNG
        )


# ==============================================================================
# VALIDAÇÃO (ENTÃO)
# ==============================================================================
@then('o sistema deve exibir o status do projeto como "Cessão de pagamento finalizada"')
def step_validate_status_faturamento(page: Page, admin_page: AdminPage):
    with allure.step("Validando transição de status para Faturamento/Cessão finalizada"):
        # O status final baseia-se no log que você me mandou ("Cessão de pagamento finalizada").
        # Substitua pelo locator correto mapeado na AdminPage amanhã.
        status_locator = page.locator("text=Cessão de pagamento finalizada")
        expect(status_locator).to_be_visible(timeout=20000)

        # 📸 Captura Allure Final do Gate 07
        allure.attach(
            page.screenshot(full_page=True),
            name="Gate07_Sucesso_Faturamento",
            attachment_type=allure.attachment_type.PNG
        )