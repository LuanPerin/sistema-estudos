import streamlit as st
import pandas as pd
from crud_helper import create_crud_interface
from db_manager import get_connection
from auth import require_auth, get_current_user
from datetime import date, datetime
import time

st.set_page_config(page_title="Cadastros", layout="wide")

# Require authentication
require_auth()
current_user = get_current_user()
user_id = current_user['CODIGO']

st.title("🗂️ Cadastros")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Áreas", "Matérias", "Ciclos", "Grades", "Projetos"])

with tab1:
    create_crud_interface("EST_AREA", {
        'fields': [{'name': 'NOME', 'label': 'Nome da Área', 'type': 'text'}],
        'list_columns': ['CODIGO', 'NOME']
    }, custom_title="Gerenciar Áreas")

with tab2:
    create_crud_interface("EST_MATERIA", {
        'fields': [
            {'name': 'NOME', 'label': 'Nome da Matéria', 'type': 'text'},
            {'name': 'COD_AREA', 'label': 'Área', 'type': 'select', 'source': 'EST_AREA'},
            {'name': 'REVISAO', 'label': 'Revisão', 'type': 'checkbox'} 
        ],
        'list_columns': ['CODIGO', 'NOME', 'COD_AREA']
    }, custom_title="Gerenciar Matérias")

with tab3:
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
            cols = st.columns([0.5, 3, 1, 0.5, 0.5])
            cols[0].markdown("**#**")
            cols[1].markdown("**Matéria**")
            cols[2].markdown("**Minutos**")
            
            for index, row in items.iterrows():
                c1, c2, c3, c4, c5 = st.columns([0.5, 3, 1, 0.5, 0.5])
                c1.text(str(row['INDICE']))
                c2.text(row['MATERIA'])
                c3.text(f"{row['QTDE_MINUTOS']:.0f}")
                
                if c4.button("✏️", key=f"edit_item_{row['CODIGO']}"):
                    st.session_state['mode_ciclo_item'] = 'EDIT'
                    st.session_state['edit_ciclo_item'] = row['CODIGO']
                    st.rerun()
                    
                if c5.button("🗑️", key=f"del_item_{row['CODIGO']}"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM EST_CICLO_ITEM WHERE CODIGO = ?", (row['CODIGO'],))
                    conn.commit()
                    conn.close()
                    if st.session_state['edit_ciclo_item'] == row['CODIGO']:
                        st.session_state['mode_ciclo_item'] = 'LIST'
                        st.session_state['edit_ciclo_item'] = None
                    st.rerun()
        
        conn.close()
        
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
                
                c_sub, c_can = st.columns(2)
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

with tab4:
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
            
        if not g_items.empty:
            g_items['DIA_NOME'] = g_items['DIA_SEMANA'].map(days)
            
            cols = st.columns([2, 1, 1, 1, 0.5, 0.5])
            cols[0].markdown("**Dia**")
            cols[1].markdown("**Início**")
            cols[2].markdown("**Fim**")
            cols[3].markdown("**Min**")
            
            for index, row in g_items.iterrows():
                c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 0.5, 0.5])
                c1.text(row['DIA_NOME'])
                c2.text(row['HORA_INICIAL'])
                c3.text(row['HORA_FINAL'])
                c4.text(f"{row['QTDE_MINUTOS']:.0f}")
                
                if c5.button("✏️", key=f"edit_gitem_{row['CODIGO']}"):
                    st.session_state['mode_grade_item'] = 'EDIT'
                    st.session_state['edit_grade_item'] = row['CODIGO']
                    st.rerun()
                    
                if c6.button("🗑️", key=f"del_gitem_{row['CODIGO']}"):
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
            is_edit_gitem = st.session_state['mode_grade_item'] == 'EDIT'
            form_title = "Editar Horário" if is_edit_gitem else "Adicionar Horário"
            
            # Fetch data if editing
            gitem_data = {}
            if is_edit_gitem and st.session_state['edit_grade_item']:
                conn = get_connection()
                gitem_df = pd.read_sql_query(f"SELECT * FROM EST_GRADE_ITEM WHERE CODIGO = {st.session_state['edit_grade_item']}", conn)
                conn.close()
                if not gitem_df.empty:
                    gitem_data = gitem_df.iloc[0].to_dict()

            with st.form("form_grade_item"):
                st.markdown(f"**{form_title}**")
                c1, c2, c3, c4 = st.columns(4)
                
                default_dia = int(gitem_data.get('DIA_SEMANA', 2))
                dia = c1.selectbox("Dia", options=list(days.keys()), index=list(days.keys()).index(default_dia), format_func=lambda x: days[x])
                
                def parse_time(t_str):
                    try: return pd.to_datetime(t_str).time()
                    except: return None
                    
                default_ini = parse_time(gitem_data.get('HORA_INICIAL'))
                default_fim = parse_time(gitem_data.get('HORA_FINAL'))
                
                inicio = c2.time_input("Início", value=default_ini)
                fim = c3.time_input("Fim", value=default_fim)
                
                default_mins = float(gitem_data.get('QTDE_MINUTOS', 60))
                mins = c4.number_input("Duração (min)", value=int(default_mins))
                
                c_sub, c_can = st.columns(2)
                if c_sub.form_submit_button("💾 Salvar"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    if is_edit_gitem:
                        cursor.execute("""
                            UPDATE EST_GRADE_ITEM SET DIA_SEMANA=?, HORA_INICIAL=?, HORA_FINAL=?, QTDE_MINUTOS=? WHERE CODIGO=?
                        """, (dia, str(inicio), str(fim), mins, st.session_state['edit_grade_item']))
                        st.toast("✅ Item atualizado!", icon="✅")
                    else:
                        cursor.execute("""
                            INSERT INTO EST_GRADE_ITEM (COD_GRADE, DIA_SEMANA, HORA_INICIAL, HORA_FINAL, QTDE_MINUTOS)
                            VALUES (?, ?, ?, ?, ?)
                        """, (grade_id, dia, str(inicio), str(fim), mins))
                        st.toast("✅ Item adicionado!", icon="✅")
                    
                    conn.commit()
                    conn.close()
                    st.session_state['mode_grade_item'] = 'LIST'
                    st.session_state['edit_grade_item'] = None
                    st.rerun()

                if c_can.form_submit_button("❌ Cancelar"):
                    st.session_state['mode_grade_item'] = 'LIST'
                    st.session_state['edit_grade_item'] = None
                    st.rerun()

with tab5:
    create_crud_interface("EST_PROJETO", {
        'fields': [
            {'name': 'NOME', 'label': 'Nome do Projeto', 'type': 'text'},
            {'name': 'DATA_INICIAL', 'label': 'Início', 'type': 'date'},
            {'name': 'DATA_FINAL', 'label': 'Fim', 'type': 'date'},
            {'name': 'PADRAO', 'label': 'Padrão', 'type': 'checkbox'}
        ],
        'list_columns': ['CODIGO', 'NOME', 'DATA_INICIAL', 'DATA_FINAL']
    }, custom_title="Gerenciar Projetos")
