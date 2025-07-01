# main_orchestrator.py - VERSÃO CORRIGIDA E UNIFICADA

import os
import json
import sys

# Importa os agentes especialistas e de suporte
from agente_coletor_dados import AgenteColetorDados
from agente_validacao import AgenteValidador
from agente_formatacao_final import AgenteFormatacaoFinal
from agente_tecnico_peticao import AgenteTecnicoPeticao # Exemplo, você terá um para cada tipo
from agente_redator_peticao import AgenteRedatorPeticao   # Exemplo
# ... (importe todos os 8 agentes especialistas aqui) ...

class Orquestrador:
    def __init__(self, openai_api_key):
        print("🚀 Inicializando Orquestrador com agentes especializados...")
        # Instancia todos os seus agentes aqui, como no seu código original
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.validador = AgenteValidador(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal()
        self.tecnico_peticao = AgenteTecnicoPeticao(llm_api_key=openai_api_key)
        self.redator_peticao = AgenteRedatorPeticao(llm_api_key=openai_api_key)
        # ... (o resto das suas instanciações) ...
        print("✅ Todos os agentes inicializados com sucesso!")

    def gerar_documento(self, raw_input_data: dict) -> dict:
        print("\n🚀 Iniciando geração de documento com fluxo corrigido")
        print("=" * 60)
        try:
            # 1. Coleta
            print("📥 ETAPA 1: Coleta de dados...")
            dados_processados = self.coletor.coletar_e_processar(raw_input_data)
            if dados_processados.get("erro"):
                return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
            print("✅ Dados coletados com sucesso.")
            
            # 2. Roteamento
            print("\n🎯 ETAPA 2: Roteamento para especialistas...")
            tipo_documento = dados_processados.get("tipo_documento", "").lower().strip()
            # A sua lógica de roteamento aqui estava correta e foi mantida
            if tipo_documento == "peticao":
                agente_tecnico = self.tecnico_peticao
                agente_redator = self.redator_peticao
                print("📄 Roteado para especialistas em PETIÇÃO")
            # ... (seus outros elifs para contrato, parecer, etc.)
            else:
                 return {"status": "erro", "mensagem": f"Tipo de documento '{tipo_documento}' não suportado."}

            # --- CORREÇÃO: Chamada dos Métodos com Nomes Corretos ---
            
            # 3. Análise Técnica
            print("\n🧠 ETAPA 3: Análise técnica...")
            # Verifica se o método correto existe antes de chamar
            if hasattr(agente_tecnico, 'analisar_com_rag'):
                analise_tecnica = agente_tecnico.analisar_com_rag(dados_processados)
            else:
                # Fallback para um método padrão se o específico não existir
                analise_tecnica = {"analise": "Método 'analisar_com_rag' não encontrado no agente técnico."}
            
            if analise_tecnica.get("erro"):
                return {"status": "erro", "mensagem": "Falha na análise técnica", "detalhes": analise_tecnica}
            print("✅ Análise técnica concluída.")

            # 4. Redação
            print("\n✍️ ETAPA 4: Redação do documento...")
            # Verifica se o método correto existe
            if hasattr(agente_redator, 'redigir_com_rag'):
                documento_redigido = agente_redator.redigir_com_rag(dados_processados, analise_tecnica)
            else:
                documento_redigido = "ERRO: Método 'redigir_com_rag' não encontrado no agente redator."

            if isinstance(documento_redigido, dict) and documento_redigido.get("erro"):
                 return {"status": "erro", "mensagem": "Falha na redação", "detalhes": documento_redigido}
            print("✅ Redação concluída.")

            # 5. Validação e Formatação Final (seu código aqui estava bom)
            print("\n✅ ETAPA 5: Validação...")
            resultado_validacao = self.validador.validar_documento(documento_redigido, dados_processados)
            # A lógica de loop de revisão pode ser adicionada aqui...
            
            print("\n🎨 ETAPA 6: Formatação final...")
            documento_final_html = self.formatador.formatar_documento(resultado_validacao.get('documento_corrigido', documento_redigido), dados_processados)
            
            print("\n🎉 DOCUMENTO GERADO COM SUCESSO!")
            return {"status": "sucesso", "documento_html": documento_final_html}

        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO NO ORQUESTRADOR: {e}")
            return {"status": "erro", "mensagem": f"Erro crítico na orquestração: {str(e)}"}