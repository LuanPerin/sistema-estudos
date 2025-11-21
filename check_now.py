import sqlite3
conn = sqlite3.connect('estudos.db')
c = conn.cursor()

print('=== DADOS EM EST_ESTUDOS ===')
for row in c.execute('SELECT CODIGO, COD_PROJETO, DATA, HL_REALIZADA, DESC_AULA FROM EST_ESTUDOS ORDER BY CODIGO'):
    print(row)

print('\n=== COUNT POR DATA ===')
for row in c.execute("SELECT DATA, COUNT(*) as QTD FROM EST_ESTUDOS GROUP BY DATA ORDER BY DATA"):
    print(f"Data: {row[0]}, Qtd: {row[1]}")

conn.close()
