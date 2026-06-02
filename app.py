import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from sqlalchemy import create_engine, text

load_dotenv()

# ====================== CONFIGURAÇÕES ======================
st.set_page_config(page_title="FinancIA", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

# ====================== CSS PERSONALIZADO ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

    /* ── Reset & Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Fundo principal ── */
    .stApp {
        background: #0a0e1a;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1220 0%, #0a0e1a 100%);
        border-right: 1px solid rgba(99, 220, 160, 0.12);
    }
    [data-testid="stSidebar"] .stRadio label {
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
        color: #8a9ab5;
        padding: 6px 0;
        transition: color 0.2s;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        color: #63dca0;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Syne', sans-serif;
        color: #e2e8f4;
        font-size: 1rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #8a9ab5;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* ── Logo / Header ── */
    .financia-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 28px 0 8px 0;
        margin-bottom: 4px;
    }
    .financia-logo {
        font-size: 2.6rem;
        line-height: 1;
    }
    .financia-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #63dca0 0%, #4ab8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        line-height: 1;
    }
    .financia-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #4a5568;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 6px;
    }

    /* ── Cards de Métricas ── */
    .metric-card {
        background: linear-gradient(135deg, #111827 0%, #0f1623 100%);
        border: 1px solid rgba(99, 220, 160, 0.12);
        border-radius: 16px;
        padding: 22px 24px;
        text-align: left;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s, transform 0.2s;
    }
    .metric-card:hover {
        border-color: rgba(99, 220, 160, 0.35);
        transform: translateY(-2px);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #63dca0, #4ab8f0);
        opacity: 0.6;
    }
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        color: #4a5568;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: #e2e8f4;
        letter-spacing: -0.02em;
    }
    .metric-value.green { color: #63dca0; }
    .metric-value.red { color: #f87171; }
    .metric-value.blue { color: #4ab8f0; }
    .metric-icon {
        position: absolute;
        top: 18px; right: 20px;
        font-size: 1.6rem;
        opacity: 0.25;
    }

    /* ── Seção de boas-vindas do Chat ── */
    .chat-welcome {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px 40px 20px;
        text-align: center;
    }
    .chat-welcome-icon {
        font-size: 3.5rem;
        margin-bottom: 16px;
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    .chat-welcome-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f4;
        margin-bottom: 8px;
    }
    .chat-welcome-sub {
        font-size: 0.9rem;
        color: #4a5568;
        max-width: 420px;
        line-height: 1.6;
    }
    .suggestion-chip {
        display: inline-block;
        background: rgba(99, 220, 160, 0.08);
        border: 1px solid rgba(99, 220, 160, 0.2);
        color: #63dca0;
        border-radius: 20px;
        padding: 7px 16px;
        font-size: 0.82rem;
        margin: 5px;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        transition: background 0.2s;
    }
    .suggestion-chip:hover {
        background: rgba(99, 220, 160, 0.16);
    }

    /* ── Badge do modelo ── */
    .model-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(74, 184, 240, 0.08);
        border: 1px solid rgba(74, 184, 240, 0.2);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.75rem;
        color: #4ab8f0;
        font-family: 'Inter', sans-serif;
        margin-bottom: 16px;
    }

    /* ── Page header ── */
    .page-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #e2e8f4;
        margin-bottom: 24px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(99, 220, 160, 0.1);
    }

    /* ── Divider estilizado ── */
    hr {
        border: none;
        border-top: 1px solid rgba(99, 220, 160, 0.1) !important;
        margin: 20px 0;
    }

    /* ── Tabela / Dataframe ── */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(99, 220, 160, 0.1);
    }

    /* ── Inputs ── */
    .stTextInput input, .stNumberInput input {
        background: #111827 !important;
        border: 1px solid rgba(99, 220, 160, 0.2) !important;
        border-radius: 10px !important;
        color: #e2e8f4 !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #63dca0 !important;
        box-shadow: 0 0 0 2px rgba(99, 220, 160, 0.15) !important;
    }

    /* ── Botões ── */
    .stButton > button {
        background: linear-gradient(135deg, #63dca0, #4ab8f0) !important;
        color: #0a0e1a !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.04em !important;
        transition: opacity 0.2s, transform 0.15s !important;
    }
    .stButton > button:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }

    /* ── Chat input ── */
    [data-testid="stChatInput"] {
        border-radius: 14px !important;
        border: 1px solid rgba(99, 220, 160, 0.2) !important;
        background: #111827 !important;
    }

    /* ── Progress bar ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #63dca0, #4ab8f0) !important;
        border-radius: 10px !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #111827 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99, 220, 160, 0.15) !important;
        color: #e2e8f4 !important;
        font-family: 'Syne', sans-serif !important;
    }

    /* ── Success / Info ── */
    .stSuccess {
        background: rgba(99, 220, 160, 0.08) !important;
        border: 1px solid rgba(99, 220, 160, 0.3) !important;
        border-radius: 10px !important;
    }
    .stInfo {
        background: rgba(74, 184, 240, 0.08) !important;
        border: 1px solid rgba(74, 184, 240, 0.3) !important;
        border-radius: 10px !important;
    }

    /* ── Rodapé ── */
    .financia-footer {
        text-align: center;
        padding: 24px 0 8px 0;
        font-size: 0.72rem;
        color: #2d3748;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
    }

    /* ── Esconder elementos padrão do Streamlit ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== CONEXÃO BANCO ======================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5433/finania")
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
    st.markdown("""
    <div style="padding: 16px 0 24px 0;">
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800;
                    background:linear-gradient(135deg,#63dca0,#4ab8f0);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text; letter-spacing:-0.01em;">
            💰 FinancIA
        </div>
        <div style="font-size:0.7rem; color:#2d3748; text-transform:uppercase;
                    letter-spacing:0.1em; margin-top:4px; font-family:'Inter',sans-serif;">
            Assistente Financeiro IA
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-family:Inter;font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">NAVEGAÇÃO</p>', unsafe_allow_html=True)
    pagina = st.radio("",
                      ["💬 Chat Inteligente", "📊 Dashboard", "📋 Transações", "🎯 Metas"],
                      label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<p style="font-family:Inter;font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">CONFIGURAÇÕES DE IA</p>', unsafe_allow_html=True)
    modelo_ia = st.selectbox("Modelo", ["Gemini", "Groq", "Comparar Ambos"])
    modo_ia = st.selectbox("Modo de Resposta",
                           ["Normal", "Modo Professor", "Modo Técnico", "Modo Resumido", "Modo Detalhado"])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem; color:#2d3748; font-family:'Inter',sans-serif; line-height:1.6;">
        🟢 <span style="color:#63dca0;">Gemini 2.5 Flash</span> conectado<br>
        🟢 <span style="color:#4ab8f0;">Llama 3.3 70B</span> conectado<br>
        🟢 <span style="color:#a78bfa;">PostgreSQL</span> ativo
    </div>
    """, unsafe_allow_html=True)

# ====================== FUNÇÕES ======================
def salvar_transacao(descricao, valor, tipo, categoria):
    try:
        tipo = tipo.lower().strip()
        if tipo not in ["despesa", "receita"]:
            tipo = "despesa"
        with engine.connect() as conn:
            rows = conn.execute(text("""
                INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data)
                SELECT :desc, :valor, :tipo, id, CURRENT_DATE
                FROM categorias WHERE nome ILIKE :cat
                RETURNING id
            """), {"desc": descricao, "valor": float(valor), "tipo": tipo, "cat": f"%{categoria}%"})
            if rows.rowcount == 0:
                conn.execute(text("""
                    INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data)
                    SELECT :desc, :valor, :tipo, id, CURRENT_DATE
                    FROM categorias WHERE tipo = :tipo
                    ORDER BY id LIMIT 1
                """), {"desc": descricao, "valor": float(valor), "tipo": tipo})
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar transação: {e}")
        return False


def get_historico():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                "SELECT descricao, valor, tipo, data FROM transacoes ORDER BY data DESC LIMIT 10", conn)
        return df.to_string(index=False) if not df.empty else "Nenhuma transação registrada."
    except Exception as e:
        return f"Erro ao buscar histórico: {e}"


def get_saldo_e_df():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                """SELECT t.*, c.nome as categoria
                   FROM transacoes t
                   LEFT JOIN categorias c ON t.categoria_id = c.id
                   ORDER BY t.data DESC""", conn)
            saldo = conn.execute(text("""
                SELECT COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END), 0) -
                       COALESCE(SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END), 0)
                FROM transacoes
            """)).scalar()
        return df, float(saldo)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), 0.0


def get_totais_mes(df):
    """Retorna despesas e receitas do mês atual."""
    if df.empty:
        return 0.0, 0.0
    df_copia = df.copy()
    df_copia['data'] = pd.to_datetime(df_copia['data'])
    hoje = datetime.now()
    df_mes = df_copia[
        (df_copia['data'].dt.month == hoje.month) &
        (df_copia['data'].dt.year == hoje.year)
    ]
    despesas = float(df_mes[df_mes['tipo'] == 'despesa']['valor'].sum())
    receitas = float(df_mes[df_mes['tipo'] == 'receita']['valor'].sum())
    return despesas, receitas


# ====================== HEADER PRINCIPAL ======================
st.markdown("""
<div class="financia-header">
    <div class="financia-logo">💰</div>
    <div>
        <div class="financia-title">FinancIA</div>
        <div class="financia-subtitle">Assistente Financeiro Pessoal com IA</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ====================== CHAT ======================
if pagina == "💬 Chat Inteligente":

    modelo_label = {"Gemini": "Gemini 2.5 Flash", "Groq": "Llama 3.3 70B", "Comparar Ambos": "Gemini + Llama"}
    st.markdown(f'<div class="model-badge">🤖 {modelo_label[modelo_ia]} · {modo_ia}</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Boas-vindas quando chat está vazio
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-welcome">
            <div class="chat-welcome-icon">🤖</div>
            <div class="chat-welcome-title">Olá! Sou o FinancIA</div>
            <div class="chat-welcome-sub">
                Seu assistente financeiro pessoal com IA. Me conte sobre seus gastos,
                receitas e metas — vou te ajudar a organizar suas finanças com um toque de sarcasmo brasileiro. 😄
            </div>
            <div style="margin-top: 20px;">
                <span class="suggestion-chip">💸 Gastei R$85 no almoço</span>
                <span class="suggestion-chip">📊 Como estão minhas finanças?</span>
                <span class="suggestion-chip">🎯 Quero criar uma meta</span>
                <span class="suggestion-chip">💰 Recebi meu salário</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Fale sobre gastos, salário, metas..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("FinancIA analisando seu histórico..."):
                historico = get_historico()

                # Categorias disponíveis no banco
                categorias_disponiveis = "Alimentação, Transporte, Moradia, Delivery, Lazer, Salário, Freelance"

                full_prompt = f"""
Você é o FinancIA, assistente financeiro pessoal sarcástico e útil. Responda SEMPRE em português brasileiro.
Modo atual: {modo_ia}
Data de hoje: {datetime.now().strftime('%d/%m/%Y')}

HISTÓRICO RECENTE DO USUÁRIO:
{historico}

REGRAS CRÍTICAS PARA REGISTRO:
1. Se o usuário mencionar qualquer gasto, despesa, compra, pagamento ou receita — mesmo que de forma vaga — você DEVE registrar.
2. Use o contexto da conversa para preencher campos que faltam. Não pergunte o que já foi dito.
3. Para descrição: use o que o usuário disse (ex: "gasto de 10 mil reais", "almoço", "salário").
4. Para categoria: escolha a mais adequada dentre: {categorias_disponiveis}. Se não souber, use "Lazer" para despesas ou "Freelance" para receitas.
5. Para tipo: "despesa" para gastos/compras/pagamentos, "receita" para salário/entrada de dinheiro.
6. NUNCA coloque "?" nos campos — sempre infira um valor razoável.
7. Ao final da resposta, se houver transação identificada, coloque EXATAMENTE neste formato na última linha:
[REGISTRAR] Descrição da transação | Valor numérico sem R$ | despesa ou receita | Nome da categoria

EXEMPLO CORRETO:
[REGISTRAR] Gasto geral | 10000 | despesa | Lazer

Mensagem do usuário: {prompt}
"""

                if modelo_ia == "Gemini":
                    response = gemini_llm.invoke(full_prompt)
                    resposta = response.content
                    st.write(resposta)

                elif modelo_ia == "Groq":
                    response = groq_llm.invoke(full_prompt)
                    resposta = response.content
                    st.write(resposta)

                else:
                    # Comparar Ambos — mostra as duas respostas
                    col_gem, col_groq = st.columns(2)
                    with col_gem:
                        st.markdown('<div style="font-size:0.75rem;color:#63dca0;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">🤖 Gemini</div>', unsafe_allow_html=True)
                        r_gemini = gemini_llm.invoke(full_prompt)
                        st.write(r_gemini.content)
                    with col_groq:
                        st.markdown('<div style="font-size:0.75rem;color:#4ab8f0;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">🐎 Groq (Llama)</div>', unsafe_allow_html=True)
                        r_groq = groq_llm.invoke(full_prompt)
                        st.write(r_groq.content)
                    resposta = r_gemini.content  # usa Gemini para registro automático

                st.session_state.messages.append({"role": "assistant", "content": resposta})

                if "[REGISTRAR]" in resposta:
                    try:
                        linha = resposta.split("[REGISTRAR]")[1].strip().split("\n")[0]
                        partes = [x.strip() for x in linha.split("|")]

                        if len(partes) == 4:
                            descricao, valor_str, tipo, categoria = partes

                            # Limpar e validar valor
                            valor_str = valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
                            valor_limpo = float(valor_str) if valor_str.replace(".", "").isdigit() else None

                            # Fallbacks para campos inválidos
                            if not descricao or descricao == "?":
                                descricao = prompt[:60]  # usa o que o usuário digitou
                            if not tipo or tipo == "?" or tipo.lower() not in ["despesa", "receita"]:
                                tipo = "despesa"
                            if not categoria or categoria == "?":
                                categoria = "Lazer" if tipo == "despesa" else "Freelance"
                            if valor_limpo is None or valor_limpo <= 0:
                                # Tenta extrair número da mensagem do usuário
                                import re
                                nums = re.findall(r'[\d]+(?:[.,]\d+)?', prompt.replace(".", "").replace(",", "."))
                                valor_limpo = float(nums[0]) if nums else None

                            if valor_limpo and valor_limpo > 0:
                                if salvar_transacao(descricao, valor_limpo, tipo, categoria):
                                    st.success(f"✅ Registrado: **{descricao}** — R$ {valor_limpo:,.2f} ({tipo} · {categoria})")
                                    st.rerun()
                            else:
                                st.warning("⚠️ Não consegui identificar o valor. Pode repetir com o valor exato?")
                        else:
                            st.warning("⚠️ Formato de registro inválido retornado pela IA.")
                    except Exception as e:
                        st.warning(f"⚠️ Erro ao registrar: {e}")

# ====================== DASHBOARD ======================
elif pagina == "📊 Dashboard":
    st.markdown('<div class="page-header">📊 Dashboard Financeiro</div>', unsafe_allow_html=True)

    df, saldo = get_saldo_e_df()
    despesas_mes, receitas_mes = get_totais_mes(df)

    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        cor_saldo = "green" if saldo >= 0 else "red"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-label">Saldo Atual</div>
            <div class="metric-value {cor_saldo}">R$ {saldo:,.2f}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📉</div>
            <div class="metric-label">Despesas do Mês</div>
            <div class="metric-value red">R$ {despesas_mes:,.2f}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-label">Receitas do Mês</div>
            <div class="metric-value green">R$ {receitas_mes:,.2f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficos
    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            gastos = df[df['tipo'] == 'despesa'].groupby('categoria')['valor'].sum()
            if not gastos.empty:
                fig = px.pie(
                    values=gastos.values, names=gastos.index,
                    title="Gastos por Categoria",
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", color="#8a9ab5"),
                    title_font=dict(family="Syne", size=14, color="#e2e8f4"),
                    legend=dict(font=dict(color="#8a9ab5"))
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            df_ev = df.copy()
            df_ev['data'] = pd.to_datetime(df_ev['data'])
            evolucao = df_ev.groupby(['data', 'tipo'])['valor'].sum().reset_index()
            if not evolucao.empty:
                fig2 = px.line(
                    evolucao, x='data', y='valor', color='tipo',
                    title="Evolução por Tipo",
                    color_discrete_map={"despesa": "#f87171", "receita": "#63dca0"}
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(17,24,39,0.6)",
                    font=dict(family="Inter", color="#8a9ab5"),
                    title_font=dict(family="Syne", size=14, color="#e2e8f4"),
                    legend=dict(font=dict(color="#8a9ab5"), title_text=""),
                    xaxis=dict(gridcolor="rgba(99,220,160,0.07)"),
                    yaxis=dict(gridcolor="rgba(99,220,160,0.07)")
                )
                fig2.update_traces(line=dict(width=2.5))
                st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#e2e8f4;margin:16px 0 12px;">Últimas Transações</div>', unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(
            df.head(10)[['data', 'descricao', 'valor', 'tipo', 'categoria']],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Nenhuma transação registrada ainda.")

# ====================== TRANSAÇÕES ======================
elif pagina == "📋 Transações":
    st.markdown('<div class="page-header">📋 Todas as Transações</div>', unsafe_allow_html=True)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                """SELECT t.id, t.data, t.descricao, t.valor, t.tipo, c.nome as categoria
                   FROM transacoes t
                   LEFT JOIN categorias c ON t.categoria_id = c.id
                   ORDER BY t.data DESC""", conn)

        if not df.empty:
            # Filtros rápidos
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                tipo_filtro = st.selectbox("Filtrar por tipo", ["Todos", "despesa", "receita"])
            with col_f2:
                categorias_disponiveis = ["Todas"] + sorted(df['categoria'].dropna().unique().tolist())
                cat_filtro = st.selectbox("Filtrar por categoria", categorias_disponiveis)
            with col_f3:
                st.markdown("<br>", unsafe_allow_html=True)
                st.metric("Total de registros", len(df))

            df_filtrado = df.copy()
            if tipo_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_filtro]
            if cat_filtro != "Todas":
                df_filtrado = df_filtrado[df_filtrado['categoria'] == cat_filtro]

            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma transação registrada ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar transações: {e}")

# ====================== METAS ======================
elif pagina == "🎯 Metas":
    st.markdown('<div class="page-header">🎯 Minhas Metas Financeiras</div>', unsafe_allow_html=True)

    with st.expander("➕ Criar Nova Meta", expanded=False):
        with st.form("nova_meta"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                nome = st.text_input("Nome da Meta", placeholder="Ex: Viagem para o Japão")
            with col_b:
                valor_meta = st.number_input("Valor Total (R$)", min_value=100.0, step=50.0)
            with col_c:
                data_limite = st.date_input("Data Limite", value=date(2026, 12, 31))
            if st.form_submit_button("✅ Criar Meta"):
                if nome.strip():
                    try:
                        with engine.connect() as conn:
                            conn.execute(text("""
                                INSERT INTO metas (nome, valor_meta, data_limite, valor_atual)
                                VALUES (:nome, :valor_meta, :data_limite, 0)
                            """), {"nome": nome, "valor_meta": valor_meta, "data_limite": data_limite})
                            conn.commit()
                        st.success("🎯 Meta criada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar meta: {e}")
                else:
                    st.warning("Por favor, informe um nome para a meta.")

    st.markdown('<div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#e2e8f4;margin:16px 0 12px;">Metas em Andamento</div>', unsafe_allow_html=True)

    try:
        with engine.connect() as conn:
            metas = pd.read_sql("SELECT * FROM metas ORDER BY data_limite", conn)
    except Exception as e:
        st.error(f"Erro ao carregar metas: {e}")
        metas = pd.DataFrame()

    if not metas.empty:
        for _, meta in metas.iterrows():
            progresso = min((meta['valor_atual'] / meta['valor_meta']) * 100, 100) if meta['valor_meta'] > 0 else 0
            dias_restantes = (pd.to_datetime(meta['data_limite']) - pd.Timestamp.now()).days

            with st.container():
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#111827,#0f1623);
                            border:1px solid rgba(99,220,160,0.12);
                            border-radius:14px; padding:20px 24px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                        <div>
                            <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#e2e8f4;">{meta['nome']}</div>
                            <div style="font-size:0.78rem;color:#4a5568;margin-top:3px;">
                                {"⏰ " + str(dias_restantes) + " dias restantes" if dias_restantes > 0 else "⚠️ Prazo encerrado"}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:#63dca0;">{progresso:.0f}%</div>
                            <div style="font-size:0.75rem;color:#4a5568;">R$ {meta['valor_atual']:,.2f} / R$ {meta['valor_meta']:,.2f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.progress(progresso / 100)

                col1, col2 = st.columns([3, 1])
                with col1:
                    novo_valor = st.number_input(
                        "Atualizar valor atual (R$)",
                        value=float(meta['valor_atual']),
                        key=f"v_{meta['id']}",
                        min_value=0.0,
                        step=50.0
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Atualizar", key=f"b_{meta['id']}"):
                        try:
                            with engine.connect() as conn:
                                conn.execute(
                                    text("UPDATE metas SET valor_atual = :valor WHERE id = :id"),
                                    {"valor": novo_valor, "id": meta['id']}
                                )
                                conn.commit()
                            st.success("✅ Meta atualizada!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {e}")
    else:
        st.info("Nenhuma meta cadastrada ainda. Crie sua primeira meta acima! 🎯")

# ====================== RODAPÉ ======================
st.markdown('<div class="financia-footer">FinancIA v2.8 · Gemini + Groq + PostgreSQL · Assistente Financeiro Pessoal com IA</div>', unsafe_allow_html=True)
