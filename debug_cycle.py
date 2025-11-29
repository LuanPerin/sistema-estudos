import sqlite3
import pandas as pd
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

print("--- Projects ---")
projects = cursor.execute("SELECT * FROM EST_PROJETO").fetchall()
for p in projects:
    print(f"Project: {p['CODIGO']} - {p['NOME']}")
    
    user_id = p['COD_USUARIO']
    print(f"  User ID: {user_id}")
    
    # Get Cycle
    ciclo = cursor.execute("SELECT CODIGO FROM EST_CICLO WHERE PADRAO = 'S' AND COD_USUARIO = ?", (user_id,)).fetchone()
    if not ciclo:
        print("  No default cycle found.")
        continue
        
    cod_ciclo = ciclo['CODIGO']
    print(f"  Cycle ID: {cod_ciclo}")
    
    # Run the query from study_engine.py
    print("  --- Cycle Items Query Result ---")
    try:
        cycle_items = cursor.execute("""
            SELECT ci.*, m.NOME as MATERIA 
            FROM EST_CICLO_ITEM ci
            JOIN EST_MATERIA m ON ci.COD_MATERIA = m.CODIGO
            WHERE ci.COD_CICLO = ? 
            ORDER BY ci.INDICE
        """, (cod_ciclo,)).fetchall()
        
        for item in cycle_items:
            # Check if MATERIA key exists and print it
            materia_val = item['MATERIA'] if 'MATERIA' in item.keys() else "KEY_MISSING"
            print(f"    Item {item['CODIGO']}: COD_MATERIA={item['COD_MATERIA']} | MATERIA='{materia_val}'")
            
    except Exception as e:
        print(f"    Error executing query: {e}")

conn.close()
