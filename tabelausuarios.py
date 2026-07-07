import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecotech")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def conectar_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def criar_tabelas():
    """Cria as tabelas de usuários e plantas do usuário"""
    conn = conectar_db()
    cur = conn.cursor()
    
    try:
        # DROPAR TABELAS ANTIGAS (se existirem com UUID)
        print("🗑️  Removendo tabelas antigas...")
        cur.execute("DROP TABLE IF EXISTS usuarios_plantas CASCADE")
        cur.execute("DROP TABLE IF EXISTS usuarios CASCADE")
        print("✓ Tabelas antigas removidas")
        
        # Tabela de usuários (SERIAL = INTEGER auto-increment)
        cur.execute("""
            CREATE TABLE usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Tabela 'usuarios' criada")
        
        # Tabela de plantas do usuário (usuario_id referencia id INTEGER)
        cur.execute("""
            CREATE TABLE usuarios_plantas (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                nome VARCHAR(100) NOT NULL,
                especie VARCHAR(100),
                icone VARCHAR(10),
                umidade_minima INTEGER,
                umidade_maxima INTEGER,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Tabela 'usuarios_plantas' criada")
        
        conn.commit()
        print("\n✅ Tabelas criadas com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        conn.rollback()
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("\n🔧 CRIANDO TABELAS DE USUÁRIOS\n")
    criar_tabelas()