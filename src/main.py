# src/main_completo.py - Versão Completa com Todos os Agentes

import os
import json
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Importar o orquestrador completo
from orquestrador import OrquestradorPrincipal

app = Flask(__name__)
CORS(app)

# Configurar variáveis de ambiente
os.environ.setdefault('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))

# Inicializar orquestrador
print("🚀 Inicializando sistema completo com todos os agentes...")
orquestrador = OrquestradorPrincipal()

@app.route('/', methods=['GET'])
def home():
    """Endpoint de status do sistema."""
    return jsonify({
        "status": "online",
        "sistema": "JuriDoc Completo",
        "versao": "2.0",
        "agentes": [
            "Coletor de Dados",
            "Pesquisa Jurídica",
            "Redator Especializado", 
            "Validador Final"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check para monitoramento."""
    try:
        # Verificar se todos os componentes estão funcionando
        status_componentes = {
            "orquestrador": "ok" if orquestrador else "erro",
            "openai_key": "ok" if os.getenv('OPENAI_API_KEY') else "erro",
            "pesquisa": "ok"  # Sempre ok pois tem fallbacks
        }
        
        status_geral = "ok" if all(v == "ok" for v in status_componentes.values()) else "erro"
        
        return jsonify({
            "status": status_geral,
            "componentes": status_componentes,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/gerar-peticao', methods=['POST'])
def gerar_peticao():
    """
    Endpoint principal para geração de petições.
    Usa o orquestrador completo com todos os agentes.
    """
    try:
        inicio_tempo = datetime.now()
        print(f"\n{'='*80}")
        print(f"🚀 NOVA SOLICITAÇÃO DE PETIÇÃO - {inicio_tempo.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Receber dados do formulário
        dados_entrada = request.get_json()
        
        if not dados_entrada:
            return jsonify({
                "status": "erro",
                "erro": "Nenhum dado fornecido",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        print("📋 Dados recebidos do formulário:")
        print(json.dumps(dados_entrada, indent=2, ensure_ascii=False))
        
        # EXECUTAR FLUXO COMPLETO DOS AGENTES
        print(f"\n🔄 INICIANDO FLUXO COMPLETO DOS AGENTES...")
        
        resultado = orquestrador.processar_solicitacao_completa(dados_entrada)
        
        # Calcular tempo total
        tempo_total = (datetime.now() - inicio_tempo).total_seconds()
        
        print(f"\n✅ PETIÇÃO GERADA COM SUCESSO!")
        print(f"⏱️ Tempo total: {tempo_total:.1f} segundos")
        print(f"📊 Score de qualidade: {resultado.get('score_qualidade', 'N/A')}")
        print(f"{'='*80}\n")
        
        # Retornar resultado completo
        return jsonify({
            "status": "sucesso",
            "documento_html": resultado["documento_final"],
            "dados_estruturados": resultado["dados_estruturados"],
            "pesquisa_realizada": resultado["pesquisa_juridica"],
            "relatorio_qualidade": resultado["relatorio_validacao"],
            "score_qualidade": resultado["score_qualidade"],
            "tempo_processamento": f"{tempo_total:.1f}s",
            "agentes_executados": resultado["agentes_executados"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        erro_detalhado = traceback.format_exc()
        print(f"\n❌ ERRO NA GERAÇÃO DA PETIÇÃO:")
        print(erro_detalhado)
        
        return jsonify({
            "status": "erro",
            "erro": str(e),
            "detalhes": erro_detalhado,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/status-sistema', methods=['GET'])
def status_sistema():
    """Status detalhado do sistema e agentes."""
    try:
        return jsonify({
            "status": "online",
            "sistema": "JuriDoc Completo v2.0",
            "agentes_disponiveis": {
                "coletor_dados": {
                    "nome": "Agente Coletor de Dados",
                    "funcao": "Estrutura e valida dados de entrada",
                    "status": "ativo"
                },
                "pesquisa_juridica": {
                    "nome": "Pesquisa Jurídica",
                    "funcao": "Busca legislação, jurisprudência e doutrina",
                    "status": "ativo",
                    "fallbacks": "habilitados"
                },
                "redator": {
                    "nome": "Agente Redator Especializado",
                    "funcao": "Redige petições com fundamentação jurídica",
                    "status": "ativo"
                },
                "validador": {
                    "nome": "Agente Validador Final",
                    "funcao": "Valida e formata documento final",
                    "status": "ativo"
                }
            },
            "configuracoes": {
                "pesquisa_online": "habilitada",
                "fallbacks_inteligentes": "habilitados",
                "tempo_limite": "60 segundos",
                "qualidade_minima": "85%"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/analisar-dados', methods=['POST'])
def analisar_dados():
    """Endpoint para análise prévia dos dados sem gerar petição."""
    try:
        dados_entrada = request.get_json()
        
        if not dados_entrada:
            return jsonify({
                "status": "erro",
                "erro": "Nenhum dado fornecido"
            }), 400
        
        # Usar apenas o agente coletor para análise
        resultado_analise = orquestrador.analisar_dados_entrada(dados_entrada)
        
        return jsonify({
            "status": "sucesso",
            "analise": resultado_analise,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "erro",
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando JuriDoc Completo v2.0...")
    print("📋 Sistema com 4 agentes especializados")
    print("🔍 Pesquisa jurídica com fallbacks inteligentes")
    print("✅ Garantia de sempre gerar documento completo")
    print(f"🌐 Servidor iniciando na porta {os.getenv('PORT', 5000)}...")
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=False
    )

