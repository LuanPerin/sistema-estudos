import sqlite3
import pandas as pd
from db_manager import get_connection

def check_schema():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"🔍 Verificando {len(tables)} tabelas no banco de dados...\n")
    
    segregation_map = {
        'EST_USUARIO': 'N/A (Tabela de Usuários)',
        'EST_AREA': 'Direta (COD_USUARIO)',
        'EST_MATERIA': 'Direta (COD_USUARIO)',
        'EST_PROJETO': 'Direta (COD_USUARIO)',
        'EST_CICLO': 'Direta (COD_USUARIO)',
        'EST_GRADE_SEMANAL': 'Direta (COD_USUARIO)',
        'EST_CICLO_ITEM': 'Indireta (via EST_CICLO)',
        'EST_GRADE_ITEM': 'Indireta (via EST_GRADE_SEMANAL)',
        'EST_PROGRAMACAO': 'Indireta (via EST_PROJETO)',
        'EST_ESTUDOS': 'Indireta (via EST_PROJETO)'
    }
    
    status_report = []
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        has_user = 'COD_USUARIO' in columns
        has_project = 'COD_PROJETO' in columns
        has_cycle = 'COD_CICLO' in columns
        has_grade = 'COD_GRADE' in columns
        
        status = "❌ NÃO SEGREGADA"
        details = ""
        
        if table in segregation_map:
            expected = segregation_map[table]
            
            if "Direta" in expected:
                if has_user:
                    status = "✅ OK (Direta)"
                else:
                    status = "❌ FALHA (Falta COD_USUARIO)"
            elif "Indireta" in expected:
                if "EST_PROJETO" in expected and has_project:
                    status = "✅ OK (Indireta via Projeto)"
                elif "EST_CICLO" in expected and has_cycle:
                    status = "✅ OK (Indireta via Ciclo)"
                elif "EST_GRADE_SEMANAL" in expected and has_grade:
                    status = "✅ OK (Indireta via Grade)"
            else:
                status = "✅ OK (Tabela Base)"
        
        print(f"Tabela: {table:<20} | {status}")
        if not has_user and "Direta" in segregation_map.get(table, ""):
             print(f"   ⚠️ ALERTA: Coluna COD_USUARIO não encontrada!")

    conn.close()

if __name__ == "__main__":
    check_schema()
