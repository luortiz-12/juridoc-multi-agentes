# src/main.py - Versão Simplificada JuriDoc

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import traceback
from agente_peticao import AgentePeticao

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Verificar se a API key do OpenAI está configurada
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("ERRO CRÍTICO: Variável de ambiente OPENAI_API_KEY não definida!")
    
    # Inicializar o agente de petição
    agente_peticao = AgentePeticao(openai_api_key=OPENAI_API_KEY)
    
    @app.route("/")
    def index():
        return jsonify({
            "status": "ativo",
            "servico": "JuriDoc Simplificado",
            "versao": "2.0",
            "foco": "Petições Iniciais",
            "endpoints": [
                "/api/gerar-peticao",
                "/api/status"
            ]
        })
    
    @app.route("/api/gerar-peticao", methods=['POST'])
    def gerar_peticao():
        """
        Endpoint principal para gerar petições iniciais.
        Recebe dados do n8n e retorna a petição em HTML.
        """
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
            
            print(f"📥 Recebendo dados para petição: {json.dumps(dados_entrada, indent=2, ensure_ascii=False)}")
            
            # Gerar a petição usando o agente simplificado
            resultado = agente_peticao.gerar_peticao(dados_entrada)
            
            if resultado.get("status") == "sucesso":
                print("✅ Petição gerada com sucesso!")
                return jsonify(resultado), 200
            else:
                print(f"❌ Erro na geração: {resultado}")
                return jsonify(resultado), 500
                
        except Exception as e:
            print(f"❌ ERRO CRÍTICO NO ENDPOINT /gerar-peticao: {e}")
            traceback.print_exc()
            return jsonify({
                "status": "erro", 
                "mensagem": "Ocorreu um erro interno inesperado no servidor.",
                "detalhes": str(e)
            }), 500
    
    @app.route("/api/status", methods=['GET'])
    def status():
        """Endpoint de status para verificar se o serviço está funcionando."""
        return jsonify({
            "status": "ativo", 
            "mensagem": "JuriDoc Simplificado funcionando.",
            "versao": "2.0",
            "foco": "Petições Iniciais"
        }), 200
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

