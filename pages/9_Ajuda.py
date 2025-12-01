import streamlit as st
from auth import require_auth

# Note: st.set_page_config handled in App.py
# require_auth handled by App.py navigation logic

st.title("📘 Manual do Usuário e Conceitos")

tab_conceitos, tab_passo, tab_faq, tab_suporte = st.tabs(["🧠 Conceitos (Metodologia)", "👣 Passo a Passo", "❓ Dúvidas Frequentes", "📞 Suporte"])

with tab_conceitos:
    st.markdown("""
    ### O que é o Sistema de Gestão de Estudos?
    
    Este não é apenas um cronômetro ou uma agenda. É uma ferramenta baseada na metodologia de **Ciclos de Estudo** combinada com **Revisão Espaçada**.
    
    #### 1. O Ciclo de Estudos
    Em vez de uma agenda rígida ("Segunda: Português, Terça: Matemática"), usamos uma **fila de matérias**.
    *   Você define a sequência: Matéria A -> Matéria B -> Matéria C.
    *   Se você não conseguir estudar hoje, não tem problema! A fila não anda. Amanhã você continua exatamente de onde parou (Matéria A).
    *   Isso elimina a culpa de "atrasar a agenda" e garante que você estude todas as matérias proporcionalmente.
    
    #### 2. Revisão Espaçada (O Segredo da Aprovação)
    O sistema sabe que nosso cérebro esquece. Por isso, ele agenda revisões automaticamente:
    *   **24h:** Revisão rápida do que foi visto ontem.
    *   **7 dias:** Reforço semanal.
    *   **30 dias:** Consolidação mensal.
    
    > **O Robô trabalha para você:** Quando você clica em "Gerar Programação", o sistema primeiro aloca todas as revisões necessárias e só depois preenche o tempo livre com matérias novas do ciclo.
    """)

with tab_passo:
    st.markdown("### Guia Rápido de Uso")
    
    with st.expander("1. Configuração Inicial (A Base)", expanded=True):
        st.markdown("""
        Antes de tudo, vá em **Cadastros**:
        1.  **Matérias:** Cadastre tudo o que você pretende estudar.
        3.  **Projeto:** Crie seu objetivo (ex: "Concurso X") e selecione-o na Home.
        4.  **Ciclo:** Crie a sequência de matérias e o tempo de cada uma.
        """)
        
    with st.expander("2. Gestão de Conteúdos (Edital Verticalizado)"):
        st.markdown("""
        Vá em **Cadastros** -> **Ciclos** -> **Ver Conteúdos**:
        1.  **Adicionar Tópicos:** Digite um por um ou use a **Importação Inteligente** (cole o texto do edital numerado).
        2.  **Organizar:** Use as setas ⬆️⬇️ para definir a ordem de estudo.
        3.  **Acompanhar:** Marque como "Finalizado" conforme avança.
        
        *Dica: O sistema vai sugerir o próximo tópico não finalizado automaticamente na tela "Estudar".*
        """)

    with st.expander("3. Planejamento (O Robô em Ação)"):
        st.markdown("""
        Vá em **Planejamento**:
        1.  Escolha a **Data Base** (quando quer começar).
        2.  Escolha o **Período** (quantos dias quer planejar).
        3.  Clique em **Gerar Programação**.
        
        *O sistema vai preencher seus horários livres com as revisões e o ciclo.*
        """)
        
    with st.expander("4. Execução (Hora de Estudar)"):
        st.markdown("""
        Vá em **Estudar**:
        1.  O sistema mostra a **Meta de Hoje** (priorizando atrasados).
        2.  Dê o **Play** ▶️.
        3.  Ao terminar, clique em **Finalizar** ⏹️.
        
        *O sistema salva o tempo e já marca a tarefa como concluída na agenda.*
        """)

with tab_faq:
    st.markdown("""
    ### Perguntas Frequentes
    
    **1. O sistema sobrescreve minha agenda se eu gerar de novo?**
    *Não.* O sistema respeita o que já existe. Ele só preenche os "buracos" vazios. Se quiser refazer um dia, exclua os itens dele manualmente antes de gerar.
    
    **2. O que acontece se eu não estudar hoje?**
    As tarefas de hoje ficarão como "Pendentes". Amanhã, elas aparecerão no topo da lista na tela "Estudar" como prioridade.
    
    **3. Como funciona o Lançamento Retroativo?**
    Se você estudou longe do computador, vá na tela **Estudar** -> **Histórico** -> **Lançamento Retroativo**. Isso garante que suas estatísticas e revisões fiquem em dia.
    
    **4. Posso editar um estudo errado?**
    78:     Sim! No histórico da tela **Estudar**, clique no lápis (✏️) para corrigir a matéria, o tempo ou a descrição.
    79:     """)
    
with tab_suporte:
    st.markdown("### 📞 Suporte via Google Meet")
    st.info("Precisa de ajuda em tempo real? Inicie uma chamada de vídeo com nosso suporte.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input for username only
        username = st.text_input("Usuário do Suporte", placeholder="email-do-suporte", help="Digite apenas o usuário (antes do @gmail.com)")
        
        # Handle empty username for display
        display_email = f"{username}@gmail.com" if username else "email-do-suporte@gmail.com"
        
        st.markdown(f"""
        **Instruções:**
        1. Clique no botão abaixo para abrir uma nova sala do Meet.
        2. Na sala, clique em **"Adicionar pessoas"**.
        3. Convide o email: `{display_email}`
        """)
        
    with col2:
        st.markdown("<br>", unsafe_allow_html=True) # Spacer
        # Link to meet.new
        st.link_button("🎥 Iniciar Atendimento", "https://meet.google.com/new", type="primary", use_container_width=True)

    st.divider()
    st.caption("Nota: O Google Meet abrirá em uma nova aba. Certifique-se de estar logado em sua conta Google.")
