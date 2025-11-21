import sqlite3
import pandas as pd

conn = sqlite3.connect('estudos.db')

print("=" * 50)
print("VERIFICAÇÃO DO BANCO DE DADOS")
print("=" * 50)

# Total de registros
print("\n📊 TOTAIS:")
print(f"  EST_ESTUDOS: {pd.read_sql_query('SELECT COUNT(*) as total FROM EST_ESTUDOS', conn).iloc[0]['total']}")
print(f"  EST_PROGRAMACAO: {pd.read_sql_query('SELECT COUNT(*) as total FROM EST_PROGRAMACAO', conn).iloc[0]['total']}")

# EST_ESTUDOS
print("\n📚 EST_ESTUDOS (primeiros 5):")
df_estudos = pd.read_sql_query("""
    SELECT CODIGO, COD_PROJETO, DATA, HL_REALIZADA, DESC_AULA 
    FROM EST_ESTUDOS 
    ORDER BY CODIGO DESC
    LIMIT 5
""", conn)
print(df_estudos.to_string())

# EST_PROGRAMACAO
print("\n📅 EST_PROGRAMACAO (primeiros 5):")
df_prog = pd.read_sql_query("""
    SELECT CODIGO, COD_PROJETO, DATA, HL_PREVISTA, DESC_AULA, STATUS 
    FROM EST_PROGRAMACAO 
    ORDER BY CODIGO DESC
    LIMIT 5
""", conn)
print(df_prog.to_string())

# Projetos
print("\n🎯 EST_PROJETO:")
df_proj = pd.read_sql_query("SELECT * FROM EST_PROJETO", conn)
print(df_proj.to_string())

# Verificar dados por projeto
print("\n📊 DADOS POR PROJETO:")
for idx, proj_row in df_proj.iterrows():
    proj_id = proj_row['CODIGO']
    proj_name = proj_row['NOME']
    
    estudos_count = pd.read_sql_query(f"SELECT COUNT(*) as total FROM EST_ESTUDOS WHERE COD_PROJETO = {proj_id}", conn).iloc[0]['total']
    prog_count = pd.read_sql_query(f"SELECT COUNT(*) as total FROM EST_PROGRAMACAO WHERE COD_PROJETO = {proj_id}", conn).iloc[0]['total']
    
    print(f"\n  Projeto {proj_id} - {proj_name}:")
    print(f"    Estudos: {estudos_count}")
    print(f"    Programação: {prog_count}")

conn.close()
print("\n" + "=" * 50)
