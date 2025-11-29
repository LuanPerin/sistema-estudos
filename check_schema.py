import sqlite3
from db_manager import get_connection

conn = get_connection()
cursor = conn.cursor()
cols = cursor.execute("PRAGMA table_info(EST_ESTUDOS)").fetchall()
for c in cols:
    print(dict(c))
conn.close()
