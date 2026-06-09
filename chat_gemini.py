from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine, text
from datetime import datetime

load_dotenv()

# ====================== CONFIGURAÇÕES ======================
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5433/finania"
engine = create_engine(DATABASE_URL)

# === API 1: Gemini ===
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

# === API 2: Groq ===
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)

# System Prompt Forte
system_prompt = """
Você é o FinancIA, um assistente financeiro pessoal profissional e confiável.
Hoje é {data_atual}.

REGRAS IMPORTANTES:
- Comunique-se de forma clara, objetiva e respeitosa, como um consultor financeiro experiente
- Foque em finanças pessoais e ofereça orientações embasadas
- Seja empático — finanças podem ser um tema sensível para muitas pessoas
- Se o usuário tentar desviar do tema, redirecione educadamente para finanças
- Responda sempre em português brasileiro
"""

prompt_template = ChatPromptTemplate.from_template(system_prompt + "\n\nUsuário: {user_input}")

print("🤖 FinancIA v2.0 - Comparação Gemini vs Groq")
print("As duas IAs vão responder para comparação")
print("Digite 'sair' para encerrar\n")

while True:
    user_input = input("Você: ")
    
    if user_input.lower() in ['sair', 'exit', 'quit']:
        print("👋 FinancIA: Até mais!")
        break

    if not user_input.strip():
        continue

    try:
        prompt = prompt_template.format(
            data_atual=datetime.now().strftime("%d/%m/%Y"),
            user_input=user_input
        )

        print(f"\n{'='*60}")

        # === Resposta do Gemini ===
        print("🤖 GEMINI:")
        response_gemini = gemini_llm.invoke(prompt)
        print(response_gemini.content)

        print(f"\n{'-'*60}")

        # === Resposta do Groq ===
        print("🐎 GROQ (Llama 3.3):")
        response_groq = groq_llm.invoke(prompt)
        print(response_groq.content)

        print(f"{'='*60}\n")

        # Registro automático (usando Gemini)
        if "[REGISTRAR]" in response_gemini.content:
            try:
                linha = response_gemini.content.split("[REGISTRAR]")[1].strip()
                descricao, valor, tipo, categoria = [x.strip() for x in linha.split("|")]
                tipo = tipo.lower()
                
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data)
                        SELECT :desc, :valor, :tipo, id, CURRENT_DATE
                        FROM categorias WHERE nome ILIKE :cat
                    """), {"desc": descricao, "valor": float(valor), "tipo": tipo, "cat": categoria})
                    conn.commit()
                print(f"✅ Transação registrada automaticamente!\n")
            except:
                pass

    except Exception as e:
        print(f"❌ Erro: {e}\n")