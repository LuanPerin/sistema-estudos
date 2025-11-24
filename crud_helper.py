import streamlit as st
import pandas as pd
import time
from db_manager import get_connection
from auth import get_current_user

def create_crud_interface(table_name, model_config, custom_title=None):
    """
    Generates a standard List/Add/Edit/Delete interface.
    
    model_config: dict
    {
        'fields': [
            {'name': 'NOME', 'label': 'Nome', 'type': 'text'},
            {'name': 'COD_AREA', 'label': 'Area', 'type': 'select', 'source': 'EST_AREA'}
        ],
        'list_columns': ['CODIGO', 'NOME']
    }
    """
    # Get current user for filtering
    current_user = get_current_user()
    user_id = current_user['CODIGO'] if current_user else None
    
    # --- State Management ---
    # We use a composite key for state to avoid conflicts between tabs
    state_key_id = f"crud_{table_name}_id"
    state_key_mode = f"crud_{table_name}_mode" # 'LIST', 'EDIT', 'NEW'
    state_key_confirm_delete = f"crud_{table_name}_confirm_delete"
    
    if state_key_id not in st.session_state:
        st.session_state[state_key_id] = None
    if state_key_mode not in st.session_state:
        st.session_state[state_key_mode] = 'LIST'
    if state_key_confirm_delete not in st.session_state:
        st.session_state[state_key_confirm_delete] = None

    # --- Header & Actions ---
    col_header, col_new = st.columns([4, 1])
    with col_header:
        title = custom_title if custom_title else f"Gerenciar {table_name}"
        st.subheader(title)
    with col_new:
        if st.button("➕ Novo", key=f"btn_new_{table_name}"):
            st.session_state[state_key_mode] = 'NEW'
            st.session_state[state_key_id] = None
            st.rerun()

    # --- List ---
    conn = get_connection()
    
    # Check if table has COD_USUARIO column
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    has_user_column = 'COD_USUARIO' in columns
    
    # Build query with user filter if applicable
    if has_user_column and user_id:
        query = f"SELECT * FROM {table_name} WHERE COD_USUARIO = ?"
        df = pd.read_sql_query(query, conn, params=(user_id,))
    else:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    
    if not df.empty:
        # Header Row
        cols = st.columns([4, 0.5, 0.5])
        cols[0].markdown("**Registro**")
        cols[1].markdown("**Editar**")
        cols[2].markdown("**Excluir**")
        
        for index, row in df.iterrows():
            col1, col2, col3 = st.columns([4, 0.5, 0.5])
            with col1:
                # Format columns for display
                display_values = []
                for col in model_config.get('list_columns', df.columns):
                    val = row[col]
                    # Check if this column is a date field
                    field_config = next((f for f in model_config['fields'] if f['name'] == col), None)
                    if field_config and field_config['type'] == 'date' and val:
                        try:
                            val = pd.to_datetime(val).strftime('%d/%m/%Y')
                        except: pass
                    display_values.append(str(val))
                
                display_text = " | ".join(display_values)
                st.text(display_text)
            with col2:
                if st.button("✏️", key=f"edit_{table_name}_{row['CODIGO']}"):
                    st.session_state[state_key_mode] = 'EDIT'
                    st.session_state[state_key_id] = row['CODIGO']
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"del_{table_name}_{row['CODIGO']}"):
                    st.session_state[state_key_confirm_delete] = row['CODIGO']
                    st.rerun()
        
        # Delete Confirmation Dialog
        if st.session_state[state_key_confirm_delete]:
            @st.dialog("Confirmar Exclusão")
            def confirm_delete():
                st.warning(f"⚠️ Tem certeza que deseja excluir este registro?")
                st.caption("Esta ação não pode ser desfeita.")
                
                col_yes, col_no = st.columns(2)
                if col_yes.button("✅ Sim, Excluir", use_container_width=True):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM {table_name} WHERE CODIGO = ?", (st.session_state[state_key_confirm_delete],))
                    conn.commit()
                    conn.close()
                    
                    # Reset states
                    if st.session_state[state_key_id] == st.session_state[state_key_confirm_delete]:
                        st.session_state[state_key_mode] = 'LIST'
                        st.session_state[state_key_id] = None
                    st.session_state[state_key_confirm_delete] = None
                    
                    st.toast("✅ Registro excluído com sucesso!", icon="✅")
                    time.sleep(1)
                    st.rerun()
                    
                if col_no.button("❌ Cancelar", use_container_width=True):
                    st.session_state[state_key_confirm_delete] = None
                    st.rerun()
            
            confirm_delete()
        
        st.divider()
    else:
        st.info("Nenhum registro encontrado.")

    # --- Form (Conditional Visibility) ---
    if st.session_state[state_key_mode] in ['NEW', 'EDIT']:
        is_edit = st.session_state[state_key_mode] == 'EDIT'
        form_title = "Editar Registro" if is_edit else "Adicionar Novo"
        
        st.markdown(f"### {form_title}")
        
        # Fetch data if Edit
        record_data = {}
        if is_edit and st.session_state[state_key_id]:
            conn = get_connection()
            record_df = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE CODIGO = ?", conn, params=(st.session_state[state_key_id],))
            conn.close()
            if not record_df.empty:
                record_data = record_df.iloc[0].to_dict()
        
        with st.form(f"form_{table_name}"):
            form_data = {}
            for field in model_config['fields']:
                default_val = record_data.get(field['name']) if is_edit else None
                
                if field['type'] == 'text':
                    form_data[field['name']] = st.text_input(field['label'], value=default_val if default_val else "")
                elif field['type'] == 'number':
                    form_data[field['name']] = st.number_input(field['label'], step=1.0, value=float(default_val) if default_val else 0.0)
                elif field['type'] == 'select':
                    conn = get_connection()
                    
                    # Check if source table has COD_USUARIO
                    cursor = conn.cursor()
                    cursor.execute(f"PRAGMA table_info({field['source']})")
                    src_cols = [col[1] for col in cursor.fetchall()]
                    
                    if 'COD_USUARIO' in src_cols and user_id:
                        opts = pd.read_sql_query(f"SELECT CODIGO, NOME FROM {field['source']} WHERE COD_USUARIO = ?", conn, params=(user_id,))
                    else:
                        opts = pd.read_sql_query(f"SELECT CODIGO, NOME FROM {field['source']}", conn)
                    
                    conn.close()
                    options_map = {row['CODIGO']: row['NOME'] for _, row in opts.iterrows()}
                    
                    idx = 0
                    if default_val and default_val in list(options_map.keys()):
                        idx = list(options_map.keys()).index(default_val)
                        
                    form_data[field['name']] = st.selectbox(
                        field['label'], 
                        options=list(options_map.keys()), 
                        index=idx,
                        format_func=lambda x: options_map.get(x, str(x))
                    )
                elif field['type'] == 'time':
                    val = None
                    if default_val:
                        try:
                            val = pd.to_datetime(default_val).time()
                        except: pass
                    form_data[field['name']] = st.time_input(field['label'], value=val)
                elif field['type'] == 'date':
                    val = None
                    if default_val:
                        try:
                            val = pd.to_datetime(default_val).date()
                        except: pass
                    form_data[field['name']] = st.date_input(field['label'], value=val, format="DD/MM/YYYY")
                elif field['type'] == 'checkbox':
                    # Handle S/N mapping
                    is_checked = (default_val == 'S')
                    val = st.checkbox(field['label'], value=is_checked)
                    form_data[field['name']] = 'S' if val else 'N'

            c1, c2 = st.columns(2)
            if c1.form_submit_button("💾 Salvar"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    vals = [str(v) for v in form_data.values()]
                    
                    if is_edit:
                        set_clause = ', '.join([f"{k} = ?" for k in form_data.keys()])
                        vals.append(st.session_state[state_key_id])
                        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE CODIGO = ?", vals)
                        st.toast("✅ Registro atualizado!", icon="✅")
                    else:
                        # Add COD_USUARIO automatically if table has that column
                        if has_user_column and user_id:
                            form_data['COD_USUARIO'] = user_id
                            vals.append(user_id)
                        
                        cols = ', '.join(form_data.keys())
                        placeholders = ', '.join(['?'] * len(form_data))
                        cursor.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", vals)
                        st.toast("✅ Registro criado!", icon="✅")
                    
                    conn.commit()
                    conn.close()
                    st.session_state[state_key_mode] = 'LIST'
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            
            if c2.form_submit_button("❌ Cancelar"):
                st.session_state[state_key_mode] = 'LIST'
                st.rerun()
