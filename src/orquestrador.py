# orquestrador.py - Versão Final com Seleção Dinâmica e Logs Aprimorados

import os
import traceback
from typing import Dict, Any, List
from datetime import datetime

from agente_coletor_dados import AgenteColetorDados
from pesquisa_juridica import PesquisaJuridica
from agente_pesquisa_contratos import AgentePesquisaContratos
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
            # COMENTÁRIO: Adicionados separadores e logs de resumo para cada etapa.
            print("\n" + "="*50)
            print("--- ETAPA 1: AGENTE COLETOR DE DADOS ---")
            resultado_coletor = self.agente_coletor.coletar_e_processar(dados_entrada)
            if resultado_coletor.get("status") == "erro": return resultado_coletor
            dados_estruturados = resultado_coletor.get('dados_estruturados', {})
            
            tipo_documento = dados_estruturados.get('tipo_documento', 'Petição')
            fundamentos_pesquisa = dados_estruturados.get('fundamentos_necessarios', [])
            
            print(f"\n[RESUMO COLETOR]")
            print(f"  -> Tipo de Documento Identificado: {tipo_documento}")
            print(f"  -> Termos para Pesquisa: {fundamentos_pesquisa}")
            
            print("\n" + "="*50)
            print("--- ETAPA 2: AGENTE DE PESQUISA ---")
            if tipo_documento == "Contrato":
                print("  -> Selecionando Agente de Pesquisa de Contratos...")
                agente_pesquisa_ativo = self.pesquisa_juridica_contratos
            else:
                print("  -> Selecionando Agente de Pesquisa Jurídica (Petições/Outros)...")
                agente_pesquisa_ativo = self.pesquisa_juridica_peticoes

            resultado_pesquisa = agente_pesquisa_ativo.pesquisar_fundamentacao_completa(
                fundamentos=fundamentos_pesquisa,
                tipo_acao=tipo_documento
            )
            
            print("\n[RESUMO PESQUISA]")
            # Adapta o resumo para os diferentes tipos de pesquisa
            if tipo_documento == "Contrato":
                print(f"  -> Conteúdos de Contratos encontrados: {len(resultado_pesquisa.get('conteudos_extraidos', []))}")
            else:
                print(f"  -> Conteúdos de Legislação encontrados: {len(resultado_pesquisa.get('legislacao', []))}")
                print(f"  -> Conteúdos de Jurisprudência encontrados: {len(resultado_pesquisa.get('jurisprudencia', []))}")
                print(f"  -> Conteúdos de Doutrina encontrados: {len(resultado_pesquisa.get('doutrina', []))}")

            print("\n" + "="*50)
            print("--- ETAPA 3: AGENTE REDATOR (Ciclo de Redação e Validação) ---")
            
            agente_redator_ativo = self._selecionar_redator(tipo_documento)
            print(f"  -> Agente '{agente_redator_ativo.__class__.__name__}' selecionado para a redação.")

            max_tentativas = 3
            tentativa_atual = 0
            documento_atual = ""
            recomendacoes = []
            
            while tentativa_atual < max_tentativas:
                tentativa_atual += 1
                print(f"\n--- TENTATIVA DE REDAÇÃO Nº {tentativa_atual} ---")
                
                resultado_redacao = agente_redator_ativo.redigir_peticao_completa(
                    dados_estruturados=dados_estruturados,
                    pesquisa_juridica=resultado_pesquisa,
                    documento_anterior=documento_atual,
                    recomendacoes=recomendacoes
                )
                
                if resultado_redacao.get("status") == "erro": return resultado_redacao
                documento_atual = resultado_redacao.get('documento_html', '')
                
                print("\n--- VALIDAÇÃO DA TENTATIVA Nº " + str(tentativa_atual) + " ---")
                resultado_validacao = self.agente_validador.validar_e_formatar(documento_atual, dados_estruturados)
                
                print(f"[RESUMO VALIDAÇÃO TENTATIVA {tentativa_atual}]")
                print(f"  -> Status: {resultado_validacao.get('status', 'erro').upper()}")
                print(f"  -> Score de Qualidade: {resultado_validacao.get('score_qualidade', 0):.2f}%")

                if resultado_validacao.get("status") == "aprovado":
                    print("  -> Decisão: Documento APROVADO.")
                    break
                
                recomendacoes = resultado_validacao.get("recomendacoes", [])
                print(f"  -> Decisão: Documento REPROVADO. Recomendações para a próxima tentativa: {recomendacoes}")
                if tentativa_atual >= max_tentativas:
                    print("⚠️ Número máximo de tentativas atingido. Usando a melhor versão disponível.")

            documento_final = resultado_validacao.get('documento_validado', documento_atual)
            
            print("\n" + "="*50)
            print("--- ETAPA 4: FINALIZAÇÃO ---")
            print("✅ PROCESSAMENTO COMPLETO FINALIZADO!")
            return {
                "status": "sucesso",
                "documento_final": documento_final,
            }
            
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": str(e)}

    def _selecionar_redator(self, tipo_documento: str):
        """Seleciona o agente redator apropriado com base no tipo de documento."""
        if "Contrato" in tipo_documento: return self.agente_redator_contratos
        if "Trabalhista" in tipo_documento: return self.agente_redator_trabalhista
        if "Queixa-Crime" in tipo_documento: return self.agente_redator_queixa_crime
        if "Habeas Corpus" in tipo_documento: return self.agente_redator_habeas_corpus
        if "Parecer Jurídico" in tipo_documento: return self.agente_redator_parecer
        return self.agente_redator_civel # Padrão