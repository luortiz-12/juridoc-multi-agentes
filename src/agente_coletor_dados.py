# agente_coletor_dados.py - Versão 3.0 (Integração N8N)

import json
import re
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v3.0 - Robusto para Integração N8N.
    - Mapeia corretamente os campos variáveis do formulário do site.
    - Identifica o contexto jurídico (Trabalhista, Civil, Criminal) com base nos campos preenchidos.
    - Consolida inteligentemente os fatos de múltiplos campos em uma única narrativa.
    - Extrai os fundamentos jurídicos corretos a partir do contexto real dos fatos.
    - Estrutura os dados de forma limpa para os agentes subsequentes.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v3.0 (N8N)...")
        # Não há necessidade de inicializar LLM aqui, a lógica será baseada em regras e análise de texto.
        print("✅ Agente Coletor pronto para processar dados do N8N.")

    def coletar_e_processar(self, dados_brutos_n8n: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ponto de entrada principal do agente. Recebe o JSON do N8N e retorna a estrutura de dados processada.
        """
        try:
            print("📊 Iniciando coleta e processamento de dados do N8N...")
            
            # ETAPA 1: Identificar o contexto e extrair os dados relevantes
            contexto, dados_relevantes = self._identificar_contexto_e_dados(dados_brutos_n8n)
            print(f"🔍 Contexto jurídico identificado: {contexto}")

            # ETAPA 2: Consolidar os fatos em uma única narrativa
            fatos_consolidados = self._consolidar_fatos(dados_relevantes)
            
            # ETAPA 3: Extrair os fundamentos jurídicos com base nos fatos consolidados
            fundamentos = self._extrair_fundamentos_necessarios(fatos_consolidados, contexto)
            print(f"🔑 Fundamentos extraídos para pesquisa: {fundamentos}")

            # ETAPA 4: Montar a estrutura final e limpa
            dados_estruturados = self._montar_estrutura_final(dados_relevantes, fatos_consolidados, fundamentos, contexto)
            
            print("✅ Dados coletados e estruturados com sucesso.")
            return {
                "status": "sucesso",
                "dados_estruturados": dados_estruturados
            }

        except Exception as e:
            print(f"❌ Erro crítico no Agente Coletor de Dados: {e}")
            traceback.print_exc()
            return {
                "status": "erro",
                "erro": f"Falha no processamento dos dados de entrada: {e}"
            }

    def _identificar_contexto_e_dados(self, dados_brutos: Dict[str, Any]) -> (str, Dict[str, Any]):
        """
        Analisa os campos preenchidos para determinar a área do direito e extrair os dados brutos relevantes.
        """
        # COMENTÁRIO: Esta função é a nova inteligência central. Ela verifica quais campos específicos de cada área
        # foram preenchidos para decidir o tipo de ação.
        
        dados_relevantes = {k: v for k, v in dados_brutos.items() if v is not None and str(v).strip() != ""}

        # Verificação prioritária para casos trabalhistas
        campos_trabalhistas = ['datadmissaoTrabalhista', 'salarioTrabalhista', 'motivosaidaTrablhista', 'InfoExtraTrabalhista']
        if any(campo in dados_relevantes for campo in campos_trabalhistas):
            return "Ação Trabalhista", dados_relevantes

        # Adicionar outras lógicas para Civil, Criminal, etc. aqui
        # Exemplo para Criminal:
        campos_criminais = ['datafatoCriminal', 'localfatoCriminal', 'NomeVitimaCriminal']
        if any(campo in dados_relevantes for campo in campos_criminais):
            return "Queixa-Crime", dados_relevantes

        # Fallback para Cível
        return "Ação Cível", dados_relevantes

    def _consolidar_fatos(self, dados: Dict[str, Any]) -> str:
        """
        Junta informações de múltiplos campos de texto para criar uma narrativa de fatos unificada.
        """
        # COMENTÁRIO: Esta função resolve o problema de informações espalhadas.
        # Ela constrói uma história completa para o Agente Redator.
        narrativa = []
        
        if dados.get("fatos"):
            narrativa.append(str(dados["fatos"]))
        
        # Consolidação específica para dados trabalhistas
        if dados.get("jornadaTrabalhista"):
            narrativa.append(f"A jornada de trabalho era a seguinte: {dados['jornadaTrabalhista']}.")
        if dados.get("motivosaidaTrablhista"):
            narrativa.append(f"O motivo da saída foi: {dados['motivosaidaTrablhista']}.")
        if dados.get("InfoExtraTrabalhista"):
            narrativa.append(f"Informações adicionais relevantes: {dados['InfoExtraTrabalhista']}.")
            
        # Adicionar outras consolidações para Civil, Criminal, etc. aqui

        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str) -> List[str]:
        """
        Extrai os termos jurídicos chave dos fatos consolidados para guiar a pesquisa.
        Esta é a correção para o bug da pesquisa genérica.
        """
        # COMENTÁRIO: Lógica aprimorada para extrair os termos corretos.
        # Agora, a pesquisa será muito mais precisa.
        fundamentos = set()
        texto_analise = fatos.lower()

        if contexto == "Ação Trabalhista":
            fundamentos.add("direito trabalhista")
            fundamentos.add("CLT")
            if "pejotização" in texto_analise or "pessoa jurídica" in texto_analise or "abrir uma empresa" in texto_analise:
                fundamentos.update(["reconhecimento de vínculo empregatício", "pejotização fraude trabalhista", "artigo 3º da CLT requisitos", "princípio da primazia da realidade", "subordinação jurídica"])
            if "horas extras" in texto_analise:
                fundamentos.update(["horas extras", "CLT art. 59"])
            if "assédio moral" in texto_analise or "humilhante" in texto_analise:
                fundamentos.update(["assédio moral", "danos morais"])
            if "estabilidade" in texto_analise or "doença ocupacional" in texto_analise:
                fundamentos.update(["doença ocupacional", "estabilidade acidentária", "Lei 8.213/91 art. 118", "danos morais acidentários"])
            if not fundamentos: # Fallback
                fundamentos.add("verbas rescisórias")
        
        # Adicionar lógicas para outras áreas aqui
        
        return list(fundamentos) if fundamentos else ["direito civil", "código civil"]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        """
        Monta o dicionário final com os dados limpos e estruturados.
        """
        # COMENTÁRIO: Mapeamento dos novos nomes de campos do N8N para a estrutura interna padronizada.
        autor = {
            "nome": dados.get("clienteNome", "[NOME DO AUTOR]"),
            "qualificacao": dados.get("qualificacaoCliente", "[QUALIFICAÇÃO DO AUTOR]")
        }
        reu = {
            "nome": dados.get("nomedaParte", "[NOME DO RÉU]"),
            "qualificacao": dados.get("Qualificação", "[QUALIFICAÇÃO DO RÉU]")
        }
        
        estrutura_final = {
            "autor": autor,
            "reu": reu,
            "tipo_acao": contexto,
            "fatos": fatos_consolidados,
            "pedidos": dados.get("pedido", "[PEDIDOS A SEREM ESPECIFICADOS]"),
            "valor_causa": f"R$ {dados.get('valorCausa', '0.00')}",
            "documentos": dados.get("documentos", ""),
            "fundamentos_necessarios": fundamentos,
            "competencia": "Justiça do Trabalho" if contexto == "Ação Trabalhista" else "Justiça Comum",
            "observacoes": f"Documentos anexos: {dados.get('documentos', 'N/A')}",
            "urgencia": False
        }
        
        # Adiciona dados específicos do contrato de trabalho, se existirem
        if contexto == "Ação Trabalhista":
            estrutura_final.update({
                "data_admissao": dados.get("datadmissaoTrabalhista"),
                "data_demissao": dados.get("datademissaoTrabalhista"),
                "salario": dados.get("salarioTrabalhista"),
                "cargo": dados.get("cargo", "[CARGO A SER INFORMADO]"), # Assumindo que um campo 'cargo' possa existir
                "jornada": dados.get("jornadaTrabalhista"),
                "motivo_saida": dados.get("motivosaidaTrablhista")
            })

        return estrutura_final
