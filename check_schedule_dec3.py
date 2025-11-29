import sqlite3
from db_manager import get_connection

def check_dec3():
    conn = get_connection()
    cursor = conn.cursor()
    
    target_date = '2025-12-09'
    print(f"Checking schedule for {target_date} (Project 1)...")
    
    rows = cursor.execute("""
        SELECT HR_INICIAL_PREVISTA, DESC_AULA, HL_PREVISTA
        FROM EST_PROGRAMACAO
        WHERE DATA = ? AND COD_PROJETO = 1
        ORDER BY HR_INICIAL_PREVISTA
    """, (target_date,)).fetchall()
    
    if not rows:
        print("No tasks found for this date.")
    else:
        for r in rows:
            print(f"- {r['HR_INICIAL_PREVISTA']}: {r['DESC_AULA']} ({r['HL_PREVISTA']:.2f}h)")
            
    conn.close()

if __name__ == "__main__":
    check_dec3()
