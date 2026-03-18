import time
import allure
from pytest_bdd import scenarios, when, then
from playwright.sync_api import Page, expect
from pages.admin.admin_page import AdminPage

# ==========================================
# CARREGAMENTO DA FEATURE
# ==========================================
scenarios('../features/admin/admin.feature')


# NOTA: Os @given e os @when genéricos (capturar ID e atualizar página)
# estão centralizados no conftest.py!

# ==============================================================================
# MODO Admin - ESTRITO AO GATE 05
# ==============================================================================



#Implementar chamada liberar telefone





#***********************************************

@when('aciono os serviços de aprovação interna, documentação e biometria via Modo Admin')
def step_trigger_modo_admin(admin, context_data: dict, page: Page):
    projeto_id = context_data.get('projeto_id')

    with allure.step(f"Orquestração Gate 05 - ID: {projeto_id}"):

        # --- 1. DOCS ---
        with allure.step("Fase 1: Aprovar Documentação"):
            admin.aprovar_documentacao(projeto_id, comentario="Aprovação de documentação via automação QA SolAgora")
            page.reload()
            page.wait_for_load_state("networkidle")
            allure.attach(page.screenshot(full_page=True), name="Status_Pos_Documentacao",
                          attachment_type=allure.attachment_type.PNG)

        # --- 2. BIOMETRIA ---
        with allure.step("Fase 2: Finalizar Biometria"):
            admin.finalizar_biometria(projeto_id)
            time.sleep(2)
            page.reload()
            page.wait_for_load_state("networkidle")
            allure.attach(page.screenshot(full_page=True), name="Status_Pos_Biometria",
                          attachment_type=allure.attachment_type.PNG)

            # --- 3. LOOP DE MESA INTERNA ---
            sucesso_mesa = False
            with allure.step("Fase 3: Mesa Interna e Emissão CCB"):
                for tentativa in range(15):
                    page.reload()
                    page.wait_for_load_state("networkidle")

                    _, sys_status, biz_status = admin._get_status_hml(projeto_id)
                    print(f"Tentativa {tentativa + 1}: Status Banco = {biz_status} ({sys_status})")

                    # Sucesso: Sai do loop
                    if sys_status in ['waiting_signatures', 'signature']:
                        sucesso_mesa = True
                        break

                    # Ação 1: Aprova na Mesa
                    elif sys_status in ['waiting_external_analysis', 'external_analysis']:
                        try:
                            admin.aprovar_projeto(projeto_id)
                        except:
                            pass

                    # Ação 2: Reforça Biometria se cair
                    elif sys_status == 'waiting_biometrics':
                        admin.finalizar_biometria(projeto_id)

                    # Ação 3 (O PULO DO GATO 🐈): Aciona os serviços de CCB e Assinatura!
                    elif sys_status == 'waiting_process_bmp':
                        print("⚙️ Status BMP detectado! Chamando serviços de emissão de CCB e Assinatura...")
                        try:
                            admin.emitir_ccb(projeto_id)
                            time.sleep(2)
                            admin.aguardar_assinatura(projeto_id)
                        except Exception as e:
                            print(f"Aviso ao tentar forçar CCB: {e}")

                    time.sleep(5)

                if not sucesso_mesa:
                    print("Aviso: Loop da mesa estourou o tempo, tentando forçar sequência...")

            # A Fase 4 antiga (fora do loop) pode até ser deletada se quiser, pois agora o loop faz o trabalho!

        # --- 4. GARANTIR EMISSÃO DE CCB E LIBERAÇÃO ---
        with allure.step("Fase 4: Emissão CCB e Liberação de Assinaturas"):
            _, sys_status, _ = admin._get_status_hml(projeto_id)
            if sys_status != 'waiting_signatures':
                try:
                    admin.emitir_ccb(projeto_id)
                    time.sleep(2)
                    admin.aguardar_assinatura(projeto_id)
                except Exception as e:
                    print(f"Fallback CCB info: {e}")

        # --- ATUALIZA A TELA PARA VER O RESULTADO FINAL DO GATE 05 ---
        page.reload()
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        allure.attach(page.screenshot(full_page=True), name="Status_Final_Gate_05",
                      attachment_type=allure.attachment_type.PNG)


# ==============================================================================
# VALIDAÇÃO (ENTÃO)
# ==============================================================================

@then('o sistema deve exibir o status do projeto como "Aguardando Assinatura"')
def step_validate_final_status(page: Page, admin_page: AdminPage):
    with allure.step("Validando se o fluxo parou no Gate 05 com sucesso"):
        expect(admin_page.label_aguardando_assinatura).to_be_visible(timeout=20000)

        allure.attach(
            page.screenshot(full_page=True),
            name="Gate05_Sucesso_Aprovado",
            attachment_type=allure.attachment_type.PNG
        )