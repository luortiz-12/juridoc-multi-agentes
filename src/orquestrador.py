# orquestrador.py - Versão Final com a Nova Arquitetura de Agentes Especializados

import os
import traceback
from typing import Dict, Any, List
from datetime import datetime

<<<<<<< HEAD
# Importa todos os agentes necessários
=======
# COMENTÁRIO: Importamos o novo agente identificador e todos os coletores especializados.
>>>>>>> parent of fe5ac5e (agente de pesquisa jurisprudencia)
from agente_identificador import AgenteIdentificador
from agente_coletor_civel import AgenteColetorCivel
from agente_coletor_trabalhista import AgenteColetorTrabalhista
from agente_coletor_contratos import AgenteColetorContratos
from agente_coletor_parecer import AgenteColetorParecer
from agente_coletor_queixa_crime import AgenteColetorQueixaCrime
from agente_coletor_habeas_corpus import AgenteColetorHabeasCorpus
from agente_coletor_estudo_de_caso import AgenteColetorEstudoDeCaso

from pesquisa_juridica import PesquisaJuridica
from agente_pesquisa_contratos import AgentePesquisaContratos
from agente_pesquisador_jurisprudencia import AgentePesquisadorJurisprudencia

from agente_redator_trabalhista import AgenteRedatorTrabalhista
from agente_redator_civel import AgenteRedatorCivel
from agente_redator_queixa_crime import AgenteRedatorQueixaCrime
from agente_redator_habeas_corpus import AgenteRedatorHabeasCorpus
from agente_redator_parecer import AgenteRedatorParecer
from agente_redator_contratos import AgenteRedatorContratos
from agente_redator_estudo_de_caso import AgenteRedatorEstudoDeCaso
from agente_redator_jurisprudencia import AgenteRedatorJurisprudencia

from agente_validador import AgenteValidador

class OrquestradorPrincipal:
    def __init__(self):
        print("Inicializando Orquestrador Principal com Agentes Especializados...")
        
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_api_key:
            raise ValueError("ERRO CRÍTICO: DEEPSEEK_API_KEY não encontrada no ambiente.")
        
        print("✅ Chave da API encontrada pelo Orquestrador.")

        # COMENTÁRIO: Inicializamos o novo agente identificador e um dicionário com todos os coletores.
        self.agente_identificador = AgenteIdentificador()
        self.coletores = {
            "Ação Cível": AgenteColetorCivel(),
            "Ação Trabalhista": AgenteColetorTrabalhista(),
            "Contrato": AgenteColetorContratos(),
            "Parecer Jurídico": AgenteColetorParecer(),
            "Queixa-Crime": AgenteColetorQueixaCrime(),
            "Habeas Corpus": AgenteColetorHabeasCorpus(),
            "Estudo de Caso": AgenteColetorEstudoDeCaso(),
        }
        
        self.pesquisa_juridica_peticoes = PesquisaJuridica()
        self.pesquisa_juridica_contratos = AgentePesquisaContratos()
        self.agente_pesquisador_jurisprudencia = AgentePesquisadorJurisprudencia()
        
        # Inicializa todos os agentes redatores num dicionário para fácil acesso.
        self.redatores = {
            "Ação Cível": AgenteRedatorCivel(api_key=deepseek_api_key),
            "Ação Trabalhista": AgenteRedatorTrabalhista(api_key=deepseek_api_key),
            "Contrato": AgenteRedatorContratos(api_key=deepseek_api_key),
            "Parecer Jurídico": AgenteRedatorParecer(api_key=deepseek_api_key),
            "Queixa-Crime": AgenteRedatorQueixaCrime(api_key=deepseek_api_key),
            "Habeas Corpus": AgenteRedatorHabeasCorpus(api_key=deepseek_api_key),
            "Estudo de Caso": AgenteRedatorEstudoDeCaso(api_key=deepseek_api_key),
            "Pesquisa de Jurisprudência": AgenteRedatorJurisprudencia(),
        }
        
        self.agente_validador = AgenteValidador()
        
        print("Orquestrador Principal inicializado com todos os agentes configurados.")
    
    # COMENTÁRIO: Esta é a nova função que estava em falta.
    # Ela lida exclusivamente com o fluxo de pesquisa de jurisprudência.
    def processar_pesquisa_jurisprudencia(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print("\n--- FLUXO DE PESQUISA DE JURISPRUDÊNCIA INICIADO ---")
            
            termos_pesquisa_str = dados_entrada.get("termo-pesquisa", "")
            termos_pesquisa = [termo.strip() for termo in termos_pesquisa_str.split(',') if termo.strip()]
            print(f"  -> Termos a serem pesquisados: {termos_pesquisa}")

            resultados = self.agente_pesquisador_jurisprudencia.pesquisar(termos_pesquisa)
            
            agente_redator_jurisprudencia = self.redatores.get("Pesquisa de Jurisprudência")
            resultado_formatado = agente_redator_jurisprudencia.formatar_resultados(termos_pesquisa, resultados)
            
            print("✅ FLUXO DE PESQUISA DE JURISPRUDÊNCIA FINALIZADO!")
            return {"status": "sucesso", "documento_final": resultado_formatado.get("documento_html")}
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": f"Erro no fluxo de pesquisa de jurisprudência: {e}"}

    def processar_solicitacao_completa(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """
        COMENTÁRIO: Esta função continua a ser responsável por todos os outros documentos,
        e o seu funcionamento não foi alterado.
        """
        try:
            print("\n" + "="*60)
            print("🚀 INICIANDO NOVO FLUXO DE GERAÇÃO DE DOCUMENTO �")
            print("="*60)

            # ETAPA 1: AGENTE IDENTIFICADOR
            print("\n--- ETAPA 1: Identificação do Tipo de Documento ---")
            resultado_identificador = self.agente_identificador.identificar_documento(dados_entrada)
            if resultado_identificador.get("status") == "erro": return resultado_identificador
            tipo_documento = resultado_identificador.get("tipo_documento", "Ação Cível")
            print(f"  -> Documento identificado como: {tipo_documento}")

            # ETAPA 2: AGENTE COLETOR DE DADOS ESPECIALIZADO
            print("\n--- ETAPA 2: Coleta de Dados Especializada ---")
            agente_coletor_ativo = self.coletores.get(tipo_documento)
            if not agente_coletor_ativo:
                raise ValueError(f"Nenhum agente coletor encontrado para o tipo: {tipo_documento}")
            print(f"  -> Acionando Agente: {agente_coletor_ativo.__class__.__name__}")
            resultado_coletor = agente_coletor_ativo.coletar_e_processar(dados_entrada)
<<<<<<< HEAD
=======
            if resultado_coletor.get("status") == "erro": return resultado_coletor
>>>>>>> parent of fe5ac5e (agente de pesquisa jurisprudencia)
            dados_estruturados = resultado_coletor.get('dados_estruturados', {})
            print("[RESUMO COLETOR]")
            print(f"  -> Fundamentos para Pesquisa: {dados_estruturados.get('fundamentos_necessarios', [])}")

            # ETAPA 3: AGENTE DE PESQUISA ESPECIALIZADO
            print("\n--- ETAPA 3: Pesquisa Jurídica ---")
            if tipo_documento == "Contrato":
                agente_pesquisa_ativo = self.pesquisa_juridica_contratos
            else:
                agente_pesquisa_ativo = self.pesquisa_juridica_peticoes
            print(f"  -> Acionando Agente: {agente_pesquisa_ativo.__class__.__name__}")
            resultado_pesquisa = agente_pesquisa_ativo.pesquisar_fundamentacao_completa(
                fundamentos=dados_estruturados.get('fundamentos_necessarios', []),
                tipo_acao=tipo_documento
            )

            # ETAPA 4: AGENTE REDATOR ESPECIALIZADO (COM CICLO DE FEEDBACK)
            print("\n--- ETAPA 4: Redação e Validação Iterativa ---")
            agente_redator_ativo = self.redatores.get(tipo_documento)
            if not agente_redator_ativo:
                raise ValueError(f"Nenhum agente redator encontrado para o tipo: {tipo_documento}")
            print(f"  -> Acionando Agente: {agente_redator_ativo.__class__.__name__}")

            max_tentativas = 3
            documento_atual = ""
            recomendacoes = []
            
            for tentativa_atual in range(1, max_tentativas + 1):
                print(f"\n--- TENTATIVA DE REDAÇÃO Nº {tentativa_atual} ---")
                resultado_redacao = agente_redator_ativo.redigir_peticao_completa(
                    dados_estruturados=dados_estruturados,
                    pesquisa_juridica=resultado_pesquisa,
                    documento_anterior=documento_atual,
                    recomendacoes=recomendacoes
                )
                if resultado_redacao.get("status") == "erro": return resultado_redacao
                documento_atual = resultado_redacao.get('documento_html', '')
                
                print(f"\n--- VALIDAÇÃO DA TENTATIVA Nº {tentativa_atual} ---")
                resultado_validacao = self.agente_validador.validar_e_formatar(documento_atual, dados_estruturados)
                
                if resultado_validacao.get("status") == "aprovado":
                    print("✅ Documento APROVADO pelo Agente Validador.")
                    break
                
                recomendacoes = resultado_validacao.get("recomendacoes", [])
                print(f"❌ Documento REPROVADO. Recomendações para a próxima tentativa: {recomendacoes}")
                if tentativa_atual == max_tentativas:
                    print("⚠️ Número máximo de tentativas atingido. Usando a melhor versão disponível.")

            documento_final = resultado_validacao.get('documento_validado', documento_atual)
            
            print("\n" + "="*60)
            print("✅ PROCESSAMENTO COMPLETO FINALIZADO!")
            print("="*60)
            return {
                "status": "sucesso",
                "documento_final": documento_final,
            }
            
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": str(e)}