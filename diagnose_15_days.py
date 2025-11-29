import sqlite3
from datetime import date, timedelta
from db_manager import get_connection
from study_engine import generate_schedule
import pandas as pd

conn = get_connection()
cursor = conn.cursor()

# 1. Check User and Project
proj = cursor.execute("SELECT CODIGO, COD_USUARIO FROM EST_PROJETO WHERE COD_USUARIO = 1 LIMIT 1").fetchone()
if not proj:
    print("No project found.")
    exit()
    
pid = proj['CODIGO']
uid = proj['COD_USUARIO']
print(f"Project: {pid}, User: {uid}")

# 2. Check History for the last 30 days (triggers for revisions)
today = date.today()
start_check = today - timedelta(days=35)
print(f"\nChecking history since {start_check}...")

history = cursor.execute("""
    SELECT DATA, SUM(HL_REALIZADA) as TOTAL 
    FROM EST_ESTUDOS 
    WHERE COD_PROJETO = ? AND DATA >= ?
    GROUP BY DATA
    ORDER BY DATA
""", (pid, start_check.isoformat())).fetchall()

if not history:
    print("⚠️ NO STUDY HISTORY FOUND in the last 35 days.")
    print("   -> Consequently, NO automatic revisions (24h, 7d, 30d) will be generated.")
else:
    print(f"Found {len(history)} days with study history:")
    for h in history:
        print(f"  - {h['DATA']}: {h['TOTAL']}h")

# 3. Generate Schedule for 15 days
print("\nGenerating Schedule for 30 days...")
msg = generate_schedule(pid, today, 30)
print(f"Result: {msg}")

# 4. Inspect Generated Revisions
print("\nInspecting Generated Schedule (Revisions Only):")
revisions = cursor.execute("""
    SELECT DATA, DESC_AULA, HL_PREVISTA 
    FROM EST_PROGRAMACAO 
    WHERE COD_PROJETO = ? AND DESC_AULA LIKE '%Revisão%'
    ORDER BY DATA
""", (pid,)).fetchall()

if not revisions:
    print("❌ NO REVISIONS SCHEDULED.")
else:
    for r in revisions:
        print(f"  - {r['DATA']}: {r['DESC_AULA']} ({r['HL_PREVISTA']:.2f}h)")

conn.close()
