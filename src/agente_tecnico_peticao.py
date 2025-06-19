# agente_tecnico_peticao.py

import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

# Ferramenta 1: Busca online real
def buscar_google_jurisprudencia(query: str) -> str:
    """Use esta ferramenta para buscar jurisprudência, súmulas, artigos de lei e notícias jurídicas na internet."""
    print(f"--- Usando Ferramenta: buscando no Google por '{query}' ---")
    try:
        # Usando o comando que você confirmou que funciona no seu ambiente.
        search_results = GoogleSearch(queries=[query])
        return json.dumps(search_results)
    except Exception as e:
        return f"Ocorreu um erro ao buscar no Google: {e}"

# Ferramenta 2: Placeholder para uma API de legislação futura
def buscar_no_lexml(termo_da_lei: str) -> str:
    """Use esta ferramenta para buscar o texto oficial de leis e decretos."""
    print(f"--- Usando Ferramenta Manual: buscando no LexML por '{termo_da_lei}' ---")
    return "Resultado simulado da LexML."

# REMOVIDO: A ferramenta de busca em casos similares (RAG) foi retirada conforme solicitado.

class AgenteTecnicoPeticao:
    """
    Agente especialista que usa ferramentas de busca online para pesquisar e
    construir a tese jurídica para uma petição.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        
        # ATUALIZADO: A lista de ferramentas agora contém apenas as ferramentas online.
        self.tools = [
            Tool(
                name="BuscaGoogleJurisprudencia",
                func=buscar_google_jurisprudencia,
                description="Busca jurisprudência, leis e notícias jurídicas na internet. Essencial para fundamentar petições."
            ),
            Tool(
                name="BuscaTextoDeLeiNoLexML",
                func=buscar_no_lexml,
                description="Busca o texto oficial de um artigo de lei específico."
            )
        ]
        
        # ATUALIZADO: O prompt foi simplificado para focar apenas nas ferramentas online.
        react_prompt_template = """
            Você é um advogado pesquisador sênior e sua missão é construir uma tese jurídica sólida. Para isso, você deve usar as ferramentas de pesquisa online disponíveis.

            **REGRAS OBRIGATÓRIAS PARA USAR FERRAMENTAS:**
            1. Você DEVE seguir o ciclo 'Thought -> Action -> Action Input -> Observation'.
            2. O seu pensamento (Thought) deve descrever o que você está prestes a fazer.
            3. A sua ação (Action) deve ser EXATAMENTE um dos seguintes nomes de ferramentas: {tool_names}
            4. A sua entrada da ação (Action Input) deve ser o termo da busca.

            **EXEMPLO DO CICLO:**
            Thought: Preciso encontrar jurisprudência recente sobre dano moral por inscrição indevida no Serasa.
            Action: BuscaGoogleJurisprudencia
            Action Input: jurisprudência STJ dano moral inscrição indevida Serasa
            Observation: [O resultado da ferramenta será inserido aqui]

            **FINALIZAÇÃO:**
            Quando você tiver coletado todas as informações necessárias, você DEVE parar de usar ferramentas e fornecer sua resposta final, que deve ser **APENAS E SOMENTE** o objeto JSON, sem nenhum outro texto antes ou depois.

            **DADOS DO CASO ATUAL:**
            {input}

            **Formato Final da Resposta (JSON Válido):**
            ```json
            {{
                "fundamentos_legais": [{{"lei": "...", "artigos": "...", "descricao": "..."}}],
                "principios_juridicos": ["..."],
                "jurisprudencia_relevante": "Cite uma Súmula ou o resumo de uma decisão encontrada com as ferramentas.",
                "analise_juridica_detalhada": "Parágrafo explicando como os fatos se conectam com a tese jurídica encontrada."
            }}
            ```
            Inicie seu trabalho agora.

            Thought: {agent_scratchpad}
        """
        
        # A formatação do prompt com .partial() é mantida, pois é a correção para o ValueError.
        tool_names = ", ".join([tool.name for tool in self.tools])
        # A renderização das ferramentas agora é feita via .partial() para maior robustez
        # Embora o LangChain possa fazer isso implicitamente, ser explícito evita erros.
        # Formatando a lista de ferramentas para o prompt
        tools_string = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        
        prompt = ChatPromptTemplate.from_template(react_prompt_template).partial(
            tool_names=tool_names,
            tools=tools_string
        )
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
        
    def analisar_dados(self, dados_processados: dict) -> dict:
        dados_processados_str = json.dumps(dados_processados, ensure_ascii=False, indent=2)
        try:
            # O scratchpad é passado automaticamente pelo AgentExecutor, não precisa estar no invoke.
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