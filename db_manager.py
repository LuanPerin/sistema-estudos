import sqlite3
import os

DB_NAME = 'estudos.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tables from metadata_operacoes.sql related to Studies
    
    # EST_AREA
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_AREA (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME TEXT
    )
    ''')
    
    # EST_MATERIA
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_MATERIA (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME TEXT,
        COD_AREA INTEGER,
        REVISAO TEXT, -- CHAR(1)
        FOREIGN KEY(COD_AREA) REFERENCES EST_AREA(CODIGO)
    )
    ''')
    
    # EST_CICLO
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_CICLO (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME TEXT,
        TOTAL_HORAS REAL,
        TOTAL_MINUTOS REAL,
        PADRAO TEXT -- CHAR(1)
    )
    ''')
    
    # EST_CICLO_ITEM
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_CICLO_ITEM (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        COD_CICLO INTEGER,
        INDICE INTEGER,
        COD_MATERIA INTEGER,
        QTDE_MINUTOS REAL,
        QTDE_HORAS REAL,
        FOREIGN KEY(COD_CICLO) REFERENCES EST_CICLO(CODIGO),
        FOREIGN KEY(COD_MATERIA) REFERENCES EST_MATERIA(CODIGO)
    )
    ''')
    
    # EST_GRADE_SEMANAL
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_GRADE_SEMANAL (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME TEXT,
        TOTAL_MINUTOS REAL,
        TOTAL_HORAS REAL,
        PADRAO TEXT,
        MEDIA_DIARIA REAL
    )
    ''')
    
    # EST_GRADE_ITEM
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_GRADE_ITEM (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        COD_GRADE INTEGER,
        INDICE INTEGER,
        QTDE_MINUTOS INTEGER,
        DIA_SEMANA INTEGER, -- 1=Dom, 2=Seg...
        QTDE_HORAS REAL,
        HORA_INICIAL TEXT, -- TIME
        HORA_FINAL TEXT, -- TIME
        FOREIGN KEY(COD_GRADE) REFERENCES EST_GRADE_SEMANAL(CODIGO)
    )
    ''')
    
    # EST_PROJETO
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_PROJETO (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME TEXT,
        DATA_INICIAL TEXT, -- DATE
        DATA_FINAL TEXT, -- DATE
        PADRAO TEXT
    )
    ''')
    
    # EST_ESTUDOS (History)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_ESTUDOS (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        COD_GRADE INTEGER,
        COD_PROJETO INTEGER,
        COD_CICLO INTEGER,
        COD_CICLO_ITEM INTEGER,
        COD_GRADE_ITEM INTEGER,
        DATA TEXT, -- DATE
        DIA INTEGER,
        CONT_CICLO INTEGER,
        HR_INICIAL_PREVISTA TEXT,
        HR_FINAL_PREVISTA TEXT,
        HR_INICIAL_EFETIVA TEXT,
        HR_FINAL_EFETIVA TEXT,
        HL_PREVISTA REAL,
        HL_REALIZADA REAL,
        DESC_AULA TEXT,
        VISUALIZADA_INICIAL INTEGER,
        VISUALIZADA_FINAL INTEGER,
        VISUALIZADA_QTDE INTEGER,
        QUESTOES INTEGER,
        CERTAS INTEGER,
        ERRADAS INTEGER,
        PCT_QUESTOES REAL,
        COD_REVISAO_24_H INTEGER,
        COD_REVISAO_7_D INTEGER,
        COD_REVISAO_30_D INTEGER,
        TIPO INTEGER, -- 1-3=Rev, 4=PDF, 5=Video
        AULA INTEGER,
        COD_ITEM_ANTERIOR INTEGER,
        SEMANA INTEGER,
        DIA_SEMANA INTEGER,
        FOREIGN KEY(COD_PROJETO) REFERENCES EST_PROJETO(CODIGO),
        FOREIGN KEY(COD_CICLO) REFERENCES EST_CICLO(CODIGO)
    )
    ''')
    
    # EST_PROGRAMACAO (Future Schedule - similar to EST_ESTUDOS but for planning)
    # In the original DB, EST_PROGRAMACAO was used in the SP. We'll create it here.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_PROGRAMACAO (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        COD_GRADE INTEGER,
        COD_PROJETO INTEGER,
        COD_CICLO INTEGER,
        COD_CICLO_ITEM INTEGER,
        DATA TEXT,
        DIA INTEGER,
        HR_INICIAL_PREVISTA TEXT,
        HR_FINAL_PREVISTA TEXT,
        HL_PREVISTA REAL,
        HL_REALIZADA REAL,
        DESC_AULA TEXT,
        TIPO INTEGER,
        STATUS TEXT DEFAULT 'PENDENTE' -- PENDENTE, CONCLUIDO, ADIADO
    )
    ''')
    
    # EST_USUARIO - Nova tabela para autenticação
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_USUARIO (
        CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME TEXT NOT NULL,
        EMAIL TEXT NOT NULL UNIQUE,
        SENHA_HASH TEXT NOT NULL,
        ATIVO TEXT DEFAULT 'S',
        IS_ADMIN TEXT DEFAULT 'N',
        DATA_CRIACAO TEXT,
        ULTIMO_ACESSO TEXT
    )
    ''')

    # EST_SESSAO - Tabela para persistência de login
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EST_SESSAO (
        TOKEN TEXT PRIMARY KEY,
        COD_USUARIO INTEGER,
        DATA_CRIACAO TEXT,
        DATA_EXPIRACAO TEXT,
        FOREIGN KEY(COD_USUARIO) REFERENCES EST_USUARIO(CODIGO)
    )
    ''')
    
    conn.commit()
    
    conn.commit()
    
    # ===== MIGRATION: Add COD_USUARIO to existing tables =====
    # Check if COD_USUARIO column exists, if not, add it
    
    tables_to_migrate = ['EST_AREA', 'EST_MATERIA', 'EST_PROJETO', 'EST_CICLO', 'EST_GRADE_SEMANAL']
    
    for table in tables_to_migrate:
        # Check if column exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'COD_USUARIO' not in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN COD_USUARIO INTEGER")
                print(f"Added COD_USUARIO to {table}")
            except Exception as e:
                print(f"Note: Could not add COD_USUARIO to {table}: {e}")

    # ===== MIGRATION: Add COD_MATERIA to EST_PROGRAMACAO and EST_ESTUDOS =====
    tables_with_materia = ['EST_PROGRAMACAO', 'EST_ESTUDOS']
    for table in tables_with_materia:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'COD_MATERIA' not in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN COD_MATERIA INTEGER")
                print(f"Added COD_MATERIA to {table}")
            except Exception as e:
                print(f"Note: Could not add COD_MATERIA to {table}: {e}")

    conn.commit()
    
    # Create default admin user if no users exist
    cursor.execute("SELECT COUNT(*) FROM EST_USUARIO")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        import bcrypt
        from datetime import datetime
        
        # Create admin user (admin@estudos.com / admin123)
        admin_password = "admin123"
        salt = bcrypt.gensalt()
        admin_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO EST_USUARIO (NOME, EMAIL, SENHA_HASH, ATIVO, IS_ADMIN, DATA_CRIACAO, ULTIMO_ACESSO)
            VALUES (?, ?, ?, 'S', 'S', ?, ?)
        """, ('Administrador', 'admin@estudos.com', admin_hash, datetime.now().isoformat(), datetime.now().isoformat()))
        
        admin_id = cursor.lastrowid
        
        # Associate existing data with admin user
        for table in tables_to_migrate:
            try:
                cursor.execute(f"UPDATE {table} SET COD_USUARIO = ? WHERE COD_USUARIO IS NULL", (admin_id,))
                print(f"Associated existing {table} records with admin user")
            except Exception as e:
                print(f"Note: Could not update {table}: {e}")
        
        conn.commit()
        print(f"\n✅ Default admin user created:")
        print(f"   Email: admin@estudos.com")
        print(f"   Senha: admin123")
        print(f"   IMPORTANTE: Altere a senha após o primeiro login!")
    
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
