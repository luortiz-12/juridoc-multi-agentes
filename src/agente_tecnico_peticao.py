# agente_tecnico_peticao.py - VERSÃO INTEGRADA COM RAG
import os
import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

class AgenteTecnicoPeticao:
    """
    Agente especialista que analisa os fatos, identifica o tipo de petição
    e constrói a tese jurídica com integração RAG e busca online.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados", "contexto_rag", "busca_online"],
            template="""
            Você é um advogado pesquisador sênior, com profundo conhecimento do ordenamento jurídico brasileiro. Sua missão é analisar os fatos de um caso e construir a tese jurídica mais forte possível para uma petição inicial.

            **DADOS DO CASO (recebidos do formulário N8N):**
            {dados_processados}

            **CONTEXTO RAG DISPONÍVEL:**
            {contexto_rag}

            **BUSCA ONLINE REALIZADA:**
            {busca_online}

            **SUA TAREFA APRIMORADA COM RAG:**

            **1. ANÁLISE E CLASSIFICAÇÃO (Instrução Obrigatória):**
            Sua primeira tarefa é identificar o tipo específico de petição com base nos campos preenchidos. Siga estas regras OBRIGATORIAMENTE:
            - Se algum campo contiver as palavras 'trabalho' ou 'trabalhista' (como 'InfoExtraTrabalhista', 'datadmissaoTrabalhista'), o caso é **TRABALHISTA**. Fundamente sua pesquisa na CLT.
            - Se algum campo contiver a palavra 'crime' ou 'criminal' (como 'datafatoCriminal'), o caso é **PENAL (QUEIXA-CRIME)**. Fundamente sua pesquisa no Código Penal e no Código de Processo Penal.
            - Se algum campo contiver a palavra 'habiesCorpus', o caso é **CONSTITUCIONAL (HABEAS CORPUS)**. Fundamente sua pesquisa no Art. 5º da Constituição Federal e no Código de Processo Penal.
            - Se nenhuma das condições acima for atendida, o caso é **CÍVEL**. Fundamente sua pesquisa no Código Civil e no Código de Processo Civil.
            - Ignore completamente todos os campos que vierem com valor 'null' ou vazios. Baseie sua análise apenas nos campos que contêm informação.

            **2. PESQUISA E FUNDAMENTAÇÃO APRIMORADA:**
            - Use PRIORITARIAMENTE as informações da busca online para fundamentação atualizada
            - Complemente com o contexto RAG dos modelos de petições similares
            - Se busca online falhar, use seu conhecimento interno como fallback
            - Cite leis, artigos e jurisprudência mais recentes encontradas

            **3. ESTRUTURA DA RESPOSTA:**
            Retorne sua análise completa no formato JSON abaixo.

            **Formato Final da Resposta (DEVE ser um JSON válido):**
            ```json
            {{
                "fundamentos_legais": [{{"lei": "Nome do Código ou Lei", "artigos": "Artigos aplicáveis", "descricao": "Explicação da relevância do artigo para o caso."}}],
                "principios_juridicos": ["Princípios jurídicos que se aplicam ao caso específico."],
                "jurisprudencia_relevante": "Cite uma Súmula do STJ/STF/TST ou um entendimento pacificado relevante para a tese.",
                "analise_juridica_detalhada": "Um parágrafo completo e bem fundamentado explicando como os fatos se conectam com a lei e a jurisprudência para formar a tese da petição."
            }}
            ```
            """
        )
    
    def analisar_com_rag(self, dados_processados, contexto_rag="", busca_online=""):
        """
        Análise técnica integrada com RAG e busca online.
        """
        try:
            # Importar sistemas RAG com fallback
            try:
                from rag_simple_knowledge_base import SimpleJuriDocRAG
                from rag_real_online_search import RealJuridicalSearcher
                
                # Obter contexto RAG
                if not contexto_rag:
                    rag = SimpleJuriDocRAG()
                    contexto_rag = rag.get_relevant_context('peticao', dados_processados)
                
                # Realizar busca online
                if not busca_online:
                    searcher = RealJuridicalSearcher()
                    tipo_caso = self._identificar_tipo_caso(dados_processados)
                    busca_online = searcher.buscar_fundamentacao_juridica(tipo_caso, dados_processados)
                    
            except Exception as e:
                print(f"⚠️ RAG/Busca indisponível: {e}")
                contexto_rag = "Sistema RAG temporariamente indisponível"
                busca_online = "Busca online temporariamente indisponível"
            
            # Executar análise
            response = self.llm.invoke(
                self.prompt_template.format(
                    dados_processados=json.dumps(dados_processados, indent=2, ensure_ascii=False),
                    contexto_rag=str(contexto_rag),
                    busca_online=str(busca_online)
                )
            )
            
            return self._processar_resposta(response.content)
            
        except Exception as e:
            print(f"❌ Erro na análise técnica: {e}")
            return self._fallback_analise(dados_processados)
    
    def _identificar_tipo_caso(self, dados):
        """Identifica tipo de caso para busca direcionada."""
        dados_str = str(dados).lower()
        if 'trabalh' in dados_str:
            return 'trabalhista'
        elif 'crime' in dados_str or 'penal' in dados_str:
            return 'penal'
        elif 'habeas' in dados_str:
            return 'constitucional'
        else:
            return 'civil'
    
    def _processar_resposta(self, resposta):
        """Processa resposta do LLM e extrai JSON."""
        try:
            # Extrair JSON da resposta
            inicio = resposta.find('{')
            fim = resposta.rfind('}') + 1
            if inicio != -1 and fim > inicio:
                json_str = resposta[inicio:fim]
                return json.loads(json_str)
            else:
                return {"erro": "Formato de resposta inválido", "resposta_bruta": resposta}
        except Exception as e:
            return {"erro": f"Erro ao processar resposta: {e}", "resposta_bruta": resposta}
    
    def _fallback_analise(self, dados_processados):
        """Análise de fallback sem RAG."""
        try:
            response = self.llm.invoke(f"""
            Analise este caso jurídico e forneça fundamentação básica:
            {json.dumps(dados_processados, indent=2, ensure_ascii=False)}
            
            Retorne JSON com: fundamentos_legais, principios_juridicos, jurisprudencia_relevante, analise_juridica_detalhada
            """)
            return self._processar_resposta(response.content)
        except Exception as e:
            return {
                "fundamentos_legais": [{"lei": "Análise indisponível", "artigos": "N/A", "descricao": f"Erro: {e}"}],
                "principios_juridicos": ["Sistema em recuperação"],
                "jurisprudencia_relevante": "Indisponível temporariamente",
                "analise_juridica_detalhada": "Sistema em modo de emergência - análise manual necessária"
            }

    def analisar_caso(self, dados_processados):
        """
        Método original mantido para compatibilidade.
        """
        return self.analisar_com_rag(dados_processados)

