from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import io
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ─── CONEXÃO POSTGRESQL ───────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     "5432",
    "dbname":   "ecotech",
    "user":     "postgres",
    "password": "ga454750!",
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)


# ─── LEITURA DE DADOS ─────────────────────────────────────────────────────────
def ler_todos(sensor_id=None, limit=None):
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query  = "SELECT id, sensor_id, planta_id, umidade, data_hora FROM leituras"
    params = []

    if sensor_id:
        query += " WHERE sensor_id = %s"
        params.append(sensor_id)

    query += " ORDER BY data_hora DESC"

    if limit:
        query += " LIMIT %s"
        params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id":        str(r["id"]),
            "sensor_id": str(r["sensor_id"]),
            "planta_id": str(r["planta_id"]) if r["planta_id"] else None,
            "umidade":   float(r["umidade"]),
            "data_hora": r["data_hora"].strftime("%Y-%m-%d %H:%M:%S"),
        }
        for r in rows
    ]


# ─── RECEBER LEITURA DO ESP32 ─────────────────────────────────────────────────
@app.route("/receber", methods=["GET"])
def receber():
    umidade   = request.args.get("umidade")
    sensor_id = request.args.get("sensor_id")
    planta_id = request.args.get("planta_id")

    if umidade is None:
        return jsonify({"erro": "Parâmetro 'umidade' não informado"}), 400
    if sensor_id is None:
        return jsonify({"erro": "Parâmetro 'sensor_id' não informado"}), 400

    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute(
            """
            INSERT INTO leituras (sensor_id, planta_id, umidade, data_hora)
            VALUES (%s, %s, %s, NOW())
            """,
            (sensor_id, planta_id or None, float(umidade))
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True, "mensagem": "Dados salvos com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ─── ROTA POST ────────────────────────────────────────────────────────────────
@app.route("/leitura", methods=["POST"])
def salvar_leitura():
    dados = request.get_json()
    if not dados or "sensor_id" not in dados or "umidade" not in dados:
        return jsonify({"erro": "Informe 'sensor_id' e 'umidade' no body"}), 400

    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute(
            """
            INSERT INTO leituras (sensor_id, planta_id, umidade, data_hora)
            VALUES (%s, %s, %s, NOW())
            """,
            (dados["sensor_id"], dados.get("planta_id"), float(dados["umidade"]))
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ─── LISTAR DADOS ─────────────────────────────────────────────────────────────
@app.route("/dados", methods=["GET"])
def dados():
    sensor_id = request.args.get("sensor_id")
    limit     = request.args.get("limit", 100, type=int)
    return jsonify(ler_todos(sensor_id=sensor_id, limit=limit))


# ─── ÚLTIMA LEITURA ───────────────────────────────────────────────────────────
@app.route("/ultima", methods=["GET"])
def ultima():
    sensor_id = request.args.get("sensor_id")
    lista = ler_todos(sensor_id=sensor_id, limit=1)
    if not lista:
        return jsonify({"erro": "Sem dados"}), 404
    return jsonify(lista[0])


# ─── SENSORES ─────────────────────────────────────────────────────────────────
@app.route("/sensores", methods=["GET"])
def listar_sensores():
    try:
        conn = get_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM sensores ORDER BY criado_em DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/sensores", methods=["POST"])
def criar_sensor():
    dados = request.get_json()
    if not dados or "usuario_id" not in dados or "nome" not in dados:
        return jsonify({"erro": "Informe 'usuario_id' e 'nome'"}), 400

    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute(
            """
            INSERT INTO sensores (usuario_id, nome, mac_address, local, ativo, criado_em)
            VALUES (%s, %s, %s, %s, TRUE, NOW())
            RETURNING id
            """,
            (dados["usuario_id"], dados["nome"],
             dados.get("mac_address"), dados.get("local"))
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True, "id": str(new_id)}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ─── EXPORTAR PDF ─────────────────────────────────────────────────────────────
@app.route("/exportar/pdf", methods=["GET"])
def exportar_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        return jsonify({"erro": "Execute: pip install reportlab"}), 500

    sensor_id = request.args.get("sensor_id")
    lista     = ler_todos(sensor_id=sensor_id)
    buffer    = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm,   bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    story  = []

    titulo_style = ParagraphStyle("Titulo", parent=styles["Title"],
                                  fontSize=18, textColor=colors.HexColor("#1a2540"), spaceAfter=6)
    sub_style    = ParagraphStyle("Sub", parent=styles["Normal"],
                                  fontSize=9, textColor=colors.HexColor("#8a9bb3"), spaceAfter=16)

    story.append(Paragraph("EcoTech — Relatório de Umidade", titulo_style))
    story.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  |  Total: {len(lista)} registros",
        sub_style))
    story.append(Spacer(1, 0.4*cm))

    if not lista:
        story.append(Paragraph("Nenhum dado registrado.", styles["Normal"]))
    else:
        tabela_dados = [["#", "Data / Hora", "Sensor ID", "Umidade (%)"]]
        for i, row in enumerate(lista, 1):
            tabela_dados.append([
                str(i), row["data_hora"],
                str(row["sensor_id"])[:8] + "...",
                f'{row["umidade"]}%'
            ])

        tabela = Table(tabela_dados, colWidths=[1*cm, 6*cm, 5*cm, 3*cm], repeatRows=1)
        tabela.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1a2540")),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,0), 10),
            ("ALIGN",         (0,0), (-1,0), "CENTER"),
            ("BOTTOMPADDING", (0,0), (-1,0), 8),
            ("TOPPADDING",    (0,0), (-1,0), 8),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,1), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#f0f4ff")]),
            ("TEXTCOLOR",     (3,1), (3,-1), colors.HexColor("#16a34a")),
            ("FONTNAME",      (3,1), (3,-1), "Helvetica-Bold"),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#d1d9e6")),
            ("LINEBELOW",     (0,0), (-1,0),  1.5, colors.HexColor("#4ade80")),
            ("TOPPADDING",    (0,1), (-1,-1), 5),
            ("BOTTOMPADDING", (0,1), (-1,-1), 5),
        ]))
        story.append(tabela)

    doc.build(story)
    buffer.seek(0)

    nome = f"umidade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=nome, mimetype="application/pdf")


# ─── EXPORTAR CSV ─────────────────────────────────────────────────────────────
@app.route("/exportar/csv", methods=["GET"])
def exportar_csv():
    import csv as csv_mod
    sensor_id = request.args.get("sensor_id")
    lista     = ler_todos(sensor_id=sensor_id)

    output = io.StringIO()
    writer = csv_mod.writer(output)
    writer.writerow(["Data / Hora", "Sensor ID", "Planta ID", "Umidade (%)"])
    for row in lista:
        writer.writerow([row["data_hora"], row["sensor_id"], row["planta_id"], row["umidade"]])

    output.seek(0)
    nome = f"umidade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        as_attachment=True, download_name=nome, mimetype="text/csv; charset=utf-8"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)