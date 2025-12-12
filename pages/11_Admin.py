import streamlit as st
import pandas as pd
import time
from auth import require_auth, get_current_user, get_all_users, admin_update_user, delete_user

# Require authentication
require_auth()

# Check Admin Access
user = get_current_user()
if not user or user.get('IS_ADMIN') != 'S':
    st.error("⛔ Acesso Negado. Esta página é restrita a administradores.")
    st.stop()

st.set_page_config(page_title="Administração de Usuários", page_icon="🛡️", layout="wide")

st.title("🛡️ Administração de Usuários")

# List Users
users = get_all_users()

if users:
    df = pd.DataFrame(users)
    
    # Display as table
    st.dataframe(
        df,
        column_config={
            "CODIGO": "ID",
            "NOME": "Nome",
            "EMAIL": "Email",
            "ATIVO": "Ativo?",
            "IS_ADMIN": "Admin?",
            "IS_ADMIN": "Admin?",
            "METODO_AUTH": "Login via",
            "DATA_CRIACAO": "Criado em",
            "ULTIMO_ACESSO": "Último Acesso"
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    st.subheader("✏️ Editar Usuário")
    
    # Select User
    user_options = {u['CODIGO']: f"{u['CODIGO']} - {u['NOME']} ({u['EMAIL']})" for u in users}
    selected_id = st.selectbox("Selecione o Usuário para editar:", options=list(user_options.keys()), format_func=lambda x: user_options[x])
    
    if selected_id:
        # Get selected user data
        selected_user = next((u for u in users if u['CODIGO'] == selected_id), None)
        
        if selected_user:
            with st.form("admin_edit_user"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Nome", value=selected_user['NOME'])
                    new_email = st.text_input("Email", value=selected_user['EMAIL'])
                    new_pass = st.text_input("Nova Senha (deixe em branco para manter)", type="password")
                
                with col2:
                    is_active = st.selectbox("Ativo?", ["S", "N"], index=0 if selected_user['ATIVO'] == 'S' else 1)
                    is_admin = st.selectbox("Administrador?", ["S", "N"], index=0 if selected_user['IS_ADMIN'] == 'S' else 1)
                
                submitted = st.form_submit_button("💾 Salvar Alterações")
                
                if submitted:
                    result = admin_update_user(
                        selected_id, 
                        new_name, 
                        new_email, 
                        new_pass if new_pass else None,
                        is_active,
                        is_admin
                    )
                    
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
            
            st.divider()
            
            # --- DELETE USER SECTION ---
            st.subheader("🗑️ Zona de Perigo")
            
            if selected_user['IS_ADMIN'] == 'S':
                st.info("🔒 **Usuário Protegido:** Contas de Administrador não podem ser excluídas.")
            else:
                st.warning("Atenção: A exclusão é irreversível e removerá TODOS os dados do usuário (Estudos, Histórico, Configurações).")
                
                with st.expander("Apagar Usuário"):
                    confirm_delete = st.checkbox(f"Estou ciente e quero excluir o usuário permanentemente: {selected_user['NOME']}")
                    
                    if confirm_delete:
                        if st.button("💥 CONFIRMAR EXCLUSÃO", type="primary"):
                            # Avoid self-deletion if logged in as same user (though logic permits, it kicks you out)
                            if selected_id == user['CODIGO']:
                                st.error("Você não pode se auto-excluir por aqui.")
                            else:
                                res_del = delete_user(selected_id)
                                if res_del['success']:
                                    st.success(res_del['message'])
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(res_del['message'])

else:
    st.info("Nenhum usuário encontrado.")
