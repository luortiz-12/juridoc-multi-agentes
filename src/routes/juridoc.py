from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import sys
import os

# Adicionar o diretório src ao path para importar os agentes
# Esta linha pode precisar ser ajustada se main_orchestrator.py não estiver diretamente no mesmo nível que juridoc.py
# (Se main_orchestrator.py está em src/ e juridoc.py está em src/routes/,
# o sys.path.insert pode precisar apontar para '../' ou ser ajustado na importação do orquestrador)
# Mas, para o exemplo, vamos considerar que 'main_orchestrator.py' está acessível.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../') # Ajuste para apontar para o diretório 'src' se 'main_orchestrator.py' estiver lá.


from main_orchestrator import Orquestrador

juridoc_bp = Blueprint('juridoc', __name__)

# ATENÇÃO: NUNCA EXPOR CHAVES DE API DIRETAMENTE NO CÓDIGO FONTE!
# Obtém a chave da variável de ambiente 'OPENAI_API_KEY'
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("ERRO: Variável de ambiente OPENAI_API_KEY não definida!")
    sys.exit(1) # Impede que a aplicação inicie sem a chave

orquestrador = Orquestrador(openai_api_key=OPENAI_API_KEY)

@juridoc_bp.route('/gerar-documento', methods=['POST'])
@cross_origin()
def gerar_documento():
    """
    Endpoint para gerar documentos jurídicos.
    Recebe dados JSON e retorna o documento HTML gerado.
    """
    try:
        # Obter dados JSON da requisição
        dados_entrada = request.get_json()

        if not dados_entrada:
            return jsonify({
                "status": "erro",
                "mensagem": "Nenhum dado foi fornecido na requisição."
            }), 400

        # Gerar o documento usando o orquestrador
        resultado = orquestrador.gerar_documento(dados_entrada)

        if resultado["status"] == "sucesso":
            return jsonify({
                "status": "sucesso",
                "documento_html": resultado["documento_html"],
                "mensagem": "Documento gerado com sucesso."
            }), 200
        else:
            return jsonify({
                "status": "erro",
                "mensagem": resultado["mensagem"],
                "detalhes": resultado.get("detalhes", "")
            }), 500

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": "Erro interno do servidor.",
            "detalhes": str(e)
        }), 500

@juridoc_bp.route('/status', methods=['GET'])
@cross_origin()
def status():
    """
    Endpoint para verificar se o serviço está funcionando.
    """
    return jsonify({
        "status": "ativo",
        "mensagem": "Serviço JuriDoc Multi-Agentes está funcionando.",
        "versao": "1.0.0"
    }), 200

@juridoc_bp.route('/tipos-documento', methods=['GET'])
@cross_origin()
def tipos_documento():
    """
    Endpoint para listar os tipos de documento suportados.
    """
    return jsonify({
        "tipos_suportados": [
            {
                "tipo": "peticao",
                "descricao": "Petição inicial para ações judiciais",
                "campos_obrigatorios": [
                    "contratante", "contratado", "historico_peticao",
                    "fatos_peticao", "pedido_peticao", "valor_causa_peticao"
                ]
            },
            {
                "tipo": "contrato",
                "descricao": "Contratos diversos (prestação de serviços, etc.)",
                "campos_obrigatorios": [
                    "contratante", "contratado", "objeto", "valor",
                    "tipoContrato"
                ]
            }
        ]
    }), 200