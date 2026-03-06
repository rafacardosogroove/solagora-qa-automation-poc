import allure
from playwright.sync_api import APIRequestContext


class ProjetoAPI:
    def __init__(self, request: APIRequestContext):
        self.request = request
        # ATENÇÃO: Troquei para .hom. (Homologação).
        # O seu cURL estava apontando para .tec.br (Produção)
        self.base_url = "https://integrator-api.hom.solagora.com.br"

    @allure.step("API: Aprovar/Finalizar Biometria do Projeto ID: {project_id}")
    def finalizar_biometria(self, project_id: str):
        endpoint = f"{self.base_url}/project-services/projects/{project_id}/status/finalize-biometrics"

        # Montamos o cabeçalho idêntico ao seu cURL
        headers = {
            "accept": "application/json",
            "Internal-Token": "WppdM1IF7SB52jCsLGni2ponSqepwBGB",
            # Idealmente, mover para variável de ambiente no futuro
            "Role": "employee.master"
            # O Playwright já gerencia cookies da sessão atual automaticamente se precisar,
            # mas geralmente esse Internal-Token + Role já bypassam o Cloudflare em APIs de backend.
        }

        # Dispara o PATCH
        response = self.request.patch(endpoint, headers=headers)

        # Validação de Segurança: Se a API falhar, o teste quebra aqui com a mensagem de erro
        assert response.ok, f"Falha na API: {response.status} - {response.text()}"

        return response