import streamlit as st
import os
from PIL import Image

def show_manual():
    st.title("📘 Manual Simplificado")
    st.markdown("Bem-vindo ao guia rápido de utilização do Sistema de Estudos. Siga o passo a passo abaixo para configurar e maximizar seus resultados.")
    
    # Path to images (Relative to project root)
    IMG_DIR = "manual_images"
    
    # helper to display step
    def step(title, description, img_filename):
        st.header(title)
        st.markdown(description)
        try:
            img_path = os.path.join(IMG_DIR, img_filename)
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.warning(f"Imagem não encontrada: {img_filename}")
        except Exception as e:
            st.error(f"Erro ao carregar imagem: {e}")
        st.divider()

    # --- 1. Acesso ao Sistema ---
    st.subheader("1. Acesso e Cadastro")
    step("Login com Google", 
         "Você pode acessar o sistema rapidamente utilizando sua conta Google. Basta clicar no botão 'Entrar com Google'.",
         "Figura - 1.1 Login com conta google.png")
    
    step("Criar Nova Conta", 
         "Caso prefira, crie uma conta com e-mail e senha. Clique em 'Criar conta' abaixo do formulário de login.",
         "Figura - 1.2 Login - Criar Conta.png")
         
    step("Preencher Cadastro", 
         "Preencha seus dados corretamente. A senha deve ser forte para sua segurança.",
         "Figura - 1.3 Login - Cadastrar usuário.png")

    # --- 2. Visão Geral ---
    st.subheader("2. Tela Inicial")
    step("Dashboard", 
         "Após o login, você verá o Dashboard. Aqui você monitora suas horas de estudo, dias seguidos (streak) e evolução.",
         "Figura - 2. Tela Home inicial.png")

    # --- 3. Cadastros Básicos ---
    st.subheader("3. Cadastros Básicos (Base de Conhecimento)")
    
    step("Grades Semanais", 
         "Acesse o menu 'Cadastros' e selecione 'Base de Conhecimento'. Comece definindo suas Grades Semanais (seus horários livres).",
         "Figura - 3.1 - Cadastros básicos - Grades Semanais.png")
         
    step("Novo Horário", 
         "Adicione os horários que você tem disponível para estudar em cada dia da semana.",
         "Figura - 3.1.2 - Cadastros básicos - Grades Semanais - Horários - Novo.png")
         
    step("Áreas de Conhecimento", 
         "Cadastre as grandes áreas que você estuda (ex: Direito, Exatas, Línguas).",
         "Figura - 3.2 - Cadastros básicos - Áreas de Conhecimento.png")
         
    step("Matérias", 
         "Cadastre as matérias específicas dentro de cada área. É aqui que você detalha o que vai estudar.",
         "Figura - 3.3 - Cadastros básicos - Matérias.png")

    # --- 4. Estratégia ---
    st.subheader("4. Estratégia & Projetos")
    
    step("Criar Projeto", 
         "Ainda em 'Cadastros', mude para 'Estratégia & Projetos'. Crie um novo projeto (ex: Concurso X, Faculdade Y).",
         "Figura - 4.1 - Estratégia & Projetos - Projetos - Novo.png")
         
    step("Ciclos de Estudo", 
         "Defina seu Ciclo de Estudos. O Ciclo determina a sequência das matérias.",
         "Figura - 4.2 - Estratégia & Projetos - Ciclos - Novo.png")
         
    step("Adicionar Itens ao Ciclo", 
         "Insira as matérias no ciclo e defina o peso (tempo) de cada uma.",
         "Figura - 4.2.1 - Estratégia & Projetos - Itens do Ciclo - Novo.png")
         
    step("Conteúdo Programático", 
         "Clique no ícone de pasta para adicionar os tópicos (assuntos) de cada matéria.",
         "Figura - 4.2.2.1 - Estratégia & Projetos - Itens do Ciclo - Conteúdos.png")
         
    step("Importação em Lote", 
         "Você pode colar uma lista de tópicos de uma vez só para ganhar tempo.",
         "Figura - 4.2.2.3 - Estratégia & Projetos - Itens do Ciclo - Conteúdos - Inserir em Lote.png")

    # --- 5. Planejamento ---
    st.subheader("5. Planejamento Automático")
    
    step("Gerar Programação", 
         "Vá para o menu 'Planejamento'. Defina a data base e o período (dias) e clique em 'Gerar Programação'. O sistema cruzará sua grade com seu ciclo.",
         "Figura - 5.1.1 - Planejamento - Gerar Programação de Teste - 45 dias.png")
         
    step("Visualizar Cronograma", 
         "Veja o cronograma gerado dia a dia.",
         "Figura - 5.1.2 - Planejamento - Gerar Programação de Teste - Programação Gerada.png")

    # --- 6. Estudar ---
    st.subheader("6. Hora de Estudar")
    
    step("Meta do Dia", 
         "No menu 'Estudar', o sistema mostra sua meta de hoje. Clique para iniciar o cronômetro.",
         "Figura - 6.2 - Estudar - Tela Inicial - Estudando a Primeira atividade programada.png")
         
    step("Finalizar Estudo", 
         "Ao terminar, clique em 'Finalizar'. O sistema registra as horas e já atualiza o progresso do conteúdo.",
         "Figura - 6.2.1 - Estudar - Tela Inicial - Finalizando a  Primeira atividade programada.png")

    # --- 7. Acompanhamento ---
    st.subheader("7. Acompanhando o Progresso")
    
    step("Métricas de Evolução", 
         "Volte para a Home para ver seus gráficos atualizados. Acompanhe o previsto vs realizado.",
         "Figura - 7.1 - Home - Tela Inicial - Acompanhamento das métricas do projeto.png")
         
    step("Progresso do Conteúdo", 
         "Veja quantos % de cada matéria você já cobriu.",
         "Figura - 7.2.2 - Home - Acompanhamento de métricas - Progresso do Conteúdo.png")
    
    # Footer
    st.info("Este manual é um guia rápido. Explore o sistema para descobrir mais funcionalidades!")
    
show_manual()
