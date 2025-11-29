import sqlite3
from datetime import date
from db_manager import get_connection
from study_engine import generate_schedule

conn = get_connection()
cursor = conn.cursor()

# Project 1
pid = 1

# Start Date: 30/11/2025
start_date = date(2025, 11, 30)

print(f"Generating Schedule for 60 days starting {start_date}...")
msg = generate_schedule(pid, start_date, 60)
print(f"Result: {msg}")

print("\nInspecting Generated Schedule (Revisions Only):")
revisions = cursor.execute("""
    SELECT DATA, DESC_AULA, HL_PREVISTA, HR_INICIAL_PREVISTA
    FROM EST_PROGRAMACAO 
    WHERE COD_PROJETO = ? AND DESC_AULA LIKE '%Revisão%'
    ORDER BY DATA
""", (pid,)).fetchall()

if not revisions:
    print("❌ NO REVISIONS SCHEDULED.")
else:
    for r in revisions:
        print(f"  - {r['DATA']} ({r['HR_INICIAL_PREVISTA']}): {r['DESC_AULA']} ({r['HL_PREVISTA']:.2f}h)")

conn.close()
