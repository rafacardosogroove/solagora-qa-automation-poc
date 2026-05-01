import allure
import os
from playwright.sync_api import Page, expect


class ModalContaEnergiaPage:
    def __init__(self, page: Page):
        self.page = page
        self.btn_abrir_modal = page.get_by_text("Conta de energia", exact=False)
        # Scoped ao dialog para evitar match em dropdowns fora do modal
        self.combo_origem = page.locator(".p-dialog div.p-dropdown").filter(has_text="Selecione")
        self.input_valor_energia = page.get_by_test_id("energy-value-field")
        self.area_upload_trigger = page.get_by_text("Selecione o arquivo")
        self.btn_confirmar = page.get_by_role("button", name="Confirmar informações")

    @allure.step("Ação Complexa: Iniciar e concluir upload de conta de energia ({origem})")
    def realizar_upload_energia(self, origem: str, arquivo: str, valor: str = "1000"):
        # Aguarda a seção de documentação carregar antes de verificar a necessidade
        self.page.wait_for_timeout(2000)

        # Verifica se o perfil do cliente dispensa o envio da conta de energia
        dispensado = self.page.get_by_text("não há necessidade", exact=False)
        if dispensado.count() > 0:
            with allure.step("Conta de energia dispensada para este perfil de cliente — etapa ignorada"):
                allure.attach(self.page.screenshot(), name="energia_dispensada",
                              attachment_type=allure.attachment_type.PNG)
            return

        with allure.step("Abrir modal e informar a Distribuidora"):
            self.btn_abrir_modal.first.wait_for(state="visible", timeout=45000)
            # Itera cada ocorrência até o modal abrir (evita clicar no heading estático)
            for idx in range(self.btn_abrir_modal.count()):
                self.btn_abrir_modal.nth(idx).scroll_into_view_if_needed()
                self.btn_abrir_modal.nth(idx).click()
                try:
                    self.combo_origem.wait_for(state="visible", timeout=3000)
                    break
                except Exception:
                    continue
            self.combo_origem.wait_for(state="visible", timeout=30000)
            self.combo_origem.click()
            self.page.wait_for_timeout(800)
            self.page.get_by_role("option", name=origem, exact=True).click()

        with allure.step("Preencher campo de Consumo/Valor para habilitar validação"):
            self.input_valor_energia.click()
            self.input_valor_energia.clear()
            self.page.keyboard.type(valor, delay=100)
            self.page.keyboard.press("Tab")

        with allure.step(f"Injetar arquivo físico no navegador: {arquivo}"):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "../../"))
            path_arquivo = os.path.join(project_root, "data", arquivo)

            # Injeta diretamente no input[type='file'] dentro do modal (sem OS file picker)
            input_file = self.page.locator(".p-dialog input[type='file']")
            if input_file.count() > 0:
                input_file.first.set_input_files(path_arquivo)
            else:
                # Fallback: usa file chooser se input não for encontrado diretamente
                with self.page.expect_file_chooser() as fc_info:
                    self.area_upload_trigger.click()
                file_chooser = fc_info.value
                file_chooser.set_files(path_arquivo)
            self.page.wait_for_timeout(3000)

        with allure.step("Aguardar processamento e confirmar envio do arquivo"):
            # Aguarda o botão estar visível E habilitado (upload deve completar antes)
            self.btn_confirmar.wait_for(state="visible", timeout=15000)
            expect(self.btn_confirmar).to_be_enabled(timeout=20000)
            allure.attach(self.page.screenshot(), name="pre_confirmar_click",
                          attachment_type=allure.attachment_type.PNG)
            self.page.wait_for_timeout(2000)
            self.btn_confirmar.click()
            # Aguarda o modal fechar ou mostrar estado de sucesso
            try:
                self.page.locator(".p-dialog-mask").wait_for(state="hidden", timeout=15000)
            except Exception:
                # Modal pode ter reaberto com mensagem de sucesso; aguarda estabilizar
                allure.attach(self.page.screenshot(), name="pos_confirmar_dialog_state",
                              attachment_type=allure.attachment_type.PNG)
                self.page.wait_for_timeout(5000)