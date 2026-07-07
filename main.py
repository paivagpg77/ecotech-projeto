from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

ARQUIVO_CSV = "umidade.csv"

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÃO DO BANCO DE DADOS
# ═══════════════════════════════════════════════════════
DATABASE_URL = os.getenv("DATABASE_URL")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecotech")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def conectar_db():
    """Conecta ao banco de dados PostgreSQL (Render ou local)"""
    try:
        if DATABASE_URL:
            # Produção (Render) - usa a URL completa
            return psycopg2.connect(DATABASE_URL)
        else:
            # Local - usa variáveis separadas
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

# ═══════════════════════════════════════════════════════
# ROTAS DE PLANTAS
# ═══════════════════════════════════════════════════════

@app.route("/api/plantas/buscar", methods=["GET"])
def buscar_plantas():
    """Busca plantas pelo nome no banco de dados"""
    q = request.args.get('q', '').strip()
    
    if len(q) < 2:
        return jsonify({
            "erro": "Mínimo 2 caracteres",
            "plantas": []
        }), 400
    
    try:
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco", "plantas": []}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                id, perenual_id, nome_en, nome_pt, 
                agua_minima, agua_maxima, ciclo_vida,
                imagem_url
            FROM plantas_perenual
            WHERE LOWER(nome_pt) LIKE LOWER(%s) OR LOWER(nome_en) LIKE LOWER(%s)
            LIMIT 10
        """, (f"%{q}%", f"%{q}%"))
        
        plantas = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            "resultado": len(plantas),
            "plantas": [dict(p) for p in plantas]
        })
    
    except Exception as e:
        print(f"Erro ao buscar plantas: {e}")
        return jsonify({"erro": str(e), "plantas": []}), 500

@app.route("/api/plantas/lista", methods=["GET"])
def listar_plantas():
    """Lista todas as plantas com paginação"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    if limit > 100:
        limit = 100
    
    offset = (page - 1) * limit
    
    try:
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Contar total
        cur.execute("SELECT COUNT(*) as total FROM plantas_perenual WHERE nome_pt IS NOT NULL")
        total = cur.fetchone()['total']
        
        # Buscar plantas
        cur.execute("""
            SELECT 
                id, perenual_id, nome_en, nome_pt, 
                agua_minima, agua_maxima, ciclo_vida,
                imagem_url
            FROM plantas_perenual
            WHERE nome_pt IS NOT NULL
            ORDER BY nome_pt
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        plantas = cur.fetchall()
        cur.close()
        conn.close()
        
        total_pages = (total + limit - 1) // limit
        
        return jsonify({
            "pagina": page,
            "limite": limit,
            "total": total,
            "total_paginas": total_pages,
            "plantas": [dict(p) for p in plantas]
        })
    
    except Exception as e:
        print(f"Erro ao listar plantas: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/api/plantas/total", methods=["GET"])
def total_plantas():
    """Retorna total de plantas no banco"""
    try:
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM plantas_perenual WHERE nome_pt IS NOT NULL")
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return jsonify({"total": total})
    
    except Exception as e:
        print(f"Erro ao contar plantas: {e}")
        return jsonify({"erro": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# AUTENTICAÇÃO (Usuários)
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        senha = data.get('senha', '')
        email = data.get('email', '').strip()
        
        if not username or not senha:
            return jsonify({"erro": "Usuário e senha obrigatórios"}), 400
        
        if len(username) < 3:
            return jsonify({"erro": "Usuário deve ter pelo menos 3 caracteres"}), 400
        
        if len(senha) < 4:
            return jsonify({"erro": "Senha deve ter pelo menos 4 caracteres"}), 400
        
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
        cur = conn.cursor()
        
        # Verifica se usuário já existe
        cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"erro": "Usuário já existe"}), 409
        
        # Cria usuário
        cur.execute(
            "INSERT INTO usuarios (username, senha, email) VALUES (%s, %s, %s) RETURNING id",
            (username, senha, email)
        )
        usuario_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            "sucesso": True,
            "mensagem": "Usuário criado com sucesso",
            "usuario_id": usuario_id,
            "username": username
        }), 201
        
    except Exception as e:
        print(f"Erro ao registrar: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Faz login do usuário"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        senha = data.get('senha', '')
        
        if not username or not senha:
            return jsonify({"erro": "Usuário e senha obrigatórios"}), 400
        
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
        cur = conn.cursor()
        cur.execute("SELECT id, username, senha FROM usuarios WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row or row[2] != senha:
            return jsonify({"erro": "Usuário ou senha inválidos"}), 401
        
        return jsonify({
            "sucesso": True,
            "usuario_id": row[0],
            "username": row[1],
            "mensagem": "Login realizado com sucesso"
        }), 200
        
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route('/api/auth/usuario/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):
    """Retorna dados do usuário"""
    try:
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
        cur = conn.cursor()
        cur.execute("SELECT id, username, email FROM usuarios WHERE id = %s", (usuario_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        return jsonify({"id": row[0], "username": row[1], "email": row[2]}), 200
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# PLANTAS DO USUÁRIO
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/usuarios/<int:usuario_id>/plantas', methods=['GET'])
def listar_plantas_usuario(usuario_id):
    """Lista plantas do usuário"""
    try:
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
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
        
        return jsonify({"plantas": plantas, "total": len(plantas)}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/usuarios/<int:usuario_id>/plantas', methods=['POST'])
def criar_planta_usuario(usuario_id):
    """Cria nova planta para o usuário"""
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        especie = data.get('especie', '').strip()
        icone = data.get('icone', '🌱')
        umidade_min = data.get('umidade_minima', 40)
        umidade_max = data.get('umidade_maxima', 70)
        
        if not nome:
            return jsonify({"erro": "Nome da planta obrigatório"}), 400
        
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
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
        
        return jsonify({
            "sucesso": True,
            "planta": {"id": planta_id, "nome": nome},
            "mensagem": "Planta salva com sucesso"
        }), 201
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/usuarios/<int:usuario_id>/plantas/<int:planta_id>', methods=['PUT'])
def atualizar_planta_usuario_rota(usuario_id, planta_id):
    """Atualiza uma planta do usuário"""
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        especie = data.get('especie', '').strip()
        icone = data.get('icone', '🌱')
        umidade_min = data.get('umidade_minima', 40)
        umidade_max = data.get('umidade_maxima', 70)
        
        if not nome:
            return jsonify({"erro": "Nome da planta obrigatório"}), 400
        
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
        cur = conn.cursor()
        cur.execute("""
            UPDATE usuarios_plantas
            SET nome = %s, especie = %s, icone = %s, umidade_minima = %s, umidade_maxima = %s
            WHERE id = %s AND usuario_id = %s
        """, (nome, especie, icone, umidade_min, umidade_max, planta_id, usuario_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"sucesso": True, "mensagem": "Planta atualizada"}), 200
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/usuarios/<int:usuario_id>/plantas/<int:planta_id>', methods=['DELETE'])
def deletar_planta_usuario_rota(usuario_id, planta_id):
    """Deleta uma planta do usuário"""
    try:
        conn = conectar_db()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500
        
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM usuarios_plantas WHERE id = %s AND usuario_id = %s",
            (planta_id, usuario_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"sucesso": True, "mensagem": "Planta deletada"}), 200
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ═══════════════════════════════════════════════════════
# ROTAS ORIGINAIS (UMIDADE)
# ═══════════════════════════════════════════════════════

def garantir_csv():
    if not os.path.exists(ARQUIVO_CSV) or os.path.getsize(ARQUIVO_CSV) == 0:
        with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["data_hora", "umidade"])


@app.route("/receber", methods=["GET"])
def receber():
    garantir_csv()

    umidade = request.args.get("umidade")

    if umidade is None:
        return "Parametro 'umidade' nao informado", 400

    with open(ARQUIVO_CSV, "a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            umidade
        ])

    return "Dados salvos com sucesso", 200


@app.route("/dados", methods=["GET"])
def dados():
    garantir_csv()

    lista = []

    with open(ARQUIVO_CSV, "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            if "data_hora" in linha and "umidade" in linha:
                lista.append({
                    "data_hora": linha["data_hora"],
                    "umidade": linha["umidade"]
                })

    return jsonify(lista)


@app.route("/ultima", methods=["GET"])
def ultima():
    garantir_csv()

    lista = []
 
    with open(ARQUIVO_CSV, "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            if "data_hora" in linha and "umidade" in linha:
                lista.append({  
                    "data_hora": linha["data_hora"],
                    "umidade": linha["umidade"]
                })

    if len(lista) == 0:
        return jsonify({
            "erro": "sem dados"
        }), 404

    return jsonify(lista[-1])


if __name__ == "__main__":
    garantir_csv()
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)