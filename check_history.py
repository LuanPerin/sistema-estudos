import sqlite3
from db_manager import get_connection

def check_history():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT DATA, TIPO FROM EST_ESTUDOS WHERE COD_PROJETO = 1 ORDER BY DATA").fetchall()
    print("History Dates:")
    for r in rows:
        print(f"{r['DATA']} (Tipo {r['TIPO']})")
    conn.close()

if __name__ == "__main__":
    check_history()
