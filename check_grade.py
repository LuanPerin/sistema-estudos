import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

# Get default grade
grade = cursor.execute("SELECT CODIGO FROM EST_GRADE_SEMANAL WHERE COD_USUARIO = 1 LIMIT 1").fetchone()
if not grade:
    print("No grade found.")
else:
    gid = grade['CODIGO']
    print(f"Grade ID: {gid}")
    items = cursor.execute("SELECT * FROM EST_GRADE_ITEM WHERE COD_GRADE = ? ORDER BY DIA_SEMANA, HORA_INICIAL", (gid,)).fetchall()
    for i in items:
        print(f"Day {i['DIA_SEMANA']}: {i['HORA_INICIAL']} - {i['HORA_FINAL']} ({i['QTDE_MINUTOS']} min)")

conn.close()
