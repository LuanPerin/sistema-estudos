
import streamlit as st
import pandas as pd
import json
from db_manager import get_connection
from auth import get_current_user
import time

# Note: st.set_page_config handled in App.py
# require_auth handled by App.py navigation logic

st.title("💾 Backup e Restauração")

current_user = get_current_user()
if not current_user:
    st.warning("Acesso negado. Por favor, faça login.")
    st.stop()
user_id = current_user['CODIGO']

tab_export, tab_import, tab_clean = st.tabs(["📤 Exportar Dados", "📥 Restaurar Backup", "🗑️ Limpar Dados"])

# --- EXPORT ---
with tab_export:
    st.markdown("### Exportar Estratégia e Dados")
    st.info("Gera um arquivo JSON contendo todas as suas configurações: Áreas, Matérias, Ciclos, Conteúdos, Projetos e Histórico.")
    
    if st.button("📦 Gerar Arquivo de Backup"):
        conn = get_connection()
        backup_data = {
            "version": "1.0",
            "timestamp": time.time(),
            "data": {}
        }
        
        tables = [
            "EST_AREA", "EST_MATERIA", 
            "EST_GRADE_SEMANAL", "EST_GRADE_ITEM", 
            "EST_PROJETO", 
            "EST_CICLO", "EST_CICLO_ITEM", "EST_CONTEUDO_CICLO",
            "EST_ESTUDOS", "EST_PROGRAMACAO"
        ]
        
        try:
            for table in tables:
                # Check if table has COD_USUARIO
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in cursor.fetchall()]
                
                if 'COD_USUARIO' in cols:
                    df = pd.read_sql_query(f"SELECT * FROM {table} WHERE COD_USUARIO = ?", conn, params=(user_id,))
                else:
                    # Tables like EST_CICLO_ITEM, EST_CONTEUDO_CICLO don't have COD_USUARIO directly,
                    # they depend on parent tables.
                    # However, for simplicity in this version, we will fetch ALL and filter in logic or 
                    # better: rely on the fact that we are exporting a "Strategy" which might be shared.
                    # BUT, for strict backup, we must filter.
                    
                    # Dependency Filtering Logic
                    if table == "EST_CICLO_ITEM":
                        df = pd.read_sql_query(f"""
                            SELECT ci.* FROM EST_CICLO_ITEM ci
                            JOIN EST_CICLO c ON ci.COD_CICLO = c.CODIGO
                            WHERE c.COD_USUARIO = ?
                        """, conn, params=(user_id,))
                    elif table == "EST_CONTEUDO_CICLO":
                        df = pd.read_sql_query(f"""
                            SELECT cc.* FROM EST_CONTEUDO_CICLO cc
                            JOIN EST_CICLO_ITEM ci ON cc.COD_CICLO_ITEM = ci.CODIGO
                            JOIN EST_CICLO c ON ci.COD_CICLO = c.CODIGO
                            WHERE c.COD_USUARIO = ?
                        """, conn, params=(user_id,))
                    elif table == "EST_GRADE_ITEM":
                        df = pd.read_sql_query(f"""
                            SELECT gi.* FROM EST_GRADE_ITEM gi
                            JOIN EST_GRADE_SEMANAL g ON gi.COD_GRADE = g.CODIGO
                            WHERE g.COD_USUARIO = ?
                        """, conn, params=(user_id,))
                    else:
                        # Fallback (should not happen for the main tables listed above if schema is correct)
                        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

                backup_data["data"][table] = df.to_dict(orient="records")
            
            # Serialize
            json_str = json.dumps(backup_data, indent=4, default=str)
            
            st.success("Backup gerado com sucesso!")
            st.download_button(
                label="⬇️ Baixar backup_estudos.json",
                data=json_str,
                file_name="backup_estudos.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Erro ao gerar backup: {e}")
        finally:
            conn.close()

# --- IMPORT ---
with tab_import:
    st.markdown("### Restaurar Backup")
    st.warning("⚠️ **Atenção:** A restauração irá **APAGAR** todos os seus dados atuais e substitui-los pelo backup.")
    
    uploaded_file = st.file_uploader("Selecione o arquivo .json", type=["json"])
    
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            
            if "version" not in data or "data" not in data:
                st.error("Arquivo inválido ou corrompido.")
            else:
                st.info(f"Arquivo carregado. Versão: {data.get('version')}")
                
                if st.button("🚀 Iniciar Restauração"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    # 1. Atomic Clean & Restore
                    try:
                        # DELETE Existing Data (Reverse Order)
                        delete_order = [
                            "EST_PROGRAMACAO", "EST_ESTUDOS",
                            "EST_CONTEUDO_CICLO",
                            "EST_CICLO_ITEM",
                            "EST_CICLO",
                            "EST_PROJETO",
                            "EST_GRADE_ITEM",
                            "EST_GRADE_SEMANAL",
                            "EST_MATERIA",
                            "EST_AREA"
                        ]
                        
                        progress_text = "Limpando dados antigos..."
                        progress_bar = st.progress(0, text=progress_text)
                        
                        for idx_del, table in enumerate(delete_order):
                            progress_bar.progress((idx_del + 1) / len(delete_order), text=f"Limpando {table}...")
                            # Check if table has COD_USUARIO
                            cursor.execute(f"PRAGMA table_info({table})")
                            cols = [c[1] for c in cursor.fetchall()]
                            
                            if 'COD_USUARIO' in cols:
                                cursor.execute(f"DELETE FROM {table} WHERE COD_USUARIO = ?", (user_id,))
                            else:
                                # Dependency Deletion Logic (Cascade simulation)
                                # Since we are deleting parents (Ciclo, Grade, Area) that belong to the user,
                                # and we assume SQLite Foreign Keys with ON DELETE CASCADE are NOT enabled or relied upon here for safety,
                                # we should manually delete orphans or rely on the fact that we delete parents later?
                                # Actually, to be safe and avoid FK constraint errors if enforced:
                                # We must delete Children FIRST.
                                
                                # EST_CONTEUDO_CICLO -> EST_CICLO_ITEM -> EST_CICLO (User)
                                if table == "EST_CONTEUDO_CICLO":
                                    cursor.execute(f"""
                                        DELETE FROM EST_CONTEUDO_CICLO WHERE COD_CICLO_ITEM IN (
                                            SELECT CODIGO FROM EST_CICLO_ITEM WHERE COD_CICLO IN (
                                                SELECT CODIGO FROM EST_CICLO WHERE COD_USUARIO = ?
                                            )
                                        )
                                    """, (user_id,))
                                elif table == "EST_CICLO_ITEM":
                                    cursor.execute(f"""
                                        DELETE FROM EST_CICLO_ITEM WHERE COD_CICLO IN (
                                            SELECT CODIGO FROM EST_CICLO WHERE COD_USUARIO = ?
                                        )
                                    """, (user_id,))
                                elif table == "EST_GRADE_ITEM":
                                    cursor.execute(f"""
                                        DELETE FROM EST_GRADE_ITEM WHERE COD_GRADE IN (
                                            SELECT CODIGO FROM EST_GRADE_SEMANAL WHERE COD_USUARIO = ?
                                        )
                                    """, (user_id,))
                        
                        # 2. Import Logic with ID Remapping
                        id_map = {
                            "EST_AREA": {},
                            "EST_MATERIA": {},
                            "EST_GRADE_SEMANAL": {},
                            "EST_GRADE_ITEM": {}, 
                            "EST_PROJETO": {},
                            "EST_CICLO": {},
                            "EST_CICLO_ITEM": {},
                            "EST_CONTEUDO_CICLO": {}, 
                            "EST_ESTUDOS": {},
                            "EST_PROGRAMACAO": {}
                        }
                        
                        tables_order = [
                            "EST_AREA", "EST_MATERIA", 
                            "EST_GRADE_SEMANAL", "EST_GRADE_ITEM", 
                            "EST_PROJETO", 
                            "EST_CICLO", "EST_CICLO_ITEM", "EST_CONTEUDO_CICLO",
                            "EST_ESTUDOS", "EST_PROGRAMACAO"
                        ]
                        
                        for idx, table in enumerate(tables_order):
                            progress_text = f"Importando {table}..."
                            progress_bar.progress((idx + 1) / len(tables_order), text=progress_text)
                            
                            records = data["data"].get(table, [])
                            
                            for row in records:
                                old_id = row['CODIGO']
                                
                                # Prepare Row for Insert
                                row.pop('CODIGO', None)
                                
                                # Set Current User
                                if 'COD_USUARIO' in row:
                                    row['COD_USUARIO'] = user_id
                                    
                                # Remap Foreign Keys
                                if table == "EST_MATERIA":
                                    row['COD_AREA'] = id_map["EST_AREA"].get(row['COD_AREA'])
                                    
                                elif table == "EST_GRADE_ITEM":
                                    row['COD_GRADE'] = id_map["EST_GRADE_SEMANAL"].get(row['COD_GRADE'])
                                    
                                elif table == "EST_CICLO_ITEM":
                                    row['COD_CICLO'] = id_map["EST_CICLO"].get(row['COD_CICLO'])
                                    row['COD_MATERIA'] = id_map["EST_MATERIA"].get(row['COD_MATERIA'])
                                    
                                elif table == "EST_CONTEUDO_CICLO":
                                    row['COD_CICLO_ITEM'] = id_map["EST_CICLO_ITEM"].get(row['COD_CICLO_ITEM'])
                                    
                                elif table == "EST_ESTUDOS" or table == "EST_PROGRAMACAO":
                                    row['COD_PROJETO'] = id_map["EST_PROJETO"].get(row['COD_PROJETO'])
                                    row['COD_CICLO'] = id_map["EST_CICLO"].get(row['COD_CICLO'])
                                    row['COD_CICLO_ITEM'] = id_map["EST_CICLO_ITEM"].get(row['COD_CICLO_ITEM']) if row.get('COD_CICLO_ITEM') else None
                                    row['COD_GRADE'] = id_map["EST_GRADE_SEMANAL"].get(row['COD_GRADE']) if row.get('COD_GRADE') else None
                                    row['COD_GRADE_ITEM'] = id_map["EST_GRADE_ITEM"].get(row['COD_GRADE_ITEM']) if row.get('COD_GRADE_ITEM') else None
                                    row['COD_MATERIA'] = id_map["EST_MATERIA"].get(row['COD_MATERIA']) if row.get('COD_MATERIA') else None
                                
                                # Construct INSERT
                                # Filter keys to match table columns
                                cursor.execute(f"PRAGMA table_info({table})")
                                valid_cols = {c[1] for c in cursor.fetchall()}
                                filtered_row = {k: v for k, v in row.items() if k in valid_cols}
                                
                                columns = ', '.join(filtered_row.keys())
                                placeholders = ', '.join(['?'] * len(filtered_row))
                                values = tuple(filtered_row.values())
                                
                                cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
                                new_id = cursor.lastrowid
                                
                                # Store Mapping
                                id_map[table][old_id] = new_id
                            
                        conn.commit()
                        st.success("✅ Restauração concluída com sucesso! Seus dados antigos foram substituídos.")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                        
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Erro durante a importação: {e}")
                        st.error("As alterações foram desfeitas.")
                    finally:
                        conn.close()
                            
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")

# --- CLEAN ---
with tab_clean:
    st.markdown("### 🗑️ Limpar Banco de Dados")
    st.error("⚠️ **PERIGO:** Esta ação apagará **TODOS** os seus dados (Áreas, Matérias, Ciclos, Histórico, etc.). Apenas seu usuário e senha serão mantidos.")
    st.markdown("Use esta opção se quiser começar do zero.")
    
    confirm_clean = st.checkbox("Estou ciente de que esta ação é irreversível e desejo apagar meus dados.")
    
    if st.button("💣 Apagar Tudo", type="primary", disabled=not confirm_clean):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            delete_order = [
                "EST_PROGRAMACAO", "EST_ESTUDOS",
                "EST_CONTEUDO_CICLO",
                "EST_CICLO_ITEM",
                "EST_CICLO",
                "EST_PROJETO",
                "EST_GRADE_ITEM",
                "EST_GRADE_SEMANAL",
                "EST_MATERIA",
                "EST_AREA"
            ]
            
            progress_text = "Apagando dados..."
            progress_bar = st.progress(0, text=progress_text)
            
            for idx, table in enumerate(delete_order):
                # Check if table has COD_USUARIO
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in cursor.fetchall()]
                
                if 'COD_USUARIO' in cols:
                    cursor.execute(f"DELETE FROM {table} WHERE COD_USUARIO = ?", (user_id,))
                else:
                    # Dependency Deletion Logic
                    if table == "EST_CONTEUDO_CICLO":
                        cursor.execute(f"""
                            DELETE FROM EST_CONTEUDO_CICLO WHERE COD_CICLO_ITEM IN (
                                SELECT CODIGO FROM EST_CICLO_ITEM WHERE COD_CICLO IN (
                                    SELECT CODIGO FROM EST_CICLO WHERE COD_USUARIO = ?
                                )
                            )
                        """, (user_id,))
                    elif table == "EST_CICLO_ITEM":
                        cursor.execute(f"""
                            DELETE FROM EST_CICLO_ITEM WHERE COD_CICLO IN (
                                SELECT CODIGO FROM EST_CICLO WHERE COD_USUARIO = ?
                            )
                        """, (user_id,))
                    elif table == "EST_GRADE_ITEM":
                        cursor.execute(f"""
                            DELETE FROM EST_GRADE_ITEM WHERE COD_GRADE IN (
                                SELECT CODIGO FROM EST_GRADE_SEMANAL WHERE COD_USUARIO = ?
                            )
                        """, (user_id,))
                
                progress_bar.progress((idx + 1) / len(delete_order))
            
            conn.commit()
            st.success("✅ Todos os dados foram apagados com sucesso! Sua conta agora está vazia.")
            st.balloons()
            time.sleep(2)
            st.rerun()
            
        except Exception as e:
            conn.rollback()
            st.error(f"Erro ao limpar dados: {e}")
        finally:
            conn.close()
