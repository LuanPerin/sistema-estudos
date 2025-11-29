import sqlite3
from datetime import date, timedelta
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()

# 1. Clear Schedule
print("Clearing Schedule...")
cursor.execute("DELETE FROM EST_PROGRAMACAO")

# 2. Insert Dummy History for Yesterday (to trigger 24h revision)
today = date.today()
yesterday = today - timedelta(days=1)
print(f"Inserting dummy history for {yesterday}...")

# Check if exists first to avoid duplicates
cursor.execute("DELETE FROM EST_ESTUDOS WHERE DESC_AULA = 'Browser Test Dummy'")

cursor.execute("""
    INSERT INTO EST_ESTUDOS (COD_PROJETO, COD_MATERIA, DATA, HL_REALIZADA, DESC_AULA, TIPO)
    VALUES (1, 1, '2025-11-23', 6.0, 'Restored History', 4)
""", )

conn.commit()
print("Preparation complete.")
conn.close()
