
import sqlite3
import pandas as pd

conn = sqlite3.connect('estudos.db')
cursor = conn.cursor()

# Get Project ID for 'Banco do Brasil 2026' (User 1)
proj = cursor.execute("SELECT CODIGO FROM EST_PROJETO WHERE NOME LIKE '%Banco do Brasil%'").fetchone()
project_id = proj[0] if proj else 1

print(f"Project ID: {project_id}")

print("\n--- SCHEDULE FOR 2025-11-29 ---")
df = pd.read_sql_query("""
    SELECT CODIGO, DATA, HR_INICIAL_PREVISTA, DESC_AULA, STATUS 
    FROM EST_PROGRAMACAO 
    WHERE COD_PROJETO = ? AND DATA = '2025-11-29'
    ORDER BY HR_INICIAL_PREVISTA
""", conn, params=(project_id,))

print(df)
conn.close()
