import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

print("Fixing NULL TIPO in EST_ESTUDOS...")
cursor.execute("UPDATE EST_ESTUDOS SET TIPO = 4 WHERE TIPO IS NULL")
conn.commit()
print(f"Updated {cursor.rowcount} rows.")

conn.close()
