# main_orchestrator.py - VERSÃO FINAL SIMPLIFICADA

import os
import json
from agente_coletor_dados import AgenteColetorDados
from agente_tecnico_peticao import AgenteTecnicoPeticao
from agente_redator_peticao import AgenteRedatorPeticao
from agente_validacao import AgenteValidador
from agente_formatacao_final import AgenteFormatacaoFinal

class Orquestrador:
    def __init__(self, openai_api_key):
        print("🚀 Inicializando Orquestrador focado em Petições...")
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.tecnico = AgenteTecnicoPeticao(llm_api_key=openai_api_key)
        self.redator = AgenteRedatorPeticao(llm_api_key=openai_api_key)
        self.validador = AgenteValidador(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal()
        print("✅ Orquestrador pronto.")

    def gerar_documento(self, raw_input_data: dict) -> dict:
        print("\n🚀 Iniciando geração de petição...")
        
        # 1. Coletar Dados
        print("ETAPA 1: Coleta de dados...")
        dados_processados = self.coletor.coletar_e_processar(raw_input_data)
        if dados_processados.get("erro"):
            return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
        
        # 2. Análise Técnica (com pesquisa online)
        print("ETAPA 2: Análise técnica e pesquisa...")
        analise_tecnica = self.tecnico.analisar_dados(dados_processados)
        if analise_tecnica.get("erro"):
            return {"status": "erro", "mensagem": "Falha na análise técnica", "detalhes": analise_tecnica}
        
        # 3. Redação do Documento
        print("ETAPA 3: Redação do documento...")
        resultado_redacao = self.redator.redigir_documento(dados_processados, analise_tecnica)
        if resultado_redacao.get("erro"):
            return {"status": "erro", "mensagem": "Falha na redação", "detalhes": resultado_redacao}
        documento_html = resultado_redacao.get("documento")
        
        # Opcional: A lógica de validação e loop de revisão pode ser adicionada aqui

        # 4. Formatação Final
        print("ETAPA 4: Formatação final...")
        documento_final = self.formatador.formatar_documento(documento_html, dados_processados)
        
        print("🎉 DOCUMENTO GERADO COM SUCESSO!")
        return {"status": "sucesso", "documento_html": documento_final}