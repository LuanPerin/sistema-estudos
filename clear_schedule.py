import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

print("Cleaning EST_PROGRAMACAO...")
cursor.execute("DELETE FROM EST_PROGRAMACAO")
conn.commit()
print(f"Deleted {cursor.rowcount} rows.")

conn.close()
