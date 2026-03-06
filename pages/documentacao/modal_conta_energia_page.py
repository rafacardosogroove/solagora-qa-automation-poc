import allure
from playwright.sync_api import Page


class ModalContaEnergiaPage:
    def __init__(self, page: Page):
        self.page = page
        # Seletores baseados na image_15f47e.png
        self.combo_origem = page.locator("div.select-input__container")
        self.input_file = page.locator("input[type='file']")
        self.btn_confirmar = page.get_by_role("button", name="Confirmar informações")


#Ajustar trecho
    @allure.step("Modal: Upload de conta de energia")
    def realizar_upload_energia(self, origem, arquivo):
        # 1. Seleciona Local ou Remoto no combo customizado
        self.combo_origem.click()
        self.page.get_by_text(origem, exact=True).click()

        # 2. Upload do arquivo (Playwright injeta no input hidden)
        # O arquivo deve estar em: data/test_files/
        self.input_file.set_input_files(f"data/{arquivo}")
        # 3. Confirma para fechar o modal
        self.btn_confirmar.click()