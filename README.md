# 📚 Sistema de Gestão de Estudos

Gerenciador de estudos pessoal desenvolvido em Python com Streamlit. O sistema foi criado para permitir o planejamento e gerenciamento inteligente de ciclos de estudo, transformando seu planejamento em aprovação.

---

# 📘 Manual do Usuário

Bem-vindo ao seu novo **Sistema de Gestão de Estudos**! 
Este manual foi desenhado para guiar você desde os primeiros passos até o domínio completo da ferramenta.

## 🌟 1. Visão Geral
O sistema foi criado para permitir o planejamento e gerenciamento inteligente de ciclos de estudo. Diferente de uma agenda comum, ele entende que você precisa **revisar** o que estudou e se adapta à sua rotina.

### O Fluxo do Sucesso
O uso do sistema segue uma lógica de "construção":
1.  **Base:** Cadastrar o que estudar (Matérias) e quando estudar (Grade).
2.  **Estratégia:** Definir o Projeto (ex: Concurso X) e o Ciclo (sequência de matérias).
3.  **Planejamento:** O sistema gera sua agenda automaticamente.
4.  **Ação:** Você estuda, o sistema cronometra e agenda as revisões.

---

## ⚙️ 2. Configurações Iniciais (A Base)
Antes de começar a estudar, precisamos "ensinar" ao sistema sobre sua rotina e seus objetivos. Vá para a tela **Cadastros**.

### 2.1. Áreas e Matérias
*   **Áreas:** São os grandes grupos (ex: "Direito", "Exatas", "Línguas"). Servem para organizar.
*   **Matérias:** O conteúdo propriamente dito (ex: "Português", "Direito Constitucional", "Raciocínio Lógico").
    *   *Dica:* Cadastre todas as matérias que você pretende estudar em seus diversos projetos. Elas são reutilizáveis!

### 2.2. Grades Semanais (Sua Disponibilidade)
Aqui você define **quando** pode estudar.
*   Crie uma Grade (ex: "Rotina de Trabalho").
*   Clique em **Gerenciar** e adicione seus horários livres (ex: Segunda das 19:00 às 22:00).
*   **Importante:** Marque sua grade principal como **Padrão**. O sistema usará ela para calcular suas metas.

### 2.3. Projetos (O Objetivo)
Um projeto é o seu foco atual. Pode ser um concurso específico ("Receita Federal 2025") ou um objetivo de longo prazo ("Aprender Inglês").
*   Defina uma data de início e fim.
*   **Atenção:** Na tela **Home**, você sempre deve selecionar qual Projeto está "ativo" naquele momento. Tudo o que você vê no sistema muda conforme o projeto selecionado.

### 2.4. Ciclos de Estudo (A Estratégia)
O Ciclo é a "fila" de matérias que você vai rodar.
1.  Crie um Ciclo (ex: "Ciclo Básico - Iniciante").
2.  Adicione as matérias e o tempo sugerido para cada uma (ex: 60 min de Português -> 90 min de Constitucional -> ...).
3.  Quando você terminar a última matéria, o ciclo recomeça automaticamente.

---

## 📅 3. O Planejamento Inteligente
Com tudo cadastrado, vá para a tela **Planejamento**. É aqui que a mágica acontece.

### Gerando a Programação
Você não precisa preencher sua agenda manualmente.
1.  Na barra lateral, defina a **Data Base** (quando quer começar).
2.  Defina o **Período** (quantos dias quer planejar, ex: 7 ou 15 dias).
3.  Clique em **🚀 Gerar Programação**.

**O que o sistema faz por você:**
*   Distribui as matérias do seu Ciclo dentro dos horários da sua Grade Semanal.
*   **🧠 Mágica das Revisões:** O sistema olha o que você já estudou e **automaticamente** agende revisões de 24h, 7 dias e 30 dias. Você nunca mais esquecerá de revisar!

> **Dica de Ouro:** Sua rotina mudou? Sem problemas! Ajuste sua Grade Semanal e gere a programação novamente a partir de hoje. O sistema realinha tudo para sua nova realidade.

---

## ⏱️ 4. Hora de Estudar (Execução)
Vá para a tela **Estudar**.

### O Cronômetro
*   O sistema mostra sua **Meta de Hoje** baseada no planejamento.
*   Clique em **▶️ Iniciar**. O cronômetro começa a rodar.
*   Pode pausar para um café ☕ e retomar depois.
*   Ao clicar em **⏹️ Finalizar**, o sistema salva suas horas líquidas e já calcula quando será sua próxima revisão desse assunto.

### Lançamento Retroativo (Válvula de Escape)
Esqueceu de ligar o timer? Estudou pelo celular no ônibus?
*   Na tela **Estudar**, desça até o Histórico.
*   Clique em **➕ Lançamento Retroativo**.
*   Informe a matéria, data e tempo. O sistema registra tudo para não furar as estatísticas.

---

## 📊 5. Monitoramento (Dashboard)
A tela **Home** é seu centro de comando.

*   **🔥 Dias Seguidos:** Mantenha a chama acesa! Estude todo dia para aumentar seu "streak".
*   **⏳ Horas Hoje / Totais:** Acompanhe seu volume de estudo com precisão.
*   **🎯 Horas Planejadas:** Veja se você está cumprindo o que prometeu para si mesmo.
*   **Gráficos:** Acompanhe sua evolução diária e a distribuição por matéria.

---

# 🛠️ Instalação e Execução Técnica

Para rodar o projeto localmente:

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Execute a aplicação:**
    ```bash
    streamlit run Login.py
    ```

3.  **Acesso:**
    O sistema abrirá automaticamente no seu navegador (geralmente em `http://localhost:8501`).

---
**Bons estudos e rumo à aprovação! 🎓**
