"""
Página de Login - Ponto de entrada do aplicativo
"""

import streamlit as st
from auth import authenticate, is_authenticated, get_current_user, create_session, check_session_cookie, get_cookie_manager
from db_manager import init_db

# Instantiate cookie manager once
cookie_manager = get_cookie_manager(key="login_page")

# Note: st.set_page_config moved to App.py
# Note: init_db moved to App.py

# Tentar restaurar sessão via cookie
if check_session_cookie(cookie_manager):
    st.rerun()

# Se já estiver autenticado, redirecionar para Home (App.py will handle this by showing logged in nav)
if is_authenticated():
    st.rerun()

# CSS customizado para centralizar e estilizar
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 3rem;
        max-width: 500px;
    }
    </style>
""", unsafe_allow_html=True)

# Logo e título
st.markdown("<h1 style='text-align: center;'>📚</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Sistema de Estudos</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Faça login para continuar</p>", unsafe_allow_html=True)

st.divider()

# Formulário de login
with st.form("login_form"):
    email = st.text_input("Email", placeholder="seu@email.com")
    senha = st.text_input("Senha", type="password", placeholder="Sua senha")
    
    col1, col2 = st.columns(2)
    with col1:
        login_button = st.form_submit_button("🔐 Entrar", use_container_width=True, type="primary")
    with col2:
        # Botão de cadastro será implementado fora do form
        pass

if login_button:
    if not email or not senha:
        st.error("❌ Por favor, preencha todos os campos")
    else:
        with st.spinner("Autenticando..."):
            user = authenticate(email, senha)
            
            if user:
                st.session_state['user'] = user
                
                # Criar sessão persistente
                create_session(user['CODIGO'], cookie_manager)
                
                st.success(f"✅ Bem-vindo(a), {user['NOME']}!")
                st.balloons()
                # Pequeno delay para mostrar mensagem e garantir que o cookie seja salvo
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ Email ou senha inválidos")
                st.warning("💡 Dica: Verifique se digitou corretamente")

st.divider()

# Link para cadastro
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<p style='text-align: center;'>Não tem uma conta?</p>", unsafe_allow_html=True)
    if st.button("📝 Criar conta", use_container_width=True):
        st.switch_page("pages/0_Cadastro_Usuario.py")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; color: #999; font-size: 0.8rem;'>
    Sistema de Gerenciamento de Estudos v2.0<br>
    🔒 Suas informações estão seguras
    </p>
""", unsafe_allow_html=True)
