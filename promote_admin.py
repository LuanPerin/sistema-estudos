import toml
import os
import requests
import json
import sqlite3

def execute_turso_http(url, token, sql, args=[]):
    # Convert libsql:// to https://
    http_url = url.replace("libsql://", "https://")
    endpoint = f"{http_url}/v2/pipeline"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Turso HTTP API format
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql,
                    "args": args
                }
            },
            {
                "type": "close"
            }
        ]
    }
    
    response = requests.post(endpoint, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")
        
    data = response.json()
    
    # Check for errors in results
    if "results" in data:
        for res in data["results"]:
            if res.get("type") == "error":
                raise Exception(f"SQL Error: {res.get('error')}")
                
    return data

def promote_to_admin():
    print("--- Promover Usuário a Admin ---")
    
    # Load secrets
    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    
    db_mode = "local"
    turso_url = None
    turso_token = None
    
    try:
        with open(secrets_path, "r") as f:
            secrets = toml.load(f)
            
        db_mode = secrets.get("DB_MODE", "local")
        turso_url = secrets.get("TURSO_URL")
        turso_token = secrets.get("TURSO_TOKEN")
        
        print(f"📂 Secrets carregados de: {secrets_path}")
        
    except Exception as e:
        print(f"⚠️ Erro ao ler secrets ({e}). Usando banco LOCAL.")

    email = input("Digite o email do usuário: ").strip()
    
    if not email:
        print("Email inválido.")
        return

    if db_mode == "online" and turso_url and turso_token:
        print(f"🌍 Conectando ao TURSO (HTTP): {turso_url}")
        try:
            # 1. Get User ID
            data = execute_turso_http(turso_url, turso_token, "SELECT CODIGO, NOME FROM EST_USUARIO WHERE EMAIL = ?", [{"type": "text", "value": email.lower()}])
            
            # Parse result (Turso HTTP returns specific JSON structure)
            # results[0] -> response for first request (execute)
            # response -> result -> rows
            rows = data["results"][0]["response"]["result"]["rows"]
            
            if not rows:
                print(f"❌ Usuário com email '{email}' não encontrado no Turso.")
                return
                
            # Turso rows are list of values, e.g. [[1, "Luan"]] (if JSON) or objects
            # Actually Turso HTTP v2 returns values in 'rows' array of arrays
            user_id = rows[0][0]["value"] # value wrapper
            user_name = rows[0][1]["value"]
            
            # 2. Update
            execute_turso_http(turso_url, turso_token, "UPDATE EST_USUARIO SET IS_ADMIN = 'S' WHERE CODIGO = ?", [{"type": "integer", "value": str(user_id)}])
            
            print(f"✅ Sucesso! O usuário '{user_name}' ({email}) agora é ADMINISTRADOR no Turso.")
            
        except Exception as e:
            print(f"❌ Erro no Turso: {e}")
            import traceback
            traceback.print_exc()
            
    else:
        print("🏠 Modo LOCAL. Conectando ao SQLite.")
        try:
            conn = sqlite3.connect('estudos.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT CODIGO, NOME FROM EST_USUARIO WHERE EMAIL = ?", (email.lower(),))
            user = cursor.fetchone()
            
            if not user:
                print(f"❌ Usuário com email '{email}' não encontrado.")
                return
                
            cursor.execute("UPDATE EST_USUARIO SET IS_ADMIN = 'S' WHERE CODIGO = ?", (user['CODIGO'],))
            conn.commit()
            print(f"✅ Sucesso! O usuário '{user['NOME']}' ({email}) agora é ADMINISTRADOR (Local).")
            conn.close()
        except Exception as e:
            print(f"❌ Erro local: {e}")

if __name__ == "__main__":
    promote_to_admin()
