from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine, text
from datetime import datetime

load_dotenv()

# ====================== CONFIGURAÇÕES ======================
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5433/finania"
engine = create_engine(DATABASE_URL)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

prompt_template = ChatPromptTemplate.from_template("""
Você é o FinanIA, um assistente financeiro sarcástico, direto e bem brasileiro.
Hoje é {data_atual}.

Responda de forma natural e sarcástica.
Se for para registrar uma transação, no final coloque exatamente:
[REGISTRAR] Descricao | Valor | Tipo | Categoria

Importante: Use "despesa" ou "receita" sempre em minúsculo no campo Tipo.

Usuário: {user_input}
""")

print("🤖 FinanIA com LangChain + Banco de Dados (Versão Corrigida)")
print("Digite 'sair' para encerrar\n")

while True:
    user_input = input("Você: ")
    
    if user_input.lower() in ['sair', 'exit', 'quit']:
        print("👋 FinanIA: Até mais!")
        break

    if not user_input.strip():
        continue

    prompt = prompt_template.format(
        data_atual=datetime.now().strftime("%d/%m/%Y"),
        user_input=user_input
    )

    try:
        response = llm.invoke(prompt)
        resposta_ia = response.content
        
        print(f"\nFinanIA: {resposta_ia}\n")

        # Registro automático
        if "[REGISTRAR]" in resposta_ia:
            try:
                linha = resposta_ia.split("[REGISTRAR]")[1].strip()
                descricao, valor, tipo, categoria = [x.strip() for x in linha.split("|")]
                
                # Normaliza o tipo para minúsculo
                tipo = tipo.lower().strip()
                
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data)
                        SELECT :desc, :valor, :tipo, id, CURRENT_DATE
                        FROM categorias 
                        WHERE nome ILIKE :cat
                    """), {
                        "desc": descricao,
                        "valor": float(valor),
                        "tipo": tipo,
                        "cat": categoria
                    })
                    conn.commit()
                
                print(f"✅ Transação registrada com sucesso: {descricao} - R$ {valor}\n")
                
            except Exception as e:
                print(f"⚠️ Erro ao registrar: {e}\n")

    except Exception as e:
        print(f"❌ Erro: {e}\n")