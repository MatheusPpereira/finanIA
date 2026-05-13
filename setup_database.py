from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql://postgres:postgres123@localhost:5433/finania"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True ajuda a ver o que está acontecendo

def criar_banco_completo():
    try:
        with engine.connect() as conn:
            print("🔄 Iniciando criação das tabelas...\n")

            # Cria as tabelas
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL UNIQUE,
                    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('despesa', 'receita')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id SERIAL PRIMARY KEY,
                    descricao TEXT NOT NULL,
                    valor NUMERIC(12,2) NOT NULL,
                    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('despesa', 'receita')),
                    categoria_id INTEGER REFERENCES categorias(id),
                    data DATE NOT NULL DEFAULT CURRENT_DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS metas (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(150) NOT NULL,
                    valor_meta NUMERIC(12,2) NOT NULL,
                    valor_atual NUMERIC(12,2) DEFAULT 0,
                    data_limite DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # Insere categorias iniciais
            conn.execute(text("""
                INSERT INTO categorias (nome, tipo) VALUES 
                ('Alimentação', 'despesa'),
                ('Transporte', 'despesa'),
                ('Moradia', 'despesa'),
                ('Delivery', 'despesa'),
                ('Lazer', 'despesa'),
                ('Salário', 'receita'),
                ('Freelance', 'receita')
                ON CONFLICT (nome) DO NOTHING;
            """))

            conn.commit()
            print("✅ Tabelas criadas e categorias inseridas com sucesso!\n")

            # Verifica se realmente criou
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
            tables = [row[0] for row in result.fetchall()]
            print("📋 Tabelas existentes:", tables)

    except SQLAlchemyError as e:
        print(f"❌ Erro no banco: {e}")

if __name__ == "__main__":
    criar_banco_completo()