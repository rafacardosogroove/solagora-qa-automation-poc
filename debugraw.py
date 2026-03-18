import json
from pathlib import Path
from utils.hml_client import hml


def extrair_dados_geograficos(project_id):
    raiz = Path(__file__).resolve().parent.parent
    hml.configure(env_file=str(raiz / ".env"))

    conn = hml._db_conn("project")
    try:
        cur = conn.cursor()
        query = """
            SELECT action, location, is_location_granted, created 
            FROM project.device_location_data 
            WHERE project_id = %s ORDER BY created DESC;
        """
        cur.execute(query, (project_id,))
        rows = cur.fetchall()

        print(f"\n🌍 AUDITORIA DE GEOLOCALIZAÇÃO: {project_id}")
        print("=" * 90)
        template = "{:<25} | {:<15} | {:<15} | {:<15}"
        print(template.format("ETAPA", "LATITUDE", "LONGITUDE", "STATUS GPS"))
        print("-" * 90)

        for action, location, granted, created in rows:
            lat, lon, status = "N/A", "N/A", "BLOQUEADO"

            if location and location != 'null':
                try:
                    data = json.loads(location)
                    lat = data.get("Latitude", "Erro")
                    lon = data.get("Longitude", "Erro")
                    status = "CAPTURADO"
                    if lat == 37.4220936: status = "SIMULADO (GOOGLE)"
                except:
                    status = "ERRO FORMATO"

            print(template.format(str(action), str(lat), str(lon), status))

    finally:
        conn.close()


if __name__ == "__main__":
    extrair_dados_geograficos("c19649b2-7e9a-4e9a-9f6a-130775f13928")