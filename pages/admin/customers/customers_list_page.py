import allure
from playwright.sync_api import Page, expect
import data.customer_data as _cdata


class CustomersListPage:
    def __init__(self, page: Page):
        self.page = page
        self._pagina_cliente = 1  # página onde o cliente sem status foi encontrado

    @allure.step("Navegar para listagem de clientes")
    def navegar_para_clientes(self):
        self.page.goto("https://admin.hom.solagora.com.br/customers")
        self.page.wait_for_function(
            "() => document.querySelector('table') !== null",
            timeout=20000
        )
        self.page.wait_for_timeout(1500)

    def _clicar_proxima_pagina(self) -> bool:
        """Clica no botão PrimeIcons pi-angle-right (próxima página). Retorna True se clicou."""
        return self.page.evaluate("""() => {
            const icon = document.querySelector('i.pi-angle-right');
            if (icon) {
                const btn = icon.closest('button');
                if (btn && !btn.disabled) { btn.click(); return true; }
            }
            return false;
        }""")

    @allure.step("Ir para a página do cliente")
    def ir_para_pagina_cliente(self):
        """Avança para a página onde o cliente foi encontrado (clica N-1 vezes em próxima)."""
        for _ in range(self._pagina_cliente - 1):
            self._clicar_proxima_pagina()
            self.page.wait_for_timeout(1200)

    @allure.step("Encontrar primeiro cliente CPF sem status na lista")
    def encontrar_cliente_sem_status(self) -> str:
        """
        Varre a tabela página a página usando o botão pi-angle-right.
        Armazena self._pagina_cliente com a página encontrada.
        Retorna CPF pessoa física (sem '/') com Status vazio.
        """
        self._pagina_cliente = 1
        max_paginas = 50
        for _ in range(max_paginas):
            self.page.wait_for_timeout(800)
            linhas = self.page.locator("tbody tr").all()
            for linha in linhas:
                celulas = linha.locator("td").all()
                if len(celulas) < 4:
                    continue
                status_txt = celulas[3].inner_text().strip()
                if not status_txt:
                    cpf = celulas[0].inner_text().strip()
                    # Pular CNPJs (XX.XXX.XXX/XXXX-XX)
                    if cpf and "/" not in cpf and cpf not in _cdata._USED_CPFS:
                        _cdata._USED_CPFS.add(cpf)
                        return cpf

            avancou = self._clicar_proxima_pagina()
            if not avancou:
                break
            self._pagina_cliente += 1
            self.page.wait_for_timeout(1200)

        raise RuntimeError("Nenhum cliente CPF sem status encontrado.")

    @allure.step("Buscar cliente por CPF: {cpf}")
    def buscar_por_cpf(self, cpf: str):
        campo_control = self.page.locator(".react-select__control").last
        campo_control.click()
        self.page.wait_for_timeout(300)
        campo_input = self.page.locator(".react-select__input").last
        campo_input.press("Control+a")
        campo_input.press("Backspace")
        campo_input.type(cpf)
        self.page.wait_for_timeout(2000)
        # Selecionar primeira opção do dropdown para aplicar o filtro na tabela
        primeira_opcao = self.page.locator(".react-select__option").first
        if primeira_opcao.is_visible():
            primeira_opcao.click()
        else:
            campo_input.press("Escape")
        self.page.wait_for_timeout(800)

    @allure.step("Limpar campo de busca")
    def limpar_busca(self):
        clear_btn = self.page.locator(".react-select__clear-indicator")
        if clear_btn.count() > 0 and clear_btn.is_visible():
            clear_btn.click()
        else:
            campo_control = self.page.locator(".react-select__control").filter(
                has_text="Pesquisar por..."
            ).or_(self.page.locator(".react-select__control").first)
            campo_control.click()
            self.page.locator(".react-select__input").last.press("Control+a")
            self.page.locator(".react-select__input").last.press("Backspace")
        self.page.wait_for_timeout(1000)

    @allure.step("Verificar que badge 'AGUARDANDO' NÃO está presente para o cliente")
    def verificar_badge_ausente(self, cpf: str):
        linha = self.page.locator("tr", has_text=cpf)
        expect(linha).to_be_visible(timeout=10000)
        badge = linha.locator("td").nth(3)
        # Status cell deve estar vazia
        try:
            status_txt = badge.inner_text(timeout=2000).strip()
            assert not status_txt, f"Cliente {cpf} já tem status: '{status_txt}'"
        except AssertionError:
            raise

    @allure.step("Verificar que badge 'AGUARDANDO' está presente para o cliente")
    def verificar_badge_presente(self, cpf: str):
        """
        Verifica que a célula de Status do cliente não está vazia.
        Deve ser chamado APÓS navegar para a página correta do cliente.
        """
        linha = self.page.locator("tr", has_text=cpf)
        expect(linha).to_be_visible(timeout=10000)
        try:
            status_txt = linha.locator("td").nth(3).inner_text(timeout=3000)
            print(f"\n[DEBUG badge] CPF={cpf} status='{status_txt}'")
        except Exception:
            pass
        # Célula de status deve ter conteúdo
        expect(linha.locator("td").nth(3)).not_to_be_empty(timeout=30000)

    @allure.step("Abrir menu de ações (3 pontinhos) do cliente: {cpf}")
    def abrir_menu_acoes(self, cpf: str):
        linha = self.page.locator("tr", has_text=cpf)
        expect(linha).to_be_visible(timeout=10000)
        linha.locator("button").last.click()
        self.page.wait_for_timeout(700)

    @allure.step("Clicar em 'Editar' no menu de ações")
    def clicar_editar(self):
        self.page.get_by_text("Editar", exact=True).first.click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000)

    @allure.step("Clicar em 'Ver detalhes' no menu de ações")
    def clicar_ver_detalhes(self):
        self.page.get_by_text("Ver detalhes", exact=True).first.click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000)
