import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecotech")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")


if not DB_PASSWORD:
    print("Aviso: DB_PASSWORD não foi encontrado no .env")
    print(f"Procurando em: {env_path}")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cur = conn.cursor()
    
    
    cur.execute("DROP TABLE IF EXISTS plantas_perenual CASCADE;")
    conn.commit()
    
    print("Tabela deletada! Agora roda: python sync_plantas_perenual.py")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}") 