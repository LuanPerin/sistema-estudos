import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db_manager import get_connection
from auth import require_auth

# Configuração da Página
st.set_page_config(page_title="Dashboard Administrativo", page_icon="📊", layout="wide")

# Verificar Permissão
require_auth()
user = st.session_state.get('user')
if not user or user.get('IS_ADMIN') != 'S':
    st.error("⛔ Acesso Negado. Esta área é restrita a administradores.")
    st.stop()

st.title("📊 Dashboard Administrativo")
st.markdown("Monitoramento de métricas de uso, engajamento e saúde da plataforma.")
st.divider()

# --- Helpers de Dados ---
def get_kpis():
    conn = get_connection()
    try:
        # Total Usuários
        total_users = pd.read_sql("SELECT COUNT(*) as count FROM EST_USUARIO", conn)['count'][0]
        
        # Usuários Ativos (30 dias) - Considera quem tem sessão OU criou algo recentemente
        # Simplificação: Quem tem data de ultimo acesso > 30 dias
        query_active = """
        SELECT COUNT(*) as count 
        FROM EST_USUARIO 
        WHERE date(ULTIMO_ACESSO) >= date('now', '-30 days')
        """
        active_users = pd.read_sql(query_active, conn)['count'][0]
        
        # Total de Horas Estudadas
        total_hours = pd.read_sql("SELECT SUM(HL_REALIZADA) as total FROM EST_ESTUDOS", conn)['total'][0]
        if pd.isna(total_hours): total_hours = 0
        
        # Total de Registros de Estudo
        total_records = pd.read_sql("SELECT COUNT(*) as count FROM EST_ESTUDOS", conn)['count'][0]
        
        return total_users, active_users, total_hours, total_records
    finally:
        conn.close()

def get_evolution_data():
    conn = get_connection()
    try:
        # Cadastros por Mês
        query_users = """
        SELECT strftime('%Y-%m', DATA_CRIACAO) as mes, COUNT(*) as novos_usuarios
        FROM EST_USUARIO
        GROUP BY 1
        ORDER BY 1
        """
        df_users = pd.read_sql(query_users, conn)
        
        # Estudos por Dia (Últimos 30 dias)
        query_studies = """
        SELECT DATA as dia, COUNT(*) as estudos
        FROM EST_ESTUDOS 
        WHERE date(DATA) >= date('now', '-30 days')
        GROUP BY 1
        ORDER BY 1
        """
        df_studies = pd.read_sql(query_studies, conn)
        
        return df_users, df_studies
    finally:
        conn.close()

def get_top_subjects():
    conn = get_connection()
    try:
        query = """
        SELECT m.NOME as Materia, SUM(e.HL_REALIZADA) as Horas
        FROM EST_ESTUDOS e
        JOIN EST_MATERIA m ON e.COD_MATERIA = m.CODIGO
        GROUP BY m.NOME
        ORDER BY Horas DESC
        LIMIT 10
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def get_user_health():
    conn = get_connection()
    try:
        query = """
        SELECT 
            u.CODIGO, 
            u.NOME, 
            u.EMAIL, 
            u.ULTIMO_ACESSO,
            (SELECT COUNT(*) FROM EST_ESTUDOS e WHERE e.COD_USUARIO = u.CODIGO) as Qtd_Estudos,
            (SELECT SUM(HL_REALIZADA) FROM EST_ESTUDOS e WHERE e.COD_USUARIO = u.CODIGO) as Total_Horas
        FROM EST_USUARIO u
        ORDER BY u.ULTIMO_ACESSO DESC
        """
        df = pd.read_sql(query, conn)
        # Preencher NaNs com 0 para horas
        df['Total_Horas'] = df['Total_Horas'].fillna(0)
        return df
    finally:
        conn.close()

# --- Renderização ---

# 1. Big Numbers
kpi_total, kpi_active, kpi_hours, kpi_records = get_kpis()

c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Total Usuários", kpi_total)
c2.metric("🟢 Usuários Ativos (30d)", kpi_active, help="Logaram nos últimos 30 dias")
c3.metric("⏱️ Horas Totais", f"{kpi_hours:.1f}h")
c4.metric("📚 Registros de Estudo", kpi_records)

st.divider()

# 2. Gráficos de Evolução e Top Matérias
col_charts_1, col_charts_2 = st.columns([1.5, 1])

with col_charts_1:
    st.subheader("📈 Volume Diário de Estudos (30d)")
    df_users, df_studies = get_evolution_data()
    if not df_studies.empty:
        st.bar_chart(df_studies.set_index('dia'), color="#ff4b4b")
    else:
        st.info("Sem dados de estudos recentes.")

with col_charts_2:
    st.subheader("🏆 Top Matérias (Horas)")
    df_top = get_top_subjects()
    if not df_top.empty:
        st.dataframe(df_top, hide_index=True, use_container_width=True, 
                     column_config={"Horas": st.column_config.NumberColumn(format="%.1f h")})
    else:
        st.info("Sem registros suficientes.")

# --- Helper de Projetos ---
def get_project_stats():
    conn = get_connection()
    try:
        # 1. Top Projetos com mais horas (mostrando o Dono)
        query_top_proj = """
        SELECT 
            p.NOME || ' (' || u.NOME || ')' as Projeto,
            SUM(e.HL_REALIZADA) as Horas
        FROM EST_PROJETO p
        JOIN EST_USUARIO u ON p.COD_USUARIO = u.CODIGO
        JOIN EST_ESTUDOS e ON e.COD_PROJETO = p.CODIGO
        GROUP BY 1
        ORDER BY Horas DESC
        LIMIT 5
        """
        df_top_proj = pd.read_sql(query_top_proj, conn)
        
        # 2. Status Geral dos Projetos (Quantos Ativos? Baseado em Data Final)
        # Como não existe coluna ATIVO, consideramos Ativo se DATA_FINAL is NULL ou >= Hoje
        query_status = """
        SELECT 
            count(*) as Total, 
            SUM(CASE WHEN (DATA_FINAL IS NULL OR DATA_FINAL >= date('now')) THEN 1 ELSE 0 END) as Ativos
        FROM EST_PROJETO
        """
        df_status = pd.read_sql(query_status, conn)
        
        return df_top_proj, df_status
    finally:
        conn.close()

# --- Renderização ---

tab_overview, tab_projects = st.tabs(["📊 Visão Geral", "🚀 Projetos"])

with tab_overview:
    # 1. Big Numbers
    kpi_total, kpi_active, kpi_hours, kpi_records = get_kpis()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Usuários", kpi_total)
    c2.metric("🟢 Usuários Ativos (30d)", kpi_active, help="Logaram nos últimos 30 dias")
    c3.metric("⏱️ Horas Totais", f"{kpi_hours:.1f}h")
    c4.metric("📚 Registros de Estudo", kpi_records)

    st.divider()

    # 2. Gráficos de Evolução e Top Matérias
    col_charts_1, col_charts_2 = st.columns([1.5, 1])

    with col_charts_1:
        st.subheader("📈 Volume Diário de Estudos (30d)")
        df_users, df_studies = get_evolution_data()
        if not df_studies.empty:
            st.bar_chart(df_studies.set_index('dia'), color="#ff4b4b")
        else:
            st.info("Sem dados de estudos recentes.")

    with col_charts_2:
        st.subheader("🏆 Top Matérias (Horas)")
        df_top = get_top_subjects()
        if not df_top.empty:
            st.dataframe(df_top, hide_index=True, use_container_width=True, 
                         column_config={"Horas": st.column_config.NumberColumn(format="%.1f h")})
        else:
            st.info("Sem registros suficientes.")

    # 3. Tabela de Saúde dos Usuários
    st.divider()
    st.subheader("O Raio-X da Base (Health Score)")

    df_health = get_user_health()
    if not df_health.empty:
        # Formatar data
        try:
            df_health['ULTIMO_ACESSO'] = pd.to_datetime(df_health['ULTIMO_ACESSO']).dt.strftime('%d/%m/%Y %H:%M')
        except:
            pass
            
        st.dataframe(
            df_health,
            hide_index=True,
            use_container_width=True,
            column_config={
                "CODIGO": "ID",
                "NOME": "Nome",
                "EMAIL": "Email",
                "ULTIMO_ACESSO": "Último Acesso",
                "Qtd_Estudos": st.column_config.NumberColumn("Qtd. Estudos"),
                "Total_Horas": st.column_config.ProgressColumn(
                    "Total Horas",
                    format="%.1f h",
                    min_value=0,
                    max_value=float(df_health['Total_Horas'].max()) if not df_health.empty else 100,
                ),
            }
        )
    else:
        st.info("Nenhum usuário encontrado.")

with tab_projects:
    st.subheader("🚀 Projetos de Estudo")

    df_top_proj, df_proj_status = get_project_stats()

    c_p1, c_p2 = st.columns([1, 2])

    with c_p1:
        total_proj = df_proj_status['Total'][0]
        # Handle cases where Ativos might be None if no rows
        active_proj = df_proj_status['Ativos'][0] if df_proj_status['Ativos'][0] is not None else 0
        
        st.metric("Total Projetos", total_proj)
        st.metric("Projetos Ativos (Data Final)", active_proj, help="Considera projetos sem data final ou com data futura.")
        
    with c_p2:
        st.write("🔥 **Projetos com mais esforço (Horas):**")
        if not df_top_proj.empty:
            # Bar chart horizontal
            st.bar_chart(df_top_proj.set_index('Projeto'), color="#4CAF50", horizontal=True)
        else:
            st.info("Nenhum dado de horário por projeto.")
