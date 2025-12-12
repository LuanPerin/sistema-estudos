import streamlit as st
import pandas as pd
from db_manager import get_connection
from auth import require_auth, get_current_user
import time

# Require authentication
require_auth()
current_user = get_current_user()
user_id = current_user['CODIGO']

st.title("⚙️ Configurações")

# Function to get or create config
def get_user_config(u_id):
    conn = get_connection()
    try:
        # Check if config exists
        df = pd.read_sql_query("SELECT * FROM EST_CONFIGURACAO WHERE COD_USUARIO = ?", conn, params=(u_id,))
        
        if df.empty:
            # Create default config
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO EST_CONFIGURACAO (COD_USUARIO, TEMA_APP, TEMA_WEB, REV_24H, REV_7D, REV_30D)
                VALUES (?, 'light', 'light', 0.25, 1.0, 2.0)
            """, (u_id,))
            conn.commit()
            # Fetch again
            df = pd.read_sql_query("SELECT * FROM EST_CONFIGURACAO WHERE COD_USUARIO = ?", conn, params=(u_id,))
        
        return df.iloc[0]
    finally:
        conn.close()

# Load Config
config = get_user_config(user_id)

with st.form("config_form"):
    st.subheader("🎨 Aparência")
    
    # Theme Selection
    theme_options = ["light", "dark"]
    pk_theme = theme_options.index(config['TEMA_WEB']) if config['TEMA_WEB'] in theme_options else 0
    
    new_theme = st.radio(
        "Tema da Aplicação Web", 
        options=theme_options,
        index=pk_theme,
        format_func=lambda x: "Claro (Light)" if x == "light" else "Escuro (Dark)",
        horizontal=True
    )
    
    st.divider()
    
    st.subheader("⏱️ Tempo das Revisões")
    st.caption("Defina quanto tempo (em horas) você quer dedicar para cada tipo de revisão.")
    
    # Sliders for Revision Times
    # Convert DB values (float hours) to slider values
    rev_24h = st.slider("Revisão de 24 horas", min_value=0.1, max_value=5.0, value=float(config['REV_24H']), step=0.1, format="%.1fh")
    rev_7d = st.slider("Revisão de 7 dias", min_value=0.1, max_value=5.0, value=float(config['REV_7D']), step=0.1, format="%.1fh")
    rev_30d = st.slider("Revisão de 30 dias", min_value=0.1, max_value=5.0, value=float(config['REV_30D']), step=0.1, format="%.1fh")
    
    st.divider()
    
    if st.form_submit_button("💾 Salvar Configurações", type="primary"):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE EST_CONFIGURACAO 
                SET TEMA_WEB = ?, REV_24H = ?, REV_7D = ?, REV_30D = ?
                WHERE COD_USUARIO = ?
            """, (new_theme, rev_24h, rev_7d, rev_30d, user_id))
            conn.commit()
            st.toast("✅ Configurações salvas com sucesso!", icon="✅")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
        finally:
            conn.close()
