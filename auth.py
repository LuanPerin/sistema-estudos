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
    
    if not senha or len(senha) < 6:
        return {'success': False, 'message': 'Senha deve ter pelo menos 6 caracteres'}
    
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
            SELECT CODIGO, NOME, EMAIL, SENHA_HASH, ATIVO
            FROM EST_USUARIO
            WHERE EMAIL = ?
        """, (email.lower(),))
        
        user = cursor.fetchone()
        
        if not user:
            return None
        
        user_id, nome, email_db, senha_hash, ativo = user
        
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
            'ATIVO': ativo
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
        
        if senha and len(senha) >= 6:
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
            SELECT s.COD_USUARIO, u.NOME, u.EMAIL, u.ATIVO
            FROM EST_SESSAO s
            JOIN EST_USUARIO u ON s.COD_USUARIO = u.CODIGO
            WHERE s.TOKEN = ? AND s.DATA_EXPIRACAO > ?
        """, (token, datetime.now().isoformat()))
        
        result = cursor.fetchone()
        
        if result:
            user_id, nome, email, ativo = result
            
            if ativo == 'S':
                # Restaurar usuário na sessão
                st.session_state['user'] = {
                    'CODIGO': user_id,
                    'NOME': nome,
                    'EMAIL': email,
                    'ATIVO': ativo
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
    
    # Limpar outros dados da sessão
    keys_to_keep = ['db_initialized']
    keys_to_delete = [key for key in st.session_state.keys() if key not in keys_to_keep]
    
    for key in keys_to_delete:
        del st.session_state[key]
