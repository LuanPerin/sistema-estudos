
import sqlite3

conn = sqlite3.connect('estudos.db')
cursor = conn.cursor()

# Fix the CORRECT record: PORTUGUÊS at 08:00 (ID 3177 based on previous output order)
# 0: 3177 (08:00)
# 1: 3178 (09:00)
# 2: 3179 (10:00)
# 3: 3180 (11:00) - This one was fixed by mistake

cursor.execute("UPDATE EST_PROGRAMACAO SET STATUS = 'CONCLUIDO' WHERE CODIGO = 3177")
conn.commit()

print(f"Fixed record 3177 (PORTUGUÊS). Rows affected: {cursor.rowcount}")

# Optional: Revert 3180 if needed, but user probably doesn't mind if it's done.
# Let's leave 3180 as is unless user complains.

conn.close()
