import os
from dotenv import load_dotenv
from google import genai
from sqlalchemy import create_engine, text
from datetime import datetime

load_dotenv()

# ====================== CONFIGURAÇÕES ======================
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5433/finania"
engine = create_engine(DATABASE_URL)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("🤖 FinanIA v0.3 - Com Banco de Dados Ativo")
print("Teste comandos como: 'gastei 85 no almoço', 'recebi salário', etc.")
print("Digite 'sair' para encerrar\n")

while True:
    user_input = input("Você: ")
    
    if user_input.lower() in ['sair', 'exit', 'quit']:
        print("👋 FinanIA: Até mais! Cuide bem do seu dinheiro.")
        break

    if not user_input.strip():
        continue

    # Prompt para o Gemini
    prompt = f"""
    Você é o FinanIA, um assistente financeiro sarcástico, brasileiro e direto.
    Data atual: {datetime.now().strftime('%d/%m/%Y')}
    
    Usuário: "{user_input}"
    
    Responda de forma natural e sarcástica.
    Se for para registrar uma transação, no final da resposta coloque exatamente neste formato:
    [REGISTRAR] Descricao | Valor | Tipo | Categoria
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        resposta = response.text
        print(f"\nFinanIA: {resposta}\n")

        # Tenta registrar automaticamente
        if "[REGISTRAR]" in resposta:
            try:
                linha = resposta.split("[REGISTRAR]")[1].strip()
                descricao, valor, tipo, categoria = [x.strip() for x in linha.split("|")]
                
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO transacoes (descricao, valor, tipo, categoria_id, data)
                        SELECT :desc, :valor, :tipo, id, CURRENT_DATE
                        FROM categorias 
                        WHERE nome ILIKE :cat
                    """), {"desc": descricao, "valor": float(valor), "tipo": tipo, "cat": categoria})
                    conn.commit()
                
                print(f"✅ Registrado com sucesso: {descricao} - R$ {valor}\n")
            except Exception as e:
                print(f"⚠️ Não consegui registrar: {e}\n")

    except Exception as e:
        print(f"❌ Erro: {e}\n")