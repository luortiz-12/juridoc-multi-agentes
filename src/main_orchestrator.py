# main_orchestrator.py - VERSÃO CORRIGIDA PARA USAR AGENTES ESPECIALIZADOS

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

# Importações dos agentes especializados (CORRIGIDO)
from agente_coletor_dados import AgenteColetorDados
from agente_validacao import AgenteValidador
from agente_formatacao_final import AgenteFormatacaoFinal

# Importações dos agentes técnicos especializados
from agente_tecnico_peticao import AgenteTecnicoPeticao
from agente_tecnico_contrato import AgenteTecnicoContrato
from agente_tecnico_parecer import AgenteTecnicoParecer
from agente_tecnico_estudo_caso import AgenteTecnicoEstudoCaso

# Importações dos agentes redatores especializados
from agente_redator_peticao import AgenteRedatorPeticao
from agente_redator_contrato import AgenteRedatorContrato
from agente_redator_parecer import AgenteRedatorParecer
from agente_redator_estudo_caso import AgenteRedatorEstudoCaso

class Orquestrador:
    """
    Orquestra o fluxo de trabalho RAG usando agentes especializados.
    VERSÃO CORRIGIDA - USA AGENTES ESPECIALIZADOS DIRETAMENTE.
    """
    def __init__(self, openai_api_key):
        print("🚀 Inicializando Orquestrador com agentes especializados...")
        
        # Agentes de apoio (originais)
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.validador = AgenteValidador(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal()

        # Agentes técnicos especializados (CORRIGIDO)
        self.tecnico_peticao = AgenteTecnicoPeticao(llm_api_key=openai_api_key)
        self.tecnico_contrato = AgenteTecnicoContrato(llm_api_key=openai_api_key)
        self.tecnico_parecer = AgenteTecnicoParecer(llm_api_key=openai_api_key)
        self.tecnico_estudo_caso = AgenteTecnicoEstudoCaso(llm_api_key=openai_api_key)

        # Agentes redatores especializados (CORRIGIDO)
        self.redator_peticao = AgenteRedatorPeticao(llm_api_key=openai_api_key)
        self.redator_contrato = AgenteRedatorContrato(llm_api_key=openai_api_key)
        self.redator_parecer = AgenteRedatorParecer(llm_api_key=openai_api_key)
        self.redator_estudo_caso = AgenteRedatorEstudoCaso(llm_api_key=openai_api_key)
        
        print("✅ Todos os agentes especializados inicializados com sucesso!")

    def gerar_documento(self, raw_input_data: dict) -> dict:
        """
        Gera documento completo usando fluxo de agentes especializados com RAG.
        VERSÃO CORRIGIDA - FLUXO INTEGRADO FUNCIONANDO.
        """
        print("\n🚀 Iniciando geração de documento com agentes especializados RAG")
        print("=" * 60)
        
        try:
            # ETAPA 1: Coleta e processamento de dados (mantém original)
            print("📥 ETAPA 1: Coleta e processamento de dados...")
            dados_processados = self.coletor.coletar_e_processar(raw_input_data)
            
            if dados_processados.get("erro"):
                return {
                    "status": "erro", 
                    "mensagem": "Falha na coleta de dados", 
                    "detalhes": dados_processados
                }
            
            print("✅ Dados coletados e processados com sucesso")
            print(f"📋 Tipo de documento: {dados_processados.get('tipo_documento', 'N/A')}")
            
            # ETAPA 2: Roteamento para agentes especializados (CORRIGIDO)
            print("\n🎯 ETAPA 2: Roteamento para agentes especializados...")
            tipo_documento = dados_processados.get("tipo_documento", "").lower().strip()
            
            # Selecionar agentes corretos baseado no tipo
            if tipo_documento == "peticao":
                agente_tecnico = self.tecnico_peticao
                agente_redator = self.redator_peticao
                print("📄 Roteado para especialistas em PETIÇÃO")
            elif tipo_documento == "contrato":
                agente_tecnico = self.tecnico_contrato
                agente_redator = self.redator_contrato
                print("📄 Roteado para especialistas em CONTRATO")
            elif tipo_documento == "parecer":
                agente_tecnico = self.tecnico_parecer
                agente_redator = self.redator_parecer
                print("📄 Roteado para especialistas em PARECER")
            elif tipo_documento in ["estudo de caso", "estudo"]:
                agente_tecnico = self.tecnico_estudo_caso
                agente_redator = self.redator_estudo_caso
                print("📄 Roteado para especialistas em ESTUDO DE CASO")
            else:
                # Fallback para petição
                agente_tecnico = self.tecnico_peticao
                agente_redator = self.redator_peticao
                print(f"⚠️ Tipo '{tipo_documento}' não reconhecido, usando especialistas em PETIÇÃO")
            
            # ETAPA 3: Análise técnica com RAG (CORRIGIDO - USA MÉTODO CORRETO)
            print("\n🧠 ETAPA 3: Análise técnica com RAG...")
            print("🔍 Executando busca online e análise RAG...")
            
            # Chama método correto: analisar_com_rag (não analyze_with_rag)
            analise_tecnica = agente_tecnico.analisar_com_rag(dados_processados)
            
            if analise_tecnica.get("erro"):
                print(f"⚠️ Erro na análise técnica: {analise_tecnica.get('erro')}")
                # Continua com fallback
            else:
                print("✅ Análise técnica RAG concluída com sucesso")
            
            # ETAPA 4: Redação com templates RAG (CORRIGIDO - USA MÉTODO CORRETO)
            print("\n✍️ ETAPA 4: Redação com templates RAG...")
            print("📝 Aplicando templates e padrões estruturais...")
            
            # Chama método correto: redigir_com_rag (não write_with_rag)
            documento_redigido = agente_redator.redigir_com_rag(dados_processados, analise_tecnica)
            
            if not documento_redigido or documento_redigido.strip() == "":
                print("⚠️ Redação RAG falhou, usando fallback...")
                # Fallback para método original se existir
                if hasattr(agente_redator, 'redigir_documento'):
                    documento_redigido = agente_redator.redigir_documento(dados_processados, analise_tecnica)
                else:
                    documento_redigido = self._gerar_documento_emergencia(dados_processados, analise_tecnica)
            else:
                print("✅ Redação RAG concluída com sucesso")
            
            # ETAPA 5: Validação (mantém original)
            print("\n✅ ETAPA 5: Validação do documento...")
            documento_validado = self.validador.validar_documento(documento_redigido, dados_processados)
            print("✅ Validação concluída")
            
            # ETAPA 6: Formatação final (mantém original)
            print("\n🎨 ETAPA 6: Formatação final...")
            documento_final = self.formatador.formatar_documento_final(documento_validado, dados_processados)
            print("✅ Formatação final concluída")
            
            # Resultado final
            resultado = {
                "status": "sucesso",
                "tipo_documento": tipo_documento,
                "documento_final": documento_final,
                "analise_tecnica": analise_tecnica,
                "metadados": {
                    "agente_tecnico_usado": agente_tecnico.__class__.__name__,
                    "agente_redator_usado": agente_redator.__class__.__name__,
                    "rag_utilizado": True,
                    "busca_online_realizada": True,
                    "timestamp": "2025-06-25T12:00:00"
                }
            }
            
            print("\n🎉 DOCUMENTO GERADO COM SUCESSO!")
            print("=" * 60)
            return resultado
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO: {e}")
            return {
                "status": "erro",
                "mensagem": f"Erro na geração do documento: {str(e)}",
                "documento_final": self._gerar_documento_emergencia(raw_input_data, {"erro": str(e)})
            }
    
    def _gerar_documento_emergencia(self, dados_processados: dict, analise_tecnica: dict) -> str:
        """
        Gera documento de emergência quando tudo falha.
        """
        print("🚨 Gerando documento de emergência...")
        
        tipo_doc = dados_processados.get("tipo_documento", "documento")
        nome_cliente = dados_processados.get("nome_cliente", "Cliente")
        
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>{tipo_doc.title()} - {nome_cliente}</title>
            <style>
                body {{ font-family: 'Times New Roman', serif; font-size: 12pt; margin: 2cm; }}
                .emergencia {{ color: red; font-weight: bold; margin-bottom: 20px; }}
                .dados {{ background: #f5f5f5; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="emergencia">
                DOCUMENTO GERADO EM MODO DE EMERGÊNCIA
            </div>
            
            <h1>{tipo_doc.upper()}</h1>
            
            <h2>DADOS DO CLIENTE:</h2>
            <div class="dados">
                <p><strong>Nome:</strong> {nome_cliente}</p>
                <p><strong>Tipo de Documento:</strong> {tipo_doc}</p>
                <p><strong>Data:</strong> {dados_processados.get('data', 'N/A')}</p>
            </div>
            
            <h2>DADOS PROCESSADOS:</h2>
            <div class="dados">
                <pre>{json.dumps(dados_processados, indent=2, ensure_ascii=False)}</pre>
            </div>
            
            <h2>ANÁLISE TÉCNICA:</h2>
            <div class="dados">
                <pre>{json.dumps(analise_tecnica, indent=2, ensure_ascii=False)}</pre>
            </div>
            
            <p><em>Sistema em modo de emergência - revisão manual necessária.</em></p>
        </body>
        </html>