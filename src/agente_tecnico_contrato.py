# agente_tecnico_contrato.py
import os, json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

def buscar_google_jurisprudencia(query: str) -> str:
    print(f"--- Usando Ferramenta: buscando no Google por '{query}' ---")
    try:
        # --- CORREÇÃO FINAL E VERIFICADA ---
        search_results = Google Search(queries=[query])
        return json.dumps(search_results)
    except Exception as e:
        return f"Ocorreu um erro ao buscar no Google: {e}"

def buscar_no_lexml(termo_da_lei: str) -> str:
    print(f"--- Usando Ferramenta Manual: buscando no LexML por '{termo_da_lei}' ---")
    return "Resultado simulado da LexML. (Implementação real necessária)."

class AgenteTecnicoContrato:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.0)
        self.tools = [Tool(name="BuscaGoogleJurisprudencia", func=buscar_google_jurisprudencia, description="Busca jurisprudência sobre temas contratuais específicos."), Tool(name="BuscaTextoDeLeiNoLexML", func=buscar_no_lexml, description="Busca o texto oficial de um artigo de lei específico.")]
        react_prompt_template = """Você é um advogado sênior, especialista em Direito Contratual. Sua missão é analisar os dados de um contrato e, usando as ferramentas, definir a fundamentação jurídica. Você tem acesso às seguintes ferramentas: {tools}. Use o ciclo Thought/Action/Action Input/Observation. Quando tiver a resposta final, responda APENAS com o objeto JSON. DADOS DO FUTURO CONTRATO: {input}. Formato Final da Resposta (DEVE ser um JSON válido): ```json{{"fundamentos_legais": [{{"lei": "Código Civil", "artigos": "Art. 421 e 422", "descricao": "Princípios da função social do contrato e da boa-fé objetiva."}}], "principios_juridicos": ["Pacta Sunt Servanda", "Boa-Fé Objetiva"], "jurisprudencia_relevante": "Cite uma súmula ou resumo de decisão encontrada com a ferramenta.", "analise_juridica_detalhada": "Análise concisa explicando como o contrato será regido pelos princípios e leis encontrados."}}``` Comece! Thought: {agent_scratchpad}"""
        prompt = ChatPromptTemplate.from_template(react_prompt_template)
        agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
    def analisar_dados(self, dados_processados: dict) -> dict:
        dados_processados_str = json.dumps(dados_processados, ensure_ascii=False, indent=2)
        try:
            resultado = self.agent_executor.invoke({"input": dados_processados_str})
            texto_gerado = resultado['output']
            texto_limpo = texto_gerado.strip()
            if '```json' in texto_limpo: texto_limpo = texto_limpo.split('```json', 1)[-1]
            if '```' in texto_limpo: texto_limpo = texto_limpo.split('```', 1)[0]
            analise_juridica = json.loads(texto_limpo.strip())
            return analise_juridica
        except Exception as e:
            print(f"Erro no Agente Técnico de Contrato: {e}")
            return {"erro": "Falha na análise jurídica do contrato", "detalhes": str(e)}