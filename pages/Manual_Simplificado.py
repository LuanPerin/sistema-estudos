import streamlit as st
import os

def show_manual():
    st.title("📘 Manual do Usuário - Sistema de Estudos")
    
    # Path to images (Relative to project root for deployment)
    IMG_DIR = "manual_images"
    
    # Helper for images
    def show_img(filename, caption=None):
        try:
            # Flexible path handling: try relative first, then absolute fallback if ensuring local dev
            img_path = os.path.join(IMG_DIR, filename)
            if not os.path.exists(img_path):
                 # Try absolute path for local debug if relative fails (optional fallback)
                 abs_base = r"c:\Users\MOREFINE\Downloads\Operacoes\estudos_python\manual_images"
                 img_path = os.path.join(abs_base, filename)

            if os.path.exists(img_path):
                st.image(img_path, caption=caption, use_container_width=True)
            else:
                st.warning(f"Imagem não encontrada: {filename}")
        except Exception:
            st.warning(f"Erro ao carregar imagem: {filename}")

    # --- INTRODUÇÃO ---
    with st.expander("📚 INTRODUÇÃO – CONCEITOS (Leia isto primeiro!)", expanded=True):
        st.markdown("""
        ### Fundamentos do Protocolo de Revisão (24h, 7 dias e 30 dias)
        O Sistema de Estudos utiliza uma programação automática de revisões em três momentos: **24 horas**, **7 dias** e **30 dias** depois que você estuda um conteúdo. Esses intervalos não foram escolhidos por acaso — eles seguem como o cérebro funciona naturalmente para aprender e lembrar melhor.
        
        #### 📉 1. Por que esquecemos tão rápido?
        Depois que estudamos algo pela primeira vez, o cérebro tende a esquecer grande parte do conteúdo nas primeiras horas e dias. Isso é normal — faz parte do funcionamento natural da memória. 
        *Sem revisão, você pode esquecer 50% a 70% do que estudou em apenas 24 horas.*
        
        #### ⏱️ 2. Revisão de 24 horas — reforço logo após o primeiro contato
        *   **Quando:** Dia seguinte ao estudo inicial.
        *   **Por quê:** Durante o sono, o cérebro organiza o que aprendeu. Revisar após 24h impede que o conteúdo seja descartado.
        *   **Resumo:** Transforma o conteúdo em uma memória mais estável.
        
        #### 📅 3. Revisão de 7 dias — o momento ideal para testar a memória
        *   **Quando:** Uma semana depois.
        *   **Por quê:** Lembrar exige "esforço", e esse esforço fortalece o "músculo" da memória.
        *   **Resumo:** Evita que a memória enfraqueça novamente.
        
        #### 🗓️ 4. Revisão de 30 dias — fixando de vez
        *   **Quando:** Um mês depois.
        *   **Por quê:** Transforma o conhecimento em algo duradouro (Longo Prazo).
        *   **Resumo:** Garante que o conteúdo seja lembrado por muito mais tempo.
        
        > **🎯 O que isso significa para você?**
        > Você não precisa lembrar quando revisar. **O sistema faz isso automaticamente.** Basta seguir a programação!
        """)

    st.divider()

    # --- 1. ACESSO ---
    st.header("1. Acesso e Autenticação")
    st.markdown("Para acessar a aplicação, o usuário dispõe de duas opções de autenticação:")
    
    st.subheader("Opção A: Login via Google")
    st.write("Utilize sua conta Google existente para um acesso rápido e integrado.")
    show_img("Figura - 1.1 Login com conta google.png", "Figura 1.1 - Login com Google")
    
    st.subheader("Opção B: Cadastro de Usuário")
    st.write("É possível criar uma conta exclusiva utilizando e-mail e senha.")
    st.info("**Requisitos da Senha:** 8 caracteres, 1 letra maiúscula, 1 caractere especial (!@#$).")
    show_img("Figura - 1.2 Login - Criar Conta.png", "Figura 1.2 - Criar Conta")
    show_img("Figura - 1.3 Login - Cadastrar usuário.png", "Figura 1.3 - Cadastro Completo")

    # --- 2. HOME ---
    st.header("2. Visão Geral (Home)")
    st.markdown("Após o login, você será direcionado à tela inicial (Dashboard). Aqui você monitora suas horas, dias seguidos e evolução.")
    show_img("Figura - 2. Tela Home inicial.png", "Figura 2 - Dashboard Inicial")

    # --- 3. CADASTROS BÁSICOS ---
    st.header("3. Cadastros Básicos (Configuração Inicial)")
    st.markdown("Antes de criar um projeto, é necessário alimentar o sistema com: **Disponibilidade (Grade)**, **Áreas** e **Matérias**.")
    
    st.subheader("3.1. Definindo a Grade Semanal")
    st.markdown("Defina sua agenda de forma realista. Vá em: **Cadastros > Base de Conhecimento > Grades Semanais**.")
    show_img("Figura - 3.1 - Cadastros básicos - Grades Semanais.png")
    
    st.markdown("**1. Crie a Grade:** Clique em `+ Novo`, dê um nome (ex: Padrão) e marque como 'Padrão'.")
    show_img("Figura - 3.1.1 - Cadastros básicos - Grades Semanais - Novo.png")
    
    st.markdown("**2. Adicione Horários:** Clique em `Novo Horário` dentro da grade para adicionar períodos (ex: Segunda, 19h às 22h).")
    show_img("Figura - 3.1.2 - Cadastros básicos - Grades Semanais - Horários - Novo.png")
    show_img("Figura - 3.1.3 - Cadastros básicos - Grades Semanais - Horários - Salvar.png")
    show_img("Figura - 3.1.4 - Cadastros básicos - Grades Semanais - Horários - Completo.png")

    st.subheader("3.2. Cadastrando Áreas do Conhecimento")
    st.markdown("Organize por grandes grupos (Ex: Humanas, Direito, TI). Vá em **Base de Conhecimento > Áreas**.")
    show_img("Figura - 3.2 - Cadastros básicos - Áreas de Conhecimento.png")
    show_img("Figura - 3.2.1 - Cadastros básicos - Áreas de Conhecimento - Novo.png")
    show_img("Figura - 3.2.2 - Cadastros básicos - Áreas de Conhecimento - Completo.png")

    st.subheader("3.3. Cadastrando Matérias")
    st.markdown("Cadastre as disciplinas específicas (Ex: Português, Direito Const.). Vá em **Base de Conhecimento > Matérias**.")
    show_img("Figura - 3.3 - Cadastros básicos - Matérias.png")
    
    st.warning("**⚠️ IMPORTANTE:** Crie uma matéria chamada **REVISÃO** e marque a opção **'Revisão'**. Ela será vital para o agendamento automático.")
    show_img("Figura - 3.3.1 - Cadastros básicos - Matérias - Revisão.png")
    show_img("Figura - 3.3.2 - Cadastros básicos - Matérias - Completo.png")

    # --- 4. ESTRATÉGIA ---
    st.header("4. Estratégia e Projetos")
    
    st.subheader("4.1. Criando o Projeto")
    st.markdown("Vá em **Cadastros > Estratégia & Projetos > Projetos**. Crie um novo (Ex: 'Pos Edital') e marque como **Padrão**.")
    show_img("Figura - 4.1 - Estratégia & Projetos - Projetos - Novo.png")
    show_img("Figura - 4.1.1 - Estratégia & Projetos - Projetos - Completo.png")

    st.subheader("4.2. Configurando o Ciclo de Estudos")
    st.markdown("Vá em **Aba Ciclos**. Crie um ciclo (Ex: 'Ciclo Inicial') e marque como **Padrão**.")
    show_img("Figura - 4.2 - Estratégia & Projetos - Ciclos - Novo.png")

    st.subheader("4.3. Itens do Ciclo e Conteúdos")
    st.markdown("Adicione as matérias ao ciclo clicando em **`+ Novo Item`**.")
    show_img("Figura - 4.2.1 - Estratégia & Projetos - Itens do Ciclo - Novo.png")
    show_img("Figura - 4.2.2 - Estratégia & Projetos - Itens do Ciclo - Salvar.png")
    
    st.markdown("### Inserindo Conteúdos (Edital Verticalizado)")
    st.markdown("No item criado, clique no botão **📂 (Ver Conteúdos)**.")
    show_img("Figura - 4.2.2.1 - Estratégia & Projetos - Itens do Ciclo - Conteúdos.png")
    
    st.markdown("Você pode inserir um a um ou em **Lote** (colando uma lista).")
    show_img("Figura - 4.2.2.2 - Estratégia & Projetos - Itens do Ciclo - Conteúdos - Inserir Individual.png")
    show_img("Figura - 4.2.2.3 - Estratégia & Projetos - Itens do Ciclo - Conteúdos - Inserir em Lote.png")
    show_img("Figura - 4.2.2.4 - Estratégia & Projetos - Itens do Ciclo - Conteúdos - Completo.png")
    show_img("Figura - 4.2.2.5 - Estratégia & Projetos - Itens do Ciclo - Conteúdos - Finalizar.png")
    
    st.info("**ATENÇÃO:** Lembre-se de adicionar um Item de Ciclo para a matéria **REVISÃO** com tempo curto (ex: 0.10 horas ou 10 min), para que o sistema tenha espaço para alocar as revisões.")
    show_img("Figura - 4.2.3 - Estratégia & Projetos - Itens do Ciclo - Revisão.png")

    # --- 5. PLANEJAMENTO ---
    st.header("5. Planejamento Automático")
    st.markdown("Acesse o menu **Planejamento**. Defina a data base e os dias (ex: 7 a 15 dias). Clique em **Gerar Programação**.")
    show_img("Figura - 5.1 - Planejamento - Tela Inicial.png")
    show_img("Figura - 5.1.1 - Planejamento - Gerar Programação de Teste - 45 dias.png")
    
    st.markdown("O sistema alocará aulas e revisões automaticamente.")
    show_img("Figura - 5.1.2 - Planejamento - Gerar Programação de Teste - Programação Gerada.png")
    show_img("Figura - 5.1.3 - Planejamento - Gerar Programação de Teste - Programação Gerada - Revisões.png")
    
    st.markdown("As configurações de tempo de revisão podem ser ajustadas em Ajuda/Configurações, se necessário.")
    show_img("Figura - 5.1.4 - Configurações - Configurar Tempo de Revisões.png")

    # --- 6. ESTUDAR ---
    st.header("6. Execução: Hora de Estudar")
    st.markdown("Acesse o menu **Estudar**. Veja a meta do dia.")
    
    st.markdown("### Ajuste de Grade (Exemplo)")
    st.markdown("Se precisar estudar no Domingo e não estava previsto, ajuste a Grade Semanal e gere novamente.")
    show_img("Figura - 6.1 - Estudar - Tela Inicial - Grade Não Previa Domingo como Dia de estudo.png")
    show_img("Figura - 6.1.1 - Estudar - Removendo a programação já lançada para poder incluir o domingo.png")
    show_img("Figura - 6.1.2 - Estudar - Incluindo Domingo na Grade de Horas Semanais.png")
    show_img("Figura - 6.1.3 - Estudar - Regerando a programação de estudos agora contemplando domingo.png")
    
    st.markdown("### Iniciando o Estudo")
    st.markdown("Clique em **▶️ Iniciar / Retomar** para ligar o timer.")
    show_img("Figura - 6.2 - Estudar - Tela Inicial - Estudando a Primeira atividade programada.png")
    
    st.markdown("Ao terminar, clique em **⏹️ Finalizar**.")
    show_img("Figura - 6.2.1 - Estudar - Tela Inicial - Finalizando a  Primeira atividade programada.png")
    show_img("Figura - 6.2.2 - Estudar - Tela Inicial - Editando a Primeira atividade finalizada.png")
    
    st.markdown("O sistema trará a próxima matéria automaticamente.")
    show_img("Figura - 6.2.3 - Estudar - Tela Inicial - Repetindo o processo para as demais atividades programadas de estudo.png")
    show_img("Figura - 6.2.4 - Estudar - Tela Inicial - Programação do dia finalizada.png")
    show_img("Figura - 6.2.5 - Estudar - Confirmando a Conclusão das atividades planejadas.png")

    # --- 7. MONITORAMENTO ---
    st.header("7. Monitoramento e Métricas")
    st.markdown("Acompanhe na **Home** ou no **Perfil**.")
    show_img("Figura - 7.1 - Home - Tela Inicial - Acompanhamento das métricas do projeto.png")
    show_img("Figura - 7.2 - Home - Tela Inicial - Acompanhamento das métricas do projeto.png")
    
    st.markdown("Para avançar no gráfico 'Progresso do Conteúdo', marque os tópicos como 'Finalizado'.")
    show_img("Figura - 7.2.1 - Itens do Ciclos - Conteúdos - Finalizando manualmente um contéudo.png")
    show_img("Figura - 7.2.2 - Home - Acompanhamento de métricas - Progresso do Conteúdo.png")

    # --- 8. BACKUP ---
    st.header("8. Backup e Dados")
    st.markdown("Acesse **Backup & Dados** no menu Admin ou Configurações (se disponível) para baixar seus dados.")
    show_img("Figura - 8.1 - Backup & Dados - Gerar Backup e Restauração dos dados do projeto de estudo.png")

    st.divider()
    st.success("Bons estudos e rumo à aprovação!")

if __name__ == "__main__":
    show_manual()
