import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

print("Cleaning up test history...")
cursor.execute("DELETE FROM EST_ESTUDOS WHERE DESC_AULA = 'Dummy History'")
conn.commit()
print(f"Deleted {cursor.rowcount} test records.")

conn.close()
