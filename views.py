from flask import Blueprint, request, jsonify
from utils import (
    get_all, get_by_id, add, update, delete,
    filter_by_tipo, filter_by_cidade
)

imoveis_bp = Blueprint("imoveis", __name__)

@imoveis_bp.get("/imoveis")
def listar_imoveis():
    tipo = request.args.get("tipo")
    cidade = request.args.get("cidade")

    data = get_all()
    if tipo:
        data = [i for i in data if i.get("tipo", "").lower() == tipo.lower()]
    if cidade:
        data = [i for i in data if i.get("cidade", "").lower() == cidade.lower()]

    return jsonify(data), 200

@imoveis_bp.get("/imoveis/<int:imovel_id>")
def obter_imovel(imovel_id: int):
    imovel = get_by_id(imovel_id)
    if not imovel:
        return jsonify({"error": "Imóvel não encontrado"}), 404
    return jsonify(imovel), 200

@imoveis_bp.post("/imoveis")
def criar_imovel():
    if not request.is_json:
        return jsonify({"error": "Corpo deve ser JSON"}), 400

    payload = request.get_json()

    obrigatorios = ["logradouro", "cidade"]
    faltando = [c for c in obrigatorios if c not in payload or payload[c] in (None, "")]
    if faltando:
        return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(faltando)}"}), 400

    novo = add(payload)
    return jsonify(novo), 201

@imoveis_bp.put("/imoveis/<int:imovel_id>")
def atualizar_imovel(imovel_id: int):
    if not request.is_json:
        return jsonify({"error": "Corpo deve ser JSON"}), 400

    payload = request.get_json()
    imovel = update(imovel_id, payload)
    if not imovel:
        return jsonify({"error": "Imóvel não encontrado"}), 404
    return jsonify(imovel), 200

@imoveis_bp.delete("/imoveis/<int:imovel_id>")
def remover_imovel(imovel_id: int):
    ok = delete(imovel_id)
    if not ok:
        return jsonify({"error": "Imóvel não encontrado"}), 404
    return jsonify({"message": "Imóvel removido com sucesso"}), 200

@imoveis_bp.get("/imoveis/tipo/<string:tipo>")
def listar_por_tipo(tipo: str):
   #tipo = request.args.get("tipo")
    if filter_by_tipo(tipo):
        return jsonify(filter_by_tipo(tipo)), 200
    return jsonify({"error": "Tipo não encontrado"}), 404

@imoveis_bp.get("/imoveis/cidade/<string:cidade>")
def listar_por_cidade(cidade: str):
    if filter_by_cidade(cidade):
        return jsonify(filter_by_cidade(cidade)), 200
    return jsonify({"error": "Cidade não encontrada"}), 404

