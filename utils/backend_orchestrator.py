import time
import allure


class OrquestradorBackend:
    def __init__(self, hml_client):
        self.api = hml_client

    @allure.step("Orquestrador: Aprovar Gate 05 (Documentação, Biometria e Mesa)")
    def orquestrar_gate_05(self, project_id):
        # 1. Aprovar Doc
        self.api.aprovar_documentacao(project_id, comentario="Aprovação Automática Macro QA")

        # 2. Biometria
        self.api.finalizar_biometria(project_id)

        # 3. Mesa Interna (Loop inteligente)
        for tentativa in range(15):
            _, sys_status, _ = self.api._get_status_hml(project_id)
            if sys_status in ['waiting_signatures', 'signature']:
                break
            elif sys_status in ['waiting_external_analysis', 'external_analysis']:
                try:
                    self.api.aprovar_projeto(project_id)
                except:
                    pass
            elif sys_status == 'waiting_biometrics':
                self.api.finalizar_biometria(project_id)
            time.sleep(4)

        # 4. CCB
        try:
            self.api.emitir_ccb(project_id)
            time.sleep(2)
            self.api.aguardar_assinatura(project_id)
        except:
            pass

    @allure.step("Orquestrador: Aprovar Gate 06 (Assinatura Eletrônica)")
    def orquestrar_gate_06(self, project_id):
        self.api.finalizar_assinatura(project_id)
        time.sleep(3)

    @allure.step("Orquestrador: Aprovar Gate 07 (Faturamento, Cessão e Callbacks)")
    def orquestrar_gate_07(self, project_id):
        # 1. Classifica a nota (Igual seu log)
        self.api.classificar_nota(project_id, tipo="NFV")

        # 2. Aprovar cessão (com try/except pois no seu log deu 400 mas seguiu)
        try:
            self.api.aprovar_cessao(project_id)
        except Exception as e:
            print(f"Aviso na aprovação da cessão: {e}")

        # 3. Callbacks 10 e 9 (Igual seu log com intervalo)
        self.api.enviar_callbacks_cessao(project_id, intervalo=10)
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