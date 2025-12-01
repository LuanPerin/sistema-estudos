import sqlite3

def create_table():
    conn = sqlite3.connect('estudos.db')
    cursor = conn.cursor()
    
    # Create EST_CONTEUDO_CICLO table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS EST_CONTEUDO_CICLO (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        COD_CICLO_ITEM INTEGER NOT NULL,
        DESCRICAO TEXT NOT NULL,
        OBSERVACOES TEXT,
        FINALIZADO TEXT DEFAULT 'N',
        FOREIGN KEY (COD_CICLO_ITEM) REFERENCES EST_CICLO_ITEM (CODIGO) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()
    print("Tabela EST_CONTEUDO_CICLO criada com sucesso.")

if __name__ == "__main__":
    create_table()
