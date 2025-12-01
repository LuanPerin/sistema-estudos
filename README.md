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

### 2.4. Ciclos de Estudo e Conteúdos (Edital Verticalizado)
O Ciclo é a "fila" de matérias que você vai rodar.
1.  Crie um Ciclo (ex: "Ciclo Básico - Iniciante").
2.  Adicione as matérias e o tempo sugerido para cada uma.
3.  **Novo:** Clique em **Ver Conteúdos** para cadastrar os tópicos do edital.
    *   **Importação Inteligente:** Cole o texto do edital (ex: "1. Português 2. Matemática...") e o sistema importa tudo automaticamente.
    *   **Ordenação:** Use as setas ⬆️⬇️ para priorizar o que estudar primeiro.

---

## 📅 3. O Planejamento Inteligente
Com tudo cadastrado, vá para a tela **Planejamento**. É aqui que a mágica acontece.

### Gerando a Programação
Você não precisa preencher sua agenda manualmente.
1.  Na barra lateral, defina a **Data Base** (quando quer começar).
2.  Defina o **Período** (quantos dias quer planejar, ex: 7 ou 15 dias).
3.  Clique em **🚀 Gerar Programação**.

### 🧠 Regras de Negócio (Como o Robô Pensa)
Entender isso ajuda você a tirar o máximo do sistema:

1.  **Preenchimento de Lacunas:** O sistema **NUNCA sobrescreve** dias que já têm programação.
    *   *Exemplo:* Se você já tem metas para Segunda e Terça, e pede para gerar a semana toda, ele vai pular esses dois dias e preencher apenas de Quarta em diante.
    *   *Dica:* Se quiser refazer um dia, exclua os itens dele manualmente (ícone de lixeira) e gere novamente.

2.  **Respeito à Grade:** O sistema só agenda estudos em dias que têm horário na sua **Grade Semanal**.
    *   *Exemplo:* Se Domingo está vazio na sua Grade, o sistema pula o Domingo (considera folga).

3.  **Prioridade de Alocação:**
    *   **1º Revisões:** O sistema sempre tenta encaixar primeiro as revisões pendentes (24h, 7 dias, 30 dias).
    *   **2º Ciclo:** O tempo que sobrar é preenchido com as matérias do Ciclo, na ordem exata de onde você parou.

---

## ⏱️ 4. Hora de Estudar (Execução)
Vá para a tela **Estudar**.

### A Fila de Estudos (Meta de Hoje)
O sistema escolhe o que você deve estudar agora seguindo esta ordem de prioridade:
1.  **Atrasados:** Tudo o que ficou pendente de dias anteriores.
2.  **Hoje:** As metas do dia atual.
3.  **Sugestão Inteligente:** O sistema indica exatamente qual **tópico** do conteúdo você deve estudar (ex: "Português - Sintaxe"), baseado na sua ordem de prioridade.

### O Cronômetro
*   Clique em **▶️ Iniciar**. O cronômetro começa a rodar.
*   Ao clicar em **⏹️ Finalizar**, duas coisas acontecem:
    1.  O tempo líquido é salvo no seu Histórico.
    2.  A meta da agenda é marcada automaticamente como **CONCLUIDO**.

### Edição e Ajustes
*   **Errou o timer?** Vá no histórico (logo abaixo do timer), clique no lápis (✏️) e ajuste o tempo, a matéria ou a descrição.
*   **Lançamento Retroativo:** Use o botão **➕ Lançamento Retroativo** para registrar estudos feitos fora do computador.

---

## 📊 5. Monitoramento (Dashboard)
A tela **Home** é seu centro de comando.

*   **🔥 Dias Seguidos:** Mantenha a chama acesa! Estude todo dia para aumentar seu "streak".
*   **⏳ Horas Hoje / Totais:** Acompanhe seu volume de estudo com precisão.
*   **🎯 Horas Planejadas:** Veja se você está cumprindo o que prometeu para si mesmo.
*   **📚 Abas de Acompanhamento:**
    *   **Horas por Disciplina:** Tabela detalhada do tempo investido.
    *   **Progresso do Conteúdo:** Gráfico visual de quanto do edital você já "matou" (só aparece se tiver conteúdos cadastrados).

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
