"""
Página de Cadastro de Novo Usuário
"""

import streamlit as st
from auth import create_user, is_authenticated, create_session, get_cookie_manager
import re

# Note: st.set_page_config handled in App.py

# Se já estiver autenticado, redirecionar para Home
if is_authenticated():
    st.switch_page("pages/Home.py")

# CSS customizado
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 600px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center;'>📝 Criar Conta</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Preencha os dados abaixo para criar sua conta</p>", unsafe_allow_html=True)

st.divider()

# Formulário de cadastro
with st.form("cadastro_form"):
    nome = st.text_input("Nome Completo *", placeholder="Seu nome completo")
    email = st.text_input("Email *", placeholder="seu@email.com")
    
    col1, col2 = st.columns(2)
    with col1:
        senha = st.text_input("Senha *", type="password", placeholder="Mínimo 6 caracteres")
    with col2:
        senha_confirma = st.text_input("Confirmar Senha *", type="password", placeholder="Digite novamente")
    
    st.caption("* Campos obrigatórios")
    
    submitted = st.form_submit_button("✅ Criar Conta", use_container_width=True, type="primary")

if submitted:
    # Validações
    errors = []
    
    if not nome or len(nome.strip()) < 3:
        errors.append("Nome deve ter pelo menos 3 caracteres")
    
    if not email or '@' not in email or '.' not in email.split('@')[1]:
        errors.append("Email inválido")
    
    if not senha or len(senha) < 6:
        errors.append("Senha deve ter pelo menos 6 caracteres")
    
    if senha != senha_confirma:
        errors.append("As senhas não coincidem")
    
    if errors:
        for error in errors:
            st.error(f"❌ {error}")
    else:
        with st.spinner("Criando sua conta..."):
            result = create_user(nome, email, senha)
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                st.balloons()
                st.balloons()
                
                # Auto Login Logic
                # 1. Set User in Session
                st.session_state['user'] = result['user']
                
                # 2. Create Persistent Cookie
                cookie_manager = get_cookie_manager(key="signup_page")
                create_session(result['user']['CODIGO'], cookie_manager)
                
                st.success("✅ Conta criada e autenticada com sucesso!")
                
                # 3. Redirect to Home
                st.info("🚀 Redirecionando para o sistema...")
                import time
                time.sleep(1)
                st.switch_page("pages/Home.py")
            else:
                st.error(f"❌ {result['message']}")

st.divider()

# Link para voltar ao login
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<p style='text-align: center;'>Já tem uma conta?</p>", unsafe_allow_html=True)
    if st.button("🔐 Fazer Login", use_container_width=True):
        st.switch_page("Login.py")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; color: #999; font-size: 0.8rem;'>
    🔒 Seus dados são criptografados com bcrypt<br>
   Nunca compartilhe sua senha com ninguém
    </p>
""", unsafe_allow_html=True)
