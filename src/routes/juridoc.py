# src/routes/juridoc.py

import os
import sys
from flask import Blueprint, request, jsonify

# --- ALTERAÇÃO 1: Importação Relativa ---
# Os '..' indicam para 'subir um nível' de diretório (da pasta 'routes' para a pasta 'src')
# para encontrar o módulo do orquestrador. É a forma correta e robusta.
from ..main_orchestrator import Orquestrador

# --- REMOVIDO ---
# A linha abaixo não é mais necessária, pois o import relativo resolve o problema de forma mais limpa.
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')


# --- ALTERAÇÃO 2: Correção do Blueprint ---
# Adicionado o 'url_prefix' para garantir que as rotas fiquem sob /api/juridoc
# e o nome interno do blueprint foi alinhado com o nome da variável.
juridoc_bp = Blueprint('juridoc_bp', __name__, url_prefix='/api/juridoc')


# Obtém a chave da API a partir das variáveis de ambiente uma vez.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    # Lança um erro se a chave não for encontrada, impedindo a inicialização.
    raise ValueError("ERRO CRÍTICO: Variável de ambiente OPENAI_API_KEY não definida!")

# Instancia o orquestrador uma vez para ser reutilizado em todas as requisições.
orquestrador = Orquestrador(openai_api_key=OPENAI_API_KEY)


@juridoc_bp.route('/gerar-documento', methods=['POST'])
def gerar_documento():
    """
    Endpoint principal para gerar documentos jurídicos.
    Recebe dados JSON e retorna o documento HTML gerado.
    """
    if not request.is_json:
        return jsonify({"status": "erro", "mensagem": "A requisição deve conter um corpo JSON."}), 400

    dados_entrada = request.get_json()
    if not dados_entrada:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado foi fornecido no corpo da requisição."}), 400

    try:
        # A lógica de chamada ao orquestrador permanece a mesma.
        resultado = orquestrador.gerar_documento(dados_entrada)
        
        # A lógica de tratamento de resposta também está correta.
        if resultado.get("status") == "sucesso":
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500

    except Exception as e:
        # Um bloco de captura de erro genérico para segurança.
        print(f"ERRO CRÍTICO NO ENDPOINT /gerar-documento: {e}")
        return jsonify({"status": "erro", "mensagem": "Ocorreu um erro interno inesperado no servidor."}), 500


@juridoc_bp.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar se o serviço está funcionando."""
    return jsonify({
        "status": "ativo",
        "mensagem": "Serviço JuriDoc Multi-Agentes (Arquitetura Especialista) está funcionando."
    }), 200


@juridoc_bp.route('/tipos-documento', methods=['GET'])
def tipos_documento():
    """Endpoint para listar os tipos de documento suportados pela nova arquitetura."""
    
    # --- ALTERAÇÃO 3: Atualização dos tipos suportados ---
    tipos = [
        {"id": "contrato", "nome": "Contrato"},
        {"id": "peticao", "nome": "Petição Inicial"},
        {"id": "parecer", "nome": "Parecer Jurídico"},
        {"id": "estudo_de_caso", "nome": "Estudo de Caso"}
    ]
    
    return jsonify({"tipos_suportados": tipos}), 200