import json
import os
from pathlib import Path
from utils.hml_client import hml


def reset_e_consultar(project_id):
    # 1. SETUP DE AMBIENTE (Garante carregamento do .env independente da pasta)
    raiz = Path(__file__).resolve().parent.parent
    caminho_env = raiz / ".env"

    if not caminho_env.exists():
        print(f"❌ Erro: Arquivo .env não encontrado em: {caminho_env}")
        return

    hml.configure(env_file=str(caminho_env))

    print(f"🚀 Iniciando Diagnóstico Robusto")
    print(f"📍 Projeto ID: {project_id}")
    print("-" * 60)

    conn = hml._db_conn("project")
    try:
        cur = conn.cursor()

        # PASSO 1: O projeto existe na tabela mestre?
        print("🔍 Checando existência na tabela 'project.project'...")
        cur.execute('SELECT "StatusId", "Created" FROM project.project WHERE id = %s', (project_id,))
        projeto_mestre = cur.fetchone()

        if not projeto_mestre:
            print("❌ ERRO: Este ID de projeto não foi encontrado no banco 'project'!")
            return
        else:
            print(f"✅ Projeto localizado! Criado em: {projeto_mestre[1]}")

        # PASSO 2: Existe algum rastro na tabela de geolocalização?
        print("🔍 Buscando registros na 'project.device_location_data'...")
        query = """
            SELECT 
                action, 
                location, 
                is_location_granted, 
                device_system, 
                created 
            FROM project.device_location_data 
            WHERE project_id = %s
            ORDER BY created DESC;
        """
        cur.execute(query, (project_id,))
        rows = cur.fetchall()

        if not rows:
            print("\n⚠️ RESULTADO: O projeto existe, mas NÃO HÁ NENHUMA linha de localização para ele.")
            print("💡 Causa provável: A automação ou o Portal não disparou o evento de captura.")
            return

        # PASSO 3: Formatação dos resultados encontrados
        print(f"\n✅ Foram encontrados {len(rows)} registro(s) de localização:")
        print("=" * 120)
        template = "{:<25} | {:<40} | {:<10} | {:<20}"
        print(template.format("AÇÃO", "LAT/LONG (TRATADA)", "PERMISSÃO", "DATA (UTC)"))
        print("-" * 120)

        for action, location, granted, system, created in rows:
            display_loc = "Vazio/Nulo"

            if location:
                # Tenta limpar e converter o texto 'location'
                try:
                    # Limpa possíveis caracteres de escape se vier stringificado
                    clean_loc = location.strip()
                    if clean_loc.startswith('{'):
                        loc_json = json.loads(clean_loc)
                        lat = loc_json.get('latitude') or loc_json.get('lat', '?')
                        lon = loc_json.get('longitude') or loc_json.get('long') or loc_json.get('lng', '?')
                        display_loc = f"Lat: {lat} / Lon: {lon}"
                    else:
                        display_loc = clean_loc  # Se for apenas "lat,long"
                except Exception:
                    display_loc = f"Erro Parse: {location[:30]}"

            permissao = "✅ SIM" if granted else "❌ NÃO"
            print(template.format(str(action), display_loc, permissao, str(created)))

    except Exception as e:
        print(f"❌ Falha técnica na consulta: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    # Substitua pelo ID que você quer testar
    ID_ALVO = "c19649b2-7e9a-4e9a-9f6a-130775f13928"
    reset_e_consultar(ID_ALVO)