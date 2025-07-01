import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun  # Ferramenta real de busca

# Ferramenta de busca real na internet (substitui GoogleSearch fictício)
buscar_web = DuckDuckGoSearchRun()

def buscar_jurisprudencia_internet(query: str) -> str:
    """Usa busca real na web para encontrar jurisprudência, leis e artigos jurídicos."""
    print(f"--- Usando DuckDuckGoSearch para: '{query}' ---")
    try:
        results = buscar_web.run(query)
        return results
    except Exception as e:
        return f"Ocorreu um erro na busca online: {e}"

class AgenteTecnicoPeticao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=llm_api_key,
            temperature=0.1
        )

        self.tools = [
            Tool(
                name="BuscaWebJuridica",
                func=buscar_jurisprudencia_internet,
                description="Busca jurisprudência, notícias jurídicas e artigos de lei atualizados na internet. Use sempre que precisar confirmar fundamentos legais ou jurisprudência recente."
            )
        ]

        react_prompt_template = """
            Você é um advogado pesquisador sênior e sua missão é construir uma tese jurídica sólida. Para isso, você deve usar a ferramenta disponível.

            **REGRAS OBRIGATÓRIAS:**
            1. Use o formato 'Thought -> Action -> Action Input -> Observation'.
            2. Use apenas a ferramenta: {tool_names}

            **ESTRATÉGIA EM CASO DE ERROS OU FALTA DE RESULTADOS:**
            - Reformule a busca.
            - Caso não consiga encontrar, use seu conhecimento interno jurídico para gerar a melhor resposta possível.

            **Ferramenta disponível:**
            {tools}

            **DADOS DO CASO:**
            {input}

            **Formato final da resposta (somente JSON):**
            ```json
            {{
              "fundamentos_legais": [{{"lei": "...", "artigos": "...", "descricao": "..."}}],
              "principios_juridicos": ["..."],
              "jurisprudencia_relevante": "...",
              "analise_juridica_detalhada": "..."
            }}
            ```

            Inicie seu raciocínio agora.

            Thought: {agent_scratchpad}
        """

        prompt = ChatPromptTemplate.from_template(react_prompt_template)

        tool_names = ", ".join([tool.name for tool in self.tools])
        tools_string = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        prompt = prompt.partial(tool_names=tool_names, tools=tools_string)

        agent = create_react_agent(self.llm, self.tools, prompt)

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=8
        )

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
            print(f"Erro na análise jurídica: {e}")
            return {"erro": "Falha na análise jurídica", "detalhes": str(e)}