import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine, text

load_dotenv()

# ====================== CONFIGURAÇÕES ======================
st.set_page_config(page_title="FinanIA", page_icon="💰", layout="wide")
st.title("💰 FinanIA")
st.markdown("**Assistente Financeiro Pessoal Inteligente | Gemini + Groq + PostgreSQL**")

# Conexão Banco
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5433/finania"
engine = create_engine(DATABASE_URL)

# ====================== IAs ======================
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"), 
    temperature=0.65
)
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    groq_api_key=os.getenv("GROQ_API_KEY"), 
    temperature=0.65
)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("Navegação")
    pagina = st.radio("Escolha uma seção:", 
                     ["💬 Chat Inteligente", "📊 Dashboard", "📋 Transações", "🎯 Metas"])

    st.divider()
    modelo_ia = st.selectbox("Modelo de IA", ["Gemini", "Groq", "Comparar Ambos"])
    modo_ia = st.selectbox("Modo da IA", 
                          ["Normal", "Modo Professor", "Modo Técnico", "Modo Resumido", "Modo Detalhado"])

# ====================== FUNÇÃO SALVAR TRANSAÇÃO ======================
def salvar_transacao(descricao, valor, tipo, categoria):
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data)
                SELECT :desc, :valor, :tipo, id, CURRENT_DATE
                FROM categorias WHERE nome ILIKE :cat
            """), {"desc": descricao, "valor": float(valor), "tipo": tipo.lower(), "cat": categoria})
            conn.commit()
        return True
    except:
        return False

# ====================== FUNÇÃO HISTÓRICO ======================
def get_historico():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT descricao, valor, tipo, data FROM transacoes ORDER BY data DESC LIMIT 10", conn)
    return df.to_string(index=False) if not df.empty else "Nenhuma transação registrada."

# ====================== CHAT ======================
if pagina == "💬 Chat Inteligente":
    st.header("💬 Chat com FinanIA")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Fale sobre gastos, salário, metas..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("FinanIA analisando seu histórico..."):
                historico = get_historico()

                full_prompt = f"""
                Você é o FinanIA, assistente financeiro sarcástico e útil.
                Modo atual: {modo_ia}
                Data: {datetime.now().strftime('%d/%m/%Y')}

                HISTÓRICO RECENTE:
                {historico}

                Responda de acordo com o modo. Se identificar gasto ou receita, no FINAL coloque:
                [REGISTRAR] Descricao | Valor | Tipo | Categoria

                Usuário: {prompt}
                """

                if modelo_ia == "Gemini":
                    response = gemini_llm.invoke(full_prompt)
                elif modelo_ia == "Groq":
                    response = groq_llm.invoke(full_prompt)
                else:
                    response = gemini_llm.invoke(full_prompt)

                resposta = response.content
                st.write(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})

                if "[REGISTRAR]" in resposta:
                    try:
                        linha = resposta.split("[REGISTRAR]")[1].strip()
                        descricao, valor, tipo, categoria = [x.strip() for x in linha.split("|")]
                        if salvar_transacao(descricao, valor, tipo, categoria):
                            st.success(f"✅ Registrado: {descricao} - R$ {valor}")
                            st.rerun()
                    except:
                        pass

# ====================== DASHBOARD ======================
elif pagina == "📊 Dashboard":
    st.header("📊 Dashboard Financeiro")
    with engine.connect() as conn:
        df = pd.read_sql("SELECT t.*, c.nome as categoria FROM transacoes t LEFT JOIN categorias c ON t.categoria_id = c.id ORDER BY t.data DESC", conn)
        saldo = conn.execute(text("""
            SELECT COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) - 
                   COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0)
            FROM transacoes
        """)).scalar()

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Saldo Atual", f"R$ {saldo:,.2f}")
    col2.metric("📉 Despesas Mês", f"R$ {df[df['tipo']=='despesa']['valor'].sum():,.2f}")
    col3.metric("📈 Receitas Mês", f"R$ {df[df['tipo']=='receita']['valor'].sum():,.2f}")

    col1, col2 = st.columns(2)
    with col1:
        if not df.empty:
            gastos = df[df['tipo']=='despesa'].groupby('categoria')['valor'].sum()
            fig = px.pie(values=gastos.values, names=gastos.index, title="Gastos por Categoria")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if not df.empty:
            df['data'] = pd.to_datetime(df['data'])
            evolucao = df.groupby('data')['valor'].sum().reset_index()
            fig2 = px.line(evolucao, x='data', y='valor', title="Evolução Financeira")
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Últimas Transações")
    st.dataframe(df.head(10)[['data', 'descricao', 'valor', 'tipo', 'categoria']], use_container_width=True, hide_index=True)

# ====================== TRANSAÇÕES ======================
elif pagina == "📋 Transações":
    st.header("📋 Todas as Transações")
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM transacoes ORDER BY data DESC", conn)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ====================== METAS ======================
elif pagina == "🎯 Metas":
    st.header("🎯 Minhas Metas Financeiras")

    with st.expander("➕ Criar Nova Meta", expanded=True):
        with st.form("nova_meta"):
            nome = st.text_input("Nome da Meta")
            valor_meta = st.number_input("Valor Total (R$)", min_value=100.0, step=50.0)
            data_limite = st.date_input("Data Limite", value=date(2026, 12, 31))
            if st.form_submit_button("Criar Meta"):
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO metas (nome, valor_meta, data_limite, valor_atual)
                        VALUES (:nome, :valor_meta, :data_limite, 0)
                    """), {"nome": nome, "valor_meta": valor_meta, "data_limite": data_limite})
                    conn.commit()
                st.success("Meta criada com sucesso!")
                st.rerun()

    st.subheader("Metas Atuais")
    with engine.connect() as conn:
        metas = pd.read_sql("SELECT * FROM metas ORDER BY data_limite", conn)

    if not metas.empty:
        for _, meta in metas.iterrows():
            progresso = (meta['valor_atual'] / meta['valor_meta']) * 100 if meta['valor_meta'] > 0 else 0
            col1, col2, col3 = st.columns([3, 1.5, 1])
            with col1:
                st.write(f"**{meta['nome']}**")
                st.progress(progresso / 100)
                st.caption(f"R$ {meta['valor_atual']:,.2f} / R$ {meta['valor_meta']:,.2f} | {meta['data_limite']}")
            with col2:
                novo_valor = st.number_input("Valor atual", value=float(meta['valor_atual']), key=f"v_{meta['id']}")
            with col3:
                if st.button("Atualizar", key=f"b_{meta['id']}"):
                    with engine.connect() as conn:
                        conn.execute(text("UPDATE metas SET valor_atual = :valor WHERE id = :id"), 
                                   {"valor": novo_valor, "id": meta['id']})
                        conn.commit()
                    st.success("Atualizado!")
                    st.rerun()
    else:
        st.info("Nenhuma meta cadastrada ainda.")

st.caption("FinanIA v2.7 - Completo com Modos, Memória e Metas")