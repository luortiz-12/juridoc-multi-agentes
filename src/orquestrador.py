# orquestrador.py - Versão Final com Seleção Dinâmica de Todos os Agentes

import os
import traceback
from typing import Dict, Any, List
from datetime import datetime

from agente_coletor_dados import AgenteColetorDados
# COMENTÁRIO: Importamos os dois agentes de pesquisa especializados.
from pesquisa_juridica import PesquisaJuridica
from agente_pesquisa_contratos import AgentePesquisaContratos
# COMENTÁRIO: Importamos todos os agentes redatores.
from agente_redator_trabalhista import AgenteRedatorTrabalhista
from agente_redator_civel import AgenteRedatorCivel
from agente_redator_queixa_crime import AgenteRedatorQueixaCrime
from agente_redator_habeas_corpus import AgenteRedatorHabeasCorpus
from agente_redator_parecer import AgenteRedatorParecer
from agente_redator_contratos import AgenteRedatorContratos
from agente_validador import AgenteValidador

class OrquestradorPrincipal:
    def __init__(self):
        print("Inicializando Orquestrador Principal com Agentes Especializados...")
        
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_api_key:
            raise ValueError("ERRO CRÍTICO: DEEPSEEK_API_KEY não encontrada no ambiente.")
        
        print("✅ Chave da API encontrada pelo Orquestrador.")

        self.agente_coletor = AgenteColetorDados()
        # COMENTÁRIO: Inicializamos os dois agentes de pesquisa.
        self.pesquisa_juridica_peticoes = PesquisaJuridica()
        self.pesquisa_juridica_contratos = AgentePesquisaContratos()
        
        # Inicializa todos os agentes redatores
        self.agente_redator_trabalhista = AgenteRedatorTrabalhista(api_key=deepseek_api_key)
        self.agente_redator_civel = AgenteRedatorCivel(api_key=deepseek_api_key)
        self.agente_redator_queixa_crime = AgenteRedatorQueixaCrime(api_key=deepseek_api_key)
        self.agente_redator_habeas_corpus = AgenteRedatorHabeasCorpus(api_key=deepseek_api_key)
        self.agente_redator_parecer = AgenteRedatorParecer(api_key=deepseek_api_key)
        self.agente_redator_contratos = AgenteRedatorContratos(api_key=deepseek_api_key)
        
        self.agente_validador = AgenteValidador()
        
        print("Orquestrador Principal inicializado com todos os agentes configurados.")
    
    def processar_solicitacao_completa(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # ETAPA 1: COLETOR DE DADOS
            resultado_coletor = self.agente_coletor.coletar_e_processar(dados_entrada)
            if resultado_coletor.get("status") == "erro": return resultado_coletor
            dados_estruturados = resultado_coletor.get('dados_estruturados', {})
            
            tipo_documento = dados_estruturados.get('tipo_documento', 'Petição')
            
            # ETAPA 2: SELEÇÃO E EXECUÇÃO DA PESQUISA ESPECIALIZADA
            # COMENTÁRIO: O orquestrador agora escolhe qual agente de pesquisa usar.
            if tipo_documento == "Contrato":
                print("... Agente de Pesquisa de Contratos selecionado.")
                agente_pesquisa_ativo = self.pesquisa_juridica_contratos
            else: # Para todos os outros tipos de documentos (petições, pareceres)
                print("... Agente de Pesquisa Jurídica (Petições) selecionado.")
                agente_pesquisa_ativo = self.pesquisa_juridica_peticoes

            resultado_pesquisa = agente_pesquisa_ativo.pesquisar_fundamentacao_completa(
                fundamentos=dados_estruturados.get('fundamentos_necessarios', []),
                tipo_acao=dados_estruturados.get('tipo_acao', '')
            )
            
            # ETAPA 3: SELEÇÃO E EXECUÇÃO DO REDATOR ESPECIALIZADO
            # COMENTÁRIO: A lógica de decisão agora inclui o novo redator de contratos.
            if tipo_documento == "Contrato":
                agente_redator_ativo = self.agente_redator_contratos
            else:
                tipo_acao = dados_estruturados.get('tipo_acao', 'Ação Cível')
                if "Trabalhista" in tipo_acao: agente_redator_ativo = self.agente_redator_trabalhista
                elif "Queixa-Crime" in tipo_acao: agente_redator_ativo = self.agente_redator_queixa_crime
                elif "Habeas Corpus" in tipo_acao: agente_redator_ativo = self.agente_redator_habeas_corpus
                elif "Parecer Jurídico" in tipo_acao: agente_redator_ativo = self.agente_redator_parecer
                else: agente_redator_ativo = self.agente_redator_civel

            resultado_redacao = agente_redator_ativo.redigir_peticao_completa(
                dados_estruturados=dados_estruturados,
                pesquisa_juridica=resultado_pesquisa
            )
            if resultado_redacao.get("status") == "erro": return resultado_redacao
            documento_html = resultado_redacao.get('documento_html', '')
            
            # ETAPA 4: VALIDADOR
            # O validador pode ser usado para todos os tipos de documentos para garantir a formatação.
            resultado_validacao = self.agente_validador.validar_e_formatar(documento_html, dados_estruturados)
            documento_final = resultado_validacao.get('documento_validado', documento_html)
            
            print("PROCESSAMENTO COMPLETO FINALIZADO!")
            return {
                "status": "sucesso",
                "documento_final": documento_final,
            }
            
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": str(e)}