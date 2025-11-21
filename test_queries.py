import sqlite3
import pandas as pd
from datetime import date

conn = sqlite3.connect('estudos.db')
project_id = 1
today = date.today().isoformat()

print(f"Data de hoje: {today}")
print(f"Projeto ID: {project_id}")
print("\n" + "=" * 50)

# Query 1: Horas Hoje
print("\n1. HORAS HOJE:")
df_today = pd.read_sql_query(
    "SELECT DATA, HL_REALIZADA, DESC_AULA FROM EST_ESTUDOS WHERE DATA = ?", 
    conn, params=(today,)
)
print(f"Registros encontrados: {len(df_today)}")
print(df_today.to_string())

# Query 2: Agenda Diária
print("\n2. AGENDA DIÁRIA:")
df_agenda = pd.read_sql_query("""
    SELECT p.DESC_AULA, p.HR_INICIAL_PREVISTA, p.HL_PREVISTA
    FROM EST_PROGRAMACAO p
    WHERE p.DATA = ?
    ORDER BY p.HR_INICIAL_PREVISTA
""", conn, params=(today,))
print(f"Registros encontrados: {len(df_agenda)}")
print(df_agenda.to_string())

# Query 3: Evolução Projeto
print("\n3. EVOLUÇÃO PROJETO:")
total_prev = pd.read_sql_query(
    "SELECT SUM(HL_PREVISTA) as T FROM EST_PROGRAMACAO WHERE COD_PROJETO = ?", 
    conn, params=(project_id,)
).iloc[0]['T'] or 0.0
total_real = pd.read_sql_query(
    "SELECT SUM(HL_REALIZADA) as T FROM EST_ESTUDOS WHERE COD_PROJETO = ?", 
    conn, params=(project_id,)
).iloc[0]['T'] or 0.0

print(f"Total Previsto: {total_prev:.2f}h")
print(f"Total Realizado: {total_real:.2f}h")

# Query 4: Disciplinas
print("\n4. DISCIPLINAS:")
df_subj = pd.read_sql_query(
    "SELECT DESC_AULA, HL_REALIZADA FROM EST_ESTUDOS WHERE COD_PROJETO = ?", 
    conn, params=(project_id,)
)
print(f"Registros encontrados: {len(df_subj)}")
print(df_subj.to_string())

# Query 5: Gráfico - Plan
print("\n5. GRÁFICO - PLANEJADO:")
df_plan = pd.read_sql_query("""
    SELECT p.DATA, p.HL_PREVISTA, m.NOME as MATERIA 
    FROM EST_PROGRAMACAO p
    LEFT JOIN EST_CICLO_ITEM ci ON p.COD_CICLO_ITEM = ci.CODIGO
    LEFT JOIN EST_MATERIA m ON ci.COD_MATERIA = m.CODIGO
    WHERE p.COD_PROJETO = ?
""", conn, params=(project_id,))
print(f"Registros encontrados: {len(df_plan)}")
print(df_plan.head().to_string())

# Query 6: Gráfico - Real
print("\n6. GRÁFICO - REALIZADO:")
df_real = pd.read_sql_query("""
    SELECT DATA, HL_REALIZADA, DESC_AULA 
    FROM EST_ESTUDOS 
    WHERE COD_PROJETO = ?
""", conn, params=(project_id,))
print(f"Registros encontrados: {len(df_real)}")
print(df_real.to_string())

conn.close()
print("\n" + "=" * 50)
