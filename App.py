import streamlit as st
from auth import is_authenticated, check_session_cookie, get_cookie_manager, logout
from db_manager import init_db
import time

# --- Global Config ---
st.set_page_config(
    page_title="Sistema de Estudos",
    page_icon="📚",
    layout="wide"
)

# --- Init DB ---
init_db()

# --- Auth Check ---
# Instantiate cookie manager once at the top level
cookie_manager = get_cookie_manager(key="app_main")

# Try to restore session if not logged in
if not is_authenticated():
    check_session_cookie(cookie_manager)

# --- Navigation Logic ---
def main():
    if is_authenticated():
        # --- Logged In Navigation ---
        
        # Define pages
        pg_home = st.Page("pages/Home.py", title="Home", icon="🏠", default=True)
        pg_plan = st.Page("pages/1_Planejamento.py", title="Planejamento", icon="📅")
        pg_study = st.Page("pages/2_Estudar.py", title="Estudar", icon="⏱️")
        
        pg_cadastros = st.Page("pages/3_Cadastros.py", title="Cadastros", icon="⚙️")
        
        pg_help = st.Page("pages/9_Ajuda.py", title="Ajuda", icon="❓")
        
        # Define Logout function as a page-like action
        def logout_action():
            logout()
            st.rerun()
            
        pg_logout = st.Page(logout_action, title="Sair", icon="🚪")

        # Group pages
        pg = st.navigation({
            "Principal": [pg_home, pg_plan, pg_study],
            "Gestão": [pg_cadastros],
            "Sistema": [pg_help, pg_logout]
        })
        
        # Sidebar User Info
        user = st.session_state.get('user', {})
        with st.sidebar:
            st.write(f"👤 **{user.get('NOME', 'Usuário')}**")
            st.divider()
            
    else:
        # --- Logged Out Navigation ---
        pg_login = st.Page("Login.py", title="Login", icon="🔐", default=True)
        pg_signup = st.Page("pages/0_Cadastro_Usuario.py", title="Criar Conta", icon="📝")
        
        pg = st.navigation([pg_login, pg_signup])

    # Run the selected page
    pg.run()

if __name__ == "__main__":
    main()
