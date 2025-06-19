# agente_tecnico_peticao.py
import os, json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

def buscar_google_jurisprudencia(query: str) -> str:
    print(f"--- Usando Ferramenta: buscando no Google por '{query}' ---")
    try:
        # --- CORREÇÃO AQUI ---
        search_results = Google Search(queries=[query])
        return json.dumps(search_results)
    except Exception as e:
        return f"Ocorreu um erro ao buscar no Google: {e}"

def buscar_no_lexml(termo_da_lei: str) -> str:
    print(f"--- Usando Ferramenta Manual: buscando no LexML por '{termo_da_lei}' ---")
    if "186" in termo_da_lei: return "LexML Resultado: 'Art. 186. Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.'"
    return "Nenhum texto oficial encontrado no LexML."

class AgenteTecnicoPeticao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        self.tools = [Tool(name="BuscaCasosSimilaresInternos", func=lambda q: "Nenhum caso similar encontrado.", description="Pesquisa no banco de dados interno por casos passados. Use ANTES de buscas externas."), Tool(name="BuscaGoogleJurisprudencia", func=buscar_google_jurisprudencia, description="Busca jurisprudência, leis e notícias na internet."), Tool(name="BuscaTextoDeLeiNoLexML", func=buscar_no_lexml, description="Busca o texto oficial de um artigo de lei específico.")]
        react_prompt_template = """Você é um advogado pesquisador sênior. Sua missão é analisar os fatos de um caso e, usando as ferramentas, construir a melhor tese jurídica. Comece usando a BuscaCasosSimilaresInternos. Você tem acesso às seguintes ferramentas: {tools}. Use o ciclo Thought/Action/Action Input/Observation. Quando tiver a resposta final, responda APENAS com o objeto JSON. DADOS DO CASO: {input}. Formato Final da Resposta (JSON válido): ```json{{"fundamentos_legais": [{{"lei": "...", "artigos": "...", "descricao": "..."}}], "principios_juridicos": ["..."], "jurisprudencia_relevante": "Cite uma Súmula ou decisão encontrada. Se encontrou um caso interno similar, mencione-o aqui.", "analise_juridica_detalhada": "Parágrafo explicando como os fatos se conectam com a tese."}}``` Comece! Thought: {agent_scratchpad}"""
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
            print(f"Erro no Agente Técnico de Petição: {e}")
            return {"erro": "Falha na análise jurídica da petição", "detalhes": str(e)}