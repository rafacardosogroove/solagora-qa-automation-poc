import allure
import os
import time
from playwright.sync_api import Page, expect


class FaturamentoPage:
    def __init__(self, page: Page):
        self.page = page

        # --- Listagem (Conforme seu HTML capturado) ---
        self.input_pesquisa = page.locator("#otherFilters")
        # Deixamos os locators abaixo como base, mas usaremos filtros dinâmicos nos métodos
        self.btn_acoes_generic = page.locator(".pi-cog")
        self.opt_continuar_generic = page.get_by_role("menuitem", name="Continuar")

        # --- Modal de Sucesso Documentação (Print 5e4193) ---
        self.btn_prosseguir_notas = page.get_by_role("button", name="Continuar para notas fiscais")

        # --- Formulário de Notas (Prints 5e411a / 5e3e56) ---
        self.input_num_nf_equip = page.get_by_label("Número da nota fiscal de equipamento")
        self.input_valor_nf_equip = page.get_by_label("Valor da nota fiscal do equipamento")
        self.upload_nf_equip = page.locator("div").filter(has_text="Nota fiscal do equipamento").locator(
            "input[type='file']")

        self.input_num_nf_serv = page.get_by_label("Número da nota fiscal de serviço")
        self.input_valor_nf_serv = page.get_by_label("Valor da nota fiscal de serviço")
        self.upload_nf_serv = page.locator("div").filter(has_text="Nota fiscal do serviço").locator(
            "input[type='file']")

        # --- Equipamentos (Print 5e3df7) ---
        self.combo_inversor = page.get_by_test_id("inversor-[0]-field")
        self.input_qtd_inversor = page.locator("input[name='inverter_quantity']")
        self.combo_modulo = page.get_by_test_id("module-[0]-field")
        self.input_qtd_modulo = page.locator("input[name='module_quantity']")
        self.btn_enviar_final = page.get_by_role("button", name="Enviar notas e informações")

    @allure.step("Localizar projeto na listagem pelo CPF: {termo}")
    def buscar_projeto_por_filtro(self, termo: str):
        # Aguarda o componente React-Select estar pronto
        self.input_pesquisa.wait_for(state="visible", timeout=10000)
        self.input_pesquisa.click()

        # Limpa e digita simulando teclado para garantir que o React perceba a mudança
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        self.input_pesquisa.press_sequentially(termo, delay=50)
        self.page.keyboard.press("Enter")

        # Espera a lista filtrar
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)

    @allure.step("Acionar engrenagem e clicar em Continuar para o CPF: {cpf}")
    def clicar_continuar_projeto(self, cpf: str):
        # Como o filtro de CPF já deixou apenas 1 resultado,
        # pegamos a primeira engrenagem (.pi-cog) que aparecer na tabela.

        with allure.step("Localizando a engrenagem de ações na listagem"):
            # Usamos o .first para garantir que ele pegue o único botão disponível
            engrenagem = self.page.locator(".pi-cog").first

            # Espera o botão estar pronto (visível e habilitado)
            engrenagem.wait_for(state="visible", timeout=10000)

            # Tira um print da tela filtrada para o Allure antes de clicar
            allure.attach(self.page.screenshot(), name="01_Lista_Filtrada_Antes_Clique")

            engrenagem.click(force=True)

        with allure.step("Clicando na opção 'Continuar' no menu flutuante"):
            # O menu do PrimeVue costuma aparecer fora da tabela, no final do <body>
            opcao_continuar = self.page.get_by_role("menuitem", name="Continuar")

            # Aguarda o menu abrir e clica
            opcao_continuar.wait_for(state="visible", timeout=5000)
            opcao_continuar.click()

            # Sincroniza a transição para o modal amarelo
            self.page.wait_for_load_state("networkidle")

    @allure.step("Prosseguir no Modal para a tela de Notas")
    def prosseguir_para_notas(self):
        self.btn_prosseguir_notas.click()
        self.page.wait_for_load_state("networkidle")

    @allure.step("Preencher Nota Fiscal de Equipamento: {numero}")
    def preencher_nf_equipamento(self, numero: str, valor: str, arquivo: str):
        # 1. Ajuste de Caminho (Sobe 2 níveis da pasta 'pages/notas_fiscais' para a raiz)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        path_arquivo = os.path.join(base_path, "data", arquivo)

        with allure.step(f"Verificando e realizando upload do arquivo: {path_arquivo}"):
            if not os.path.exists(path_arquivo):
                raise FileNotFoundError(
                    f"Arquivo não encontrado! Verifique se '{arquivo}' está na pasta /data na raiz.")

            # Usando o ID escapado para o input hidden do PrimeVue/React
            # O seletor '#equipmentInvoice\\.invoiceFile' foca direto no input de arquivo
            self.page.locator("#equipmentInvoice\\.invoiceFile").set_input_files(path_arquivo)
            self.page.wait_for_timeout(2000)  # Pequena pausa para o sistema processar o upload

        with allure.step(f"Preenchendo Número: {numero} e Valor: {valor}"):
            # 2. Preenchimento do Número (Limpando antes para garantir)
            # Usamos o seletor por nome que mapeamos antes
            input_numero = self.page.locator("input[name='equipmentInvoice.invoiceNumber']")
            input_numero.click()
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            input_numero.press_sequentially(numero, delay=50)

            # 3. Preenchimento do Valor
            input_valor = self.page.locator("input[name='equipmentInvoice.invoiceValue']")
            input_valor.click()
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            input_valor.press_sequentially(valor, delay=50)
            self.page.keyboard.press("Tab")

        allure.attach(self.page.screenshot(full_page=True), name="NF_Equipamento_Preenchida",
                      attachment_type=allure.attachment_type.PNG)

    @allure.step("Preencher Nota Fiscal de Serviço: {numero}")
    def preencher_nf_servico(self, numero: str, valor: str, arquivo: str):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        path_arquivo = os.path.join(base_path, "data", arquivo)

        with allure.step(f"Upload do arquivo de NF Serviço: {path_arquivo}"):
            if not os.path.exists(path_arquivo):
                raise FileNotFoundError(f"Arquivo não encontrado: {path_arquivo}")
            self.page.locator("#serviceInvoice\\.invoiceFile").set_input_files(path_arquivo)
            self.page.wait_for_timeout(2000)

        with allure.step(f"Preenchendo Número: {numero} e Valor: {valor}"):
            input_numero = self.page.locator("input[name='serviceInvoice.invoiceNumber']")
            input_numero.click()
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            input_numero.press_sequentially(numero, delay=50)

            input_valor = self.page.locator("input[name='serviceInvoice.invoiceValue']")
            input_valor.click()
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            input_valor.press_sequentially(valor, delay=50)
            self.page.keyboard.press("Tab")

        allure.attach(self.page.screenshot(full_page=True), name="NF_Servico_Preenchida",
                      attachment_type=allure.attachment_type.PNG)

    @allure.step("Selecionar fabricante do inversor: {fabricante} (qtd: {quantidade})")
    def selecionar_fabricante_inversor(self, fabricante: str, quantidade: str):
        self.combo_inversor.wait_for(state="visible", timeout=10000)
        self.combo_inversor.click()
        self.page.wait_for_timeout(800)
        # Debug: listar opções disponíveis
        opcoes_disponiveis = self.page.get_by_role("option").all()
        nomes = [o.text_content() for o in opcoes_disponiveis]
        print(f"[DEBUG] Opções inversor: {nomes}")
        self.page.get_by_role("option", name=fabricante, exact=False).first.wait_for(state="visible", timeout=15000)
        self.page.get_by_role("option", name=fabricante, exact=False).first.click()
        self.input_qtd_inversor.wait_for(state="visible", timeout=10000)
        self.input_qtd_inversor.fill(quantidade)

    @allure.step("Selecionar fabricante do módulo: {fabricante} (qtd: {quantidade})")
    def selecionar_fabricante_modulo(self, fabricante: str, quantidade: str):
        self.combo_modulo.wait_for(state="visible", timeout=10000)
        self.combo_modulo.click()
        self.page.wait_for_timeout(800)
        opcoes_disponiveis = self.page.get_by_role("option").all()
        nomes = [o.text_content() for o in opcoes_disponiveis]
        print(f"[DEBUG] Opções módulo: {nomes}")
        self.page.get_by_role("option", name=fabricante, exact=False).first.wait_for(state="visible", timeout=15000)
        self.page.get_by_role("option", name=fabricante, exact=False).first.click()
        self.input_qtd_modulo.fill(quantidade)

    @allure.step("Finalizar: Enviar notas e informações de equipamentos")
    def finalizar_envio_notas(self):
        self.btn_enviar_final.wait_for(state="visible", timeout=10000)
        self.btn_enviar_final.scroll_into_view_if_needed()
        self.btn_enviar_final.click()
        self.page.wait_for_load_state("networkidle", timeout=30000)