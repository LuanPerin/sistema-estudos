import sqlite3
import pandas as pd
from datetime import date, timedelta

conn = sqlite3.connect('estudos.db')
project_id = 1
today = date.today().isoformat()

print("="*60)
print("TESTE DAS QUERIES COM project_id = 1")
print("="*60)

# 1. Horas Hoje
print("\n1. HORAS HOJE:")
print(f"   Query: SELECT SUM(HL_REALIZADA) FROM EST_ESTUDOS WHERE DATA = '{today}' AND COD_PROJETO = {project_id}")
df_today = pd.read_sql_query(
    "SELECT SUM(HL_REALIZADA) as TOTAL_HORAS FROM EST_ESTUDOS WHERE DATA = ? AND COD_PROJETO = ?", 
    conn, params=(today, project_id)
)
horas_hoje = df_today['TOTAL_HORAS'].iloc[0] if df_today['TOTAL_HORAS'].iloc[0] else 0.0
print(f"   Resultado: {horas_hoje}h")

# 2. Dias Seguidos
print("\n2. DIAS SEGUIDOS:")
print(f"   Query: SELECT DISTINCT DATA FROM EST_ESTUDOS WHERE COD_PROJETO = {project_id}")
dates_df = pd.read_sql_query(
    "SELECT DISTINCT DATA FROM EST_ESTUDOS WHERE COD_PROJETO = ? ORDER BY DATA DESC", 
    conn, params=(project_id,)
)
print(f"   Datas encontradas: {dates_df['DATA'].tolist()}")

# 3. Agenda Diária
print("\n3. AGENDA DIÁRIA:")
print(f"   Query: SELECT FROM EST_PROGRAMACAO WHERE DATA = '{today}' AND COD_PROJETO = {project_id}")
df_agenda = pd.read_sql_query("""
    SELECT DESC_AULA, HR_INICIAL_PREVISTA, HL_PREVISTA
    FROM EST_PROGRAMACAO
    WHERE DATA = ? AND COD_PROJETO = ?
""", conn, params=(today, project_id))
print(f"   Registros: {len(df_agenda)}")
if len(df_agenda) > 0:
    print(df_agenda.to_string())

# 4. Semana
dt_today = date.today()
idx_weekday = (dt_today.weekday() + 1) % 7
start_week = dt_today - timedelta(days=idx_weekday)
end_week = start_week + timedelta(days=6)

print(f"\n4. EVOLUÇÃO SEMANA:")
print(f"   Período: {start_week} a {end_week}")

week_prog = pd.read_sql_query("""
    SELECT DATA, SUM(HL_PREVISTA) as HL 
    FROM EST_PROGRAMACAO 
    WHERE DATA BETWEEN ? AND ? AND COD_PROJETO = ?
    GROUP BY DATA
""", conn, params=(start_week.isoformat(), end_week.isoformat(), project_id))
print(f"   Programação: {len(week_prog)} datas")
if len(week_prog) > 0:
    print(week_prog.to_string())

week_real = pd.read_sql_query("""
    SELECT DATA, SUM(HL_REALIZADA) as HL 
    FROM EST_ESTUDOS 
    WHERE DATA BETWEEN ? AND ? AND COD_PROJETO = ?
    GROUP BY DATA
""", conn, params=(start_week.isoformat(), end_week.isoformat(), project_id))
print(f"   Estudos: {len(week_real)} datas")
if len(week_real) > 0:
    print(week_real.to_string())

# 5. Disciplinas
print(f"\n5. DISCIPLINAS:")
df_subj = pd.read_sql_query(
    "SELECT DESC_AULA, HL_REALIZADA FROM EST_ESTUDOS WHERE COD_PROJETO = ?", 
    conn, params=(project_id,)
)
print(f"   Registros: {len(df_subj)}")
if len(df_subj) > 0:
    print(df_subj.to_string())

conn.close()
print("\n" + "="*60)
