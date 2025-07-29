# orquestrador.py - Versão Final com Seleção Dinâmica de Todos os Agentes Redatores

import os
import traceback
from typing import Dict, Any, List
from datetime import datetime

from agente_coletor_dados import AgenteColetorDados
from pesquisa_juridica import PesquisaJuridica
# COMENTÁRIO: Importamos TODAS as classes de redatores especializados.
from agente_redator_trabalhista import AgenteRedatorTrabalhista
from agente_redator_civel import AgenteRedatorCivel
from agente_redator_queixa_crime import AgenteRedatorQueixaCrime
from agente_redator_habeas_corpus import AgenteRedatorHabeasCorpus
# COMENTÁRIO: Adicionada a importação do novo agente de parecer.
from agente_redator_parecer import AgenteRedatorParecer
from agente_validador import AgenteValidador

class OrquestradorPrincipal:
    def __init__(self):
        print("Inicializando Orquestrador Principal com Agentes Especializados...")
        
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_api_key:
            raise ValueError("ERRO CRÍTICO: DEEPSEEK_API_KEY não encontrada no ambiente.")
        
        print("✅ Chave da API encontrada pelo Orquestrador.")

        self.agente_coletor = AgenteColetorDados()
        self.pesquisa_juridica = PesquisaJuridica()
        
        # COMENTÁRIO: Inicializamos uma instância de CADA agente redator, passando a chave da API.
        self.agente_redator_trabalhista = AgenteRedatorTrabalhista(api_key=deepseek_api_key)
        self.agente_redator_civel = AgenteRedatorCivel(api_key=deepseek_api_key)
        self.agente_redator_queixa_crime = AgenteRedatorQueixaCrime(api_key=deepseek_api_key)
        self.agente_redator_habeas_corpus = AgenteRedatorHabeasCorpus(api_key=deepseek_api_key)
        self.agente_redator_parecer = AgenteRedatorParecer(api_key=deepseek_api_key)
        
        self.agente_validador = AgenteValidador()
        
        print("Orquestrador Principal inicializado com todos os agentes configurados.")
    
    def processar_solicitacao_completa(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print("Iniciando processamento completo...")
            agentes_executados = []
            
            # ETAPA 1: COLETOR DE DADOS
            print("ETAPA 1: Agente Coletor de Dados")
            resultado_coletor = self.agente_coletor.coletar_e_processar(dados_entrada)
            agentes_executados.append("Coletor de Dados")
            if resultado_coletor.get("status") == "erro": return resultado_coletor
            dados_estruturados = resultado_coletor.get('dados_estruturados', {})
            print("Dados estruturados: OK")
            
            # ETAPA 2: PESQUISA JURIDICA
            print("ETAPA 2: Pesquisa Juridica")
            resultado_pesquisa = self.pesquisa_juridica.pesquisar_fundamentacao_completa(
                fundamentos=dados_estruturados.get('fundamentos_necessarios', []),
                tipo_acao=dados_estruturados.get('tipo_acao', '')
            )
            agentes_executados.append("Pesquisa Juridica")
            print("Pesquisa concluida: OK")
            
            # ETAPA 3: SELEÇÃO E EXECUÇÃO DO REDATOR ESPECIALIZADO
            print("ETAPA 3: Selecionando Agente Redator Especializado...")
            tipo_acao = dados_estruturados.get('tipo_acao', 'Ação Cível')
            
            # COMENTÁRIO: Lógica de decisão expandida para incluir o novo agente de parecer.
            if "Trabalhista" in tipo_acao:
                print("... Agente Trabalhista selecionado.")
                agente_redator_ativo = self.agente_redator_trabalhista
            elif "Queixa-Crime" in tipo_acao:
                print("... Agente de Queixa-Crime selecionado.")
                agente_redator_ativo = self.agente_redator_queixa_crime
            elif "Habeas Corpus" in tipo_acao:
                print("... Agente de Habeas Corpus selecionado.")
                agente_redator_ativo = self.agente_redator_habeas_corpus
            elif "Parecer Jurídico" in tipo_acao:
                print("... Agente de Parecer Jurídico selecionado.")
                agente_redator_ativo = self.agente_redator_parecer
            else: # Cível é o padrão
                print("... Agente Cível selecionado.")
                agente_redator_ativo = self.agente_redator_civel

            resultado_redacao = agente_redator_ativo.redigir_peticao_completa(
                dados_estruturados=dados_estruturados,
                pesquisa_juridica=resultado_pesquisa
            )
            agentes_executados.append(f"Redator ({tipo_acao})")
            if resultado_redacao.get("status") == "erro": return resultado_redacao
            documento_html = resultado_redacao.get('documento_html', '')
            print(f"Documento redigido: {len(documento_html)} caracteres")
            
            # ETAPA 4: VALIDADOR
            print("ETAPA 4: Agente Validador")
            resultado_validacao = self.agente_validador.validar_e_formatar(documento_html, dados_estruturados)
            agentes_executados.append("Validador")
            documento_final = resultado_validacao.get('documento_validado', documento_html)
            
            print("PROCESSAMENTO COMPLETO FINALIZADO!")
            return {
                "status": "sucesso",
                "documento_final": documento_final,
            }
            
        except Exception as e:
            print(f"ERRO no orquestrador: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {"status": "erro", "erro": str(e)}