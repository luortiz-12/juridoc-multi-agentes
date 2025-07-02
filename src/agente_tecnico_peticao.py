# agente_peticao.py
import os
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from pesquisa_juridica import PesquisaJuridica

class AgentePeticao:
    """
    Agente simplificado especializado em gerar petições iniciais.
    Integra pesquisa jurídica via DuckDuckGo para fundamentação legal.
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            openai_api_key=openai_api_key, 
            temperature=0.2
        )
        
        # Inicializar módulo de pesquisa jurídica
        self.pesquisa = PesquisaJuridica()
        
        # Template para análise e estruturação dos dados
        self.prompt_analise = PromptTemplate(
            input_variables=["dados_entrada"],
            template="""
            Você é um advogado especialista em petições iniciais. Analise os dados fornecidos e extraia as informações essenciais para estruturar uma petição.

            DADOS RECEBIDOS:
            {dados_entrada}

            TAREFA: Extraia e organize as seguintes informações:
            1. Tipo de ação/procedimento
            2. Partes envolvidas (autor/requerente e réu/requerido)
            3. Fatos principais do caso
            4. Fundamentos jurídicos necessários
            5. Pedidos específicos
            6. Valor da causa (se aplicável)
            7. Competência/foro

            FORMATO DE RESPOSTA: JSON com as chaves:
            - "tipo_acao": string
            - "autor": dict com nome, cpf/cnpj, endereço, etc.
            - "reu": dict com nome, cpf/cnpj, endereço, etc.
            - "fatos": string descritiva
            - "fundamentos_necessarios": lista de temas jurídicos para pesquisar
            - "pedidos": lista de pedidos específicos
            - "valor_causa": string
            - "competencia": string
            - "observacoes": string com informações adicionais
            """
        )
        
        # Template para redação da petição
        self.prompt_peticao = PromptTemplate(
            input_variables=["dados_estruturados", "pesquisa_juridica"],
            template="""
            Você é um advogado processualista sênior especializado em petições iniciais.

            DADOS ESTRUTURADOS DO CASO:
            {dados_estruturados}

            FUNDAMENTAÇÃO JURÍDICA PESQUISADA:
            {pesquisa_juridica}

            TAREFA: Redija uma petição inicial completa em HTML, seguindo a estrutura formal brasileira.

            ESTRUTURA OBRIGATÓRIA:
            1. Endereçamento ao juízo
            2. Qualificação das partes
            3. Título da ação
            4. DOS FATOS
            5. DO DIREITO (com fundamentação legal pesquisada)
            6. DOS PEDIDOS
            7. Valor da causa
            8. Local, data e assinatura

            REGRAS IMPORTANTES:
            - Use HTML semântico com tags <h1>, <h2>, <p>, <strong>, etc.
            - Para informações não fornecidas, use placeholders claros: [NOME DO ADVOGADO], [OAB/UF], [ENDEREÇO], etc.
            - Cite as leis, jurisprudências e doutrinas encontradas na pesquisa
            - Mantenha linguagem técnica e formal
            - Inclua fundamentação sólida baseada na pesquisa realizada
            - Estruture os pedidos de forma clara e objetiva

            FORMATO: HTML puro, começando com <h1> e sem tags <html>, <head> ou <body>.
            """
        )
        
        self.chain_analise = LLMChain(llm=self.llm, prompt=self.prompt_analise)
        self.chain_peticao = LLMChain(llm=self.llm, prompt=self.prompt_peticao)
    
    def gerar_peticao(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal para gerar uma petição inicial.
        
        Args:
            dados_entrada: Dados recebidos do n8n ou outro sistema
            
        Returns:
            Dict com status e documento HTML gerado
        """
        try:
            print("🚀 Iniciando geração de petição...")
            
            # Etapa 1: Analisar e estruturar dados
            print("📊 Etapa 1: Analisando dados de entrada...")
            dados_estruturados = self._analisar_dados(dados_entrada)
            
            # Etapa 2: Realizar pesquisa jurídica
            print("🔍 Etapa 2: Realizando pesquisa jurídica...")
            pesquisa_juridica = self._realizar_pesquisa_juridica(dados_estruturados)
            
            # Etapa 3: Redigir petição
            print("✍️ Etapa 3: Redigindo petição...")
            peticao_html = self._redigir_peticao(dados_estruturados, pesquisa_juridica)
            
            # Etapa 4: Validar e formatar resultado
            print("✅ Etapa 4: Finalizando...")
            resultado = {
                "status": "sucesso",
                "documento_html": peticao_html,
                "dados_estruturados": dados_estruturados,
                "pesquisa_realizada": pesquisa_juridica.get("resumo_pesquisa", ""),
                "timestamp": self._get_timestamp()
            }
            
            print("🎉 Petição gerada com sucesso!")
            return resultado
            
        except Exception as e:
            print(f"❌ Erro na geração da petição: {e}")
            traceback.print_exc()
            return {
                "status": "erro",
                "mensagem": f"Erro na geração da petição: {str(e)}",
                "detalhes": traceback.format_exc()
            }
    
    def _analisar_dados(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa e estrutura os dados de entrada."""
        try:
            dados_formatados = json.dumps(dados_entrada, indent=2, ensure_ascii=False)
            resposta = self.chain_analise.run(dados_entrada=dados_formatados)
            
            # Tentar parsear como JSON
            try:
                dados_estruturados = json.loads(resposta)
            except json.JSONDecodeError:
                # Se não conseguir parsear, criar estrutura básica
                dados_estruturados = {
                    "tipo_acao": dados_entrada.get("tipo_acao", "Ação não especificada"),
                    "autor": dados_entrada.get("autor", {}),
                    "reu": dados_entrada.get("reu", {}),
                    "fatos": dados_entrada.get("fatos", "Fatos não especificados"),
                    "fundamentos_necessarios": ["direito civil", "código de processo civil"],
                    "pedidos": dados_entrada.get("pedidos", ["Pedido não especificado"]),
                    "valor_causa": dados_entrada.get("valor_causa", "A ser arbitrado"),
                    "competencia": dados_entrada.get("competencia", "Foro competente"),
                    "observacoes": resposta
                }
            
            return dados_estruturados
            
        except Exception as e:
            print(f"⚠️ Erro na análise de dados: {e}")
            # Retornar estrutura mínima em caso de erro
            return {
                "tipo_acao": dados_entrada.get("tipo_acao", "Ação não especificada"),
                "autor": dados_entrada.get("autor", {}),
                "reu": dados_entrada.get("reu", {}),
                "fatos": dados_entrada.get("fatos", "Fatos não especificados"),
                "fundamentos_necessarios": ["direito civil"],
                "pedidos": dados_entrada.get("pedidos", ["Pedido não especificado"]),
                "valor_causa": dados_entrada.get("valor_causa", "A ser arbitrado"),
                "competencia": dados_entrada.get("competencia", "Foro competente"),
                "observacoes": f"Erro na análise: {str(e)}"
            }
    
    def _realizar_pesquisa_juridica(self, dados_estruturados: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza pesquisa jurídica baseada nos fundamentos necessários."""
        try:
            fundamentos = dados_estruturados.get("fundamentos_necessarios", [])
            tipo_acao = dados_estruturados.get("tipo_acao", "")
            
            # Realizar pesquisas específicas
            resultados_pesquisa = self.pesquisa.pesquisar_fundamentos_juridicos(
                fundamentos=fundamentos,
                tipo_acao=tipo_acao
            )
            
            return resultados_pesquisa
            
        except Exception as e:
            print(f"⚠️ Erro na pesquisa jurídica: {e}")
            return {
                "leis": "Pesquisa jurídica não disponível devido a erro técnico.",
                "jurisprudencia": "Consulte jurisprudência específica para o caso.",
                "doutrina": "Consulte doutrina especializada.",
                "resumo_pesquisa": f"Erro na pesquisa: {str(e)}"
            }
    
    def _redigir_peticao(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> str:
        """Redige a petição inicial em HTML."""
        try:
            dados_formatados = json.dumps(dados_estruturados, indent=2, ensure_ascii=False)
            pesquisa_formatada = json.dumps(pesquisa_juridica, indent=2, ensure_ascii=False)
            
            peticao_html = self.chain_peticao.run(
                dados_estruturados=dados_formatados,
                pesquisa_juridica=pesquisa_formatada
            )
            
            return peticao_html
            
        except Exception as e:
            print(f"⚠️ Erro na redação: {e}")
            return f"""
            <h1>PETIÇÃO INICIAL</h1>
            <p><strong>ERRO NA GERAÇÃO:</strong> {str(e)}</p>
            <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
            """
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

