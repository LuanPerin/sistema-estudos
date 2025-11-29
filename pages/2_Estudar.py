import streamlit as st
import pandas as pd
from db_manager import get_connection
from datetime import date, datetime
import time
from auth import get_current_user

# Note: st.set_page_config handled in App.py
# require_auth handled by App.py navigation logic

current_user = get_current_user()
user_id = current_user['CODIGO']

st.title("⏱️ Estudar")

# Get selected project from session state (set in Home.py)
project_id = st.session_state.get('selected_project')

# Validate Project Ownership
if project_id:
    project_id = int(project_id)
    conn = get_connection()
    # Check if project belongs to current user
    proj_check = pd.read_sql_query(
        "SELECT CODIGO FROM EST_PROJETO WHERE CODIGO = ? AND COD_USUARIO = ?", 
        conn, params=(project_id, user_id)
    )
    conn.close()
    
    if proj_check.empty:
        st.warning("⚠️ Projeto inválido ou não pertence ao usuário atual.")
        st.info("Selecione um projeto válido na página inicial.")
        st.session_state['selected_project'] = None
        st.stop()
else:
    st.warning("⚠️ Nenhum projeto selecionado.")
    st.info("Vá para a página inicial (Home) para selecionar ou criar um projeto.")
    st.stop()

# --- Timer State Initialization ---
if 'timer_active' not in st.session_state:
    st.session_state['timer_active'] = False
if 'timer_start_time' not in st.session_state:
    st.session_state['timer_start_time'] = None
if 'timer_elapsed' not in st.session_state:
    st.session_state['timer_elapsed'] = 0.0

# --- Helper to render timer controls ---
def render_timer(task_name, task_id=None, is_extra=False, custom_desc=None):
    st.info(f"Em andamento: **{task_name}**")
    
    # Placeholder for the timer
    timer_placeholder = st.empty()
    
    # Render Buttons FIRST so they are visible while loop runs
    c1, c2, c3 = st.columns(3)
    
    # Start/Resume
    if not st.session_state['timer_active']:
        if c1.button("▶️ Iniciar / Retomar", use_container_width=True):
            st.session_state['timer_active'] = True
            st.session_state['timer_start_time'] = time.time()
            st.rerun()
    else:
        # Pause
        if c2.button("⏸️ Pausar", use_container_width=True):
            st.session_state['timer_active'] = False
            st.session_state['timer_elapsed'] += time.time() - st.session_state['timer_start_time']
            st.session_state['timer_start_time'] = None
            st.rerun()
            
    # Finish
    if c3.button("⏹️ Finalizar", use_container_width=True):
        # Finalize time calculation
        if st.session_state['timer_active']:
            st.session_state['timer_elapsed'] += time.time() - st.session_state['timer_start_time']
        
        final_hours = st.session_state['timer_elapsed'] / 3600
        
        # Save to DB
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get COD_MATERIA from Programacao or Extra Item
        cod_materia_save = None
        if task_id and not is_extra:
            # Fetch from Programacao
            prog_info = cursor.execute("SELECT COD_MATERIA, COD_CICLO_ITEM FROM EST_PROGRAMACAO WHERE CODIGO = ?", (task_id,)).fetchone()
            if prog_info:
                if prog_info['COD_MATERIA']:
                    cod_materia_save = prog_info['COD_MATERIA']
                elif prog_info['COD_CICLO_ITEM']:
                    # Fallback to Cycle Item
                    ci_info = cursor.execute("SELECT COD_MATERIA FROM EST_CICLO_ITEM WHERE CODIGO = ?", (prog_info['COD_CICLO_ITEM'],)).fetchone()
                    if ci_info: cod_materia_save = ci_info['COD_MATERIA']
        elif is_extra and st.session_state.get('extra_study_item'):
             # Extra item is a dict with 'COD_MATERIA' or we can fetch it from cycle item info
             # In the extra study logic, we store the cycle item row in session state
             # The query for items selects: ci.CODIGO, m.NOME, ci.QTDE_MINUTOS. It misses COD_MATERIA.
             # We should update the query below, but for now let's try to fetch it if missing
             extra_item = st.session_state['extra_study_item']
             if 'COD_MATERIA' in extra_item:
                 cod_materia_save = extra_item['COD_MATERIA']
             else:
                 # Fetch from DB based on cycle item code
                 ci_info = cursor.execute("SELECT COD_MATERIA FROM EST_CICLO_ITEM WHERE CODIGO = ?", (extra_item['CODIGO'],)).fetchone()
                 if ci_info: cod_materia_save = ci_info['COD_MATERIA']

        # Determine Description to Save
        final_desc = custom_desc if custom_desc else f"Estudo de {task_name}"

        cursor.execute("""
            INSERT INTO EST_ESTUDOS (COD_PROJETO, DATA, HL_REALIZADA, DESC_AULA, COD_MATERIA)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, date.today().isoformat(), final_hours, final_desc, cod_materia_save))
        
        if not is_extra:
            # Prefer session state ID if available (more reliable across reruns)
            tid_to_update = st.session_state.get('current_task_id', task_id)
            if tid_to_update:
                cursor.execute("UPDATE EST_PROGRAMACAO SET STATUS = 'CONCLUIDO' WHERE CODIGO = ?", (tid_to_update,))
                # Clear the session state ID after use
                st.session_state['current_task_id'] = None
            
        conn.commit()
        conn.close()
        
        # Reset State
        st.session_state['timer_active'] = False
        st.session_state['timer_start_time'] = None
        st.session_state['timer_elapsed'] = 0.0
        st.session_state['extra_study_item'] = None # Clear extra item if any
        
        st.toast(f"✅ Estudo finalizado! Tempo total: {final_hours*60:.0f} min", icon="✅")
        time.sleep(2)
        st.rerun()

    # Logic to update timer display
    # If active, we loop to update the placeholder
    if st.session_state['timer_active']:
        while True:
            current_session = time.time() - st.session_state['timer_start_time']
            total_elapsed = st.session_state['timer_elapsed'] + current_session
            
            # Format MM:SS
            minutes = int(total_elapsed // 60)
            seconds = int(total_elapsed % 60)
            
            timer_placeholder.markdown(f"""
                <div style="text-align: center; font-size: 48px; font-weight: bold; margin: 20px 0;">
                    {minutes:02d}:{seconds:02d}
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1) # Update every second
    else:
        # Static display if paused/stopped
        total_elapsed = st.session_state['timer_elapsed']
        minutes = int(total_elapsed // 60)
        seconds = int(total_elapsed % 60)
        timer_placeholder.markdown(f"""
            <div style="text-align: center; font-size: 48px; font-weight: bold; margin: 20px 0;">
                {minutes:02d}:{seconds:02d}
            </div>
        """, unsafe_allow_html=True)

# --- Main Logic ---

# Fetch pending tasks for today
conn = get_connection()
query = """
    SELECT 
        p.CODIGO,
        p.DATA, 
        p.DESC_AULA, 
        m.NOME as MATERIA,
        p.HL_PREVISTA
    FROM EST_PROGRAMACAO p
    LEFT JOIN EST_CICLO_ITEM ci ON p.COD_CICLO_ITEM = ci.CODIGO
    LEFT JOIN EST_MATERIA m ON ci.COD_MATERIA = m.CODIGO
    WHERE p.DATA <= ? AND p.STATUS = 'PENDENTE' AND p.COD_PROJETO = ?
    ORDER BY p.DATA, p.HR_INICIAL_PREVISTA
"""
df = pd.read_sql_query(query, conn, params=(date.today().isoformat(), project_id))
conn.close()

# Check if we are already in an extra study session
if 'extra_study_item' not in st.session_state:
    st.session_state['extra_study_item'] = None

if not df.empty:
    # Scheduled Task Logic
    task = df.iloc[0]
    st.subheader(f"📅 Meta de Hoje: {task['MATERIA']}")
    st.caption(f"Atividade: {task['DESC_AULA']} | Meta: {task['HL_PREVISTA']*60:.0f} min")
    
    # Store current task ID in session state to ensure it persists for the Finish action
    st.session_state['current_task_id'] = int(task['CODIGO'])
    
    render_timer(task['MATERIA'], task_id=task['CODIGO'], custom_desc=task['DESC_AULA'])

elif st.session_state['extra_study_item']:
    # Extra Study Logic (Active)
    item = st.session_state['extra_study_item']
    st.subheader(f"🚀 Estudo Extra: {item['NOME']}")
    
    if st.button("🔙 Cancelar / Voltar"):
        st.session_state['extra_study_item'] = None
        st.session_state['timer_active'] = False
        st.session_state['timer_elapsed'] = 0.0
        st.rerun()
        
    render_timer(item['NOME'], is_extra=True)

else:
    # No tasks, offer next cycle item
    st.success("🎉 Meta do dia concluída!")
    st.divider()
    st.markdown("### Continuar Estudando? (Ciclo)")
    
    conn = get_connection()
    # Find next item in cycle based on history
    # 1. Get default cycle for THIS USER
    ciclo = pd.read_sql_query("SELECT CODIGO FROM EST_CICLO WHERE PADRAO = 'S' AND COD_USUARIO = ?", conn, params=(user_id,))
    if not ciclo.empty:
        cod_ciclo = ciclo.iloc[0]['CODIGO']
        
        # 2. Get all items
        items = pd.read_sql_query(f"""
            SELECT ci.CODIGO, m.NOME, ci.QTDE_MINUTOS 
            FROM EST_CICLO_ITEM ci
            JOIN EST_MATERIA m ON ci.COD_MATERIA = m.CODIGO
            WHERE ci.COD_CICLO = {cod_ciclo}
            ORDER BY ci.INDICE
        """, conn)
        
        # 3. Find last studied item
        last_study = pd.read_sql_query("""
            SELECT DESC_AULA FROM EST_ESTUDOS 
            WHERE COD_PROJETO = ? 
            ORDER BY DATA DESC, CODIGO DESC LIMIT 1
        """, conn, params=(project_id,))
        
        next_idx = 0
        if not last_study.empty:
            # Try to match description to find where we stopped
            # This is a bit fuzzy, ideally we'd store COD_CICLO_ITEM in EST_ESTUDOS
            # For now, let's just let the user pick or default to first
            pass
            
        # Simple UI to pick next item
        if not items.empty:
            st.write("Sugestão de sequência:")
            
            # Create a grid of buttons for items
            for idx, row in items.iterrows():
                if st.button(f"▶️ Estudar {row['NOME']} ({row['QTDE_MINUTOS']:.0f} min)", key=f"start_extra_{row['CODIGO']}"):
                    st.session_state['extra_study_item'] = row.to_dict()
                    st.rerun()
    conn.close()

st.divider()
conn.close()

# --- Retroactive Entry ---
if 'mode_hist' not in st.session_state:
    st.session_state['mode_hist'] = 'LIST'

c_title, c_add = st.columns([4, 1])
c_title.subheader("📜 Histórico de Estudos")
if c_add.button("➕ Lançamento Retroativo"):
    st.session_state['mode_hist'] = 'NEW'
    st.rerun()

if st.session_state['mode_hist'] == 'NEW':
    st.divider()
    st.markdown("### 📝 Novo Registro Retroativo")
    
    with st.form("new_hist_form"):
        conn = get_connection()
        subjects = pd.read_sql_query("SELECT NOME FROM EST_MATERIA WHERE COD_USUARIO = ? ORDER BY NOME", conn, params=(user_id,))
        conn.close()
        
        c1, c2 = st.columns(2)
        subj_options = subjects['NOME'].tolist()
        selected_subject = c1.selectbox("Matéria", options=subj_options)
        
        # Auto-generate description
        new_desc = f"Estudo de {selected_subject}"
        st.text_input("Descrição (Automático)", value=new_desc, disabled=True)
        
        new_hl = c2.number_input("Horas Realizadas", min_value=0.1, value=1.0, step=0.1)
        new_date = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
        
        c_save, c_cancel = st.columns(2)
        if c_save.form_submit_button("💾 Salvar Registro"):
            conn = get_connection()
            cursor = conn.cursor()
            # Get COD_MATERIA for selected subject
            mat_row = cursor.execute("SELECT CODIGO FROM EST_MATERIA WHERE NOME = ? AND COD_USUARIO = ?", (selected_subject, user_id)).fetchone()
            cod_mat_new = mat_row['CODIGO'] if mat_row else None

            cursor.execute("""
                INSERT INTO EST_ESTUDOS (COD_PROJETO, DATA, HL_REALIZADA, DESC_AULA, COD_MATERIA)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, new_date.isoformat(), new_hl, new_desc, cod_mat_new))
            conn.commit()
            conn.close()
            st.session_state['mode_hist'] = 'LIST'
            st.toast("✅ Registro adicionado com sucesso!", icon="✅")
            st.rerun()
            
        if c_cancel.form_submit_button("❌ Cancelar"):
            st.session_state['mode_hist'] = 'LIST'
            st.rerun()
    st.divider()

# --- History List ---
conn = get_connection()
history = pd.read_sql_query("""
    SELECT CODIGO, DATA, DESC_AULA, HL_REALIZADA 
    FROM EST_ESTUDOS 
    WHERE COD_PROJETO = ?
    ORDER BY DATA DESC, CODIGO DESC LIMIT 50
""", conn, params=(project_id,))
conn.close()

if 'edit_hist_id' not in st.session_state:
    st.session_state['edit_hist_id'] = None

if not history.empty:
    cols = st.columns([2, 3, 1, 0.5, 0.5])
    cols[0].markdown("**Data**")
    cols[1].markdown("**Descrição**")
    cols[2].markdown("**Horas**")
    
    for index, row in history.iterrows():
        c1, c2, c3, c4, c5 = st.columns([2, 3, 1, 0.5, 0.5])
        try:
            d_fmt = pd.to_datetime(row['DATA']).strftime('%d/%m/%Y')
        except: d_fmt = row['DATA']
        
        c1.text(d_fmt)
        c2.text(row['DESC_AULA'])
        c3.text(f"{row['HL_REALIZADA']:.2f}")
        
        if c4.button("✏️", key=f"edit_hist_{row['CODIGO']}"):
            st.session_state['edit_hist_id'] = row['CODIGO']
            st.rerun()
            
        if c5.button("🗑️", key=f"del_hist_{row['CODIGO']}"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM EST_ESTUDOS WHERE CODIGO = ?", (row['CODIGO'],))
            conn.commit()
            conn.close()
            st.rerun()

    # Edit Form for History
    if st.session_state['edit_hist_id']:
        st.divider()
        st.markdown("### ✏️ Editar Registro de Estudo")
        
        conn = get_connection()
        hist_item = pd.read_sql_query("SELECT * FROM EST_ESTUDOS WHERE CODIGO = ?", conn, params=(st.session_state['edit_hist_id'],))
        conn.close()
        
        if not hist_item.empty:
            item = hist_item.iloc[0]
            with st.form("edit_hist_form"):
                conn = get_connection()
                # Fetch subjects for dropdown (ID and Name)
                subjects = pd.read_sql_query("SELECT CODIGO, NOME FROM EST_MATERIA WHERE COD_USUARIO = ? ORDER BY NOME", conn, params=(user_id,))
                conn.close()
                
                c1, c2 = st.columns(2)
                
                subj_options = subjects['NOME'].tolist()
                default_idx = 0
                
                # Logic to determine default selection
                # 1. Try by COD_MATERIA (Reliable)
                if pd.notna(item['COD_MATERIA']):
                    # Find name for this ID
                    match = subjects[subjects['CODIGO'] == item['COD_MATERIA']]
                    if not match.empty:
                        subj_name = match.iloc[0]['NOME']
                        try:
                            default_idx = subj_options.index(subj_name)
                        except ValueError: pass
                else:
                    # 2. Fallback: Try to extract from description
                    current_desc = item['DESC_AULA']
                    # Handle both prefixes
                    possible_name = current_desc.replace("Estudo de ", "").replace("Estudar ", "").strip()
                    
                    try:
                        default_idx = subj_options.index(possible_name)
                    except ValueError:
                        default_idx = 0
                
                selected_subject = c1.selectbox("Matéria", options=subj_options, index=default_idx)
                
                # Auto-generate description based on selection
                new_desc_default = f"Estudo de {selected_subject}"
                final_desc = st.text_input("Descrição", value=new_desc_default)
                
                new_hl = c2.number_input("Horas Realizadas", value=float(item['HL_REALIZADA']), step=0.1)
                
                try:
                    curr_date = pd.to_datetime(item['DATA']).date()
                except: curr_date = date.today()
                new_date = st.date_input("Data", value=curr_date, format="DD/MM/YYYY")
                
                c_save, c_cancel = st.columns(2)
                if c_save.form_submit_button("💾 Salvar Alterações"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    # Get COD_MATERIA for selected subject
                    mat_row = cursor.execute("SELECT CODIGO FROM EST_MATERIA WHERE NOME = ? AND COD_USUARIO = ?", (selected_subject, user_id)).fetchone()
                    cod_mat_edit = mat_row['CODIGO'] if mat_row else None

                    cursor.execute("""
                        UPDATE EST_ESTUDOS 
                        SET DESC_AULA=?, HL_REALIZADA=?, DATA=?, COD_MATERIA=?
                        WHERE CODIGO=?
                    """, (final_desc, new_hl, new_date.isoformat(), cod_mat_edit, st.session_state['edit_hist_id']))
                    conn.commit()
                    conn.close()
                    st.session_state['edit_hist_id'] = None
                    st.toast("✅ Histórico atualizado!", icon="✅")
                    st.rerun()
                    
                if c_cancel.form_submit_button("❌ Cancelar"):
                    st.session_state['edit_hist_id'] = None
                    st.rerun()
else:
    st.info("Nenhum histórico encontrado.")
