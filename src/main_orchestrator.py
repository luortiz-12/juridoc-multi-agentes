# main_orchestrator.py - VERSÃO CORRIGIDA E FINAL

import os
import json
import sys

# Importações dos agentes especializados
from agente_coletor_dados import AgenteColetorDados
from agente_validacao import AgenteValidador
from agente_formatacao_final import AgenteFormatacaoFinal
from agente_tecnico_peticao import AgenteTecnicoPeticao
from agente_tecnico_contrato import AgenteTecnicoContrato
from agente_tecnico_parecer import AgenteTecnicoParecer
from agente_tecnico_estudo_caso import AgenteTecnicoEstudoCaso
from agente_redator_peticao import AgenteRedatorPeticao
from agente_redator_contrato import AgenteRedatorContrato
from agente_redator_parecer import AgenteRedatorParecer
from agente_redator_estudo_caso import AgenteRedatorEstudoCaso

class Orquestrador:
    def __init__(self, openai_api_key):
        print("🚀 Inicializando Orquestrador com agentes especializados...")
        
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.validador = AgenteValidador(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal()

        self.agentes_tecnicos = {
            "peticao": AgenteTecnicoPeticao(llm_api_key=openai_api_key),
            "contrato": AgenteTecnicoContrato(llm_api_key=openai_api_key),
            "parecer": AgenteTecnicoParecer(llm_api_key=openai_api_key),
            "estudo de caso": AgenteTecnicoEstudoCaso(llm_api_key=openai_api_key)
        }
        self.agentes_redatores = {
            "peticao": AgenteRedatorPeticao(llm_api_key=openai_api_key),
            "contrato": AgenteRedatorContrato(llm_api_key=openai_api_key),
            "parecer": AgenteRedatorParecer(llm_api_key=openai_api_key),
            "estudo de caso": AgenteRedatorEstudoCaso(llm_api_key=openai_api_key)
        }
        print("✅ Todos os agentes especializados inicializados com sucesso!")

    def gerar_documento(self, raw_input_data: dict) -> dict:
        print("\n🚀 Iniciando geração de documento com fluxo corrigido")
        print("=" * 60)
        
        try:
            print("📥 ETAPA 1: Coleta de dados...")
            dados_processados = self.coletor.coletar_e_processar(raw_input_data)
            if dados_processados.get("erro"):
                return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
            print("✅ Dados coletados com sucesso.")
            
            print("\n🎯 ETAPA 2: Roteamento para especialistas...")
            tipo_documento = dados_processados.get("tipo_documento", "").lower().strip()
            
            agente_tecnico = self.agentes_tecnicos.get(tipo_documento)
            agente_redator = self.agentes_redatores.get(tipo_documento)

            if not agente_tecnico or not agente_redator:
                return {"status": "erro", "mensagem": f"Tipo de documento '{tipo_documento}' não suportado."}
            print(f"📄 Roteado para especialistas em {tipo_documento.upper()}")

            print("\n🧠 ETAPA 3: Análise técnica...")
            analise_tecnica = agente_tecnico.analisar_com_rag(dados_processados)
            if "erro" in analise_tecnica:
                print(f"⚠️ Erro na análise técnica: {analise_tecnica.get('detalhes', 'N/A')}")
            else:
                print("✅ Análise técnica concluída.")

            print("\n✍️ ETAPA 4: Redação do documento...")
            documento_redigido = agente_redator.redigir_com_rag(dados_processados, analise_tecnica)
            if isinstance(documento_redigido, dict) and "erro" in documento_redigido:
                 return {"status": "erro", "mensagem": "Falha na Redação", "detalhes": documento_redigido}
            print("✅ Redação concluída.")

            print("\n✅ ETAPA 5: Validação...")
            # --- CORREÇÃO AQUI ---
            # Passando os argumentos que faltavam para o validador.
            resultado_validacao = self.validador.validar_documento(documento_redigido, dados_processados, analise_tecnica, tipo_documento)
            print("✅ Validação concluída")
            
            documento_a_formatar = resultado_validacao.get('documento_corrigido', documento_redigido)

            print("\n🎨 ETAPA 6: Formatação final...")
            documento_final_html = self.formatador.formatar_documento_final(documento_a_formatar, dados_processados)
            print("✅ Formatação final concluída")

            resultado = {"status": "sucesso", "documento_html": documento_final_html}
            
            print("\n🎉 DOCUMENTO GERADO COM SUCESSO!")
            return resultado
            
        except Exception as e:
            import traceback
            print(f"\n❌ ERRO CRÍTICO NO ORQUESTRADOR: {e}")
            traceback.print_exc()
            return {"status": "erro", "mensagem": f"Erro crítico na orquestração: {str(e)}"}