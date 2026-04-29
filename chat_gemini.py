import os
from dotenv import load_dotenv
from google import genai

# Configuração
load_dotenv(override=True)

google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    print("❌ Erro: Chave não encontrada no arquivo .env")
    exit()

client = genai.Client(api_key=google_api_key)

print("🤖 FinanIA Chat - Digite 'sair' para encerrar\n")
print("Faça suas perguntas sobre finanças ou qualquer coisa...\n")

while True:
    pergunta = input("Você: ")
    
    if pergunta.lower() in ['sair', 'exit', 'quit']:
        print("👋 FinanIA: Até mais! Cuide bem das suas finanças.")
        break
    
    if pergunta.strip() == "":
        continue

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Você é o FinanIA, um assistente financeiro sarcástico, direto e bem brasileiro. Responda sempre em português brasileiro de forma natural e útil.\n\nPergunta: {pergunta}"
        )
        
        print(f"\nFinanIA: {response.text}\n")
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar resposta: {e}\n")