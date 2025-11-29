import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

print("Cleaning up dummy history...")
cursor.execute("DELETE FROM EST_ESTUDOS WHERE DESC_AULA = 'Browser Test Dummy'")
conn.commit()
print(f"Deleted {cursor.rowcount} records.")
conn.close()
