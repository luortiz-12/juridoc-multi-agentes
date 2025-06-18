# main_orchestrator.py

import os
import json
import sys

# Importações diretas dos módulos dos agentes
from agente_coletor_dados import AgenteColetorDados
from agente_validacao import AgenteValidador
from agente_formatacao_final import AgenteFormatacaoFinal
from agente_tecnico_contrato import AgenteTecnicoContrato
from agente_redator_contrato import AgenteRedatorContrato
from agente_tecnico_peticao import AgenteTecnicoPeticao
from agente_redator_peticao import AgenteRedatorPeticao
from agente_tecnico_parecer import AgenteTecnicoParecer
from agente_redator_parecer import AgenteRedatorParecer
from agente_tecnico_estudo_caso import AgenteTecnicoEstudoCaso
from agente_redator_estudo_caso import AgenteRedatorEstudoCaso


class Orquestrador:
    """
    Orquestra o fluxo de trabalho completo, roteando tarefas para
    agentes especialistas com base no tipo de documento.
    """
    def __init__(self, openai_api_key):
        # --- Bloco de código com a indentação CORRIGIDA ---
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.validador = AgenteValidador(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal()
        self.tecnico_contrato = AgenteTecnicoContrato(llm_api_key=openai_api_key)
        self.redator_contrato = AgenteRedatorContrato(llm_api_key=openai_api_key)
        self.tecnico_peticao = AgenteTecnicoPeticao(llm_api_key=openai_api_key)
        self.redator_peticao = AgenteRedatorPeticao(llm_api_key=openai_api_key)
        self.tecnico_parecer = AgenteTecnicoParecer(llm_api_key=openai_api_key)
        self.redator_parecer = AgenteRedatorParecer(llm_api_key=openai_api_key)
        self.tecnico_estudo_caso = AgenteTecnicoEstudoCaso(llm_api_key=openai_api_key)
        self.redator_estudo_caso = AgenteRedatorEstudoCaso(llm_api_key=openai_api_key)

    def gerar_documento(self, raw_input_data: dict) -> dict:
        # --- Bloco de código com a indentação CORRIGIDA ---
        print("\n--- Iniciando Geração de Documento com Arquitetura de Especialistas ---")
        dados_processados = self.coletor.coletar_e_processar(raw_input_data)
        if dados_processados.get("erro"):
            return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
        print("Dados coletados e processados com sucesso.")

        tipo_documento = dados_processados.get("tipo_documento", "").lower().strip()
        agente_tecnico_usado = None
        agente_redator_usado = None

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

        print(f"Roteado para especialistas de '{tipo_documento}'.")
        print("Executando Agente Técnico Especialista...")
        analise_juridica = agente_tecnico_usado.analisar_dados(dados_processados)
        if analise_juridica.get("erro"):
            return {"status": "erro", "mensagem": "Falha na análise jurídica especialista", "detalhes": analise_juridica}
        print("Análise jurídica especialista concluída.")

        documento_gerado = None
        resultado_validacao = {}
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            print(f"Executando Agente Redator Especialista (Tentativa {tentativa + 1}/{max_tentativas})...")
            resultado_redacao = agente_redator_usado.redigir_documento(
                dados_processados=dados_processados,
                analise_juridica=analise_juridica,
                documento_anterior=documento_gerado
            )
            
            if resultado_redacao.get("erro"):
                return {"status": "erro", "mensagem": "Falha na redação especialista", "detalhes": resultado_redacao}
            
            documento_gerado = resultado_redacao.get("documento", "")
            print("Documento preliminar redigido pelo especialista.")
            print("Executando Agente de Validação...")
            resultado_validacao = self.validador.validar_documento(documento_gerado, dados_processados, analise_juridica, tipo_documento)
            
            if resultado_validacao.get("erro"):
                return {"status": "erro", "mensagem": "Falha na validação do documento", "detalhes": resultado_validacao}
            
            if resultado_validacao.get("status") == "aprovado":
                print("Documento APROVADO pelo Agente de Validação.")
                break
            else:
                sugestoes = resultado_validacao.get("sugestoes_melhoria", [])
                print(f"Documento requer revisão. Sugestões: {sugestoes}")
                analise_juridica["sugestoes_revisao"] = sugestoes
                if tentativa == max_tentativas - 1:
                    print("Documento não aprovado após múltiplas tentativas.")

        if resultado_validacao.get("status") != "aprovado":
            return {"status": "erro", "mensagem": "Documento não aprovado após múltiplas tentativas de revisão.", "detalhes": resultado_validacao}

        print("Executando Agente de Formatação Final...")
        documento_final_html = self.formatador.formatar_documento(documento_gerado, dados_processados)
        print("Documento final formatado com sucesso.")
        print("--- Geração de Documento Concluída ---")
        return {"status": "sucesso", "documento_html": documento_final_html}