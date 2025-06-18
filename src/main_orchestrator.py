# main_orchestrator.py

import os
import json
import sys

# --- ALTERAÇÃO 1: IMPORTAÇÃO DOS AGENTES ---
# Removemos os agentes genéricos e importamos todos os novos especialistas.
from agente_coletor_dados import AgenteColetorDados
from agente_validador import AgenteValidador
from agente_formatacao_final import AgenteFormatacaoFinal

# Especialistas de Contrato
from agente_tecnico_contrato import AgenteTecnicoContrato
from agente_redator_contrato import AgenteRedatorContrato

# Especialistas de Petição
from agente_tecnico_peticao import AgenteTecnicoPeticao
from agente_redator_peticao import AgenteRedatorPeticao

# Especialistas de Parecer
from agente_tecnico_parecer import AgenteTecnicoParecer
from agente_redator_parecer import AgenteRedatorParecer

# Especialistas de Estudo de Caso
from agente_tecnico_estudo_caso import AgenteTecnicoEstudoCaso
from agente_redator_estudo_caso import AgenteRedatorEstudoCaso


class Orquestrador:
    def __init__(self, openai_api_key):
        # --- ALTERAÇÃO 2: INSTANCIAÇÃO DOS AGENTES ---
        # Instanciamos todos os agentes que o orquestrador poderá usar.
        
        # Agentes de Suporte (Genéricos)
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.validador = AgenteValidador(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal()

        # Agentes Especialistas
        self.tecnico_contrato = AgenteTecnicoContrato(llm_api_key=openai_api_key)
        self.redator_contrato = AgenteRedatorContrato(llm_api_key=openai_api_key)
        
        self.tecnico_peticao = AgenteTecnicoPeticao(llm_api_key=openai_api_key)
        self.redator_peticao = AgenteRedatorPeticao(llm_api_key=openai_api_key)

        self.tecnico_parecer = AgenteTecnicoParecer(llm_api_key=openai_api_key)
        self.redator_parecer = AgenteRedatorParecer(llm_api_key=openai_api_key)

        self.tecnico_estudo_caso = AgenteTecnicoEstudoCaso(llm_api_key=openai_api_key)
        self.redator_estudo_caso = AgenteRedatorEstudoCaso(llm_api_key=openai_api_key)


    def gerar_documento(self, raw_input_data: dict) -> dict:
        print("\n--- Iniciando Geração de Documento com Arquitetura de Especialistas ---")

        # Etapa 1: Coleta de Dados (Genérico)
        print("Executando Agente Coletor de Dados...")
        dados_processados = self.coletor.coletar_e_processar(raw_input_data)
        if dados_processados.get("erro"):
            return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
        print("Dados coletados e processados com sucesso.")

        tipo_documento = dados_processados.get("tipo_documento", "").lower()

        # --- ALTERAÇÃO 3: ROTEAMENTO INTELIGENTE ---
        # O orquestrador decide qual par de especialistas usar.
        agente_tecnico_usado = None
        agente_redator_usado = None

        if tipo_documento == "contrato":
            print(f"Roteando para especialistas de '{tipo_documento}'...")
            agente_tecnico_usado = self.tecnico_contrato
            agente_redator_usado = self.redator_contrato
        elif tipo_documento == "peticao":
            print(f"Roteando para especialistas de '{tipo_documento}'...")
            agente_tecnico_usado = self.tecnico_peticao
            agente_redator_usado = self.redator_peticao
        elif tipo_documento == "parecer":
            print(f"Roteando para especialistas de '{tipo_documento}'...")
            agente_tecnico_usado = self.tecnico_parecer
            agente_redator_usado = self.redator_parecer
        elif tipo_documento == "estudo de caso" or tipo_documento == "estudo": # Aceita ambas as formas
            print(f"Roteando para especialistas de 'Estudo de Caso'...")
            agente_tecnico_usado = self.tecnico_estudo_caso
            agente_redator_usado = self.redator_estudo_caso
        else:
            return {"status": "erro", "mensagem": f"Tipo de documento '{tipo_documento}' não suportado pela arquitetura de especialistas."}

        # Etapa 2: Análise Jurídica (Especialista)
        print(f"Executando Agente Técnico Especialista em {tipo_documento}...")
        analise_juridica = agente_tecnico_usado.analisar_dados(dados_processados)
        if analise_juridica.get("erro"):
            return {"status": "erro", "mensagem": "Falha na análise jurídica especialista", "detalhes": analise_juridica}
        print("Análise jurídica especialista concluída com sucesso.")

        # Etapa 3 e 4: Loop de Redação (Especialista) e Validação (Genérico)
        documento_gerado = ""
        resultado_validacao = {}
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            print(f"Executando Agente Redator Especialista (Tentativa {tentativa + 1}/{max_tentativas})...")
            resultado_redacao = agente_redator_usado.redigir_documento(dados_processados, analise_juridica)
            
            if resultado_redacao.get("erro"):
                return {"status": "erro", "mensagem": "Falha na redação especialista do documento", "detalhes": resultado_redacao}
            
            documento_gerado = resultado_redacao.get("documento", "")
            print("Documento preliminar redigido pelo especialista.")

            print("Executando Agente de Validação...")
            # Passamos o tipo_documento para o validador aprimorado
            resultado_validacao = self.validador.validar_documento(documento_gerado, dados_processados, analise_juridica, tipo_documento)
            
            if resultado_validacao.get("erro"):
                return {"status": "erro", "mensagem": "Falha na validação do documento", "detalhes": resultado_validacao}
            
            print("Validação concluída.")
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

        # Etapa 5: Formatação Final (Genérico)
        print("Executando Agente de Formatação Final...")
        documento_final_html = self.formatador.formatar_documento(documento_gerado, dados_processados)
        print("Documento final formatado com sucesso.")

        print("--- Geração de Documento Concluída ---")
        return {"status": "sucesso", "documento_html": documento_final_html}

# O bloco de teste local continua funcional, pois a interface do orquestrador não mudou.
if __name__ == '__main__':
    # ... (seu código de teste local) ...
    pass