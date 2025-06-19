# agente_tecnico_parecer.py
import os, json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

def buscar_google_jurisprudencia(query: str) -> str:
    print(f"--- Usando Ferramenta: buscando no Google por '{query}' ---")
    try:
        search_results = Google Search(queries=[query])
        return json.dumps(search_results)
    except Exception as e:
        return f"Ocorreu um erro ao buscar no Google: {e}"

class AgenteTecnicoParecer:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.0)
        self.tools = [Tool(name="BuscaGoogleJurisprudencia", func=buscar_google_jurisprudencia, description="Busca doutrina, artigos acadêmicos e jurisprudência sobre um tema jurídico específico para fundamentar uma consulta.")]
        react_prompt_template = """
            Você é um jurista e parecerista renomado. Sua missão é analisar a consulta jurídica apresentada e, usando as ferramentas disponíveis, conduzir uma pesquisa aprofundada para encontrar a legislação, doutrina e jurisprudência que respondam objetivamente à questão.
            Você tem acesso às seguintes ferramentas: {tools}
            Para usar uma ferramenta, use o formato:
            Thought: Preciso pesquisar sobre [tema da consulta].
            Action: [nome da ferramenta]
            Action Input: [termo de busca]
            Observation: [resultado da ferramenta]
            Quando tiver a resposta final, responda APENAS com o objeto JSON.

            DADOS DA CONSULTA: {input}

            Formato Final da Resposta (DEVE ser um JSON válido):
            ```json
            {{
                "fundamentos_legais": [{{"lei": "Nome da Lei/Código", "artigos": "Artigos relevantes", "descricao": "Descrição da relevância dos artigos para a consulta."}}],
                "principios_juridicos": ["Princípios que norteiam a discussão."],
                "jurisprudencia_relevante": "Cite uma decisão ou entendimento encontrado com as ferramentas que seja crucial para responder à consulta.",
                "analise_juridica_detalhada": "Análise técnica que conecta os fundamentos para formar o raciocínio central do parecer."
            }}
            ```
            Comece!
            Thought: {agent_scratchpad}
        """
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
            print(f"Erro no Agente Técnico de Parecer: {e}")
            return {"erro": "Falha na análise jurídica do parecer", "detalhes": str(e)}