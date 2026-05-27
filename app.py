import streamlit as st
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine, text
from datetime import datetime

load_dotenv()

# ====================== CONFIGURAÇÕES ======================
st.set_page_config(page_title="FinanIA", page_icon="💰", layout="wide")
st.title("💰 FinanIA - Assistente Financeiro Inteligente")
st.markdown("**JARVIS Financeiro** | Gemini + Groq + PostgreSQL")

# Conexão com Banco
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5433/finania"
engine = create_engine(DATABASE_URL)

# === Modelos ===
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    modelo_escolhido = st.radio("Escolha o modelo da IA:", 
                               ["Gemini", "Groq", "Comparar Ambos"])
    
    modo = st.selectbox("Modo da IA", 
                       ["Normal", "Professor", "Técnico", "Resumido", "Detalhado"])
    
    if st.button("📊 Ver Saldo Atual"):
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) as receitas,
                    COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0) as despesas
                FROM transacoes
            """))
            row = result.fetchone()
            saldo = row[0] - row[1]
            st.success(f"**Saldo Atual: R$ {saldo:,.2f}**")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua mensagem financeira..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("FinanIA pensando..."):
            full_prompt = f"""
            Você é o FinanIA, assistente financeiro sarcástico e útil.
            Modo: {modo}
            Data: {datetime.now().strftime('%d/%m/%Y')}
            
            Usuário: {prompt}
            """

            if modelo_escolhido == "Gemini":
                response = gemini_llm.invoke(full_prompt)
                resposta = response.content
            elif modelo_escolhido == "Groq":
                response = groq_llm.invoke(full_prompt)
                resposta = response.content
            else:  # Comparar Ambos
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Gemini:**")
                    resp_g = gemini_llm.invoke(full_prompt)
                    st.write(resp_g.content)
                with col2:
                    st.write("**Groq:**")
                    resp_q = groq_llm.invoke(full_prompt)
                    st.write(resp_q.content)
                resposta = resp_g.content  # usa Gemini como principal

            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})