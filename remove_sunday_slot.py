import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

print("Removing Sunday slot (Day 1)...")
cursor.execute("DELETE FROM EST_GRADE_ITEM WHERE COD_GRADE = 1 AND DIA_SEMANA = 1 AND HORA_INICIAL = '08:00'")
conn.commit()
print("Slot removed.")
conn.close()
