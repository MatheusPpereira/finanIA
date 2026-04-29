import os
from dotenv import load_dotenv
from google import genai

print("🔍 Iniciando teste do FinanIA (versão atualizada 2026)...\n")

load_dotenv(override=True)

google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    print("❌ ERRO: Chave não encontrada!")
    exit()

print(f"✅ Chave carregada com sucesso! ({len(google_api_key)} caracteres)")

client = genai.Client(api_key=google_api_key)

print("🚀 Enviando pergunta para o FinanIA...\n")

# Testando modelos mais recentes e estáveis
response = client.models.generate_content(
    model="gemini-2.5-flash",        # Modelo mais atual e estável
    contents=(
        "Você é o FinanIA, um assistente financeiro sarcástico, direto e bem brasileiro. "
        "Responda sempre de forma natural e em português brasileiro.\n\n"
        "O que você acha de alguém que gasta R$ 950 por mês só com delivery e iFood?"
    )
)

print("🤖 Resposta do FinanIA:")
print("=" * 70)
print(response.text)
print("=" * 70)