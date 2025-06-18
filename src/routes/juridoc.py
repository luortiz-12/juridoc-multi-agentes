# src/routes/juridoc.py

import os
import sys
from flask import Blueprint, request, jsonify

# --- ALTERAÇÃO: Usando import absoluto a partir de 'src' ---
from src.main_orchestrator import Orquestrador

juridoc_bp = Blueprint('juridoc_bp', __name__, url_prefix='/api/juridoc')

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("ERRO CRÍTICO: Variável de ambiente OPENAI_API_KEY não definida!")

orquestrador = Orquestrador(openai_api_key=OPENAI_API_KEY)

@juridoc_bp.route('/gerar-documento', methods=['POST'])
def gerar_documento():
    if not request.is_json:
        return jsonify({"status": "erro", "mensagem": "A requisição deve conter um corpo JSON."}), 400

    dados_entrada = request.get_json()
    if not dados_entrada:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado foi fornecido no corpo da requisição."}), 400

    try:
        resultado = orquestrador.gerar_documento(dados_entrada)
        if resultado.get("status") == "sucesso":
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
    except Exception as e:
        print(f"ERRO CRÍTICO NO ENDPOINT /gerar-documento: {e}")
        return jsonify({"status": "erro", "mensagem": "Ocorreu um erro interno inesperado no servidor."}), 500

# (O resto das suas rotas /status e /tipos-documento permanecem iguais)
@juridoc_bp.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ativo", "mensagem": "Serviço JuriDoc funcionando."}), 200

@juridoc_bp.route('/tipos-documento', methods=['GET'])
def tipos_documento():
    tipos = [
        {"id": "contrato", "nome": "Contrato"},
        {"id": "peticao", "nome": "Petição Inicial"},
        {"id": "parecer", "nome": "Parecer Jurídico"},
        {"id": "estudo_de_caso", "nome": "Estudo de Caso"}
    ]
    return jsonify({"tipos_suportados": tipos}), 200