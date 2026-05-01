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
            # BMP é lento — 30 tentativas × 5s = 150s máx
            sucesso_mesa = False
            bmp_tentativas = 0
            with allure.step("Fase 3: Mesa Interna e Emissão CCB"):
                for tentativa in range(30):
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
                        bmp_tentativas = 0
                        admin.finalizar_biometria(projeto_id)

                    # Ação 3: BMP — callback primeiro (emitir_ccb endpoint está 404 no HML)
                    elif sys_status in ['waiting_process_bmp', 'waiting_process']:
                        bmp_tentativas += 1
                        print(f"⚙️ Status BMP detectado (tentativa BMP {bmp_tentativas})...")
                        if bmp_tentativas <= 5:
                            # Tenta callback normal (aguarda BMP popular o Code)
                            try:
                                admin.callback_bmp(projeto_id, 10)
                            except Exception as e:
                                print(f"Aviso callback_bmp: {e}")
                        elif bmp_tentativas <= 10:
                            # Fallback: CCB direto
                            try:
                                admin.emitir_ccb(projeto_id)
                                time.sleep(2)
                                admin.aguardar_assinatura(projeto_id)
                            except Exception as e:
                                print(f"Aviso fallback CCB: {e}")
                        else:
                            # Bypass total: BMP degradado no HML — força status via DB
                            print("🚨 BMP degradado após 10 tentativas — bypass via DB")
                            try:
                                admin.bypass_bmp(projeto_id)
                                sucesso_mesa = True
                                break
                            except Exception as e:
                                print(f"Aviso bypass_bmp: {e}")

                    # Ação 4: CCB emitida — só precisar chamar aguardar_assinatura
                    elif sys_status in ['ccb_issued', 'waiting_ccb']:
                        try:
                            admin.aguardar_assinatura(projeto_id)
                        except Exception as e:
                            print(f"Aviso aguardar_assinatura: {e}")

                    time.sleep(5)

                if not sucesso_mesa:
                    print("Aviso: Loop da mesa estourou o tempo, tentando forçar sequência...")

        # --- 4. GARANTIR ASSINATURA (fallback se saiu do loop sem sucesso) ---
        with allure.step("Fase 4: Garantir Liberação de Assinaturas"):
            _, sys_status, _ = admin._get_status_hml(projeto_id)
            if sys_status not in ['waiting_signatures', 'signature']:
                try:
                    admin.aguardar_assinatura(projeto_id)
                except Exception as e:
                    print(f"Fallback aguardar_assinatura: {e}")

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