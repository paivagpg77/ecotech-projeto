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
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecotech")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def conectar_db():
    """Conecta ao banco de dados PostgreSQL"""
    try:
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
    app.run(host="0.0.0.0", port=5000, debug=True)