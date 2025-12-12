import streamlit as st
from db_manager import init_db, get_connection
from auth import get_current_user, logout
import pandas as pd
from datetime import date, timedelta

# Note: st.set_page_config handled in App.py
# require_auth handled by App.py navigation logic

# Get current user
current_user = get_current_user()
user_id = current_user['CODIGO']

c1, c2 = st.columns([0.1, 0.9])
with c1:
    st.image("icon.png", width=50)
with c2:
    st.title("Gerenciador de Estudos")

st.markdown("""
Bem-vindo ao seu gerenciador de estudos pessoal.

**Funcionalidades:**
*   **Planejamento**: Gere seu cronograma de estudos automaticamente.
*   **Estudar**: Acompanhe suas sessões com timer e registro de questões.
*   **Cadastros**: Gerencie suas matérias, ciclos e grades horárias.

Selecione uma opção no menu lateral para começar.
""")

# === Initialize Selected Project FIRST (before anything else) ===
if 'selected_project' not in st.session_state:
    # Try to get default project FOR THIS USER
    conn_init = get_connection()
    default_proj = pd.read_sql_query(
        "SELECT CODIGO FROM EST_PROJETO WHERE PADRAO = 'S' AND COD_USUARIO = ? LIMIT 1", 
        conn_init, params=(user_id,)
    )
    conn_init.close()
    
    if not default_proj.empty:
        st.session_state['selected_project'] = default_proj.iloc[0]['CODIGO']
    else:
        # Get first project as fallback
        conn_init = get_connection()
        first_proj = pd.read_sql_query(
            "SELECT CODIGO FROM EST_PROJETO WHERE COD_USUARIO = ? ORDER BY CODIGO LIMIT 1", 
            conn_init, params=(user_id,)
        )
        conn_init.close()
        
        if not first_proj.empty:
            st.session_state['selected_project'] = first_proj.iloc[0]['CODIGO']
        else:
            st.session_state['selected_project'] = None

# --- Project Selection (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Configuração")
    
    conn_sidebar = get_connection()
    projetos = pd.read_sql_query(
        "SELECT CODIGO, NOME FROM EST_PROJETO WHERE COD_USUARIO = ? ORDER BY CODIGO", 
        conn_sidebar, params=(user_id,)
    )
    conn_sidebar.close()
    
    if not projetos.empty:
        # Project selector
        selected_idx = projetos[projetos['CODIGO'] == st.session_state['selected_project']].index
        idx = selected_idx[0] if len(selected_idx) > 0 else 0
        
        selected_project = st.selectbox(
            "📁 Projeto Ativo",
            options=projetos['CODIGO'].tolist(),
            index=idx,
            format_func=lambda x: projetos[projetos['CODIGO'] == x]['NOME'].values[0]
        )
        
        # Update session state if changed
        if selected_project != st.session_state['selected_project']:
            st.session_state['selected_project'] = selected_project
            st.rerun()
    else:
        st.warning("⚠️ Nenhum projeto cadastrado. Vá em Cadastros → Projetos.")
        st.session_state['selected_project'] = None

    st.divider()
    
    # User info and logout
    st.caption(f"👤 {current_user['NOME']}")
    if st.button("🚪 Sair", use_container_width=True):
        logout()
        st.rerun()

# Dashboard Logic
conn = get_connection()
project_id = st.session_state.get('selected_project')

# Convert numpy.int64 to Python int (fixes pandas query issues)
if project_id is not None:
    project_id = int(project_id)

# Check if project is selected
if project_id is None:
    st.warning("⚠️ Nenhum projeto selecionado. Por favor, selecione um projeto na sidebar ou limpe o cache (Ctrl+Shift+R).")
    st.stop()

# 1. Horas Hoje
today = date.today().isoformat()
df_today = pd.read_sql_query("SELECT SUM(HL_REALIZADA) as TOTAL_HORAS FROM EST_ESTUDOS WHERE DATA = ? AND COD_PROJETO = ?", conn, params=(today, project_id))

horas_hoje = df_today['TOTAL_HORAS'].iloc[0] if df_today['TOTAL_HORAS'].iloc[0] else 0.0
questoes_hoje = 0 # Column QTDE_QUESTOES does not exist yet

# 2. Dias Seguidos (Streak)
# Get all unique study dates in descending order
dates_df = pd.read_sql_query("SELECT DISTINCT DATA FROM EST_ESTUDOS WHERE COD_PROJETO = ? ORDER BY DATA DESC", conn, params=(project_id,))
streak = 0
if not dates_df.empty:
    study_dates = pd.to_datetime(dates_df['DATA'], errors='coerce').dropna().dt.date.tolist()
    
    # Check if studied today or yesterday to keep streak alive
    if not study_dates:
        streak = 0
    else:
        last_study = study_dates[0]
    current_check = date.today()
    
    if last_study == current_check:
        streak = 1
        check_idx = 1
    elif last_study == current_check - timedelta(days=1):
        streak = 1
        check_idx = 1
        current_check -= timedelta(days=1) # Start checking from yesterday
    else:
        streak = 0
        check_idx = 0 # No active streak
        
    # Count backwards
    if streak > 0:
        while check_idx < len(study_dates):
            expected_date = current_check - timedelta(days=1)
            if study_dates[check_idx] == expected_date:
                streak += 1
                current_check = expected_date
                check_idx += 1
            else:
                break

# 3. Totais do Projeto
# Total Realizado
df_total_real = pd.read_sql_query("SELECT SUM(HL_REALIZADA) as TOTAL FROM EST_ESTUDOS WHERE COD_PROJETO = ?", conn, params=(project_id,))
total_horas_real = df_total_real['TOTAL'].iloc[0] if df_total_real['TOTAL'].iloc[0] else 0.0

# Total Planejado
df_total_plan = pd.read_sql_query("SELECT SUM(HL_PREVISTA) as TOTAL FROM EST_PROGRAMACAO WHERE COD_PROJETO = ?", conn, params=(project_id,))
total_horas_plan = df_total_plan['TOTAL'].iloc[0] if df_total_plan['TOTAL'].iloc[0] else 0.0

conn.close()

# Display KPIs
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Dias Seguidos", f"{streak} 🔥")
col2.metric("Horas Hoje", f"{horas_hoje:.2f}h ⏳")
col3.metric("Questões Hoje", f"{int(questoes_hoje)} ✅")
col4.metric("Horas Totais", f"{total_horas_real:.2f}h 📚")
col5.metric("Horas Planejadas", f"{total_horas_plan:.2f}h 🎯")

st.divider()
st.subheader("📊 Raio X da Preparação")

# --- 1. Agenda Diária ---
st.markdown("### 📅 Agenda Diária")
conn = get_connection()
agenda_query = """
    SELECT 
        p.DESC_AULA as Descrição,
        p.HR_INICIAL_PREVISTA as 'Hr. Inicial',
        p.HL_PREVISTA as 'Qtde Horas'
    FROM EST_PROGRAMACAO p
    WHERE p.DATA = ? AND p.COD_PROJETO = ?
    ORDER BY p.HR_INICIAL_PREVISTA
"""
df_agenda = pd.read_sql_query(agenda_query, conn, params=(today, project_id))

if not df_agenda.empty:
    # Calculate End Time and Minutes
    df_agenda['Qtde Minutos'] = df_agenda['Qtde Horas'] * 60
    
    def calc_end_time(row):
        try:
            start = pd.to_datetime(row['Hr. Inicial'], format='%H:%M:%S')
            end = start + pd.Timedelta(hours=row['Qtde Horas'])
            return end.strftime('%H:%M:%S')
        except: return "-"
        
    df_agenda['Hr. Final'] = df_agenda.apply(calc_end_time, axis=1)
    
    # Reorder columns
    df_agenda = df_agenda[['Descrição', 'Hr. Inicial', 'Hr. Final', 'Qtde Minutos', 'Qtde Horas']]
    
    st.dataframe(
        df_agenda, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Qtde Horas": st.column_config.NumberColumn(format="%.2f"),
            "Qtde Minutos": st.column_config.NumberColumn(format="%.0f")
        }
    )
else:
    st.info("Nenhuma atividade agendada para hoje.")

# --- 2. Evolução Programação - Semana ---
st.markdown("### 📈 Evolução Programação - Semana")

# Calculate Start/End of Week (Sunday to Saturday)
dt_today = date.today()
idx_weekday = (dt_today.weekday() + 1) % 7 # Mon=0 -> Sun=0 conversion
start_week = dt_today - timedelta(days=idx_weekday)
end_week = start_week + timedelta(days=6)

# Fetch Data
week_prog = pd.read_sql_query("""
    SELECT DATA, SUM(HL_PREVISTA) as HL 
    FROM EST_PROGRAMACAO 
    WHERE DATA BETWEEN ? AND ? AND COD_PROJETO = ?
    GROUP BY DATA
""", conn, params=(start_week.isoformat(), end_week.isoformat(), project_id))

week_real = pd.read_sql_query("""
    SELECT DATA, SUM(HL_REALIZADA) as HL 
    FROM EST_ESTUDOS 
    WHERE DATA BETWEEN ? AND ? AND COD_PROJETO = ?
    GROUP BY DATA
""", conn, params=(start_week.isoformat(), end_week.isoformat(), project_id))

# Build Pivot Table
days_cols = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
data_matrix = {'Tipo': ['PREVISTA', 'REALIZADA']}
for d in days_cols: data_matrix[d] = [0.0, 0.0]

# Fill Data
def fill_week_data(df, row_idx):
    for _, row in df.iterrows():
        d_obj = pd.to_datetime(row['DATA'])
        d_idx = (d_obj.weekday() + 1) % 7
        day_name = days_cols[d_idx]
        data_matrix[day_name][row_idx] = float(row['HL'])

fill_week_data(week_prog, 0)
fill_week_data(week_real, 1)

df_week = pd.DataFrame(data_matrix)
df_week['Total'] = df_week[days_cols].sum(axis=1)
df_week['Média'] = df_week['Total'] / 7

# Config for all numeric columns
week_config = {col: st.column_config.NumberColumn(format="%.2f") for col in days_cols + ['Total', 'Média']}

st.dataframe(
    df_week, 
    use_container_width=True, 
    hide_index=True,
    column_config=week_config
)

# --- 3. Evolução Programação - Projeto ---
st.markdown("### 🏗️ Evolução Programação - Projeto")

# Get Project Info
proj = pd.read_sql_query("SELECT DATA_INICIAL FROM EST_PROJETO WHERE CODIGO = ?", conn, params=(project_id,))
if not proj.empty:
    dt_inicio = pd.to_datetime(proj.iloc[0]['DATA_INICIAL']).date()
    
    # Totals
    total_prev = pd.read_sql_query("SELECT SUM(HL_PREVISTA) as T FROM EST_PROGRAMACAO WHERE COD_PROJETO = ?", conn, params=(project_id,)).iloc[0]['T'] or 0.0
    total_real = pd.read_sql_query("SELECT SUM(HL_REALIZADA) as T FROM EST_ESTUDOS WHERE COD_PROJETO = ?", conn, params=(project_id,)).iloc[0]['T'] or 0.0
    
    # Calcs
    total_days = (date.today() - dt_inicio).days + 1
    current_week = (total_days // 7) + 1
    avg_prev = total_prev / total_days if total_days > 0 else 0
    avg_real = total_real / total_days if total_days > 0 else 0
    
    df_proj = pd.DataFrame([{
        'Dt. Início': dt_inicio.strftime('%d/%m/%Y'),
        'Semana Atual': current_week,
        'Ttl Dias': total_days,
        'Ttl Hr. Previstas': total_prev,
        'Ttl Hr. Efetivas': total_real,
        'Média Hr. Prev.': avg_prev,
        'Média Hr. Efet.': avg_real
    }])
    
    st.dataframe(
        df_proj, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            'Ttl Hr. Previstas': st.column_config.NumberColumn(format="%.2f"),
            'Ttl Hr. Efetivas': st.column_config.NumberColumn(format="%.2f"),
            'Média Hr. Prev.': st.column_config.NumberColumn(format="%.2f"),
            'Média Hr. Efet.': st.column_config.NumberColumn(format="%.2f")
        }
    )

# --- 4. & 4.1 Disciplinas e Progresso ---
# First, fetch Progress Data to decide layout
conn = get_connection()
df_progress = pd.read_sql_query("""
    SELECT 
        m.NOME as MATERIA,
        COUNT(cc.CODIGO) as TOTAL,
        SUM(CASE WHEN cc.FINALIZADO = 'S' THEN 1 ELSE 0 END) as CONCLUIDO
    FROM EST_CONTEUDO_CICLO cc
    JOIN EST_CICLO_ITEM ci ON cc.COD_CICLO_ITEM = ci.CODIGO
    JOIN EST_MATERIA m ON ci.COD_MATERIA = m.CODIGO
    WHERE ci.COD_CICLO IN (
        SELECT DISTINCT COD_CICLO FROM EST_PROGRAMACAO WHERE COD_PROJETO = ?
        UNION
        SELECT DISTINCT COD_CICLO FROM EST_ESTUDOS WHERE COD_PROJETO = ?
    )
    GROUP BY m.NOME
    HAVING TOTAL > 0
    ORDER BY (CAST(CONCLUIDO AS FLOAT) / TOTAL) DESC
""", conn, params=(project_id, project_id))
conn.close()

# Define render function for Hours Table (to reuse)
def render_hours_table():
    conn = get_connection()
    # Extract Subject from Description (Simple Heuristic: Remove "Estudo de ")
    df_subj = pd.read_sql_query("SELECT DESC_AULA, HL_REALIZADA FROM EST_ESTUDOS WHERE COD_PROJETO = ?", conn, params=(project_id,))
    conn.close()
    
    if not df_subj.empty:
        df_subj['Disciplina'] = df_subj['DESC_AULA'].apply(lambda x: x.replace('Estudo de ', '').strip())
        df_grouped = df_subj.groupby('Disciplina')['HL_REALIZADA'].sum().reset_index()
        df_grouped.columns = ['Disciplina', 'Hrs. Estudadas']
        df_grouped = df_grouped.sort_values('Hrs. Estudadas', ascending=False)
        
        # Add Total Row
        total_hrs = df_grouped['Hrs. Estudadas'].sum()
        new_row = pd.DataFrame([{'Disciplina': 'TOTAL', 'Hrs. Estudadas': total_hrs}])
        df_grouped = pd.concat([df_grouped, new_row], ignore_index=True)
        
        st.dataframe(
            df_grouped, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Hrs. Estudadas": st.column_config.NumberColumn(format="%.2f")
            }
        )
    else:
        st.info("Nenhum registro de estudo encontrado.")

# Define render function for Progress Chart
def render_progress_chart():
    df_progress['PERCENT'] = (df_progress['CONCLUIDO'] / df_progress['TOTAL']) * 100
    
    import plotly.express as px
    
    fig_prog = px.bar(
        df_progress, 
        x='PERCENT', 
        y='MATERIA', 
        color='MATERIA', # Different color for each subject
        orientation='h',
        text_auto='.1f',
        labels={'PERCENT': 'Conclusão (%)', 'MATERIA': 'Matéria'},
        height=400
    )
    
    fig_prog.update_traces(
        texttemplate='%{x:.1f}%', 
        textposition='inside',
        showlegend=False # Hide legend as Y-axis already shows labels
    )
    
    fig_prog.update_layout(
        xaxis_range=[0, 100],
        yaxis={'categoryorder':'total ascending'} # Ensure consistent ordering
    )
    
    st.plotly_chart(fig_prog, use_container_width=True)

# Layout Logic
if not df_progress.empty:
    # Custom CSS to increase Tab font size to match subheaders
    st.markdown("""
        <style>
            /* Target the tab container and text specifically */
            .stTabs [data-baseweb="tab"] p {
                font-size: 1.5rem !important;
                font-weight: 700 !important;
                color: inherit !important; /* Keep default text color (usually black/dark grey) */
            }
            /* Fallback for different streamlit versions */
            .stTabs [data-baseweb="tab"] {
                font-size: 1.5rem !important;
                font-weight: 700 !important;
                color: inherit !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Show Tabs
    tab1, tab2 = st.tabs(["📚 Horas por Disciplina", "📊 Progresso do Conteúdo"])
    
    with tab1:
        render_hours_table()
        
    with tab2:
        render_progress_chart()
else:
    # Show only Table (Standard View)
    st.markdown("### 📚 Disciplinas - Hrs. Estudadas")
    render_hours_table()

# --- 5. Gráfico de Evolução Temporal ---
st.markdown("### 📉 Gráfico de Evolução (Previsto x Realizado)")

conn = get_connection()

# 1. Fetch Data
# Planned
df_plan = pd.read_sql_query("""
    SELECT p.DATA, p.HL_PREVISTA, m.NOME as MATERIA 
    FROM EST_PROGRAMACAO p
    LEFT JOIN EST_CICLO_ITEM ci ON p.COD_CICLO_ITEM = ci.CODIGO
    LEFT JOIN EST_MATERIA m ON ci.COD_MATERIA = m.CODIGO
    WHERE p.COD_PROJETO = ?
""", conn, params=(project_id,))

# Realized
df_real = pd.read_sql_query("""
    SELECT DATA, HL_REALIZADA, DESC_AULA 
    FROM EST_ESTUDOS 
    WHERE COD_PROJETO = ?
""", conn, params=(project_id,))

conn.close()

# 2. Process Data
if not df_plan.empty:
    df_plan['DATA'] = pd.to_datetime(df_plan['DATA'], errors='coerce')
    df_plan = df_plan.dropna(subset=['DATA'])
    df_plan['MATERIA'] = df_plan['MATERIA'].fillna('Outros')

if not df_real.empty:
    df_real['DATA'] = pd.to_datetime(df_real['DATA'], errors='coerce')
    df_real = df_real.dropna(subset=['DATA'])
    # Extract Subject from Description
    df_real['MATERIA'] = df_real['DESC_AULA'].apply(lambda x: x.replace('Estudo de ', '').strip() if x else 'Outros')

# 3. Filter Interface
if not df_plan.empty or not df_real.empty:
    # Get unique subjects from both dataframes
    subjects_plan = set(df_plan['MATERIA'].unique()) if not df_plan.empty else set()
    subjects_real = set(df_real['MATERIA'].unique()) if not df_real.empty else set()
    all_subjects = sorted(list(subjects_plan | subjects_real))
    
    selected_subjects = st.multiselect("Filtrar por Matéria", all_subjects, default=all_subjects)

    if selected_subjects:
        # Filter
        df_plan_filtered = df_plan[df_plan['MATERIA'].isin(selected_subjects)] if not df_plan.empty else pd.DataFrame()
        df_real_filtered = df_real[df_real['MATERIA'].isin(selected_subjects)] if not df_real.empty else pd.DataFrame()
        
        # Group by Date
        plan_by_date = df_plan_filtered.groupby('DATA')['HL_PREVISTA'].sum() if not df_plan_filtered.empty else pd.Series()
        real_by_date = df_real_filtered.groupby('DATA')['HL_REALIZADA'].sum() if not df_real_filtered.empty else pd.Series()
        
        # Combine into single DF for Chart
        chart_data = pd.DataFrame({
            'Previsto': plan_by_date,
            'Realizado': real_by_date
        }).fillna(0.0)
        
        # Sort by date
        chart_data = chart_data.sort_index()
        
        if not chart_data.empty:
            # Create Plotly chart with custom colors and value labels
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            # Previsto line (default blue)
            fig.add_trace(go.Scatter(
                x=chart_data.index,
                y=chart_data['Previsto'],
                mode='lines+markers+text',
                name='Previsto',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=8),
                text=[f'{val:.2f}' for val in chart_data['Previsto']],
                textposition='top center',
                textfont=dict(size=10)
            ))
            
            # Realizado line (dark green)
            fig.add_trace(go.Scatter(
                x=chart_data.index,
                y=chart_data['Realizado'],
                mode='lines+markers+text',
                name='Realizado',
                line=dict(color='#2ca02c', width=2),
                marker=dict(size=8),
                text=[f'{val:.2f}' for val in chart_data['Realizado']],
                textposition='bottom center',
                textfont=dict(size=10)
            ))
            
            fig.update_layout(
                xaxis_title='Data',
                yaxis_title='Horas',
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum dado para exibir no gráfico.")
    else:
        st.warning("Selecione pelo menos uma matéria para visualizar o gráfico.")
else:
    st.info("📊 Gere uma programação e registre estudos para visualizar o gráfico de evolução.")
