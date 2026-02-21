import allure
from playwright.sync_api import Page


class AcompanhamentoPropostaPage:
    def __init__(self, page: Page):
        self.page = page

        # --- STATUS DA PROPOSTA --- teste envio de email testando disparo automatico de email workflow git
        # Status laranja: "Aguardando avaliação da proposta"
        self.label_status = page.locator("text=Status: Aguardando avaliação da proposta")

        # --- LISTA DE ETAPAS (Checklist) ---
        self.etapa_acesso_app = page.locator("text=Acesso ao aplicativo Sol Agora")
        self.etapa_analise_docs = page.locator("text=Análise dos documentos e comprovantes enviados")
        self.etapa_biometria = page.locator("text=Confirmação de biometria")
        self.etapa_contrato = page.locator("text=Geração do contrato")
        self.etapa_assinatura = page.locator("text=Assinatura do contrato")
        self.etapa_pagamento = page.locator("text=Pagamento da entrada")

        # --- BOTÕES DE REENVIO (Desabilitados/Cinzas no print) ---
        self.btn_reenviar_biometria = page.get_by_role("button", name="Reenviar link da biometria")
        self.btn_reenviar_contrato = page.get_by_role("button", name="Reenviar contrato para assinatura")
        self.btn_reenviar_pagamento = page.get_by_role("button", name="Reenviar link de pagamento")

        # --- TEMPO ESTIMADO ---
        self.msg_tempo_conclusao = page.locator("text=Tempo estimado para conclusão: 5 dias úteis")  #

    @allure.step("Validar que a proposta entrou em fase de avaliação")
    def validar_status_aguardando(self):
        self.label_status.wait_for(state="visible")
        self.msg_tempo_conclusao.wait_for(state="visible")