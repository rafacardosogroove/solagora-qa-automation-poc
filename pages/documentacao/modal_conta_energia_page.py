import allure
import os
from playwright.sync_api import Page


class ModalContaEnergiaPage:
    def __init__(self, page: Page):
        self.page = page
        self.btn_abrir_modal = page.get_by_text("Conta de energia", exact=True)
        self.combo_origem = page.locator("div.p-dropdown").filter(has_text="Selecione")
        self.input_valor_energia = page.get_by_test_id("energy-value-field")
        self.area_upload_trigger = page.get_by_text("Selecione o arquivo")
        self.btn_confirmar = page.get_by_role("button", name="Confirmar informações")

    @allure.step("Ação Complexa: Iniciar e concluir upload de conta de energia ({origem})")
    def realizar_upload_energia(self, origem: str, arquivo: str, valor: str = "1000"):
        with allure.step("Abrir modal e informar a Distribuidora"):
            self.btn_abrir_modal.click()
            self.page.wait_for_timeout(800)
            self.combo_origem.click()
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

            with self.page.expect_file_chooser() as fc_info:
                self.area_upload_trigger.click()

            file_chooser = fc_info.value
            file_chooser.set_files(path_arquivo)

        with allure.step("Aguardar processamento e confirmar envio do arquivo"):
            # Substituí o expect por um wait_for natural do POM
            self.btn_confirmar.wait_for(state="visible", timeout=15000)
            self.page.wait_for_timeout(5000)
            self.btn_confirmar.click()