#!/usr/bin/env python3
"""
Cliente HTTP para ambiente de HOMOLOGACAO.

Uso:
    from hml_client import hml

    # Token
    token = hml.token()

    # Requests (token injetado automaticamente)
    resp = hml.get("/project-services/project/v1/{id}")
    resp = hml.post("/endpoint", json={"key": "value"})
    resp = hml.put("/endpoint", json={"key": "value"})
    resp = hml.delete("/endpoint")

CLI:
    python hml_client.py              # mostra token
    python hml_client.py --check      # testa conexao
"""

import sys
import os
import io
import json
import time
import random
import requests
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


class HmlClient:
    KEYCLOAK_URL = "https://employee-auth.hom.solagora.com.br/realms/kong-employee/protocol/openid-connect/token"
    CLIENT_ID = "internal-public"
    BASE_URL = "https://employee-api.solagora.tec.br"

    def __init__(self, env_file=None):
        self._token = None
        self._expires_at = 0
        self._cache_file = Path(__file__).resolve().parent / ".token_hml"
        self._env_loaded = False
        self._env_file = env_file

    def _load_env(self):
        if self._env_loaded:
            return

        # Ja tem as vars de ambiente? Nao precisa carregar .env
        if os.getenv("KEYCLOAK_HML_USERNAME") and os.getenv("KEYCLOAK_HML_PASSWORD"):
            self._env_loaded = True
            return

        # Busca .env em ordem de prioridade:
        # 1. Caminho explicito (passado no construtor)
        # 2. .env no diretorio atual (cwd)
        # 3. .env ao lado do hml_client.py
        # 4. Subindo ate 10 niveis procurando .env + .claude/
        candidates = []
        if self._env_file:
            candidates.append(Path(self._env_file))
        candidates.append(Path.cwd() / ".env")
        candidates.append(Path(__file__).resolve().parent / ".env")

        current = Path(__file__).resolve().parent
        for _ in range(10):
            candidate = current / ".env"
            if candidate.exists() and (current / ".claude").exists():
                candidates.append(candidate)
                break
            current = current.parent

        for candidate in candidates:
            if candidate.exists():
                self._parse_env_file(candidate)
                self._env_loaded = True
                return

    @staticmethod
    def _parse_env_file(filepath):
        """Carrega variaveis de um .env (dotenv ou parser manual)."""
        try:
            from dotenv import load_dotenv
            load_dotenv(filepath, override=True)
        except ImportError:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")

    def configure(self, keycloak_user=None, keycloak_pass=None, db_user=None, db_pass=None, env_file=None):
        """Configura credenciais via codigo (sem depender de .env).

        Args:
            keycloak_user: username Keycloak HML (default: superadmin)
            keycloak_pass: password Keycloak HML
            db_user: usuario do banco HML (para acesso direto)
            db_pass: senha do banco HML
            env_file: caminho para arquivo .env alternativo

        Returns:
            self (para encadear chamadas)
        """
        if env_file:
            self._env_file = env_file
            if Path(env_file).exists():
                self._parse_env_file(Path(env_file))
                self._env_loaded = True

        if keycloak_user:
            os.environ["KEYCLOAK_HML_USERNAME"] = keycloak_user
        if keycloak_pass:
            os.environ["KEYCLOAK_HML_PASSWORD"] = keycloak_pass
        if db_user:
            os.environ["DB_USERNAME"] = db_user
        if db_pass:
            os.environ["DB_PASSWORD"] = db_pass

        if keycloak_user or keycloak_pass:
            self._env_loaded = True
            # Invalida token atual para forcar re-auth
            self._token = None
            self._expires_at = 0

        return self

    def _load_cache(self):
        if not self._cache_file.exists():
            return None
        try:
            data = json.loads(self._cache_file.read_text())
            if data.get("expires_at", 0) > time.time() + 30:
                return data["access_token"], data["expires_at"]
        except Exception:
            pass
        return None

    def _save_cache(self, token, expires_in):
        expires_at = time.time() + expires_in
        self._cache_file.write_text(json.dumps({
            "access_token": token,
            "expires_at": expires_at,
        }))
        return expires_at

    def token(self):
        """Retorna token HML valido (usa cache)."""
        if self._token and self._expires_at > time.time() + 30:
            return self._token

        cached = self._load_cache()
        if cached:
            self._token, self._expires_at = cached
            return self._token

        self._load_env()
        username = os.getenv("KEYCLOAK_HML_USERNAME", "")
        password = os.getenv("KEYCLOAK_HML_PASSWORD", "")

        if not username or not password:
            raise RuntimeError(
                "KEYCLOAK_HML_USERNAME e KEYCLOAK_HML_PASSWORD precisam estar no .env"
            )

        resp = requests.post(self.KEYCLOAK_URL, data={
            "grant_type": "password",
            "client_id": self.CLIENT_ID,
            "username": username,
            "password": password,
        }, timeout=30)

        if resp.status_code != 200:
            raise RuntimeError(f"Keycloak HML retornou {resp.status_code}: {resp.text[:300]}")

        result = resp.json()
        self._token = result["access_token"]
        expires_in = result.get("expires_in", 300)
        self._expires_at = self._save_cache(self._token, expires_in)
        return self._token

    def headers(self, extra=None):
        """Headers com Authorization. Aceita headers extras."""
        h = {"Authorization": f"Bearer {self.token()}"}
        if extra:
            h.update(extra)
        return h

    def get(self, path, **kwargs):
        kwargs.setdefault("headers", self.headers())
        kwargs.setdefault("timeout", 30)
        return requests.get(f"{self.BASE_URL}{path}", **kwargs)

    def post(self, path, **kwargs):
        kwargs.setdefault("headers", self.headers())
        kwargs.setdefault("timeout", 30)
        return requests.post(f"{self.BASE_URL}{path}", **kwargs)

    def put(self, path, **kwargs):
        kwargs.setdefault("headers", self.headers())
        kwargs.setdefault("timeout", 30)
        return requests.put(f"{self.BASE_URL}{path}", **kwargs)

    def delete(self, path, **kwargs):
        kwargs.setdefault("headers", self.headers())
        kwargs.setdefault("timeout", 30)
        return requests.delete(f"{self.BASE_URL}{path}", **kwargs)

    def patch(self, path, **kwargs):
        kwargs.setdefault("headers", self.headers())
        kwargs.setdefault("timeout", 30)
        return requests.patch(f"{self.BASE_URL}{path}", **kwargs)


    # ------------------------------------------------------------------
    # Acoes de Projeto HML
    # ------------------------------------------------------------------
    INTEGRATOR_API_URL = "https://integrator-api.solagora.tec.br"
    CUSTOMER_API_URL = "https://customer-api.solagora.tec.br"
    INTERNAL_TOKEN = "WppdM1IF7SB52jCsLGni2ponSqepwBGB"

    def finalizar_biometria(self, project_id):
        """Finaliza biometria do projeto em 'Aguardando biometria'.

        Args:
            project_id: ID do projeto

        Returns:
            requests.Response
        """
        resp = self._patch_internal(
            f"{self.INTEGRATOR_API_URL}/project-services/projects/{project_id}/status/finalize-biometrics"
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro ao finalizar biometria: {resp.status_code} - {resp.text[:300]}")
        return resp

    def _internal_headers(self):
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Internal-Token": self.INTERNAL_TOKEN,
            "Role": "employee.master",
        }

    def _patch_internal(self, url):
        """PATCH com Internal-Token (endpoints internos HML)."""
        resp = requests.patch(url, headers=self._internal_headers(), timeout=30)
        return resp

    def emitir_ccb(self, project_id):
        """Emite CCB do projeto (CCB Issued).

        Args:
            project_id: ID do projeto

        Returns:
            requests.Response
        """
        resp = self._patch_internal(
            f"{self.INTEGRATOR_API_URL}/project-services/project/v1/{project_id}/ccb/issue"
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro ao emitir CCB: {resp.status_code} - {resp.text[:300]}")
        return resp

    def aguardar_assinatura(self, project_id):
        """Muda status para 'Aguardando assinaturas'.

        Args:
            project_id: ID do projeto

        Returns:
            requests.Response
        """
        resp = self._patch_internal(
            f"{self.INTEGRATOR_API_URL}/project-services/signature/{project_id}/waiting_signatures"
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro ao mudar para aguardando assinatura: {resp.status_code} - {resp.text[:300]}")
        return resp

    def finalizar_assinatura(self, project_id):
        """Avanca projeto de 'Aguardando Assinaturas' para 'Faturamento Autorizado'.

        Endpoint: PATCH /project-services/project/v1/{projectId}/waiting_billing_data

        Args:
            project_id: ID do projeto

        Returns:
            requests.Response
        """
        resp = self.patch(f"/project-services/project/v1/{project_id}/waiting_billing_data")
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro ao finalizar assinatura: {resp.status_code} - {resp.text[:300]}")
        return resp

    def classificar_nota(self, project_id, tipo="NFV"):
        """Define classificacao da nota fiscal (Nota Futura ou Nota de Venda).

        Endpoint: PATCH /cessao-services/cessao/{projectId}/document-classification

        Args:
            project_id: ID do projeto
            tipo: 'NFV' (Nota Fiscal de Venda) ou 'NFF' (Nota Fiscal Futura)

        Returns:
            requests.Response
        """
        if tipo not in ("NFV", "NFF"):
            raise ValueError(f"Tipo deve ser 'NFV' ou 'NFF', recebeu: {tipo}")
        resp = self.patch(
            f"/cessao-services/cessao/{project_id}/document-classification",
            json={"documentClassification": tipo},
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro ao classificar nota: {resp.status_code} - {resp.text[:300]}")
        return resp

    # Status IDs HML (cessao flow)
    STATUS_FATURAMENTO_AUTORIZADO = "dbffdb98-4fbf-4c07-bfe5-9160a7c36fed"
    STATUS_DOC_PAGAMENTO_ANALISE = "6cfc60eb-75cf-42fb-a3e9-4b86a356f9e9"
    STATUS_LIBERADO_PAGAMENTO = "657edb1b-6794-45eb-880f-09f470609921"

    def aprovar_cessao(self, project_id, comentario="[AUTOMACAO QA] Nota fiscal aprovada via API"):
        """Aprova nota fiscal/cessao do projeto.

        Requer status atual = 'Documentacao para pagamento em Analise' (WaitingBillingEvaluation).
        Avanca para 'Liberado para Pagamento' (ProposalReleased).

        Endpoint: PATCH /project-services/project/v1/{projectId}/invoiced-documentation-approval

        Args:
            project_id: ID do projeto
            comentario: Comentario da aprovacao

        Returns:
            requests.Response
        """
        resp = self.patch(
            f"/project-services/project/v1/{project_id}/invoiced-documentation-approval",
            json={"statusComments": comentario},
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro ao aprovar cessao: {resp.status_code} - {resp.text[:300]}")
        return resp

    def buscar_projetos_cpf(self, cpf):
        """Busca projetos de um cliente pelo CPF.

        Args:
            cpf: CPF do cliente (apenas digitos)

        Returns:
            list[dict]: Lista de projetos com id, ccb, status, created
        """
        cpf = cpf.replace(".", "").replace("-", "").replace(" ", "")
        conn = self._db_conn("project")
        try:
            cur = conn.cursor()
            cur.execute(
                'SELECT p.id, p."CCBId", ps."BusinessStatus", p."Created" '
                'FROM project.customer c '
                'JOIN project.project p ON p.id = c."ProjectId" '
                'JOIN project.status ps ON ps."Id" = p."StatusId" '
                'WHERE c."Document" = %s '
                'ORDER BY p."Created" DESC',
                (cpf,)
            )
            rows = cur.fetchall()
            return [
                {"id": str(r[0]), "ccb": r[1], "status": r[2], "created": str(r[3])}
                for r in rows
            ]
        finally:
            conn.close()

    def _get_status_hml(self, project_id):
        """Busca StatusId e SystemStatus do projeto no banco HML.

        Returns:
            tuple: (status_id, system_status, business_status)
        """
        conn = self._db_conn("project")
        try:
            cur = conn.cursor()
            cur.execute(
                'SELECT p."StatusId", ps."SystemStatus", ps."BusinessStatus" '
                'FROM project.project p '
                'JOIN project.status ps ON ps."Id" = p."StatusId" '
                'WHERE p.id = %s',
                (project_id,)
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError(f"Projeto {project_id} nao encontrado no HML")
            return row
        finally:
            conn.close()

    def _set_status_hml(self, project_id, status_id):
        """Atualiza StatusId do projeto no banco HML (project + lifecycle_manager).

        Atualiza ambas as tabelas para manter consistencia:
        - project.project.StatusId
        - project_lifecycle_manager.project.status_id
        """
        # 1. Atualizar project.project
        conn = self._db_conn("project")
        try:
            conn.autocommit = False
            cur = conn.cursor()
            cur.execute(
                'UPDATE project.project SET "StatusId" = %s WHERE id = %s',
                (status_id, project_id)
            )
            conn.commit()
            rows = cur.rowcount
        finally:
            conn.close()

        # 2. Atualizar lifecycle_manager
        try:
            conn2 = self._db_conn("project_lifecycle_manager_svc")
            conn2.autocommit = False
            cur2 = conn2.cursor()
            cur2.execute(
                'UPDATE project_lifecycle_manager.project SET status_id = %s, last_modified = NOW() WHERE id = %s',
                (status_id, project_id)
            )
            conn2.commit()
            conn2.close()
        except Exception as e:
            print(f"[aviso] Falha ao atualizar lifecycle_manager: {e}")

        return rows

    def fluxo_cessao(self, project_id, tipo_nota="NFV", comentario="[AUTOMACAO QA] Nota fiscal aprovada via API", max_retries=2):
        """Fluxo completo de cessao: classificar nota + aprovar.

        Se aprovar_cessao falhar, volta status para 'Faturamento autorizado'
        e retenta. Ao final verifica se avancou para 'Liberado para pagamento'.

        Args:
            project_id: ID do projeto
            tipo_nota: 'NFV' ou 'NFF' (default: NFV)
            comentario: comentario da aprovacao
            max_retries: tentativas maximas para aprovar_cessao (default: 2)

        Returns:
            dict com resultado: status_final, sucesso, tentativas
        """
        resultado = {"project_id": project_id, "tentativas": 0, "sucesso": False}

        # Verificar status atual
        status_id, sys_status, biz_status = self._get_status_hml(project_id)
        resultado["status_inicial"] = biz_status
        print(f"[cessao] Status atual: {biz_status} ({sys_status})")

        # Se ja esta em Liberado para Pagamento, nada a fazer
        if sys_status == "proposal_released":
            print("[cessao] Projeto ja esta em 'Liberado para Pagamento'")
            resultado["sucesso"] = True
            resultado["status_final"] = biz_status
            return resultado

        # 1. Classificar nota
        print(f"[cessao] Classificando nota como {tipo_nota}...")
        self.classificar_nota(project_id, tipo=tipo_nota)
        print(f"[cessao] Nota classificada OK")

        # 2. Aprovar cessao (com retry)
        for tentativa in range(1, max_retries + 1):
            resultado["tentativas"] = tentativa
            print(f"[cessao] Tentativa {tentativa}/{max_retries} - aprovando cessao...")

            try:
                self.aprovar_cessao(project_id, comentario=comentario)
                print(f"[cessao] Aprovacao OK na tentativa {tentativa}")
                break
            except RuntimeError as e:
                erro = str(e)
                print(f"[cessao] Erro na tentativa {tentativa}: {erro[:200]}")

                if tentativa >= max_retries:
                    resultado["erro"] = erro[:300]
                    break

                # Rollback: voltar para 'Faturamento autorizado' e retentar
                print(f"[cessao] Rollback -> Faturamento autorizado...")
                self._set_status_hml(project_id, self.STATUS_FATURAMENTO_AUTORIZADO)
                time.sleep(2)

                # Re-classificar nota apos rollback
                print(f"[cessao] Re-classificando nota como {tipo_nota}...")
                self.classificar_nota(project_id, tipo=tipo_nota)
                time.sleep(1)

        # 3. Verificar status final
        time.sleep(2)
        status_id, sys_status, biz_status = self._get_status_hml(project_id)
        resultado["status_final"] = biz_status
        resultado["sucesso"] = sys_status == "proposal_released"

        if resultado["sucesso"]:
            print(f"[cessao] SUCESSO - Projeto avancou para '{biz_status}'")
        else:
            print(f"[cessao] FALHA - Status final: '{biz_status}' ({sys_status})")

        return resultado

    def _get_bmp_operation_code(self, project_id):
        """Busca BmpOperationCode (Code) da tabela bmp.proposal no HML.

        Returns:
            str: BmpOperationCode (usado como 'proposta' no callback)
        """
        conn = self._db_conn("bmp")
        try:
            cur = conn.cursor()
            cur.execute(
                'SELECT "Code" FROM bmp.proposal WHERE "OperationCode" = %s LIMIT 1',
                (project_id,)
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError(f"Projeto {project_id} nao encontrado em bmp.proposal")
            return str(row[0])
        finally:
            conn.close()

    def callback_bmp(self, project_id, situacao):
        """Envia callback BMP para o projeto no HML.

        Usa GET com query params (conforme Postman collection).
        URL: {BASE_URL}/bmp-services/proposals/callback?proposta=X&situacao=Y&identificador=Z

        Args:
            project_id: ID do projeto (usado como 'identificador')
            situacao: codigo do callback (10=cessao iniciada, 9=cessao finalizada, etc)

        Returns:
            requests.Response
        """
        bmp_code = self._get_bmp_operation_code(project_id)
        params = {
            "identificador": project_id,
            "proposta": bmp_code,
            "situacao": situacao,
        }
        url = f"{self.BASE_URL}/bmp-services/proposals/callback"
        print(f"[callback] GET {url}?proposta={bmp_code}&situacao={situacao}&identificador={project_id}")
        resp = self.get(f"/bmp-services/proposals/callback", params=params)
        print(f"[callback] Resposta: {resp.status_code} - {resp.text[:300]}")
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Callback {situacao} falhou: {resp.status_code} - {resp.text[:300]}")
        return resp

    def enviar_callbacks_cessao(self, project_id, intervalo=5):
        """Envia callback 10 (cessao iniciada) e 9 (cessao finalizada) com intervalo.

        Args:
            project_id: ID do projeto
            intervalo: segundos entre callback 10 e 9 (default: 5)

        Returns:
            dict com resultado dos dois callbacks
        """
        resultado = {"project_id": project_id}

        # Callback 10 - Cessao iniciada
        print(f"[callbacks] Enviando callback 10 (cessao iniciada)...")
        resp10 = self.callback_bmp(project_id, 10)
        resultado["callback_10"] = {"status": resp10.status_code, "ok": resp10.status_code in (200, 204)}

        # Intervalo
        print(f"[callbacks] Aguardando {intervalo}s...")
        time.sleep(intervalo)

        # Callback 9 - Cessao finalizada
        print(f"[callbacks] Enviando callback 9 (cessao finalizada)...")
        resp9 = self.callback_bmp(project_id, 9)
        resultado["callback_9"] = {"status": resp9.status_code, "ok": resp9.status_code in (200, 204)}

        # Verificar status final
        time.sleep(2)
        _, sys_status, biz_status = self._get_status_hml(project_id)
        resultado["status_final"] = biz_status
        print(f"[callbacks] Status final: {biz_status} ({sys_status})")

        return resultado

    # ── Fluxo de Equipamento (pos-cessao) ──────────────────────────
    # IMPORTANTE: Usar SEMPRE estes metodos (via API) nesta fase.
    # NUNCA usar --set-status para estes status, pois o RabbitMQ
    # nao recebe o evento e o worker nao cria os equipamentos.
    #
    # Ordem correta:
    #   1. equip_aguardar_doc       → Aguardando doc equipamento entregue
    #   2. equip_confirmar_integrador → Aguardando confirmacao cliente
    #   3. equip_confirmar_cliente   → Equipamento entregue (auto-avanca p/ monitoracao)

    def equip_aguardar_doc(self, project_id):
        """Passo 1: Avancar para 'Aguardando documentacao de equipamento entregue'.

        Endpoint: PATCH /project-services/project/v1/{id}/waiting_equipment_delivered_documentation
        Requer: Cessao finalizada, Split falhou, ou Aguardando confirmacao equip.

        Args:
            project_id: ID do projeto

        Returns:
            requests.Response
        """
        resp = self.patch(
            f"/project-services/project/v1/{project_id}/waiting_equipment_delivered_documentation"
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro equip_aguardar_doc: {resp.status_code} - {resp.text[:300]}")
        return resp

    def equip_confirmar_integrador(self, project_id):
        """Passo 2: Avancar para 'Aguardando confirmacao do cliente de equipamento entregue'.

        Endpoint: PATCH /project-services/project/v1/{id}/waiting_confirmation_equipment_delivered
        Requer: Aguardando documentacao de equipamento entregue.

        Args:
            project_id: ID do projeto

        Returns:
            requests.Response
        """
        resp = self.patch(
            f"/project-services/project/v1/{project_id}/waiting_confirmation_equipment_delivered"
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro equip_confirmar_integrador: {resp.status_code} - {resp.text[:300]}")
        return resp

    def equip_confirmar_cliente(self, project_id):
        """Passo 3: Confirmar equipamento entregue pelo cliente.

        Endpoint: POST /project-services/project/v1/{id}/force-to-equipment-delivered
        Requer: Aguardando confirmacao do cliente de equipamento entregue.

        Apos este passo, o sistema auto-avanca para 'Dados para monitoracao da usina'
        e o worker RabbitMQ (CreateProjectEquipmentsJob) cria os equipamentos.

        Args:
            project_id: ID do projeto

        Returns:
            requests.Response
        """
        resp = self.post(f"/project-services/project/v1/{project_id}/force-to-equipment-delivered")
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro equip_confirmar_cliente: {resp.status_code} - {resp.text[:300]}")
        return resp

    def equip_forcar_monitoracao(self, project_id):
        """Fallback: Forca avanço para 'Dados para monitoração da usina'.

        Usar quando o projeto fica parado em 'Equipamento Entregue' e não
        auto-avança (ex: erro transiente no EquipmentDelivered use case).

        Endpoint: PATCH /project-services/project/v1/{id}/waiting_energy_documentation
        Requer: Equipamento Entregue, Cessão finalizada, ou Split em andamento.

        Publica evento RabbitMQ que dispara CreateProjectEquipmentsJob.

        Args:
            project_id: ID do projeto

        Returns:
            requests.Response
        """
        _, sys_status, biz_status = self._get_status_hml(project_id)
        if sys_status != "equipment_delivered":
            raise RuntimeError(
                f"Projeto nao esta em 'Equipamento Entregue' (atual: {biz_status}). "
                f"Use --equip-monitoracao apenas quando parado nesse status."
            )
        resp = self.patch(
            f"/project-services/project/v1/{project_id}/waiting_energy_documentation"
        )
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro equip_forcar_monitoracao: {resp.status_code} - {resp.text[:300]}")
        return resp

    def confirmar_equipamento_entregue(self, project_id):
        """Alias para equip_confirmar_cliente (compatibilidade)."""
        return self.equip_confirmar_cliente(project_id)

    def fund_payment_started(self, project_id):
        """Inicia split de pagamento do projeto.

        Endpoint: PATCH /project-services/project/v1/{projectId}/fund_payment_started
        """
        resp = self.patch(f"/project-services/project/v1/{project_id}/fund_payment_started")
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro fund_payment_started: {resp.status_code} - {resp.text[:300]}")
        return resp

    def fund_payment_finished(self, project_id):
        """Finaliza split de pagamento do projeto.

        Endpoint: PATCH /project-services/project/v1/{projectId}/fund_payment_finished
        """
        resp = self.patch(f"/project-services/project/v1/{project_id}/fund_payment_finished")
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro fund_payment_finished: {resp.status_code} - {resp.text[:300]}")
        return resp

    def resolver_split_pagamento(self, project_id):
        """Resolve 'Falha no Split de Pagamento' avancando para equipamento entregue.

        Endpoint: PATCH /project-services/project/v1/{projectId}/waiting_equipment_delivered_documentation

        Args:
            project_id: ID do projeto

        Returns:
            dict com resultado
        """
        resultado = {"project_id": project_id}

        _, sys_status, biz_status = self._get_status_hml(project_id)
        resultado["status_inicial"] = biz_status
        print(f"[split] Status atual: {biz_status} ({sys_status})")

        if sys_status != "split_payment_failed":
            print(f"[split] Projeto NAO esta em 'Falha no Split de Pagamento', abortando")
            resultado["erro"] = f"Status atual: {biz_status}"
            return resultado

        print(f"[split] Avancando para 'Aguardando doc equipamento entregue'...")
        resp = self.patch(
            f"/project-services/project/v1/{project_id}/waiting_equipment_delivered_documentation"
        )
        print(f"[split] Resposta: {resp.status_code}")
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"Erro ao resolver split: {resp.status_code} - {resp.text[:300]}")

        time.sleep(2)
        _, sys_status, biz_status = self._get_status_hml(project_id)
        resultado["status_final"] = biz_status
        resultado["sucesso"] = sys_status != "split_payment_failed"
        print(f"[split] Status final: {biz_status} ({sys_status})")

        return resultado

    def aprovar_documentacao(self, project_id, comentario="[AUTOMACAO QA] Documentacao aprovada via API"):
        """Aprova documentacao do projeto em 'Aguardando avaliacao da proposta'.

        Args:
            project_id: ID do projeto
            comentario: texto do comentario (minimo 30 caracteres)

        Returns:
            requests.Response
        """
        if len(comentario) < 30:
            raise ValueError(f"Comentario precisa ter no minimo 30 caracteres (tem {len(comentario)})")
        resp = self.patch(
            f"/project-services/project/v1/{project_id}/proposal-approval",
            json={"statusProposalComments": comentario},
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Erro ao aprovar documentacao: {resp.status_code} - {resp.text[:300]}")
        return resp

    def aprovar_projeto(self, project_id, comentario="[AUTOMACAO QA] Aprovado via API"):
        """Aprova projeto em 'Aguardando avaliacao interna' (mesa).

        Args:
            project_id: ID do projeto
            comentario: texto do comentario (default: tag automacao)

        Returns:
            requests.Response
        """
        resp = self.patch(
            f"/project-services/proposal/{project_id}/project-proposal-approval",
            json={"statusProposalComments": comentario},
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Erro ao aprovar projeto: {resp.status_code} - {resp.text[:300]}")
        return resp

    def reprovar_projeto(self, project_id, comentario="[AUTOMACAO QA] Reprovado via API", motivos=None):
        """Reprova projeto em 'Aguardando avaliacao interna' (mesa).

        Args:
            project_id: ID do projeto
            comentario: texto do comentario
            motivos: lista de IDs de motivos de reprovacao (opcional)

        Returns:
            requests.Response
        """
        body = {"statusProposalComments": comentario}
        if motivos:
            body["riskAnalysisReasonsId"] = motivos
        resp = self.patch(
            f"/project-services/proposal/{project_id}/project-proposal-disapproved",
            json=body,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Erro ao reprovar projeto: {resp.status_code} - {resp.text[:300]}")
        return resp

    # ------------------------------------------------------------------
    # Banco de Dados HML
    # ------------------------------------------------------------------
    DB_HOST = "solagora-psql-hml.cluster-cqd4h0vlsr95.us-east-1.rds.amazonaws.com"
    DB_PORT = 5432

    def _db_conn(self, database):
        """Retorna conexao psycopg2 para o banco HML.

        Busca credenciais especificas por banco (ex: DB_PROJECT_USERNAME)
        e faz fallback para DB_USERNAME/DB_PASSWORD se nao encontrar.
        """
        import psycopg2
        self._load_env()
        # Mapa de database -> prefixo da env var
        db_prefix = {
            "project": "DB_PROJECT",
            "project_lifecycle_manager_svc": "DB_LIFECYCLE",
            "bmp": "DB_BMP",
            "customer": "DB_CUSTOMER",
            "document": "DB_DOCUMENT",
        }
        prefix = db_prefix.get(database, "DB")
        user = os.getenv(f"{prefix}_USERNAME") or os.getenv("DB_USERNAME", "")
        pwd = os.getenv(f"{prefix}_PASSWORD") or os.getenv("DB_PASSWORD", "")
        if not user or not pwd:
            raise RuntimeError(f"Credenciais do banco '{database}' nao encontradas. "
                               f"Configure {prefix}_USERNAME/{prefix}_PASSWORD ou DB_USERNAME/DB_PASSWORD no .env")
        return psycopg2.connect(
            host=self.DB_HOST, port=self.DB_PORT,
            dbname=database, user=user, password=pwd,
            connect_timeout=15,
        )

    def ocr_toggle(self, enabled):
        """Liga ou desliga OCR para todos os document_type no HML.

        Args:
            enabled: True para ligar, False para desligar
        """
        conn = self._db_conn("document")
        conn.autocommit = False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE document.document_type SET ocr_enabled = %s "
                "WHERE ocr_enabled = %s RETURNING id, name",
                (enabled, not enabled)
            )
            rows = cur.fetchall()
            conn.commit()
            return rows
        finally:
            conn.close()

    def liberar_telefone(self, telefone, substituto="11111111111", dry_run=True):
        """Libera telefone de propostas antigas no HML.

        Args:
            telefone: telefone a liberar (ex: '11966398456')
            substituto: valor para substituir (default: '11111111111')
            dry_run: se True, apenas mostra o que faria sem alterar

        Returns:
            dict com contagem de registros afetados por tabela
        """
        import psycopg2

        telefone = telefone.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
        pattern = f"%{telefone[-9:]}"  # ultimos 9 digitos

        tabelas = [
            {"db": "customer", "schema": '"Customer"', "table": "customer", "col": "Mainphone", "label": "Customer.customer.Mainphone"},
            {"db": "project",  "schema": "project",    "table": "customer", "col": "Phone",     "label": "project.customer.Phone"},
            {"db": "project",  "schema": "project",    "table": "simulation", "col": "Telephone", "label": "project.simulation.Telephone"},
        ]

        resultado = {}
        for t in tabelas:
            chave = t["label"]
            try:
                conn = self._db_conn(t["db"])
                conn.autocommit = False
                cur = conn.cursor()
                fqn = f'{t["schema"]}.{t["table"]}'

                # Contar
                cur.execute(
                    f'SELECT COUNT(*) FROM {fqn} WHERE "{t["col"]}" LIKE %s',
                    (pattern,)
                )
                count = cur.fetchone()[0]

                if count == 0:
                    resultado[chave] = {"encontrados": 0, "atualizados": 0}
                    conn.close()
                    continue

                if dry_run:
                    resultado[chave] = {"encontrados": count, "atualizados": 0, "modo": "dry_run"}
                    conn.close()
                    continue

                # Atualizar
                cur.execute(
                    f'UPDATE {fqn} SET "{t["col"]}" = %s WHERE "{t["col"]}" LIKE %s',
                    (substituto, pattern)
                )
                conn.commit()
                resultado[chave] = {"encontrados": count, "atualizados": cur.rowcount}
                conn.close()

            except Exception as e:
                resultado[chave] = {"erro": str(e)}

        return resultado

    # ------------------------------------------------------------------
    # Utilitarios
    # ------------------------------------------------------------------
    @staticmethod
    def gerar_email(abrir_inbox=False):
        """Gera email descartavel usando tuamaeaquelaursa.com.

        O dominio aceita qualquer nome - gera um nome aleatorio sem depender
        de Playwright/navegador. Se abrir_inbox=True, abre o inbox no Chrome.

        Args:
            abrir_inbox: se True, abre o inbox no navegador

        Returns:
            str: email completo (ex: qa-test-a1b2c3@tuamaeaquelaursa.com)
        """
        import random
        import string
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        name = f"qa-test-{suffix}"
        email = f"{name}@tuamaeaquelaursa.com"

        if abrir_inbox:
            try:
                from playwright.sync_api import sync_playwright
                pw = sync_playwright().start()
                browser = pw.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(
                    f"https://tuamaeaquelaursa.com/{name}",
                    wait_until="domcontentloaded",
                    timeout=30000,
                )
                print(f"[Inbox aberto - feche o navegador quando terminar]")
                try:
                    page.wait_for_event("close", timeout=600000)
                except Exception:
                    pass
                try:
                    browser.close()
                except Exception:
                    pass
                pw.stop()
            except ImportError:
                print(f"[AVISO] Playwright nao instalado - inbox nao aberto")
                print(f"  Acesse manualmente: https://tuamaeaquelaursa.com/{name}")

        return email

    @staticmethod
    def gerar_cpf(primeiro_digito=0):
        """Gera CPF valido comecando com o digito informado.

        Args:
            primeiro_digito: primeiro digito do CPF (0-9)

        Returns:
            str: CPF com 11 digitos (sem pontuacao)
        """
        digitos = [int(primeiro_digito)]
        digitos += [random.randint(0, 9) for _ in range(8)]

        # Primeiro digito verificador
        soma = sum(d * p for d, p in zip(digitos, range(10, 1, -1)))
        resto = soma % 11
        d1 = 0 if resto < 2 else 11 - resto
        digitos.append(d1)

        # Segundo digito verificador
        soma = sum(d * p for d, p in zip(digitos, range(11, 1, -1)))
        resto = soma % 11
        d2 = 0 if resto < 2 else 11 - resto
        digitos.append(d2)

        return "".join(str(d) for d in digitos)


# Instancia singleton - importar e usar direto
hml = HmlClient()

# Atalhos diretos
gerar_cpf = HmlClient.gerar_cpf
gerar_email = HmlClient.gerar_email


def _cli_get_arg(flag, required=True):
    """Retorna o argumento apos a flag. Ex: --flag VALOR"""
    if flag not in sys.argv:
        return None
    idx = sys.argv.index(flag)
    if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--"):
        return sys.argv[idx + 1]
    if required:
        print(f"[ERRO] {flag} requer um argumento")
        sys.exit(1)
    return None


def _cli_help():
    print("""hml_client.py - CLI para automacao HML Sol Agora

OPCOES GLOBAIS:
  --env <caminho>              Apontar .env especifico
  --help                       Mostrar esta ajuda

UTILITARIOS:
  (sem argumentos)             Mostrar token HML
  --check                      Testar conexao
  --cpf [digito]               Gerar CPF valido (0-3=aprovado, 4-6=reprovado, 7-9=pendente)
  --email                      Gerar email descartavel
  --projeto-cpf <CPF>          Buscar projetos pelo CPF do cliente
  --status <PID>               Ver status do projeto
  --set-status <PID> <SID>     Alterar status (rollback)
  --liberar-telefone <TEL>     Liberar telefone [--executar]

FLUXO DO PROJETO (em ordem):
  --aprovar-doc <PID>          Aprovar documentacao [--comentario 'texto']
  --analiseinterna <PID> <acao>  Aprovar/reprovar na mesa [--comentario 'texto']
  --biometria <PID>            Finalizar biometria
  --emitir-ccb <PID>           Emitir CCB
  --aguardar-assinatura <PID>  Mudar para Aguardando assinaturas
  --finalizar-assinatura <PID> Avancar para Faturamento autorizado
  --cessao <PID>               Fluxo cessao completo [--tipo NFV|NFF]
  --classificar-nota <PID>     Classificar nota [--tipo NFV|NFF]
  --aprovar-cessao <PID>       Aprovar cessao [--comentario 'texto']
  --callback <PID>             Enviar callbacks cessao (10+9) [--intervalo 5]
  --callback-bmp <PID> <SIT>   Enviar callback individual (10 ou 9)
  --split <PID>                Resolver falha no split de pagamento
  --fund-started <PID>         Fund payment started
  --fund-finished <PID>        Fund payment finished

FLUXO DE EQUIPAMENTO (pos-cessao, SEMPRE via API, NUNCA --set-status):
  --equip-doc <PID>            Passo 1: Aguardando doc equipamento entregue
  --equip-integrador <PID>     Passo 2: Integrador confirma (aguardar confirmacao cliente)
  --equip-cliente <PID>        Passo 3: Cliente confirma → auto-avanca p/ monitoracao
  --equip-completo <PID>       Passos 1+2+3 de uma vez (fluxo completo equipamento)
  --equip-monitoracao <PID>    Fallback: forcar avanco p/ monitoracao (se parou em Equip Entregue)

FLUXO COMPLETO (todas as etapas de uma vez):
  --fluxo-completo <PID>       Executar todas etapas do projeto [--tipo NFV|NFF]
""")


if __name__ == "__main__":
    # Suporte a --env <caminho> em qualquer posicao
    if "--env" in sys.argv:
        ei = sys.argv.index("--env")
        if ei + 1 < len(sys.argv):
            hml.configure(env_file=sys.argv[ei + 1])
            sys.argv.pop(ei)  # remove --env
            sys.argv.pop(ei)  # remove caminho

    if "--help" in sys.argv or "-h" in sys.argv:
        _cli_help()
        sys.exit(0)

    # --- Utilitarios ---
    elif "--check" in sys.argv:
        try:
            t = hml.token()
            print(f"[OK] Token HML obtido ({len(t)} chars)")
            print(f"[OK] Base URL: {HmlClient.BASE_URL}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--cpf" in sys.argv:
        idx = sys.argv.index("--cpf")
        digito = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--") else 0
        print(gerar_cpf(digito))

    elif "--email" in sys.argv:
        print(gerar_email())

    elif "--projeto-cpf" in sys.argv:
        cpf = _cli_get_arg("--projeto-cpf")
        projetos = hml.buscar_projetos_cpf(cpf)
        if not projetos:
            print(f"Nenhum projeto encontrado para CPF {cpf}")
            sys.exit(1)
        print(f"Projetos do CPF {cpf}: ({len(projetos)} encontrados)\n")
        for p in projetos:
            ccb = p['ccb'] if p['ccb'] else '-'
            print(f"  {p['id']}  CCB: {ccb}  Status: {p['status']}  Criado: {p['created']}")

    elif "--status" in sys.argv:
        pid = _cli_get_arg("--status")
        try:
            sid, sys_s, biz_s = hml._get_status_hml(pid)
            print(f"Status: {biz_s} ({sys_s})")
            print(f"ID: {sid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--set-status" in sys.argv:
        idx = sys.argv.index("--set-status")
        if idx + 2 >= len(sys.argv):
            print("Uso: python hml_client.py --set-status <PROJECT_ID> <STATUS_ID>")
            sys.exit(1)
        pid = sys.argv[idx + 1]
        sid = sys.argv[idx + 2]
        try:
            rows = hml._set_status_hml(pid, sid)
            print(f"[OK] Status atualizado (project: {rows} rows)")
            new_sid, sys_s, biz_s = hml._get_status_hml(pid)
            print(f"  Novo status: {biz_s} ({sys_s})")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--liberar-telefone" in sys.argv:
        tel = _cli_get_arg("--liberar-telefone")
        executar = "--executar" in sys.argv
        print(f"{'[EXECUTANDO]' if executar else '[DRY-RUN]'} Liberando telefone {tel}...")
        res = hml.liberar_telefone(tel, dry_run=not executar)
        total_encontrados = 0
        total_atualizados = 0
        for tabela, info in res.items():
            if "erro" in info:
                print(f"  {tabela}: ERRO - {info['erro']}")
            else:
                total_encontrados += info["encontrados"]
                total_atualizados += info.get("atualizados", 0)
                status = f"{info['encontrados']} encontrados"
                if executar:
                    status += f", {info['atualizados']} atualizados"
                print(f"  {tabela}: {status}")
        print(f"\nTotal: {total_encontrados} registros encontrados", end="")
        if executar:
            print(f", {total_atualizados} atualizados")
        else:
            print(f"\n\nPara executar: python hml_client.py --liberar-telefone {tel} --executar")

    # --- Fluxo do Projeto ---
    elif "--aprovar-doc" in sys.argv:
        pid = _cli_get_arg("--aprovar-doc")
        comentario = _cli_get_arg("--comentario", required=False) or "[AUTOMACAO QA] Documentacao aprovada via API"
        try:
            hml.aprovar_documentacao(pid, comentario)
            print(f"[OK] Documentacao aprovada para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--analiseinterna" in sys.argv:
        idx = sys.argv.index("--analiseinterna")
        if idx + 1 >= len(sys.argv):
            print("Uso: python hml_client.py --analiseinterna <PROJECT_ID> [aprovar|reprovar] [--comentario 'texto']")
            sys.exit(1)
        pid = sys.argv[idx + 1]
        acao = sys.argv[idx + 2] if idx + 2 < len(sys.argv) and not sys.argv[idx + 2].startswith("--") else "aprovar"
        comentario = _cli_get_arg("--comentario", required=False)
        try:
            if acao.lower() in ("aprovar", "approve"):
                comentario = comentario or "[AUTOMACAO QA] Aprovado via API"
                hml.aprovar_projeto(pid, comentario)
                print(f"[OK] Projeto {pid} APROVADO na analise interna")
            elif acao.lower() in ("reprovar", "reject"):
                comentario = comentario or "[AUTOMACAO QA] Reprovado via API"
                hml.reprovar_projeto(pid, comentario)
                print(f"[OK] Projeto {pid} REPROVADO na analise interna")
            else:
                print(f"[ERRO] Acao invalida: {acao} (use aprovar ou reprovar)")
                sys.exit(1)
            print(f"  Comentario: {comentario}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--biometria" in sys.argv:
        pid = _cli_get_arg("--biometria")
        try:
            hml.finalizar_biometria(pid)
            print(f"[OK] Biometria finalizada para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--emitir-ccb" in sys.argv:
        pid = _cli_get_arg("--emitir-ccb")
        try:
            hml.emitir_ccb(pid)
            print(f"[OK] CCB emitida para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--aguardar-assinatura" in sys.argv:
        pid = _cli_get_arg("--aguardar-assinatura")
        try:
            hml.aguardar_assinatura(pid)
            print(f"[OK] Aguardando assinaturas para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--finalizar-assinatura" in sys.argv:
        pid = _cli_get_arg("--finalizar-assinatura")
        try:
            hml.finalizar_assinatura(pid)
            print(f"[OK] Assinatura finalizada para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--cessao" in sys.argv:
        pid = _cli_get_arg("--cessao")
        tipo = _cli_get_arg("--tipo", required=False) or "NFV"
        try:
            resultado = hml.fluxo_cessao(pid, tipo_nota=tipo)
            if resultado["sucesso"]:
                print(f"[OK] Cessao concluida para {pid}")
                print(f"  Status: {resultado['status_final']}")
                print(f"  Tentativas: {resultado['tentativas']}")
            else:
                print(f"[ERRO] Cessao falhou para {pid}")
                print(f"  Status: {resultado.get('status_final', 'desconhecido')}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--classificar-nota" in sys.argv:
        pid = _cli_get_arg("--classificar-nota")
        tipo = _cli_get_arg("--tipo", required=False) or "NFV"
        try:
            hml.classificar_nota(pid, tipo=tipo)
            print(f"[OK] Nota classificada como {tipo} para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--aprovar-cessao" in sys.argv:
        pid = _cli_get_arg("--aprovar-cessao")
        comentario = _cli_get_arg("--comentario", required=False) or "[AUTOMACAO QA] Nota fiscal aprovada via API"
        try:
            hml.aprovar_cessao(pid, comentario=comentario)
            print(f"[OK] Cessao aprovada para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--callback-bmp" in sys.argv:
        idx = sys.argv.index("--callback-bmp")
        if idx + 2 >= len(sys.argv):
            print("Uso: python hml_client.py --callback-bmp <PROJECT_ID> <SITUACAO 10|9>")
            sys.exit(1)
        pid = sys.argv[idx + 1]
        sit = int(sys.argv[idx + 2])
        try:
            hml.callback_bmp(pid, sit)
            print(f"[OK] Callback BMP situacao={sit} enviado para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--callback" in sys.argv:
        pid = _cli_get_arg("--callback")
        intervalo = int(_cli_get_arg("--intervalo", required=False) or "5")
        try:
            resultado = hml.enviar_callbacks_cessao(pid, intervalo=intervalo)
            print(f"[OK] Callbacks cessao enviados para {pid}")
            print(f"  Callback 10: {resultado.get('callback_10', 'N/A')}")
            print(f"  Callback 9: {resultado.get('callback_9', 'N/A')}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--split" in sys.argv:
        pid = _cli_get_arg("--split")
        try:
            resultado = hml.resolver_split_pagamento(pid)
            if resultado.get("sucesso"):
                print(f"[OK] Split resolvido para {pid}")
                print(f"  Status: {resultado.get('status_final', 'N/A')}")
            else:
                print(f"[ERRO] Falha ao resolver split para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    # ── Fluxo de Equipamento (SEMPRE via API) ──────────────────────
    elif "--equip-completo" in sys.argv:
        pid = _cli_get_arg("--equip-completo")
        try:
            import time
            # Passo 1
            print(f"[1/3] Aguardando doc equipamento entregue...")
            hml.equip_aguardar_doc(pid)
            _, _, biz = hml._get_status_hml(pid)
            print(f"  Status: {biz}")
            time.sleep(2)
            # Passo 2
            print(f"[2/3] Integrador confirma (aguardando confirmacao cliente)...")
            hml.equip_confirmar_integrador(pid)
            _, _, biz = hml._get_status_hml(pid)
            print(f"  Status: {biz}")
            time.sleep(2)
            # Passo 3
            print(f"[3/3] Cliente confirma equipamento entregue...")
            hml.equip_confirmar_cliente(pid)
            print("  Aguardando worker RabbitMQ (5s)...")
            time.sleep(5)
            _, sys, biz = hml._get_status_hml(pid)
            if sys == "equipment_delivered":
                print(f"  Parou em '{biz}'. Forcando avanco para monitoracao...")
                hml.equip_forcar_monitoracao(pid)
                time.sleep(5)
                _, _, biz = hml._get_status_hml(pid)
            print(f"  Status final: {biz}")
            if biz == "Dados para monitoração da usina":
                print(f"[OK] Fluxo equipamento completo! Worker criou equipamentos via RabbitMQ.")
            else:
                print(f"[AVISO] Status inesperado: {biz}. Worker pode estar lento, aguarde.")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--equip-doc" in sys.argv:
        pid = _cli_get_arg("--equip-doc")
        try:
            hml.equip_aguardar_doc(pid)
            _, _, biz = hml._get_status_hml(pid)
            print(f"[OK] {biz}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--equip-integrador" in sys.argv:
        pid = _cli_get_arg("--equip-integrador")
        try:
            hml.equip_confirmar_integrador(pid)
            _, _, biz = hml._get_status_hml(pid)
            print(f"[OK] {biz}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--equip-monitoracao" in sys.argv:
        pid = _cli_get_arg("--equip-monitoracao")
        try:
            import time
            hml.equip_forcar_monitoracao(pid)
            print(f"[OK] Avancado para 'Dados para monitoracao da usina'")
            print("  Aguardando worker RabbitMQ (5s)...")
            time.sleep(5)
            _, _, biz = hml._get_status_hml(pid)
            print(f"  Status: {biz}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--equip-cliente" in sys.argv or "--confirmar-equip" in sys.argv:
        flag = "--equip-cliente" if "--equip-cliente" in sys.argv else "--confirmar-equip"
        pid = _cli_get_arg(flag)
        try:
            import time
            hml.equip_confirmar_cliente(pid)
            print(f"[OK] Equipamento confirmado para {pid}")
            print("  Aguardando worker RabbitMQ (5s)...")
            time.sleep(5)
            _, _, biz = hml._get_status_hml(pid)
            print(f"  Status: {biz}")
            if biz == "Dados para monitoração da usina":
                print(f"  Worker criou equipamentos via RabbitMQ.")
            else:
                print(f"  [AVISO] Worker pode estar lento, aguarde e verifique.")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--fund-started" in sys.argv:
        pid = _cli_get_arg("--fund-started")
        try:
            hml.fund_payment_started(pid)
            print(f"[OK] Fund payment started para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    elif "--fund-finished" in sys.argv:
        pid = _cli_get_arg("--fund-finished")
        try:
            hml.fund_payment_finished(pid)
            print(f"[OK] Fund payment finished para {pid}")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    # --- OCR ---
    elif "--ocr" in sys.argv:
        acao = _cli_get_arg("--ocr").lower()
        if acao not in ("on", "off"):
            print("[ERRO] Use: --ocr on|off")
            sys.exit(1)
        enabled = acao == "on"
        try:
            rows = hml.ocr_toggle(enabled)
            if rows:
                for r in rows:
                    print(f"  {r[1]}: ocr_enabled = {enabled}")
                print(f"\n[OK] OCR {'LIGADO' if enabled else 'DESLIGADO'} ({len(rows)} tipos)")
            else:
                print(f"[OK] Nenhum registro alterado (OCR ja estava {'ligado' if enabled else 'desligado'})")
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)

    # --- Fluxo Completo ---
    elif "--fluxo-completo" in sys.argv:
        pid = _cli_get_arg("--fluxo-completo")
        tipo = _cli_get_arg("--tipo", required=False) or "NFV"
        import time as _time
        etapas = [
            ("Aprovar documentacao", lambda: hml.aprovar_documentacao(pid)),
            ("Aprovar na mesa", lambda: hml.aprovar_projeto(pid)),
            ("Finalizar biometria", lambda: hml.finalizar_biometria(pid)),
            ("Emitir CCB", lambda: hml.emitir_ccb(pid)),
            ("Aguardar assinatura", lambda: hml.aguardar_assinatura(pid)),
            ("Finalizar assinatura", lambda: hml.finalizar_assinatura(pid)),
            ("Fluxo cessao", lambda: hml.fluxo_cessao(pid, tipo_nota=tipo)),
            ("Callbacks cessao", lambda: hml.enviar_callbacks_cessao(pid, intervalo=5)),
        ]
        print(f"[FLUXO COMPLETO] Projeto {pid} (nota: {tipo})")
        print(f"  Total de etapas: {len(etapas)}")
        print()
        for i, (nome, fn) in enumerate(etapas, 1):
            try:
                print(f"  [{i}/{len(etapas)}] {nome}...", end=" ", flush=True)
                fn()
                print("OK")
                _time.sleep(2)
            except Exception as e:
                print(f"ERRO: {e}")
                _, sys_s, biz_s = hml._get_status_hml(pid)
                print(f"\n  Status atual: {biz_s} ({sys_s})")
                print(f"  Parado na etapa {i}. Corrija e re-execute a partir desta etapa.")
                sys.exit(1)
        # Pos-cessao: split + equipamento
        print()
        _time.sleep(3)
        _, sys_s, biz_s = hml._get_status_hml(pid)
        print(f"  Status apos cessao: {biz_s}")
        if "split" in sys_s.lower() or "split" in biz_s.lower():
            print("  [EXTRA] Resolvendo falha no split...", end=" ", flush=True)
            try:
                hml.resolver_split_pagamento(pid)
                print("OK")
                _time.sleep(3)
            except Exception as e:
                print(f"ERRO: {e}")
        _, sys_s, biz_s = hml._get_status_hml(pid)
        if "confirmacao" in biz_s.lower() or "confirmation" in sys_s.lower():
            print("  [EXTRA] Confirmando equipamento entregue...", end=" ", flush=True)
            try:
                hml.confirmar_equipamento_entregue(pid)
                print("OK")
                _time.sleep(5)
            except Exception as e:
                print(f"ERRO: {e}")
        _, sys_s, biz_s = hml._get_status_hml(pid)
        print(f"\n[CONCLUIDO] Status final: {biz_s} ({sys_s})")

    # --- Default: mostrar token ---
    else:
        try:
            print(hml.token())
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)
