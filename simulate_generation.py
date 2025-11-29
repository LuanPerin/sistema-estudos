from study_engine import generate_schedule
from datetime import date
from db_manager import get_connection

# Get the first project for the admin user (usually ID 1)
conn = get_connection()
proj = conn.execute("SELECT CODIGO FROM EST_PROJETO WHERE COD_USUARIO = 1 LIMIT 1").fetchone()
conn.close()

if proj:
    pid = proj['CODIGO']
    print(f"Generating schedule for Project ID: {pid}")
    msg = generate_schedule(pid, date.today(), 7)
    print(f"Result: {msg}")
else:
    print("No project found for user 1")
