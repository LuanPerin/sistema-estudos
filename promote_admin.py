from db_manager import get_connection
import sys

def promote_to_admin():
    print("--- Promover Usuário a Admin ---")
    email = input("Digite o email do usuário: ").strip()
    
    if not email:
        print("Email inválido.")
        return

    conn = get_connection()
    
    # Check connection type
    if 'LibsqlConnectionWrapper' in str(type(conn)):
        print("🌍 Conectado ao banco: TURSO (Online)")
    else:
        print("🏠 Conectado ao banco: LOCAL (SQLite)")
        
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT CODIGO, NOME FROM EST_USUARIO WHERE EMAIL = ?", (email.lower(),))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuário com email '{email}' não encontrado.")
            return
            
        # Update
        cursor.execute("UPDATE EST_USUARIO SET IS_ADMIN = 'S' WHERE CODIGO = ?", (user['CODIGO'],))
        conn.commit()
        
        print(f"✅ Sucesso! O usuário '{user['NOME']}' ({email}) agora é ADMINISTRADOR.")
        print("👉 Faça logout e login novamente para ver o menu 'Admin Usuários'.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    promote_to_admin()
