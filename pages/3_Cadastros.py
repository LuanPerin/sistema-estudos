import streamlit as st
import pandas as pd
from crud_helper import create_crud_interface
from db_manager import get_connection
from auth import get_current_user
from datetime import date, datetime
import time

# Note: st.set_page_config handled in App.py
# require_auth handled by App.py navigation logic

current_user = get_current_user()
if not current_user:
    st.warning("Acesso negado. Por favor, faça login.")
    st.stop()
user_id = current_user['CODIGO']

# --- Dialog for Managing Contents (Moved to global scope for persistence) ---

@st.dialog("Gerenciar Conteúdos")
def manage_contents(item_id, materia_name):
    import re # Import re for regex operations
    
    # CSS to widen the modal (Adjusted to 60vw as requested)
    st.markdown("""
        <style>
        div[data-testid="stDialog"] div[role="dialog"] {
            width: 60vw;
            max_width: 800px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.write(f"Conteúdos para: **{materia_name}**")
    
    conn = get_connection()
    
    # --- Add New Content ---
    with st.expander("Adicionar Conteúdo", expanded=True):
        tab_single, tab_bulk = st.tabs(["Individual", "Em Lote"])
        
        with tab_single:
            # (a) Alignment Fix: vertical_alignment="bottom"
            c1_add, c2_add = st.columns([4, 1], vertical_alignment="bottom")
            c_new_desc = c1_add.text_input("Novo Tópico", key="new_content_desc")
            if c2_add.button("Adicionar", key="btn_add_content"):
                if c_new_desc:
                    cursor = conn.cursor()
                    # Get max order
                    max_ord = cursor.execute("SELECT MAX(ORDEM) FROM EST_CONTEUDO_CICLO WHERE COD_CICLO_ITEM = ?", (item_id,)).fetchone()[0]
                    new_ord = (max_ord if max_ord else 0) + 1
                    
                    cursor.execute("INSERT INTO EST_CONTEUDO_CICLO (COD_CICLO_ITEM, DESCRICAO, ORDEM) VALUES (?, ?, ?)", (item_id, c_new_desc, new_ord))
                    conn.commit()
                    st.rerun()
        
        with tab_bulk:
            st.caption("Cole uma lista de tópicos (um por linha). Máximo de 90 linhas por vez.")

            # Form for robust submission and clearing
            with st.form(key="bulk_import_form", clear_on_submit=True):
                c_bulk_text = st.text_area("Texto para Importação", height=150)
                submit_bulk = st.form_submit_button("Processar e Importar")
            
            if submit_bulk:
                if c_bulk_text:
                    # Simple splitting by line
                    lines = [line.strip() for line in c_bulk_text.split('\n') if line.strip()]
                    
                    if len(lines) > 90:
                         st.error(f"❌ Limite excedido! Você tentou importar {len(lines)} itens. O máximo permitido é 90 par garantir a estabilidade.")
                    elif lines:
                        conn = get_connection()
                        cursor = conn.cursor()
                        
                        # Get current max order
                        max_ord = cursor.execute("SELECT MAX(ORDEM) FROM EST_CONTEUDO_CICLO WHERE COD_CICLO_ITEM = ?", (item_id,)).fetchone()[0]
                        start_ord = (max_ord if max_ord else 0) + 1
                        
                        # Prepare data with order
                        data_to_insert = []
                        for idx, line in enumerate(lines):
                            data_to_insert.append((item_id, line, start_ord + idx))
                            
                        cursor.executemany("INSERT INTO EST_CONTEUDO_CICLO (COD_CICLO_ITEM, DESCRICAO, ORDEM) VALUES (?, ?, ?)", data_to_insert)
                        conn.commit()
                        conn.close()
                        
                        st.toast(f"{len(lines)} tópicos importados com sucesso!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Nenhum tópico identificado. Verifique se há texto digitado.")
                else:
                    st.warning("O campo de texto está vazio.")

    st.divider()
    
    # --- List Contents ---
    # Order by ORDEM first, then CODIGO
    contents = pd.read_sql_query(f"SELECT * FROM EST_CONTEUDO_CICLO WHERE COD_CICLO_ITEM = {item_id} ORDER BY ORDEM, CODIGO", conn)
    
    if not contents.empty:
        # Progress Bar
        total = len(contents)
        done = len(contents[contents['FINALIZADO'] == 'S'])
        progress = done / total
        st.progress(progress, text=f"Progresso: {done}/{total} ({progress:.0%})")
        
        st.markdown("---")
        
        # (b) Headers
        # Adjusted columns: Status, Desc, Arrows, Delete
        h1, h2, h3, h4 = st.columns([0.5, 4, 1, 0.5])
        h1.markdown("**Status**")
        h2.markdown("**Descrição**")
        h3.markdown("**Ordem**")
        h4.markdown("**Ações**")
        
        # Convert to list of dicts for easier index handling
        content_list = contents.to_dict('records')
        
        for index, row in enumerate(content_list):
            c1, c2, c3, c4 = st.columns([0.5, 4, 1, 0.5], vertical_alignment="center")
            
            # Checkbox for Status
            is_checked = row['FINALIZADO'] == 'S'
            if c1.checkbox("Done", value=is_checked, key=f"chk_cont_{row['CODIGO']}", label_visibility="collapsed"):
                if not is_checked: # State changed to True
                    cursor = conn.cursor()
                    cursor.execute("UPDATE EST_CONTEUDO_CICLO SET FINALIZADO = 'S' WHERE CODIGO = ?", (row['CODIGO'],))
                    conn.commit()
                    st.rerun()
            else:
                if is_checked: # State changed to False
                    cursor = conn.cursor()
                    cursor.execute("UPDATE EST_CONTEUDO_CICLO SET FINALIZADO = 'N' WHERE CODIGO = ?", (row['CODIGO'],))
                    conn.commit()
                    st.rerun()
                    
            # Description
            import html
            safe_desc = html.escape(row['DESCRICAO'])
            style = "text-decoration: line-through; color: gray;" if is_checked else ""
            c2.markdown(f"<span style='{style}'>{safe_desc}</span>", unsafe_allow_html=True)
            
            # Reordering Arrows
            # Up Arrow (only if not first)
            c3_1, c3_2 = c3.columns(2)
            if index > 0:
                if c3_1.button("⬆️", key=f"up_{row['CODIGO']}", help="Mover para cima"):
                    # Swap with previous
                    prev_row = content_list[index - 1]
                    
                    # Get current ORDEM values (handle None)
                    curr_ordem = row['ORDEM'] if row['ORDEM'] is not None else index + 1
                    prev_ordem = prev_row['ORDEM'] if prev_row['ORDEM'] is not None else index
                    
                    # If they are equal (shouldn't happen often if initialized), force a spread
                    if curr_ordem == prev_ordem:
                        curr_ordem += 1
                        
                    cursor = conn.cursor()
                    cursor.execute("UPDATE EST_CONTEUDO_CICLO SET ORDEM = ? WHERE CODIGO = ?", (prev_ordem, row['CODIGO']))
                    cursor.execute("UPDATE EST_CONTEUDO_CICLO SET ORDEM = ? WHERE CODIGO = ?", (curr_ordem, prev_row['CODIGO']))
                    conn.commit()
                    st.rerun()
            
            # Down Arrow (only if not last)
            if index < len(content_list) - 1:
                if c3_2.button("⬇️", key=f"down_{row['CODIGO']}", help="Mover para baixo"):
                    # Swap with next
                    next_row = content_list[index + 1]
                    
                    curr_ordem = row['ORDEM'] if row['ORDEM'] is not None else index + 1
                    next_ordem = next_row['ORDEM'] if next_row['ORDEM'] is not None else index + 2
                    
                    if curr_ordem == next_ordem:
                        next_ordem += 1
                        
                    cursor = conn.cursor()
                    cursor.execute("UPDATE EST_CONTEUDO_CICLO SET ORDEM = ? WHERE CODIGO = ?", (next_ordem, row['CODIGO']))
                    cursor.execute("UPDATE EST_CONTEUDO_CICLO SET ORDEM = ? WHERE CODIGO = ?", (curr_ordem, next_row['CODIGO']))
                    conn.commit()
                    st.rerun()
            
            # Delete
            if c4.button("🗑️", key=f"del_cont_{row['CODIGO']}"):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM EST_CONTEUDO_CICLO WHERE CODIGO = ?", (row['CODIGO'],))
                conn.commit()
                st.rerun()
    else:
        st.info("Nenhum conteúdo cadastrado para esta matéria.")
    
    if st.button("Fechar", key="btn_close_dialog"):
        st.session_state['active_modal'] = None
        st.rerun()
    
    conn.close()


st.title("🗂️ Cadastros")

# UX: Group Selector
group = st.radio(
    "Contexto:",
    ["📚 Base de Conhecimento", "⚙️ Estratégia & Projetos"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

if group == "📚 Base de Conhecimento":
    tab_grades, tab_areas, tab_materias = st.tabs(["Grades Semanais", "Áreas", "Matérias"])

    with tab_grades:
        st.subheader("Grades Semanais")
        create_crud_interface("EST_GRADE_SEMANAL", {
            'fields': [
                {'name': 'NOME', 'label': 'Nome da Grade', 'type': 'text'},
                {'name': 'PADRAO', 'label': 'Padrão', 'type': 'checkbox'}
            ],
            'list_columns': ['CODIGO', 'NOME', 'PADRAO']
        }, custom_title="Gerenciar Grades Semanais")
        
        st.divider()
        st.subheader("Horários da Grade")
        
        conn = get_connection()
        grades = pd.read_sql_query("SELECT CODIGO, NOME FROM EST_GRADE_SEMANAL WHERE COD_USUARIO = ?", conn, params=(user_id,))
        conn.close()
        
        if not grades.empty:
            grade_id = st.selectbox("Selecione a Grade:", grades['CODIGO'], format_func=lambda x: grades[grades['CODIGO'] == x]['NOME'].values[0])
            
            # List Items
            conn = get_connection()
            days = {1: 'Domingo', 2: 'Segunda', 3: 'Terça', 4: 'Quarta', 5: 'Quinta', 6: 'Sexta', 7: 'Sábado'}
            
            g_items = pd.read_sql_query(f"SELECT * FROM EST_GRADE_ITEM WHERE COD_GRADE = {grade_id} ORDER BY DIA_SEMANA, HORA_INICIAL", conn)
            
            # State for editing grade items
            if 'mode_grade_item' not in st.session_state:
                st.session_state['mode_grade_item'] = 'LIST'
            if 'edit_grade_item' not in st.session_state:
                st.session_state['edit_grade_item'] = None
            
            # Header & New Button
            c_head, c_new = st.columns([4, 1])
            c_head.markdown("**Horários Configurados**")
            if c_new.button("➕ Novo Horário"):
                st.session_state['mode_grade_item'] = 'NEW'
                st.session_state['edit_grade_item'] = None
                st.rerun()
                
            # Display List
            if not g_items.empty:
                cols = st.columns([1, 1, 1, 0.5, 0.5])
                cols[0].markdown("**Dia**")
                cols[1].markdown("**Início**")
                cols[2].markdown("**Fim**")
                
                for index, row in g_items.iterrows():
                    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 0.5, 0.5])
                    c1.text(days.get(row['DIA_SEMANA'], 'Unknown'))
                    c2.text(row['HORA_INICIAL'])
                    c3.text(row['HORA_FINAL'])
                    
                    if c4.button("✏️", key=f"edit_gitem_{row['CODIGO']}"):
                        st.session_state['mode_grade_item'] = 'EDIT'
                        st.session_state['edit_grade_item'] = row['CODIGO']
                        st.rerun()
                        
                    if c5.button("🗑️", key=f"del_gitem_{row['CODIGO']}"):
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM EST_GRADE_ITEM WHERE CODIGO = ?", (row['CODIGO'],))
                        conn.commit()
                        conn.close()
                        if st.session_state['edit_grade_item'] == row['CODIGO']:
                            st.session_state['mode_grade_item'] = 'LIST'
                            st.session_state['edit_grade_item'] = None
                        st.rerun()
            
            conn.close()
            
            # Add/Edit Form
            if st.session_state['mode_grade_item'] in ['NEW', 'EDIT']:
                st.divider()
                is_edit_g = st.session_state['mode_grade_item'] == 'EDIT'
                form_title = "Editar Horário" if is_edit_g else "Novo Horário"
                
                # Fetch item data if editing
                g_item_data = {}
                if is_edit_g and st.session_state['edit_grade_item']:
                    conn = get_connection()
                    g_item_df = pd.read_sql_query(f"SELECT * FROM EST_GRADE_ITEM WHERE CODIGO = {st.session_state['edit_grade_item']}", conn)
                    conn.close()
                    if not g_item_df.empty:
                        g_item_data = g_item_df.iloc[0].to_dict()
                
                with st.form("form_grade_item"):
                    st.markdown(f"**{form_title}**")
                    c1, c2, c3 = st.columns(3)
                    
                    default_day = int(g_item_data.get('DIA_SEMANA', 2))
                    dia = c1.selectbox("Dia da Semana", options=list(days.keys()), index=list(days.keys()).index(default_day), format_func=lambda x: days[x])
                    
                    default_ini = datetime.strptime(g_item_data.get('HORA_INICIAL', '19:00:00'), '%H:%M:%S').time() if 'HORA_INICIAL' in g_item_data else datetime.strptime('19:00', '%H:%M').time()
                    hora_ini = c2.time_input("Hora Inicial", value=default_ini)
                    
                    default_fim = datetime.strptime(g_item_data.get('HORA_FINAL', '22:00:00'), '%H:%M:%S').time() if 'HORA_FINAL' in g_item_data else datetime.strptime('22:00', '%H:%M').time()
                    hora_fim = c3.time_input("Hora Final", value=default_fim)
                    
                    c_sub, c_can, _ = st.columns([1.3, 1.3, 10])
                    if c_sub.form_submit_button("💾 Salvar"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        
                        str_ini = hora_ini.strftime('%H:%M:%S')
                        str_fim = hora_fim.strftime('%H:%M:%S')
                        
                        if is_edit_g:
                            cursor.execute("""
                                UPDATE EST_GRADE_ITEM SET DIA_SEMANA=?, HORA_INICIAL=?, HORA_FINAL=? WHERE CODIGO=?
                            """, (dia, str_ini, str_fim, st.session_state['edit_grade_item']))
                            st.toast("✅ Horário atualizado!", icon="✅")
                        else:
                            cursor.execute("""
                                INSERT INTO EST_GRADE_ITEM (COD_GRADE, DIA_SEMANA, HORA_INICIAL, HORA_FINAL)
                                VALUES (?, ?, ?, ?)
                            """, (grade_id, dia, str_ini, str_fim))
                            st.toast("✅ Horário adicionado!", icon="✅")
                        
                        conn.commit()
                        conn.close()
                        st.session_state['mode_grade_item'] = 'LIST'
                        st.session_state['edit_grade_item'] = None
                        st.rerun()
                        
                    if c_can.form_submit_button("❌ Cancelar"):
                        st.session_state['mode_grade_item'] = 'LIST'
                        st.session_state['edit_grade_item'] = None
                        st.rerun()

    with tab_areas:
        create_crud_interface("EST_AREA", {
            'fields': [{'name': 'NOME', 'label': 'Nome da Área', 'type': 'text'}],
            'list_columns': ['CODIGO', 'NOME']
        }, custom_title="Gerenciar Áreas")

    with tab_materias:
        create_crud_interface("EST_MATERIA", {
            'fields': [
                {'name': 'NOME', 'label': 'Nome da Matéria', 'type': 'text'},
                {'name': 'COD_AREA', 'label': 'Área', 'type': 'select', 'source': 'EST_AREA'},
                {'name': 'REVISAO', 'label': 'Revisão', 'type': 'checkbox'} 
            ],
            'list_columns': ['CODIGO', 'NOME', 'COD_AREA']
        }, custom_title="Gerenciar Matérias")

else: # Estratégia & Projetos
    # [FIX] Auto-close modal if user is editing other entities
    # This prevents the "Gerenciar Conteúdos" dialog from reopening inadvertently
    # when the user switches tabs and starts editing a Project or Grade.
    if (st.session_state.get('crud_EST_PROJETO_mode', 'LIST') in ['EDIT', 'NEW'] or 
        st.session_state.get('mode_ciclo_item', 'LIST') in ['EDIT', 'NEW']):
        st.session_state['active_modal'] = None

    # Order: Projetos -> Ciclos
    tab_projetos, tab_ciclos = st.tabs(["Projetos", "Ciclos"])

    with tab_projetos:
        create_crud_interface("EST_PROJETO", {
            'fields': [
                {'name': 'NOME', 'label': 'Nome do Projeto', 'type': 'text'},
                {'name': 'DATA_INICIAL', 'label': 'Data Início', 'type': 'date'},
                {'name': 'DATA_FINAL', 'label': 'Data Fim', 'type': 'date'},
                {'name': 'PADRAO', 'label': 'Padrão', 'type': 'checkbox'}
            ],
            'list_columns': ['CODIGO', 'NOME', 'DATA_INICIAL', 'DATA_FINAL', 'PADRAO']
        }, custom_title="Gerenciar Projetos")

    with tab_ciclos:
        st.subheader("Ciclos de Estudo")
        create_crud_interface("EST_CICLO", {
            'fields': [
                {'name': 'NOME', 'label': 'Nome do Ciclo', 'type': 'text'},
                {'name': 'PADRAO', 'label': 'Padrão', 'type': 'checkbox'}
            ],
            'list_columns': ['CODIGO', 'NOME', 'PADRAO']
        }, custom_title="Gerenciar Ciclos")
        
        st.divider()
        st.subheader("Itens do Ciclo")
        
        # Select Cycle to Edit Items
        conn = get_connection()
        ciclos = pd.read_sql_query("SELECT CODIGO, NOME FROM EST_CICLO WHERE COD_USUARIO = ?", conn, params=(user_id,))
        conn.close()
        
        if not ciclos.empty:
            ciclo_id = st.selectbox("Selecione o Ciclo para adicionar matérias:", ciclos['CODIGO'], format_func=lambda x: ciclos[ciclos['CODIGO'] == x]['NOME'].values[0])
            
            # Custom Interface for Cycle Items (Master-Detail)
            # List Items
            conn = get_connection()
            items = pd.read_sql_query(f"""
                SELECT ci.CODIGO, ci.INDICE, m.NOME as MATERIA, ci.QTDE_MINUTOS, ci.COD_MATERIA 
                FROM EST_CICLO_ITEM ci
                JOIN EST_MATERIA m ON ci.COD_MATERIA = m.CODIGO
                WHERE ci.COD_CICLO = {ciclo_id}
                ORDER BY ci.INDICE
            """, conn)
            
            # State for editing items
            if 'mode_ciclo_item' not in st.session_state:
                st.session_state['mode_ciclo_item'] = 'LIST'
            if 'edit_ciclo_item' not in st.session_state:
                st.session_state['edit_ciclo_item'] = None
                
            # Header & New Button
            c_head, c_new = st.columns([4, 1])
            c_head.markdown("**Itens do Ciclo**")
            if c_new.button("➕ Novo Item"):
                st.session_state['mode_ciclo_item'] = 'NEW'
                st.session_state['edit_ciclo_item'] = None
                st.rerun()



            # Display List
            if not items.empty:
                # Adjusted columns to include Contents button
                cols = st.columns([0.5, 3, 1, 1, 0.5, 0.5])
                cols[0].markdown("**#**")
                cols[1].markdown("**Matéria**")
                cols[2].markdown("**Conteúdos**")
                cols[3].markdown("**Minutos**")
                
                for index, row in items.iterrows():
                    c1, c2, c3, c4, c5, c6 = st.columns([0.5, 3, 1, 1, 0.5, 0.5])
                    c1.text(str(row['INDICE']))
                    c2.text(row['MATERIA'])
                    
                    # Contents Button
                    if c3.button("📜 Ver", key=f"btn_cont_{row['CODIGO']}"):
                        st.session_state['active_modal'] = {'id': row['CODIGO'], 'name': row['MATERIA']}
                        st.rerun()
                        
                    c4.text(f"{row['QTDE_MINUTOS']:.0f}")
                    
                    if c5.button("✏️", key=f"edit_item_{row['CODIGO']}"):
                        st.session_state['mode_ciclo_item'] = 'EDIT'
                        st.session_state['edit_ciclo_item'] = row['CODIGO']
                        st.rerun()
                        
                    if c6.button("🗑️", key=f"del_item_{row['CODIGO']}"):
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM EST_CICLO_ITEM WHERE CODIGO = ?", (row['CODIGO'],))
                        conn.commit()
                        conn.close()
                        if st.session_state['edit_ciclo_item'] == row['CODIGO']:
                            st.session_state['mode_ciclo_item'] = 'LIST'
                            st.session_state['edit_ciclo_item'] = None
                        st.rerun()
            
            conn.close()
            
            # Persistence Check for Dialog
            if 'active_modal' in st.session_state and st.session_state['active_modal']:
                manage_contents(st.session_state['active_modal']['id'], st.session_state['active_modal']['name'])
            
            # Add/Edit Form
            if st.session_state['mode_ciclo_item'] in ['NEW', 'EDIT']:
                st.divider()
                is_edit_item = st.session_state['mode_ciclo_item'] == 'EDIT'
                form_title = "Editar Item" if is_edit_item else "Adicionar Matéria ao Ciclo"
                
                # Fetch item data if editing
                item_data = {}
                if is_edit_item and st.session_state['edit_ciclo_item']:
                    conn = get_connection()
                    item_df = pd.read_sql_query(f"SELECT * FROM EST_CICLO_ITEM WHERE CODIGO = {st.session_state['edit_ciclo_item']}", conn)
                    conn.close()
                    if not item_df.empty:
                        item_data = item_df.iloc[0].to_dict()
                
                with st.form("form_ciclo_item"):
                    st.markdown(f"**{form_title}**")
                    col1, col2, col3 = st.columns(3)
                    
                    conn = get_connection()
                    materias = pd.read_sql_query("SELECT CODIGO, NOME FROM EST_MATERIA WHERE COD_USUARIO = ?", conn, params=(user_id,))
                    conn.close()
                    
                    # Prepare options
                    options_map = {row['CODIGO']: row['NOME'] for _, row in materias.iterrows()}
                    default_mat = item_data.get('COD_MATERIA') if is_edit_item else None
                    idx_mat = list(options_map.keys()).index(default_mat) if default_mat in options_map else 0
                    
                    materia_id = col1.selectbox("Matéria", options=list(options_map.keys()), index=idx_mat, format_func=lambda x: options_map.get(x, str(x)))
                    
                    default_min = float(item_data.get('QTDE_MINUTOS', 60))
                    minutos = col2.number_input("Minutos", min_value=10, value=int(default_min), step=10)
                    
                    default_idx = int(item_data.get('INDICE', len(items)+1))
                    indice = col3.number_input("Ordem (Índice)", min_value=1, value=default_idx)
                    
                    c_sub, c_can, _ = st.columns([1.3, 1.3, 10])
                    if c_sub.form_submit_button("💾 Salvar"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        
                        if is_edit_item:
                            cursor.execute("""
                                UPDATE EST_CICLO_ITEM SET COD_MATERIA=?, QTDE_MINUTOS=?, INDICE=? WHERE CODIGO=?
                            """, (materia_id, minutos, indice, st.session_state['edit_ciclo_item']))
                            st.toast("✅ Item atualizado!", icon="✅")
                        else:
                            cursor.execute("""
                                INSERT INTO EST_CICLO_ITEM (COD_CICLO, COD_MATERIA, QTDE_MINUTOS, INDICE)
                                VALUES (?, ?, ?, ?)
                            """, (ciclo_id, materia_id, minutos, indice))
                            st.toast("✅ Item adicionado!", icon="✅")
                        
                        conn.commit()
                        conn.close()
                        st.session_state['mode_ciclo_item'] = 'LIST'
                        st.session_state['edit_ciclo_item'] = None
                        st.rerun()
                        
                    if c_can.form_submit_button("❌ Cancelar"):
                        st.session_state['mode_ciclo_item'] = 'LIST'
                        st.session_state['edit_ciclo_item'] = None
                        st.rerun()
