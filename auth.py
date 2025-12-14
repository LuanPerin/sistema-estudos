"""
Módulo de autenticação para o sistema de estudos.
Gerencia login, logout, criação de usuários e verificação de senhas.
"""

import bcrypt
import sqlite3
import streamlit as st
from datetime import datetime, timedelta
import uuid
import extra_streamlit_components as stx
from db_manager import get_connection


def hash_password(password: str) -> str:
    """
    Cria hash bcrypt da senha.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash bcrypt da senha
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica se a senha corresponde ao hash.
    
    Args:
        password: Senha em texto plano
        password_hash: Hash armazenado no banco
        
    Returns:
        True se a senha está correta, False caso contrário
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

import re

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Verifica se a senha atende aos requisitos de segurança.
    Requisitos:
    - Mínimo 8 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial (!@#$%^&*(),.?":{}|<>)
    """
    if len(password) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres"
        
    if not re.search(r'[A-Z]', password):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
        
    if not re.search(r'\d', password):
        return False, "Senha deve conter pelo menos um número"
        
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Senha deve conter pelo menos um caractere especial"
        
    return True, ""


def create_user(nome: str, email: str, senha: str) -> dict:
    """
    Cria novo usuário no sistema.
    
    Args:
        nome: Nome completo do usuário
        email: Email (usado como username)
        senha: Senha em texto plano (será hasheada)
        
    Returns:
        dict com 'success' (bool) e 'message' ou 'user_id'
    """
    # Validações básicas
    if not nome or len(nome.strip()) < 3:
        return {'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'}
    
    if not email or '@' not in email:
        return {'success': False, 'message': 'Email inválido'}
    
    if not senha:
        return {'success': False, 'message': 'Senha é obrigatória'}
        
    is_valid, msg = validate_password_strength(senha)
    if not is_valid:
        return {'success': False, 'message': msg}
        
    is_valid, msg = validate_password_strength(senha)
    if not is_valid:
        return {'success': False, 'message': msg}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se email já existe
        cursor.execute("SELECT CODIGO FROM EST_USUARIO WHERE EMAIL = ?", (email.lower(),))
        if cursor.fetchone():
            return {'success': False, 'message': 'Email já cadastrado'}
        
        # Hash da senha
        senha_hash = hash_password(senha)
        
        # Criar usuário
        cursor.execute("""
            INSERT INTO EST_USUARIO (NOME, EMAIL, SENHA_HASH, ATIVO, DATA_CRIACAO, ULTIMO_ACESSO)
            VALUES (?, ?, ?, 'S', ?, ?)
        """, (nome.strip(), email.lower(), senha_hash, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        return {
            'success': True,
            'user_id': user_id,
            'user': {
                'CODIGO': user_id,
                'NOME': nome.strip(),
                'EMAIL': email.lower(),
                'ATIVO': 'S',
                'IS_ADMIN': 0
            },
            'message': 'Usuário criado com sucesso!'
        }
        
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'Erro ao criar usuário: {str(e)}'}
    finally:
        conn.close()


def authenticate(email: str, senha: str) -> dict:
    """
    Autentica usuário verificando email e senha.
    
    Args:
        email: Email do usuário
        senha: Senha em texto plano
        
    Returns:
        dict com dados do usuário se autenticado, None caso contrário
    """
    if not email or not senha:
        return None
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar usuário por email
        cursor.execute("""
            SELECT CODIGO, NOME, EMAIL, SENHA_HASH, ATIVO, IS_ADMIN
            FROM EST_USUARIO
            WHERE EMAIL = ?
        """, (email.lower(),))
        
        user = cursor.fetchone()
        
        if not user:
            return None
        
        user_id, nome, email_db, senha_hash, ativo, is_admin = user
        
        # Verificar se usuário está ativo
        if ativo != 'S':
            return None
        
        # Verificar senha
        if not verify_password(senha, senha_hash):
            return None
        
        # Atualizar último acesso
        cursor.execute("""
            UPDATE EST_USUARIO
            SET ULTIMO_ACESSO = ?
            WHERE CODIGO = ?
        """, (datetime.now().isoformat(), user_id))
        conn.commit()
        
        # Retornar dados do usuário
        return {
            'CODIGO': user_id,
            'NOME': nome,
            'EMAIL': email_db,
            'ATIVO': ativo,
            'IS_ADMIN': is_admin
        }
        
    except Exception:
        return None
    finally:
        conn.close()


def update_user(user_id: int, nome: str, email: str, senha: str = None) -> dict:
    """
    Atualiza dados do usuário.
    
    Args:
        user_id: ID do usuário
        nome: Novo nome
        email: Novo email
        senha: Nova senha (opcional)
        
    Returns:
        dict com 'success' (bool) e 'message'
    """
    if not nome or len(nome.strip()) < 3:
        return {'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'}
    
    if not email or '@' not in email:
        return {'success': False, 'message': 'Email inválido'}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se email já existe (para outro usuário)
        cursor.execute("SELECT CODIGO FROM EST_USUARIO WHERE EMAIL = ? AND CODIGO != ?", (email.lower(), user_id))
        if cursor.fetchone():
            return {'success': False, 'message': 'Email já cadastrado por outro usuário'}
        
        if senha:
            # Validar força da senha
            is_valid, msg = validate_password_strength(senha)
            if not is_valid:
                return {'success': False, 'message': msg}
                
            # Atualizar com senha
            senha_hash = hash_password(senha)
            cursor.execute("""
                UPDATE EST_USUARIO 
                SET NOME = ?, EMAIL = ?, SENHA_HASH = ?
                WHERE CODIGO = ?
            """, (nome.strip(), email.lower(), senha_hash, user_id))
        else:
            # Atualizar sem senha
            cursor.execute("""
                UPDATE EST_USUARIO 
                SET NOME = ?, EMAIL = ?
                WHERE CODIGO = ?
            """, (nome.strip(), email.lower(), user_id))
            
        conn.commit()
        
        return {'success': True, 'message': 'Dados atualizados com sucesso!'}
        
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'Erro ao atualizar: {str(e)}'}
    finally:
        conn.close()





def get_all_users() -> list:
    """
    Retorna lista de todos os usuários (apenas para admin).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Include Auth Method logic
        cursor.execute("""
            SELECT 
                CODIGO, NOME, EMAIL, ATIVO, IS_ADMIN, DATA_CRIACAO, ULTIMO_ACESSO,
                CASE WHEN SENHA_HASH = 'GOOGLE_AUTH' THEN 'Google' ELSE 'Senha' END as METODO_AUTH
            FROM EST_USUARIO 
            ORDER BY NOME
        """)
        # Convert to dict list
        columns = [col[0] for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results
    except Exception:
        return []
    finally:
        conn.close()


def admin_update_user(user_id: int, nome: str, email: str, senha: str = None, ativo: str = 'S', is_admin: str = 'N') -> dict:
    """
    Atualiza dados do usuário (Modo Admin - permite alterar tudo).
    """
    if not nome or len(nome.strip()) < 3:
        return {'success': False, 'message': 'Nome deve ter pelo menos 3 caracteres'}
    
    if not email or '@' not in email:
        return {'success': False, 'message': 'Email inválido'}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se email já existe (para outro usuário)
        cursor.execute("SELECT CODIGO FROM EST_USUARIO WHERE EMAIL = ? AND CODIGO != ?", (email.lower(), user_id))
        if cursor.fetchone():
            return {'success': False, 'message': 'Email já cadastrado por outro usuário'}
        
        if senha:
            # Validar força da senha
            is_valid, msg = validate_password_strength(senha)
            if not is_valid:
                return {'success': False, 'message': msg}

            # Atualizar com senha
            senha_hash = hash_password(senha)
            cursor.execute("""
                UPDATE EST_USUARIO 
                SET NOME = ?, EMAIL = ?, SENHA_HASH = ?, ATIVO = ?, IS_ADMIN = ?
                WHERE CODIGO = ?
            """, (nome.strip(), email.lower(), senha_hash, ativo, is_admin, user_id))
        else:
            # Atualizar sem senha
            cursor.execute("""
                UPDATE EST_USUARIO 
                SET NOME = ?, EMAIL = ?, ATIVO = ?, IS_ADMIN = ?
                WHERE CODIGO = ?
            """, (nome.strip(), email.lower(), ativo, is_admin, user_id))
            
        conn.commit()
        return {'success': True, 'message': 'Usuário atualizado com sucesso!'}
        
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'Erro ao atualizar: {str(e)}'}
    finally:
        conn.close()


def get_current_user() -> dict:
    """
    Retorna o usuário atualmente logado do session_state.
    
    Returns:
        dict com dados do usuário ou None se não estiver logado
    """
    return st.session_state.get('user')


def is_authenticated() -> bool:
    """
    Verifica se há um usuário logado.
    
    Returns:
        True se há usuário autenticado, False caso contrário
    """
    user = st.session_state.get('user')
    return user is not None and isinstance(user, dict) and 'CODIGO' in user


def logout():
    """
    Faz logout do usuário atual.
    """
    if 'user' in st.session_state:
        del st.session_state['user']
    
    # Limpar outros dados da sessão se necessário
    # Manter apenas keys essenciais
    keys_to_keep = ['db_initialized']
    keys_to_delete = [key for key in st.session_state.keys() if key not in keys_to_keep]
    
    for key in keys_to_delete:
        del st.session_state[key]


def get_cookie_manager(key="cookie_manager"):
    """
    Retorna o gerenciador de cookies.
    Args:
        key: Chave única para o componente (evita Duplicate Widget ID)
    """
    return stx.CookieManager(key=key)


def create_session(user_id: int, manager=None):
    """
    Cria uma nova sessão persistente para o usuário.
    """
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=30)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Salvar no banco
        cursor.execute("""
            INSERT INTO EST_SESSAO (TOKEN, COD_USUARIO, DATA_CRIACAO, DATA_EXPIRACAO)
            VALUES (?, ?, ?, ?)
        """, (token, user_id, datetime.now().isoformat(), expires_at.isoformat()))
        conn.commit()
        
        # Definir cookie
        if manager is None:
            manager = get_cookie_manager(key="create_session")
            
        manager.set('study_session_token', token, expires_at=expires_at)
        
        # Store token in session state for reliable logout
        st.session_state['session_token'] = token
        
    except Exception as e:
        print(f"Erro ao criar sessão: {e}")
    finally:
        conn.close()


def check_session_cookie(manager=None):
    """
    Verifica se existe um cookie de sessão válido e loga o usuário.
    Retorna True se restaurou a sessão, False caso contrário.
    """
    # Se já estiver logado na sessão do Streamlit, retorna True
    if is_authenticated():
        return True
        
    if manager is None:
        manager = get_cookie_manager(key="check_session")
        
    token = manager.get('study_session_token')
    
    if not token:
        return False
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar sessão válida
        cursor.execute("""
            SELECT s.COD_USUARIO, u.NOME, u.EMAIL, u.ATIVO, u.IS_ADMIN
            FROM EST_SESSAO s
            JOIN EST_USUARIO u ON s.COD_USUARIO = u.CODIGO
            WHERE s.TOKEN = ? AND s.DATA_EXPIRACAO > ?
        """, (token, datetime.now().isoformat()))
        
        result = cursor.fetchone()
        
        if result:
            user_id, nome, email, ativo, is_admin = result
            
            if ativo == 'S':
                # Restaurar usuário na sessão
                st.session_state['user'] = {
                    'CODIGO': user_id,
                    'NOME': nome,
                    'EMAIL': email,
                    'ATIVO': ativo,
                    'IS_ADMIN': is_admin
                }
                # Store token for reliable logout
                st.session_state['session_token'] = token
                return True
        
        # Se chegou aqui, o token é inválido ou expirou
        # Limpar token inválido do banco (opcional, mas bom para limpeza)
        cursor.execute("DELETE FROM EST_SESSAO WHERE TOKEN = ?", (token,))
        conn.commit()
        
        # Remover cookie inválido
        manager.delete('study_session_token')
        return False
        
    except Exception as e:
        print(f"Erro ao verificar sessão: {e}")
        return False
    finally:
        conn.close()


def require_auth():
    """
    Decorator/helper para páginas que requerem autenticação.
    Redireciona para login se não estiver autenticado.
    """
    # Tenta restaurar sessão via cookie antes de barrar
    if not is_authenticated():
        if not check_session_cookie():
            st.warning("⚠️ Você precisa fazer login para acessar esta página.")
            st.info("👉 Por favor, faça login na página inicial.")
            st.stop()


def logout():
    """
    Faz logout do usuário atual e limpa cookies.
    """
    # 1. Try to get token from session state first (most reliable)
    token = st.session_state.get('session_token')
    
    # 2. Fallback to cookie manager if not in state
    cookie_manager = get_cookie_manager(key="logout")
    if not token:
        token = cookie_manager.get('study_session_token')
    
    # 3. Delete from DB
    if token:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM EST_SESSAO WHERE TOKEN = ?", (token,))
            conn.commit()
        except: pass
        finally: conn.close()
        
    # 4. Delete Cookie
    try:
        cookie_manager.delete('study_session_token')
    except Exception:
        # Ignore errors if cookie is already gone
        pass

    # 5. Clear Session State
    if 'user' in st.session_state:
        del st.session_state['user']
    
    if 'session_token' in st.session_state:
        del st.session_state['session_token']
    
    # 5. Clear Session State
    keys_to_keep = ['db_initialized']
    keys_to_delete = [key for key in st.session_state.keys() if key not in keys_to_keep]

    for key in keys_to_delete:
        del st.session_state[key]


# --- Google OAuth ---

def get_google_auth_url():
    """
    Gera a URL de autorização do Google.
    """
    try:
        client_id = st.secrets["google"]["client_id"]
        redirect_uri = st.secrets["google"]["redirect_uri"]
        
        scope = "openid email profile"
        
        url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&access_type=offline&prompt=select_account"
        return url
    except Exception as e:
        st.error(f"Erro ao configurar Google Login: {e}")
        return None

def verify_google_token(code):
    """
    Troca o código de autorização por um token e obtém dados do usuário.
    """
    try:
        import requests
        
        client_id = st.secrets["google"]["client_id"]
        client_secret = st.secrets["google"]["client_secret"]
        redirect_uri = st.secrets["google"]["redirect_uri"]
        
        # 1. Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        r = requests.post(token_url, data=data)
        if r.status_code != 200:
            return None, f"Erro ao obter token: {r.text}"
            
        tokens = r.json()
        access_token = tokens.get("access_token")
        
        # 2. Get User Info
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        r_user = requests.get(user_info_url, headers=headers)
        if r_user.status_code != 200:
            return None, "Erro ao obter dados do usuário"
            
        return r_user.json(), None
        
    except Exception as e:
        return None, str(e)

def login_google_user(user_info):
    """
    Loga ou cria usuário com dados do Google.
    """
    email = user_info.get("email")
    name = user_info.get("name")
    
    if not email:
        return None
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT CODIGO, NOME, EMAIL, ATIVO, IS_ADMIN FROM EST_USUARIO WHERE EMAIL = ?", (email.lower(),))
        user = cursor.fetchone()
        
        if user:
            # User exists, log in
            user_id, db_name, db_email, ativo, is_admin = user
            
            if ativo != 'S':
                return {'success': False, 'message': 'Usuário desativado.'}
                
            return {
                'success': True,
                'user': {
                    'CODIGO': user_id,
                    'NOME': db_name,
                    'EMAIL': db_email,
                    'ATIVO': ativo,
                    'IS_ADMIN': is_admin
                }
            }
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO EST_USUARIO (NOME, EMAIL, SENHA_HASH, ATIVO, DATA_CRIACAO, ULTIMO_ACESSO)
                VALUES (?, ?, ?, 'S', ?, ?)
            """, (name, email.lower(), 'GOOGLE_AUTH', datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                'success': True,
                'user': {
                    'CODIGO': user_id,
                    'NOME': name,
                    'EMAIL': email,
                    'ATIVO': 'S',
                    'IS_ADMIN': 'N'
                }
            }
            
    except Exception as e:
        return {'success': False, 'message': f"Erro no banco: {e}"}
    finally:
        conn.close()


def delete_user(user_id: int) -> dict:
    """
    Remove permanentemente um usuário e TODOS os seus dados relacionados.
    Realiza exclusão em cascata manual para garantir limpeza do banco.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 0. Check Validation (Prevent Admin Deletion)
        cursor.execute("SELECT IS_ADMIN FROM EST_USUARIO WHERE CODIGO = ?", (user_id,))
        row_check = cursor.fetchone()
        
        if not row_check:
            return {'success': False, 'message': 'Usuário não encontrado.'}
            
        # row_check is tuple like ('S',) or ('1',) depending on how we store, usually 'S' based on other code
        # Row factory might be active? get_connection returns objects or tuples depending on wrapper.
        # Let's use column access safely or index 0 if tuple.
        is_admin_val = row_check[0] if isinstance(row_check, (tuple, list)) else row_check['IS_ADMIN']
        
        if is_admin_val == 'S':
            return {'success': False, 'message': '⛔ Ação Bloqueada: Não é possível excluir um usuário Administrador.'}

        # 1. Tabelas Dependentes (Child) -> Parent
        # Ordem de Exclusão para evitar FK constraints (se ativas)
        
        # Tabelas que tem COD_USUARIO direto (adicionado na migração)
        tables_with_user_col = [
            'EST_SESSAO', 'EST_CONFIGURACAO', 'EST_ESTUDOS', 'EST_PROGRAMACAO', 
            'EST_PROJETO', 'EST_GRADE_ITEM', 'EST_GRADE_SEMANAL',
            'EST_CONTEUDO_CICLO', 'EST_CICLO_ITEM', 'EST_CICLO',
            'EST_MATERIA', 'EST_AREA'
        ]
        
        # Note: EST_CONTEUDO_CICLO might not have COD_USUARIO if strictly following schema,
        # but if we are careful, we delete children via their parents logic or assume
        # the migration added COD_USUARIO to everything.
        # Let's verify DB Schema in db_manager?
        # The migration logic in db_manager.py tried to add COD_USUARIO to:
        # ['EST_AREA', 'EST_MATERIA', 'EST_PROJETO', 'EST_CICLO', 'EST_GRADE_SEMANAL', 'EST_ESTUDOS', 'EST_PROGRAMACAO']
        # It did NOT add to EST_CICLO_ITEM, EST_GRADE_ITEM, EST_CONTEUDO_CICLO explicitly in the list 'tables_to_migrate'.
        # However, deleting the PARENT (Estudos, Projetos, Ciclos) technically orphans them if no cascade.
        # Ideally we should delete them.
        
        # Helper to delete orphans
        # Delete Grade Items where Grade belongs to User
        cursor.execute("DELETE FROM EST_GRADE_ITEM WHERE COD_GRADE IN (SELECT CODIGO FROM EST_GRADE_SEMANAL WHERE COD_USUARIO = ?)", (user_id,))
        
        # Delete Ciclo Items where Ciclo belongs to User
        # First delete contents of those items
        cursor.execute("""
            DELETE FROM EST_CONTEUDO_CICLO 
            WHERE COD_CICLO_ITEM IN (
                SELECT ci.CODIGO 
                FROM EST_CICLO_ITEM ci
                JOIN EST_CICLO c ON ci.COD_CICLO = c.CODIGO
                WHERE c.COD_USUARIO = ?
            )
        """, (user_id,))
        
        cursor.execute("""
            DELETE FROM EST_CICLO_ITEM 
            WHERE COD_CICLO IN (SELECT CODIGO FROM EST_CICLO WHERE COD_USUARIO = ?)
        """, (user_id,))
        
        # Now delete main tables
        main_tables = [
            'EST_SESSAO', 'EST_CONFIGURACAO', 'EST_ESTUDOS', 'EST_PROGRAMACAO', 
            'EST_PROJETO', 'EST_GRADE_SEMANAL', 'EST_CICLO', 
            'EST_MATERIA', 'EST_AREA'
        ]
        
        for table in main_tables:
            cursor.execute(f"DELETE FROM {table} WHERE COD_USUARIO = ?", (user_id,))
            
        # 2. Deletar Usuário Final
        cursor.execute("DELETE FROM EST_USUARIO WHERE CODIGO = ?", (user_id,))
        
        if cursor.rowcount == 0:
            return {'success': False, 'message': 'Usuário não encontrado.'}
            
        conn.commit()
        return {'success': True, 'message': f'Usuário e dados vinculados removidos com sucesso!'}
        
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'Erro ao excluir usuário: {str(e)}'}
    finally:
        conn.close()
