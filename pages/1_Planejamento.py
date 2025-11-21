import streamlit as st
import pandas as pd
from db_manager import get_connection
from study_engine import generate_schedule
from datetime import date
from auth import require_auth, get_current_user
import time

st.set_page_config(page_title="Planejamento", layout="wide")

# Require authentication
require_auth()
current_user = get_current_user()
user_id = current_user['CODIGO']

st.title("📅 Planejamento")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Configuração")
    
    # Get project from global session state (set in Home.py)
    project_id = st.session_state.get('selected_project')
    
    if project_id:
        conn = get_connection()
        proj = pd.read_sql_query(
            "SELECT NOME FROM EST_PROJETO WHERE CODIGO = ? AND COD_USUARIO = ?", 
            conn, params=(int(project_id), user_id)
        )
        conn.close()
        
        if not proj.empty:
            st.info(f"📁 Projeto: **{proj.iloc[0]['NOME']}**")
        
        if st.button("Gerar Programação (Próx. 7 dias)"):
            with st.spinner("Calculando revisões e ciclos..."):
                # Ensure project_id is int
                pid = int(project_id)
                msg = generate_schedule(pid, date.today(), 7)
                if "Sucesso" in msg:
                    st.toast("✅ " + msg, icon="✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
    else:
        st.warning("⚠️ Selecione um projeto na página inicial.")

# --- Calendar / List View ---
if project_id:
    st.subheader("Cronograma")
    
    conn = get_connection()
    # Join with Materia/Ciclo for readable names
    query = """
        SELECT 
            p.CODIGO,
            p.DATA, 
            p.DIA, 
            p.HR_INICIAL_PREVISTA, 
            p.HL_PREVISTA, 
            p.DESC_AULA, 
            m.NOME as MATERIA,
            p.STATUS
        FROM EST_PROGRAMACAO p
        LEFT JOIN EST_CICLO_ITEM ci ON p.COD_CICLO_ITEM = ci.CODIGO
        LEFT JOIN EST_MATERIA m ON ci.COD_MATERIA = m.CODIGO
        WHERE p.COD_PROJETO = ?
        ORDER BY p.DATA, p.HR_INICIAL_PREVISTA
    """
    df = pd.read_sql_query(query, conn, params=(int(project_id),))
    conn.close()
    
    if not df.empty:
        # State for editing schedule items
        if 'edit_prog_id' not in st.session_state:
            st.session_state['edit_prog_id'] = None

        # Group by Date for better visualization
        dates = df['DATA'].unique()
        days_map = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
        
        for d in dates:
            try:
                dt_obj = pd.to_datetime(d)
                weekday = days_map[dt_obj.weekday()]
                formatted_date = f"{dt_obj.strftime('%d/%m/%Y')} - {weekday}"
            except:
                formatted_date = d
                
            with st.expander(f"📅 {formatted_date}", expanded=(d == str(date.today()))):
                day_tasks = df[df['DATA'] == d]
                
                # Header
                cols = st.columns([3, 2, 1, 1, 1, 1, 0.5, 0.5])
                cols[0].markdown("**Matéria**")
                cols[1].markdown("**Descrição**")
                cols[2].markdown("**Início**")
                cols[3].markdown("**Fim**")
                cols[4].markdown("**Previsto (h)**")
                cols[5].markdown("**Status**")
                
                for index, row in day_tasks.iterrows():
                    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([3, 2, 1, 1, 1, 1, 0.5, 0.5])
                    
                    # Calculate End Time
                    hr_ini = row['HR_INICIAL_PREVISTA'] if row['HR_INICIAL_PREVISTA'] else "00:00:00"
                    try:
                        t_ini = pd.to_datetime(hr_ini, format="%H:%M:%S")
                        t_fim = t_ini + pd.Timedelta(hours=row['HL_PREVISTA'])
                        hr_fim = t_fim.strftime("%H:%M:%S")
                    except:
                        hr_fim = "-"
                        
                    c1.text(row['MATERIA'] if row['MATERIA'] else "-")
                    c2.text(row['DESC_AULA'])
                    c3.text(hr_ini)
                    c4.text(hr_fim)
                    c5.text(f"{row['HL_PREVISTA']:.2f}")
                    c6.text(row['STATUS'])
                    
                    if c7.button("✏️", key=f"edit_prog_{row['CODIGO']}"):
                        st.session_state['edit_prog_id'] = row['CODIGO']
                        st.rerun()
                        
                    if c8.button("🗑️", key=f"del_prog_{row['CODIGO']}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM EST_PROGRAMACAO WHERE CODIGO = ?", (row['CODIGO'],))
                        conn.commit()
                        conn.close()
                        st.rerun()

        # Edit Form Modal
        if st.session_state['edit_prog_id']:
            st.divider()
            st.markdown("### ✏️ Editar Programação")
            
            conn = get_connection()
            prog_item = pd.read_sql_query("SELECT * FROM EST_PROGRAMACAO WHERE CODIGO = ?", conn, params=(st.session_state['edit_prog_id'],))
            conn.close()
            
            if not prog_item.empty:
                item = prog_item.iloc[0]
                with st.form("edit_prog_form"):
                    c1, c2, c3 = st.columns(3)
                    new_desc = c1.text_input("Descrição", value=item['DESC_AULA'])
                    new_hl = c2.number_input("Horas Previstas", value=float(item['HL_PREVISTA']), step=0.1)
                    new_status = c3.selectbox("Status", ["PENDENTE", "CONCLUIDO", "CANCELADO"], index=["PENDENTE", "CONCLUIDO", "CANCELADO"].index(item['STATUS']))
                    
                    # Date handling
                    try:
                        curr_date = pd.to_datetime(item['DATA']).date()
                    except:
                        curr_date = date.today()
                    new_date = st.date_input("Data", value=curr_date, format="DD/MM/YYYY")

                    c_save, c_cancel = st.columns(2)
                    if c_save.form_submit_button("💾 Salvar Alterações"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE EST_PROGRAMACAO 
                            SET DESC_AULA=?, HL_PREVISTA=?, STATUS=?, DATA=?
                            WHERE CODIGO=?
                        """, (new_desc, new_hl, new_status, new_date.isoformat(), st.session_state['edit_prog_id']))
                        conn.commit()
                        conn.close()
                        st.session_state['edit_prog_id'] = None
                        st.toast("✅ Programação atualizada!", icon="✅")
                        st.rerun()
                        
                    if c_cancel.form_submit_button("❌ Cancelar"):
                        st.session_state['edit_prog_id'] = None
                        st.rerun()
    else:
        st.info("Nenhuma programação encontrada. Clique em 'Gerar Programação'.")
