import streamlit as st
from auth import require_auth, get_current_user, update_user

# Require authentication
require_auth()

st.set_page_config(page_title="Meu Perfil", page_icon="👤")

st.title("👤 Meu Perfil")

user = get_current_user()

if user:
    # Admin Badge
    if user.get('IS_ADMIN') == 'S':
        st.success("🛡️ **Conta de Administrador** - Você tem acesso total ao sistema.")
        
    with st.form("profile_form"):
        st.subheader("Dados Pessoais")
        
        new_name = st.text_input("Nome Completo", value=user['NOME'])
        new_email = st.text_input("Email", value=user['EMAIL'])
        
        st.subheader("Segurança")
        st.info("Preencha apenas se quiser alterar a senha.")
        new_password = st.text_input("Nova Senha", type="password", help="Mínimo de 8 caracteres, maiúscula, número e especial")
        confirm_password = st.text_input("Confirmar Nova Senha", type="password")
        
        submitted = st.form_submit_button("💾 Salvar Alterações")
        
        if submitted:
            # Validation
            if new_password and new_password != confirm_password:
                st.error("As senhas não coincidem!")
            else:
                result = update_user(user['CODIGO'], new_name, new_email, new_password if new_password else None)
                
                if result['success']:
                    st.success(result['message'])
                    # Update session state
                    st.session_state['user']['NOME'] = new_name
                    st.session_state['user']['EMAIL'] = new_email
                    st.rerun()
                else:
                    st.error(result['message'])
else:
    st.error("Erro ao carregar dados do usuário.")
