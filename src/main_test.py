# src/main_test.py - Versão de teste sem API key obrigatória

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

def create_test_app():
    app = Flask(__name__)
    CORS(app)
    
    @app.route("/")
    def index():
        return jsonify({
            "status": "ativo",
            "servico": "JuriDoc Simplificado - MODO TESTE",
            "versao": "2.0",
            "foco": "Petições Iniciais",
            "endpoints": [
                "/api/gerar-peticao",
                "/api/status"
            ]
        })
    
    @app.route("/api/gerar-peticao", methods=['POST'])
    def gerar_peticao():
        """Endpoint de teste para gerar petições."""
        try:
            if not request.is_json:
                return jsonify({
                    "status": "erro", 
                    "mensagem": "A requisição deve conter um corpo JSON."
                }), 400
            
            dados_entrada = request.get_json()
            if not dados_entrada:
                return jsonify({
                    "status": "erro", 
                    "mensagem": "Nenhum dado foi fornecido no corpo da requisição."
                }), 400
            
            # Simular resposta de sucesso para teste
            resultado = {
                "status": "sucesso",
                "documento_html": "<h1>PETIÇÃO INICIAL - MODO TESTE</h1><p>Esta é uma petição de teste gerada com os dados fornecidos.</p>",
                "dados_estruturados": dados_entrada,
                "pesquisa_realizada": "Pesquisa simulada para teste",
                "timestamp": "2025-07-02 10:30:00",
                "modo": "TESTE"
            }
            
            return jsonify(resultado), 200
                
        except Exception as e:
            return jsonify({
                "status": "erro", 
                "mensagem": "Erro no modo de teste",
                "detalhes": str(e)
            }), 500
    
    @app.route("/api/status", methods=['GET'])
    def status():
        """Endpoint de status para teste."""
        return jsonify({
            "status": "ativo", 
            "mensagem": "JuriDoc Simplificado funcionando em modo teste.",
            "versao": "2.0",
            "foco": "Petições Iniciais",
            "modo": "TESTE"
        }), 200
    
    return app

app = create_test_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

