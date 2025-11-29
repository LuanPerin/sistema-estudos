import sqlite3
from datetime import date, timedelta
from db_manager import get_connection
from study_engine import generate_schedule

conn = get_connection()
cursor = conn.cursor()

# 1. Clear Schedule
print("Clearing Schedule...")
cursor.execute("DELETE FROM EST_PROGRAMACAO")

# 2. Get Project and User
proj = cursor.execute("SELECT CODIGO, COD_USUARIO FROM EST_PROJETO WHERE COD_USUARIO = 1 LIMIT 1").fetchone()
pid = proj['CODIGO']
uid = proj['COD_USUARIO']

# 3. Insert Dummy History for Yesterday (to trigger 24h revision)
yesterday = date.today() - timedelta(days=1)
print(f"Inserting dummy history for {yesterday}...")

# Find a subject that is NOT revision
subj = cursor.execute("SELECT CODIGO FROM EST_MATERIA WHERE REVISAO = 'N' AND COD_USUARIO = ? LIMIT 1", (uid,)).fetchone()
if subj:
    cursor.execute("""
        INSERT INTO EST_ESTUDOS (COD_MATERIA, DATA, HL_REALIZADA, TIPO, COD_PROJETO, DIA, DESC_AULA)
        VALUES (?, ?, 1.0, 4, ?, 1, 'Dummy History')
    """, (subj['CODIGO'], yesterday.isoformat(), pid))
    conn.commit()
    print("Dummy history inserted.")
else:
    print("No subject found.")

# 4. Generate Schedule
print("Generating Schedule...")
msg = generate_schedule(pid, date.today(), 7)
print(f"Result: {msg}")

conn.close()
