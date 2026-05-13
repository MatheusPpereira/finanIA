from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# ==================== CONFIGURAÇÃO DO BANCO ====================
DATABASE_URL = "postgresql://postgres:postgres123@localhost:5433/finania"

engine = create_engine(DATABASE_URL, echo=False)  # echo=True para ver os logs SQL

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para pegar uma sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Teste de conexão
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ Conexão com o banco de dados 'finania' realizada com sucesso!")
            print(f"Porta: 5433")
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")