import sqlite3
import pandas as pd
from db_manager import get_connection

def debug_data():
    conn = get_connection()
    
    print("\n=== USERS ===")
    users = pd.read_sql_query("SELECT CODIGO, NOME, EMAIL FROM EST_USUARIO", conn)
    print(users)
    
    print("\n=== CYCLES ===")
    cycles = pd.read_sql_query("SELECT CODIGO, NOME, PADRAO, COD_USUARIO FROM EST_CICLO", conn)
    print(cycles)
    
    print("\n=== GRADES ===")
    grades = pd.read_sql_query("SELECT CODIGO, NOME, PADRAO, COD_USUARIO FROM EST_GRADE_SEMANAL", conn)
    print(grades)
    
    conn.close()

if __name__ == "__main__":
    debug_data()
