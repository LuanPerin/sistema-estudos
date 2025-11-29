import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

print("Adding Sunday slot (Day 1)...")
# Grade 1, Day 1 (Sun), 08:00-12:00
cursor.execute("""
    INSERT INTO EST_GRADE_ITEM (COD_GRADE, DIA_SEMANA, HORA_INICIAL, HORA_FINAL, QTDE_MINUTOS)
    VALUES (1, 1, '08:00', '12:00', 240)
""")
conn.commit()
print("Slot added.")
conn.close()
