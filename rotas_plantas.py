from flask import Blueprint, jsonify, request
from db import buscar_plantas_por_nome, buscar_planta_por_id, contar_plantas, buscar_plantas

plantas_bp = Blueprint('plantas', __name__, url_prefix='/api/plantas')

@plantas_bp.route('/buscar', methods=['GET'])
def buscar():
    """
    Busca plantas pelo nome
    Query: ?q=tomato
    """
    q = request.args.get('q', '').strip()
    
    if len(q) < 2:
        return jsonify({
            "erro": "Mínimo 2 caracteres",
            "plantas": []
        }), 400
    
    plantas = buscar_plantas_por_nome(q, idioma='pt')
    
    return jsonify({
        "resultado": len(plantas),
        "plantas": plantas
    })

@plantas_bp.route('/id/<int:planta_id>', methods=['GET'])
def obter_por_id(planta_id):
    """
    Busca planta específica pelo ID   
    """
    planta = buscar_planta_por_id(planta_id) 
    
    if not planta:
        return jsonify({"erro": "Planta não encontrada"}), 404
    
    return jsonify(planta)

@plantas_bp.route('/lista', methods=['GET'])
def listar(): 
    """
    Lista todas as plantas com paginação
    Query: ?page=1&limit=20
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # Limitar a 100 por página
    if limit > 100:
        limit = 100
    
    offset = (page - 1) * limit
    plantas = buscar_plantas(idioma='pt', limite=limit, offset=offset)
    total = contar_plantas()
    total_pages = (total + limit - 1) // limit
    
    return jsonify({
        "pagina": page,
        "limite": limit,
        "total": total,
        "total_paginas": total_pages,
        "plantas": plantas
    })

@plantas_bp.route('/total', methods=['GET'])
def total():
    """
    Retorna total de plantas no banco
    """
    total_plantas = contar_plantas()
    return jsonify({
        "total": total_plantas
    })