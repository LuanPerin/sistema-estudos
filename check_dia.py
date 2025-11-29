import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()
rows = cursor.execute("SELECT DATA, TIPO, HL_REALIZADA FROM EST_ESTUDOS ORDER BY DATA DESC LIMIT 20").fetchall()
print("Recent History (DATA | TIPO | HL):")
for r in rows:
    print(f"{r['DATA']} | {r['TIPO']} | {r['HL_REALIZADA']}")
conn.close()
