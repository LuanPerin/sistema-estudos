import sqlite3
import pandas as pd
from db_manager import get_connection

def check_schedule():
    conn = get_connection()
    
    print("\n=== PROJECTS ===")
    projects = pd.read_sql_query("SELECT CODIGO, NOME, COD_USUARIO FROM EST_PROJETO", conn)
    print(projects)
    
    print("\n=== SCHEDULE (EST_PROGRAMACAO) ===")
    # Get all schedule items
    schedule = pd.read_sql_query("SELECT CODIGO, COD_PROJETO, DATA, HR_INICIAL_PREVISTA, STATUS FROM EST_PROGRAMACAO", conn)
    print(schedule)
    
    conn.close()

if __name__ == "__main__":
    check_schedule()
