# src/main_v2.py - Versão Completa com Todos os Agentes

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import traceback
from orquestrador import OrquestradorPrincipal

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Verificar se a API key do OpenAI está configurada
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("ERRO CRÍTICO: Variável de ambiente OPENAI_API_KEY não definida!")
    
    # Inicializar o orquestrador principal
    try:
        orquestrador = OrquestradorPrincipal(openai_api_key=OPENAI_API_KEY)
        print("✅ Orquestrador inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro na inicialização do orquestrador: {e}")
        raise
    
    @app.route("/")
    def index():
        return jsonify({
            "status": "ativo",
            "servico": "JuriDoc Completo",
            "versao": "2.0",
            "foco": "Petições Iniciais com Agentes Especializados",
            "agentes": [
                "AgenteColetorDados",
                "PesquisaJuridica",
                "AgenteRedator", 
                "AgenteValidador"
            ],
            "endpoints": [
                "/api/gerar-peticao",
                "/api/status",
                "/api/status-sistema",
                "/api/analisar-dados"
            ]
        })
    
    @app.route("/api/gerar-peticao", methods=['POST'])
    def gerar_peticao():
        """
        Endpoint principal para gerar petições iniciais usando todos os agentes.
        Recebe dados do n8n e retorna a petição completa em HTML.
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
            
            # Gerar a petição usando o orquestrador completo
            resultado = orquestrador.gerar_peticao_completa(dados_entrada)
            
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
        """Endpoint de status básico para verificar se o serviço está funcionando."""
        return jsonify({
            "status": "ativo", 
            "mensagem": "JuriDoc Completo funcionando.",
            "versao": "2.0",
            "foco": "Petições Iniciais",
            "agentes_ativos": 4
        }), 200
    
    @app.route("/api/status-sistema", methods=['GET'])
    def status_sistema():
        """Endpoint de status detalhado do sistema e agentes."""
        try:
            status_detalhado = orquestrador.obter_status_sistema()
            return jsonify(status_detalhado), 200
        except Exception as e:
            return jsonify({
                "status": "erro",
                "mensagem": f"Erro ao obter status do sistema: {str(e)}"
            }), 500
    
    @app.route("/api/analisar-dados", methods=['POST'])
    def analisar_dados():
        """
        Endpoint para analisar dados de entrada sem gerar a petição.
        Útil para validação prévia e estimativas.
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
            
            # Gerar relatório de análise
            relatorio = orquestrador.gerar_relatorio_uso(dados_entrada)
            
            return jsonify({
                "status": "sucesso",
                "relatorio": relatorio
            }), 200
            
        except Exception as e:
            print(f"❌ Erro na análise de dados: {e}")
            return jsonify({
                "status": "erro",
                "mensagem": f"Erro na análise: {str(e)}"
            }), 500
    
    @app.route("/api/tipos-documento", methods=['GET'])
    def tipos_documento():
        """Endpoint para listar tipos de documento suportados."""
        tipos = [
            {
                "id": "peticao_inicial",
                "nome": "Petição Inicial",
                "descricao": "Petição inicial para ações cíveis",
                "status": "ativo",
                "agentes_utilizados": [
                    "AgenteColetorDados",
                    "PesquisaJuridica",
                    "AgenteRedator",
                    "AgenteValidador"
                ]
            }
        ]
        return jsonify({
            "tipos_suportados": tipos,
            "total": len(tipos)
        }), 200
    
    @app.route("/api/health", methods=['GET'])
    def health_check():
        """Endpoint de health check para monitoramento."""
        try:
            # Teste básico dos componentes
            status_sistema = orquestrador.obter_status_sistema()
            
            if status_sistema.get("status_geral") == "operacional":
                return jsonify({
                    "status": "healthy",
                    "timestamp": status_sistema.get("timestamp"),
                    "agentes_ativos": status_sistema.get("agentes_ativos", 0)
                }), 200
            else:
                return jsonify({
                    "status": "unhealthy",
                    "detalhes": status_sistema
                }), 503
                
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "erro": str(e)
            }), 503
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

