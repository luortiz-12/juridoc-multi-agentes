# main_orchestrator.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

# Importações dos agentes
from rag_agent_integration import RAGEnhancedTechnicalAgent, RAGEnhancedWriterAgent
from agente_coletor_dados import AgenteColetorDados
from agente_validacao import AgenteValidador
from agente_formatacao_final import AgenteFormatacaoFinal

class Orquestrador:
    """
    Orquestra o fluxo de trabalho RAG, roteando tarefas para
    agentes aprimorados com base no tipo de documento.
    """
    def __init__(self, openai_api_key):
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.validador = AgenteValidador(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal()

        self.tecnico_peticao = RAGEnhancedTechnicalAgent(doc_type='peticao', llm_api_key=openai_api_key)
        self.redator_peticao = RAGEnhancedWriterAgent(doc_type='peticao', llm_api_key=openai_api_key)

        self.tecnico_contrato = RAGEnhancedTechnicalAgent(doc_type='contrato', llm_api_key=openai_api_key)
        self.redator_contrato = RAGEnhancedWriterAgent(doc_type='contrato', llm_api_key=openai_api_key)
        
        self.tecnico_parecer = RAGEnhancedTechnicalAgent(doc_type='parecer', llm_api_key=openai_api_key)
        self.redator_parecer = RAGEnhancedWriterAgent(doc_type='parecer', llm_api_key=openai_api_key)
        
        self.tecnico_estudo_caso = RAGEnhancedTechnicalAgent(doc_type='estudo de caso', llm_api_key=openai_api_key)
        self.redator_estudo_caso = RAGEnhancedWriterAgent(doc_type='estudo de caso', llm_api_key=openai_api_key)
        
        # --- CORREÇÃO 1: TORNANDO O PROMPT EXPLÍCITO ---
        # Adicionamos a variável {tipo_documento} para dizer à IA exatamente o que ela deve escrever.
        redacao_prompt_template = """
            Você é um Redator Jurídico Mestre. Sua tarefa é pegar uma análise técnica detalhada e um rico contexto de redação (com guias estruturais, templates e fórmulas) e redigir o texto final de um(a) **{tipo_documento}** em HTML.
            
            **ANÁLISE TÉCNICA (O que fazer):**
            {technical_analysis}
            
            **CONTEXTO DE REDAÇÃO (Como fazer):**
            {writing_context}
            
            **REGRAS:**
            - Siga rigorosamente as recomendações, guias e templates fornecidos no contexto para redigir o(a) **{tipo_documento}**.
            - Use as fórmulas linguísticas para soar como um advogado experiente.
            - O resultado final deve ser apenas o corpo do documento em HTML, começando com a tag <h1>.
            
            Redija o(a) **{tipo_documento}** agora.
        """
        # Adicionamos 'tipo_documento' às variáveis de entrada do prompt.
        prompt = PromptTemplate(input_variables=["tipo_documento", "technical_analysis", "writing_context"], template=redacao_prompt_template)
        self.final_writing_chain = LLMChain(llm=ChatOpenAI(model="gpt-4o", openai_api_key=openai_api_key, temperature=0.2), prompt=prompt)


    def gerar_documento(self, raw_input_data: dict) -> dict:
        print("\n--- Iniciando Geração de Documento com Arquitetura RAG ---")
        
        dados_processados = self.coletor.coletar_e_processar(raw_input_data)
        if dados_processados.get("erro"):
            return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
        print("Dados coletados e processados com sucesso.")
        
        tipo_documento = dados_processados.get("tipo_documento", "").lower().strip()
        
        if tipo_documento == "contrato":
            agente_tecnico_usado = self.tecnico_contrato
            agente_redator_usado = self.redator_contrato
        elif tipo_documento == "peticao":
            agente_tecnico_usado = self.tecnico_peticao
            agente_redator_usado = self.redator_peticao
        elif tipo_documento == "parecer":
            agente_tecnico_usado = self.tecnico_parecer
            agente_redator_usado = self.redator_parecer
        elif tipo_documento in ["estudo de caso", "estudo"]:
            agente_tecnico_usado = self.tecnico_estudo_caso
            agente_redator_usado = self.redator_estudo_caso
        else:
            return {"status": "erro", "mensagem": f"Tipo de documento '{tipo_documento}' não suportado."}
            
        print(f"Roteado para especialistas RAG de '{tipo_documento}'.")
        
        print("Executando Agente Técnico RAG...")
        analise_tecnica = agente_tecnico_usado.analyze_with_rag(dados_processados)
        print("Análise técnica RAG concluída.")
        
        print("Preparando contexto de redação RAG...")
        contexto_de_redacao = agente_redator_usado.write_with_rag(dados_processados, analise_tecnica)
        print("Contexto de redação preparado.")
        
        print("Executando redação final com base no contexto RAG...")
        # --- CORREÇÃO 2: PASSANDO A NOVA VARIÁVEL ---
        # Passamos o 'tipo_documento' para o chain para que ele possa ser inserido no prompt.
        resultado_redacao = self.final_writing_chain.invoke({
            "tipo_documento": tipo_documento,
            "technical_analysis": json.dumps(analise_tecnica, ensure_ascii=False, indent=2),
            "writing_context": json.dumps(contexto_de_redacao, ensure_ascii=False, indent=2)
        })
        documento_gerado = resultado_redacao['text']
        print("Documento preliminar redigido.")

        # A lógica de validação pode ser reintroduzida aqui se desejado.

        print("Executando Agente de Formatação Final...")
        documento_final_html = self.formatador.formatar_documento(documento_gerado, dados_processados)
        print("Documento final formatado com sucesso.")

        print("--- Geração de Documento Concluída ---")
        return {"status": "sucesso", "documento_html": documento_final_html}