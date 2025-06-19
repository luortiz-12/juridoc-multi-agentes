# agente_tecnico_estudo_caso.py
import os, json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

def buscar_google_jurisprudencia(query: str) -> str:
    print(f"--- Usando Ferramenta: buscando no Google por '{query}' ---")
    try:
        # --- CORREÇÃO DE SINTAXE APLICADA ---
        search_results = Google Search(queries=[query])
        return json.dumps(search_results)
    except Exception as e:
        return f"Ocorreu um erro ao buscar no Google: {e}"

class AgenteTecnicoEstudoCaso:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.0)
        self.tools = [Tool(name="BuscaGoogleJurisprudencia", func=buscar_google_jurisprudencia, description="Busca doutrina e jurisprudência sobre um tema jurídico para analisar um caso de estudo.")]
        react_prompt_template = """Você é um professor de Direito e pesquisador. Sua missão é decompor um estudo de caso, identificar a questão jurídica central e realizar uma pesquisa para encontrar os fundamentos que iluminam o problema de múltiplos ângulos. Você tem acesso às seguintes ferramentas: {tools}. Use o ciclo Thought/Action/Action Input/Observation. Quando tiver a resposta final, responda APENAS com o objeto JSON. DADOS DO ESTUDO DE CASO: {input}. Formato Final da Resposta (DEVE ser um JSON válido): ```json{{"fundamentos_legais": [{{"lei": "...", "artigos": "...", "descricao": "..."}}], "principios_juridicos": ["..."], "jurisprudencia_relevante": "Cite uma ou mais decisões análogas ou que definam o entendimento sobre a questão central do caso.", "analise_juridica_detalhada": "Resumo da tensão jurídica do caso, conectando os fatos aos fundamentos."}}``` Comece! Thought: {agent_scratchpad}"""
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
            print(f"Erro no Agente Técnico de Estudo de Caso: {e}")
            return {"erro": "Falha na análise jurídica do estudo de caso", "detalhes": str(e)}