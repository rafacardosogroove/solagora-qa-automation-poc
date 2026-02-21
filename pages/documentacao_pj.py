import allure
import re
from playwright.sync_api import Page


class DocumentacaoPJPage:
    def __init__(self, page: Page):
        self.page = page

        # --- SEÇÃO: DOCUMENTOS E COMPROVANTES (PJ) ---
        # Agora são 4 tipos de documentos com botões '+' individuais
        self.btn_add_conta_energia = page.locator("div").filter(has_text=re.compile(r"^Conta de energia$")).locator(
            "button")
        self.btn_add_contrato_social = page.locator("div").filter(has_text=re.compile(r"^Contrato Social$")).locator(
            "button")
        self.btn_add_comprovante_renda = page.locator("div").filter(
            has_text=re.compile(r"^Comprovante de renda$")).locator("button")
        self.btn_add_comprovante_endereco = page.locator("div").filter(
            has_text=re.compile(r"^Comprovante de endereço no nome do cliente final$")).locator("button")

        # --- SEÇÃO: ENDEREÇOS (INSTALAÇÃO E COBRANÇA) ---
        # Note que agora existem DOIS mapas, um para cada endereço
        self.mapa_instalacao = page.locator("#map").nth(0)
        self.mapa_cobranca = page.locator("#map").nth(1)
        self.switch_mesmo_endereco = page.locator("div.p-inputswitch")

        # --- SEÇÃO: INFORMAÇÕES DO CLIENTE (PJ) ---
        # Mudança nos labels: Razão Social e CNPJ
        self.input_razao_social = page.get_by_label("Razão social")  # Valor: Galileu Galilei
        self.input_cnpj = page.get_by_label("Número do CNPJ")  # Valor: 99.999.999/9999-99

        # --- SEÇÃO: CONTATO DO CLIENTE (REPRESENTANTE LEGAL) ---
        self.input_email_rep = page.get_by_label("Email do sócio/representante legal")
        self.input_celular_rep = page.get_by_label("Celular do sócio/representante legal - Principal")
        self.input_tel_fixo_rep = page.get_by_label("Celular do sócio/representante legal - Telefone fixo")

        # --- SEÇÃO: INFORMAÇÕES DOS SÓCIOS/AVALISTA ---
        self.switch_avalista = page.locator("div").filter(has_text="Avalista").locator(".p-inputswitch")
        self.input_cpf_socio = page.get_by_placeholder("000.000.000-00")
        self.input_nome_socio = page.get_by_placeholder("Nome completo")
        self.btn_adicionar_socio = page.get_by_role("button", name="Adicionar sócio")

        # Tabela de sócios
        self.tabela_socios = page.locator("table")

        # --- BOTÃO FINAL ---
        self.btn_enviar = page.get_by_role("button", name="Enviar documentação")

    @allure.step("Preencher informações do sócio/representante")
    def adicionar_socio_detalhes(self, cpf, nome, celular, email):
        self.input_cpf_socio.fill(cpf)
        self.input_nome_socio.fill(nome)
        self.input_celular_rep.nth(1).fill(celular)  # O placeholder se repete
        self.btn_adicionar_socio.click()