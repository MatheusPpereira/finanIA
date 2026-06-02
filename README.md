<div align="center">

# 💰 FinancIA

### Assistente Financeiro Pessoal com Inteligência Artificial

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/gemini)
[![Groq](https://img.shields.io/badge/Llama_3.3_70B-F54E27?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)

> Gerencie suas finanças pessoais conversando com IA. Registre gastos, visualize seu histórico e acompanhe metas financeiras — tudo em linguagem natural.

</div>

---

## 📋 Sobre o Projeto

O **FinancIA** é uma aplicação web de finanças pessoais que combina uma interface moderna com o poder de modelos de linguagem de última geração. O diferencial está na naturalidade: em vez de preencher formulários, o usuário simplesmente conversa — *"gastei R$85 no almoço hoje"* — e a IA registra, categoriza e organiza automaticamente.

O projeto integra dois modelos de IA (Google Gemini e Meta Llama via Groq), um banco de dados PostgreSQL e um dashboard interativo com gráficos em tempo real.

---

## ✨ Funcionalidades

### 💬 Chat Inteligente
- Converse em linguagem natural sobre seus gastos e receitas
- A IA detecta transações na mensagem e **registra automaticamente** no banco
- Suporte a múltiplos **modos de resposta**: Normal, Professor, Técnico, Resumido e Detalhado
- Escolha entre **Gemini 2.5 Flash**, **Llama 3.3 70B** ou compare os dois simultaneamente

### 📊 Dashboard
- Saldo atual, despesas e receitas do **mês corrente**
- Gráfico de pizza com gastos por categoria
- Gráfico de linha com evolução financeira separada por tipo
- Tabela com as últimas transações

### 📋 Transações
- Listagem completa do histórico financeiro
- Filtros por **tipo** (despesa/receita) e **categoria**

### 🎯 Metas Financeiras
- Crie metas com valor alvo e prazo
- Acompanhe o progresso com barra visual
- Veja quantos dias restam para cada meta

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| [Streamlit](https://streamlit.io) | Interface web |
| [LangChain](https://langchain.com) | Integração com modelos de IA |
| [Google Gemini 2.5 Flash](https://deepmind.google/gemini) | Modelo de linguagem principal |
| [Groq + Llama 3.3 70B](https://groq.com) | Modelo de linguagem alternativo |
| [PostgreSQL](https://postgresql.org) | Banco de dados |
| [SQLAlchemy](https://sqlalchemy.org) | ORM e conexão com banco |
| [Plotly](https://plotly.com) | Gráficos interativos |
| [Pandas](https://pandas.pydata.org) | Manipulação de dados |

---

## 🚀 Como Rodar Localmente

### Pré-requisitos

- Python 3.10+
- PostgreSQL instalado e rodando
- Chave de API do [Google Gemini](https://aistudio.google.com/app/apikey)
- Chave de API do [Groq](https://console.groq.com)

### 1. Clone o repositório

```bash
git clone https://github.com/MatheusPpereira/finanIA.git
cd finanIA
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GOOGLE_API_KEY=sua_chave_google_aqui
GROQ_API_KEY=sua_chave_groq_aqui
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5433/financia
```

### 4. Configure o banco de dados

Crie o banco no PostgreSQL:

```sql
CREATE DATABASE financia;
```

Execute o script de configuração:

```bash
python setup_database.py
```

Ou restaure o backup incluso:

```bash
psql -U postgres -d financia -f backup_finania.sql
```

### 5. Rode a aplicação

```bash
streamlit run app.py
```

Acesse em: **http://localhost:8501**

---

## 🗃️ Estrutura do Banco de Dados

```
financia
├── categorias       (id, nome, tipo, created_at)
├── transacoes       (id, descricao, valor, tipo, categoria_id, data, created_at)
└── metas            (id, nome, valor_meta, valor_atual, data_limite, created_at)
```

**Categorias padrão incluídas:**

| Categoria | Tipo |
|---|---|
| Alimentação | despesa |
| Transporte | despesa |
| Moradia | despesa |
| Delivery | despesa |
| Lazer | despesa |
| Salário | receita |
| Freelance | receita |

---

## 📁 Estrutura do Projeto

```
finanIA/
├── app.py               # Aplicação principal (Streamlit)
├── chat_gemini.py       # Versão CLI para comparar Gemini vs Groq
├── database.py          # Configuração da conexão com o banco
├── setup_database.py    # Script de criação das tabelas
├── check_db.py          # Script de verificação do banco
├── test_gemini.py       # Teste de conexão com a API Gemini
├── backup_finania.sql   # Backup do banco de dados
├── requirements.txt     # Dependências do projeto
├── .env                 # Variáveis de ambiente (não versionado)
└── .gitignore
```

---

## 🔐 Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|---|---|---|
| `GOOGLE_API_KEY` | Chave da API do Google Gemini | ✅ |
| `GROQ_API_KEY` | Chave da API do Groq | ✅ |
| `DATABASE_URL` | URL de conexão com o PostgreSQL | ✅ |

> ⚠️ **Nunca** versione o arquivo `.env` nem exponha suas chaves publicamente.

---

## 💡 Como usar o Chat

O chat entende linguagem natural. Exemplos do que você pode dizer:

```
"Gastei R$85 no almoço hoje"
"Recebi meu salário de R$3.500"
"Paguei R$120 de Uber essa semana"
"Comprei mantimentos por R$200 no mercado"
"Como estão minhas finanças esse mês?"
"Estou gastando muito com delivery?"
```

A IA registra automaticamente as transações identificadas e responde com análises e dicas financeiras.

---

## 🎓 Contexto Acadêmico

Projeto desenvolvido como trabalho de conclusão de curso, explorando a integração de **Large Language Models (LLMs)** em aplicações de finanças pessoais. O projeto demonstra na prática:

- Integração com múltiplas APIs de IA (Google e Meta/Groq)
- Extração de informações estruturadas a partir de linguagem natural
- Persistência de dados com PostgreSQL via SQLAlchemy
- Desenvolvimento de interfaces web com Streamlit

---

## 👨‍💻 Autor

**Matheus P. Pereira**
- GitHub: [@MatheusPpereira](https://github.com/MatheusPpereira)

---

<div align="center">

**FinancIA v2.8** · Feito com 💚 e muito café

</div>
