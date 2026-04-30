import time
import allure


class OrquestradorBackend:
    def __init__(self, hml_client):
        self.api = hml_client

    @allure.step("Orquestrador: Aprovar Gate 05 (Documentação, Biometria e Mesa)")
    def orquestrar_gate_05(self, project_id):
        # 1. Aprovar documentação
        self.api.aprovar_documentacao(project_id, comentario="Aprovação Automática Macro QA - OK")
        time.sleep(2)

        # 2. Loop inteligente — trata cada status sequencialmente (máx 225s)
        bmp_tentativas = 0
        for tentativa in range(45):
            _, sys_status, _ = self.api._get_status_hml(project_id)
            print(f"[Gate05] tentativa={tentativa} status={sys_status}")
            if sys_status in ['waiting_signatures', 'signature']:
                break
            elif sys_status in ['waiting_external_analysis', 'external_analysis']:
                try:
                    self.api.aprovar_projeto(project_id)
                except Exception as e:
                    print(f"[Gate05] aprovar_projeto err: {e}")
            elif sys_status in ['waiting_process', 'waiting_process_bmp']:
                bmp_tentativas += 1
                if bmp_tentativas <= 5:
                    try:
                        self.api.callback_bmp(project_id, 10)
                    except Exception as e:
                        print(f"[Gate05] BMP callback err: {e}")
                elif bmp_tentativas <= 10:
                    # Fallback: CCB direto
                    try:
                        self.api.emitir_ccb(project_id)
                        time.sleep(2)
                        self.api.aguardar_assinatura(project_id)
                        print(f"[Gate05] CCB fallback OK")
                    except Exception as e:
                        print(f"[Gate05] CCB fallback err: {e}")
                else:
                    # Bypass total: BMP degradado no HML — força status via DB
                    print(f"[Gate05] 🚨 BMP degradado após 10 tentativas — bypass via DB")
                    try:
                        self.api.bypass_bmp(project_id)
                        break
                    except Exception as e:
                        print(f"[Gate05] bypass_bmp err: {e}")
            elif sys_status == 'waiting_biometrics':
                bmp_tentativas = 0  # reset ao ver novo ciclo de biometria
                try:
                    self.api.finalizar_biometria(project_id)
                except Exception as e:
                    print(f"[Gate05] biometria err: {e}")
            elif sys_status in ['ccb_issued', 'waiting_ccb']:
                try:
                    self.api.aguardar_assinatura(project_id)
                except Exception as e:
                    print(f"[Gate05] aguardar_assinatura err: {e}")
            time.sleep(5)

        # 3. CCB (se ainda não saiu do loop em waiting_signatures)
        _, final_status, _ = self.api._get_status_hml(project_id)
        if final_status not in ['waiting_signatures', 'signature']:
            try:
                self.api.emitir_ccb(project_id)
                time.sleep(2)
                self.api.aguardar_assinatura(project_id)
            except Exception as e:
                print(f"[Gate05] CCB/assinatura err: {e}")

    @allure.step("Orquestrador: Aprovar Gate 06 (Assinatura Eletrônica)")
    def orquestrar_gate_06(self, project_id):
        # Aguarda status que permite assinatura (máx 90s)
        for _ in range(18):
            _, sys_status, _ = self.api._get_status_hml(project_id)
            if sys_status in ['waiting_signatures', 'signature', 'waiting_entry_payment', 'waiting_client_confirmation']:
                break
            # Se CCB foi emitida mas não foi para aguardando assinatura, forçar
            if sys_status in ['ccb_issued', 'waiting_ccb']:
                try:
                    self.api.aguardar_assinatura(project_id)
                except Exception:
                    pass
            time.sleep(5)
        self.api.finalizar_assinatura(project_id)
        time.sleep(3)

    @allure.step("Orquestrador: Aprovar Gate 07 (Faturamento, Cessão e Callbacks)")
    def orquestrar_gate_07(self, project_id):
        _, sys_status, _ = self.api._get_status_hml(project_id)
        print(f"[Gate07] status inicial: {sys_status}")

        # Se já está liberado para pagamento, nada a fazer
        if sys_status == "proposal_released":
            print("[Gate07] Projeto já em proposal_released, pulando cessão")
        else:
            # 1. Garante estado correto para classificar_nota
            # classificar_nota requer NF já subida (waiting_billing_evaluation)
            # No macro chain pulamos UI — forçamos status via DB se necessário
            if sys_status not in ("waiting_billing_evaluation", "waiting_billing_data"):
                print(f"[Gate07] Status inesperado: {sys_status} — forçando faturamento_autorizado")
                self.api._set_status_hml(project_id, self.api.STATUS_FATURAMENTO_AUTORIZADO)
                time.sleep(2)
                sys_status = "waiting_billing_data"

            if sys_status == "waiting_billing_data":
                # Força estado de NF em análise (simula upload via UI)
                print("[Gate07] Forçando status doc_pagamento_analise (simula NF subida)")
                self.api._set_status_hml(project_id, self.api.STATUS_DOC_PAGAMENTO_ANALISE)
                time.sleep(2)

            # 2. Classifica a nota
            try:
                self.api.classificar_nota(project_id, tipo="NFV")
                print("[Gate07] classificar_nota OK")
            except Exception as e:
                print(f"[Gate07] classificar_nota falhou ({e}) — forçando proposal_released via DB")
                self.api._set_status_hml(project_id, self.api.STATUS_LIBERADO_PAGAMENTO)
                time.sleep(2)

            # 3. Aprovar cessão
            try:
                self.api.aprovar_cessao(project_id)
                print("[Gate07] aprovar_cessao OK")
            except Exception as e:
                print(f"[Gate07] aprovar_cessao err: {e} — forçando proposal_released via DB")
                self.api._set_status_hml(project_id, self.api.STATUS_LIBERADO_PAGAMENTO)
                time.sleep(2)

        # 4. Callbacks cessão (BMP) — tenta, falha silenciosa (BMP pode estar degradado)
        try:
            self.api.enviar_callbacks_cessao(project_id, intervalo=10)
            print("[Gate07] callbacks cessão OK")
        except Exception as e:
            print(f"[Gate07] callbacks cessão err (ignorado): {e}")

        time.sleep(3)

    @allure.step("Orquestrador: Aprovar Gate 08 (Equipamento Entregue e Monitoração)")
    def orquestrar_gate_08(self, project_id):
        # 1. Aguarda Doc
        self.api.equip_aguardar_doc(project_id)
        time.sleep(2)

        # 2. Cliente Confirma
        self.api.equip_confirmar_cliente(project_id)
        time.sleep(5)  # Aguarda worker RabbitMQ

        # 3. Fallback: Se o worker for lento (igual aconteceu no seu CLI), força a monitoração
        _, sys_status, _ = self.api._get_status_hml(project_id)
        if sys_status == "equipment_delivered":
            self.api.equip_forcar_monitoracao(project_id)
            time.sleep(4)