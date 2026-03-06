import allure
import os  # Necessário para localizar o arquivo na raiz do projeto
from playwright.sync_api import Page, expect


class ModalContaEnergiaPage:
    def __init__(self, page: Page):
        self.page = page

        # 1. Acionador do Modal
        self.btn_abrir_modal = page.get_by_text("Conta de energia", exact=True)

        # 2. Elementos internos do Modal
        self.combo_origem = page.locator("div.p-dropdown").filter(has_text="Selecione")
        self.input_valor_energia = page.get_by_test_id("energy-value-field")
        self.area_upload_trigger = page.get_by_text("Selecione o arquivo")
        self.btn_confirmar = page.get_by_role("button", name="Confirmar informações")

    @allure.step("Modal: Realizar fluxo completo de upload de conta")
    def realizar_upload_energia(self, origem, arquivo, valor="1000"):
        # Passo 1: Abre o modal
        self.btn_abrir_modal.click()
        self.page.wait_for_timeout(800)

        # Passo 2: Seleciona a Origem
        self.combo_origem.click()
        self.page.get_by_role("option", name=origem, exact=True).click()

        # Passo 3: Preenche o Valor Gasto (Garante habilitação do botão)
        self.input_valor_energia.click()
        self.input_valor_energia.clear()
        self.page.keyboard.type(valor, delay=100)
        self.page.keyboard.press("Tab")

        # Passo 4: Upload do arquivo (Correção de Caminho)
        # Pegamos o caminho absoluto para evitar o FileNotFoundError
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Sobe da pasta 'pages/documentacao' para a raiz 'solagora-qa-automation-poc'
        project_root = os.path.abspath(os.path.join(current_dir, "../../"))
        path_arquivo = os.path.join(project_root, "data", arquivo)

        with self.page.expect_file_chooser() as fc_info:
            self.area_upload_trigger.click()

        file_chooser = fc_info.value
        file_chooser.set_files(path_arquivo)

        try:
            # Esperamos até 15 segundos para dar uma margem de segurança sobre os 5s reais
            expect(self.btn_confirmar).to_be_enabled(timeout=15000)

            self.page.wait_for_timeout(5000)
            self.btn_confirmar.click()
        except AssertionError:
            # Caso o botão não habilite, tiramos um print para o Allure entender o motivo
            allure.attach(self.page.screenshot(), name="Erro_Botao_Confirmar_Desabilitado",
                          attachment_type=allure.attachment_type.PNG)
            raise