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
    """Conecta ao banco de dados PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def buscar_plantas_por_nome(nome, idioma='pt'):
    """Busca plantas pelo nome"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        query = "SELECT id, perenual_id, nome_en, nome_pt, agua_minima, agua_maxima FROM plantas_perenual WHERE LOWER(nome_pt) LIKE LOWER(%s) OR LOWER(nome_en) LIKE LOWER(%s) LIMIT 20"
        cur.execute(query, (f'%{nome}%', f'%{nome}%'))
        
        colunas = [desc[0] for desc in cur.description]
        plantas = [dict(zip(colunas, row)) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return plantas
    except Exception as e:
        print(f"Erro ao buscar plantas: {e}")
        return []

def buscar_planta_por_id(planta_id):
    """Busca planta específica pelo ID"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute("SELECT id, perenual_id, nome_en, nome_pt, agua_minima, agua_maxima FROM plantas_perenual WHERE id = %s", (planta_id,))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not row:
            return None
        
        colunas = [desc[0] for desc in cur.description]
        return dict(zip(colunas, row))
    except Exception as e:
        print(f"Erro ao buscar planta: {e}")
        return None

def contar_plantas():
    """Conta total de plantas"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM plantas_perenual")
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        return total
    except Exception as e:
        print(f"Erro ao contar plantas: {e}")
        return 0

def buscar_plantas(idioma='pt', limite=20, offset=0):
    """Lista plantas com paginação"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT id, perenual_id, nome_en, nome_pt, agua_minima, agua_maxima FROM plantas_perenual ORDER BY nome_pt ASC LIMIT %s OFFSET %s",
            (limite, offset)
        )
        
        colunas = [desc[0] for desc in cur.description]
        plantas = [dict(zip(colunas, row)) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return plantas
    except Exception as e:
        print(f"Erro ao listar plantas: {e}")
        return []


# ═════════════════════════════════════════════════════════════════════════════
# USUÁRIOS
# ═════════════════════════════════════════════════════════════════════════════

def criar_usuario(username, senha, email=''):
    """Cria um novo usuário"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO usuarios (username, senha, email) VALUES (%s, %s, %s) RETURNING id",
            (username, senha, email)
        )
        usuario_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"id": usuario_id, "username": username}
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return None

def buscar_usuario(username):
    """Busca usuário por username"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute("SELECT id, username, senha FROM usuarios WHERE username = %s", (username,))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not row:
            return None
        
        return {"id": row[0], "username": row[1], "senha": row[2]}
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def buscar_usuario_por_id(usuario_id):
    """Busca usuário por ID"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute("SELECT id, username, email FROM usuarios WHERE id = %s", (usuario_id,))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not row:
            return None
        
        return {"id": row[0], "username": row[1], "email": row[2]}
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None


# ═════════════════════════════════════════════════════════════════════════════
# PLANTAS DO USUÁRIO
# ═════════════════════════════════════════════════════════════════════════════

def salvar_planta_usuario(usuario_id, nome, especie, icone, umidade_min, umidade_max):
    """Salva planta do usuário no PostgreSQL"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO usuarios_plantas (usuario_id, nome, especie, icone, umidade_minima, umidade_maxima)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (usuario_id, nome, especie, icone, umidade_min, umidade_max))
        
        planta_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return {"id": planta_id, "nome": nome}
    except Exception as e:
        print(f"Erro ao salvar planta: {e}")
        return None

def buscar_plantas_usuario(usuario_id):
    """Busca todas as plantas do usuário"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, nome, especie, icone, umidade_minima, umidade_maxima
            FROM usuarios_plantas
            WHERE usuario_id = %s
            ORDER BY criado_em DESC
        """, (usuario_id,))
        
        colunas = [desc[0] for desc in cur.description]
        plantas = [dict(zip(colunas, row)) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return plantas
    except Exception as e:
        print(f"Erro ao buscar plantas do usuário: {e}")
        return []

def deletar_planta_usuario(usuario_id, planta_id):
    """Deleta uma planta do usuário"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute(
            "DELETE FROM usuarios_plantas WHERE id = %s AND usuario_id = %s",
            (planta_id, usuario_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Erro ao deletar planta: {e}")
        return False

def atualizar_planta_usuario(usuario_id, planta_id, nome, especie, icone, umidade_min, umidade_max):
    """Atualiza uma planta do usuário"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE usuarios_plantas
            SET nome = %s, especie = %s, icone = %s, umidade_minima = %s, umidade_maxima = %s
            WHERE id = %s AND usuario_id = %s
        """, (nome, especie, icone, umidade_min, umidade_max, planta_id, usuario_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar planta: {e}")
        return False