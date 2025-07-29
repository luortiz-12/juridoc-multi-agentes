# orquestrador.py - Versão Final com Ciclo de Feedback Iterativo

import os
import traceback
from typing import Dict, Any

# ... (todas as importações dos agentes)
from agente_coletor_dados import AgenteColetorDados
from pesquisa_juridica import PesquisaJuridica
from agente_pesquisa_contratos import AgentePesquisaContratos
from agente_redator_trabalhista import AgenteRedatorTrabalhista
from agente_redator_civel import AgenteRedatorCivel
# ... etc.
from agente_validador import AgenteValidador

class OrquestradorPrincipal:
    def __init__(self):
        # ... (inicialização dos agentes como antes)
        print("Inicializando Orquestrador Principal com Ciclo de Feedback...")
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_api_key: raise ValueError("DEEPSEEK_API_KEY não encontrada.")
        self.agente_coletor = AgenteColetorDados()
        self.pesquisa_juridica_peticoes = PesquisaJuridica()
        self.pesquisa_juridica_contratos = AgentePesquisaContratos()
        self.agente_redator_civel = AgenteRedatorCivel(api_key=deepseek_api_key)
        # ... inicializar todos os outros redatores
        self.agente_validador = AgenteValidador()
        print("Orquestrador Principal inicializado.")
    
    def processar_solicitacao_completa(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # ETAPA 1 & 2: Coleta e Pesquisa (como antes)
            resultado_coletor = self.agente_coletor.coletar_e_processar(dados_entrada)
            if resultado_coletor.get("status") == "erro": return resultado_coletor
            dados_estruturados = resultado_coletor.get('dados_estruturados', {})
            
            tipo_documento = dados_estruturados.get('tipo_documento', 'Petição')
            
            if tipo_documento == "Contrato":
                agente_pesquisa_ativo = self.pesquisa_juridica_contratos
            else:
                agente_pesquisa_ativo = self.pesquisa_juridica_peticoes

            resultado_pesquisa = agente_pesquisa_ativo.pesquisar_fundamentacao_completa(
                fundamentos=dados_estruturados.get('fundamentos_necessarios', []),
                tipo_acao=dados_estruturados.get('tipo_acao', '')
            )
            
            # ETAPA 3: CICLO DE REDAÇÃO E VALIDAÇÃO
            print("ETAPA 3: Iniciando Ciclo de Redação e Validação...")
            
            # Seleciona o agente redator ativo (lógica de seleção como antes)
            # ... (código de seleção omitido por brevidade)
            tipo_acao = dados_estruturados.get('tipo_acao', 'Ação Cível')
            if "Trabalhista" in tipo_acao: agente_redator_ativo = self.agente_redator_trabalhista
            # ... etc.
            else: agente_redator_ativo = self.agente_redator_civel

            # COMENTÁRIO: Início do novo ciclo iterativo.
            max_tentativas = 3
            tentativa_atual = 0
            documento_atual = ""
            recomendacoes = []
            
            while tentativa_atual < max_tentativas:
                tentativa_atual += 1
                print(f"\n--- TENTATIVA DE REDAÇÃO Nº {tentativa_atual} ---")
                
                # Chama o redator, passando o feedback das tentativas anteriores (se houver)
                resultado_redacao = agente_redator_ativo.redigir_peticao_completa(
                    dados_estruturados=dados_estruturados,
                    pesquisa_juridica=resultado_pesquisa,
                    documento_anterior=documento_atual,
                    recomendacoes=recomendacoes
                )
                
                if resultado_redacao.get("status") == "erro": return resultado_redacao
                documento_atual = resultado_redacao.get('documento_html', '')
                
                # Envia o rascunho para o validador
                resultado_validacao = self.agente_validador.validar_e_formatar(documento_atual, dados_estruturados)
                
                # Verifica se o documento foi aprovado
                if resultado_validacao.get("status") == "aprovado":
                    print("✅ Documento APROVADO pelo Agente Validador.")
                    break # Sai do ciclo
                
                # Se reprovado, prepara para a próxima tentativa
                recomendacoes = resultado_validacao.get("recomendacoes", [])
                print(f"❌ Documento REPROVADO. Preparando para a tentativa {tentativa_atual + 1} com novas instruções.")
                if tentativa_atual >= max_tentativas:
                    print("⚠️ Número máximo de tentativas atingido. Usando a melhor versão disponível.")

            print("PROCESSAMENTO COMPLETO FINALIZADO!")
            return {
                "status": "sucesso",
                "documento_final": documento_atual,
            }
            
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": str(e)}
