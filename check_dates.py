from datetime import date
import sqlite3

conn = sqlite3.connect('estudos.db')
c = conn.cursor()

print('Data do sistema:', date.today().isoformat())

print('\nDatas em EST_ESTUDOS:')
for row in c.execute('SELECT DISTINCT DATA FROM EST_ESTUDOS ORDER BY DATA'):
    print('  ', row[0])

print('\nDatas em EST_PROGRAMACAO:')
for row in c.execute('SELECT DISTINCT DATA FROM EST_PROGRAMACAO ORDER BY DATA'):
    print('  ', row[0])

conn.close()
