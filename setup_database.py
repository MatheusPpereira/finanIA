"""
setup_database.py — FinancIA
Execute este script UMA VEZ para criar o banco do zero.
Para resetar dados de teste, use: python setup_database.py --reset
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5433/finania")
engine = create_engine(DATABASE_URL, echo=False)


def criar_tabelas(conn):
    print("📦 Criando tabelas...")

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS categorias (
            id          SERIAL PRIMARY KEY,
            nome        VARCHAR(100) NOT NULL UNIQUE,
            tipo        VARCHAR(20)  NOT NULL CHECK (tipo IN ('despesa', 'receita')),
            icone       VARCHAR(10)  DEFAULT '💸',
            created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
        );
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id           SERIAL PRIMARY KEY,
            descricao    TEXT         NOT NULL,
            valor        NUMERIC(12,2) NOT NULL CHECK (valor > 0),
            tipo         VARCHAR(20)  NOT NULL CHECK (tipo IN ('despesa', 'receita')),
            categoria_id INTEGER      REFERENCES categorias(id) ON DELETE SET NULL,
            data         DATE         NOT NULL DEFAULT CURRENT_DATE,
            observacao   TEXT,
            created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
        );
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS metas (
            id          SERIAL PRIMARY KEY,
            nome        VARCHAR(150) NOT NULL,
            descricao   TEXT,
            valor_meta  NUMERIC(12,2) NOT NULL CHECK (valor_meta > 0),
            valor_atual NUMERIC(12,2) DEFAULT 0 CHECK (valor_atual >= 0),
            data_limite DATE,
            concluida   BOOLEAN      DEFAULT FALSE,
            created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
        );
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id           SERIAL PRIMARY KEY,
            categoria_id INTEGER REFERENCES categorias(id) ON DELETE CASCADE,
            valor_limite NUMERIC(12,2) NOT NULL CHECK (valor_limite > 0),
            mes          INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
            ano          INTEGER NOT NULL,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (categoria_id, mes, ano)
        );
    """))

    print("   ✅ Tabelas criadas.")


def criar_indices(conn):
    print("🔍 Criando índices de performance...")
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_transacoes_data     ON transacoes(data DESC);",
        "CREATE INDEX IF NOT EXISTS idx_transacoes_tipo     ON transacoes(tipo);",
        "CREATE INDEX IF NOT EXISTS idx_transacoes_mes_ano  ON transacoes(EXTRACT(MONTH FROM data), EXTRACT(YEAR FROM data));",
        "CREATE INDEX IF NOT EXISTS idx_transacoes_cat      ON transacoes(categoria_id);",
        "CREATE INDEX IF NOT EXISTS idx_metas_data_limite   ON metas(data_limite);",
    ]
    for idx in indices:
        conn.execute(text(idx))
    print("   ✅ Índices criados.")


def inserir_categorias(conn):
    print("🏷️  Inserindo categorias padrão...")
    conn.execute(text("""
        INSERT INTO categorias (nome, tipo, icone) VALUES
            ('Alimentação',   'despesa', '🍽️'),
            ('Transporte',    'despesa', '🚗'),
            ('Moradia',       'despesa', '🏠'),
            ('Delivery',      'despesa', '🛵'),
            ('Lazer',         'despesa', '🎉'),
            ('Saúde',         'despesa', '💊'),
            ('Educação',      'despesa', '📚'),
            ('Vestuário',     'despesa', '👕'),
            ('Assinaturas',   'despesa', '📱'),
            ('Outros',        'despesa', '💸'),
            ('Salário',       'receita', '💼'),
            ('Freelance',     'receita', '💻'),
            ('Investimentos', 'receita', '📈'),
            ('Outros Ganhos', 'receita', '💰')
        ON CONFLICT (nome) DO NOTHING;
    """))
    print("   ✅ Categorias inseridas.")


def resetar_dados(conn):
    print("🗑️  Resetando dados de transações e metas...")
    conn.execute(text("DELETE FROM orcamentos;"))
    conn.execute(text("DELETE FROM metas;"))
    conn.execute(text("DELETE FROM transacoes;"))
    conn.execute(text("ALTER SEQUENCE transacoes_id_seq RESTART WITH 1;"))
    conn.execute(text("ALTER SEQUENCE metas_id_seq RESTART WITH 1;"))
    conn.execute(text("ALTER SEQUENCE orcamentos_id_seq RESTART WITH 1;"))
    print("   ✅ Dados resetados. Categorias mantidas.")


def verificar(conn):
    print("\n📋 Verificação final:")
    tabelas = conn.execute(text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' ORDER BY table_name;
    """)).fetchall()
    for t in tabelas:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {t[0]}")).scalar()
        print(f"   ✅ {t[0]:20s} → {count} registros")

    cats = conn.execute(text("SELECT nome, tipo FROM categorias ORDER BY tipo, nome")).fetchall()
    print(f"\n🏷️  Categorias disponíveis ({len(cats)}):")
    for c in cats:
        print(f"   {'📤' if c[1]=='receita' else '📥'} {c[0]} ({c[1]})")


def main():
    reset = "--reset" in sys.argv

    try:
        with engine.connect() as conn:
            print(f"\n{'='*50}")
            print("  FinancIA — Setup do Banco de Dados")
            print(f"{'='*50}\n")

            criar_tabelas(conn)
            criar_indices(conn)
            inserir_categorias(conn)

            if reset:
                resetar_dados(conn)

            conn.commit()
            verificar(conn)

            print(f"\n{'='*50}")
            print("  ✅ Banco configurado com sucesso!")
            if reset:
                print("  🗑️  Dados de teste removidos.")
            print(f"{'='*50}\n")

    except SQLAlchemyError as e:
        print(f"\n❌ Erro no banco: {e}")
        print("Verifique se o PostgreSQL está rodando e a DATABASE_URL está correta no .env")
        sys.exit(1)


if __name__ == "__main__":
    main()
