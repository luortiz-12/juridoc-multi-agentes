# agente_tecnico_peticao.py

import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

# --- ALTERAÇÃO 1: MELHORANDO O RETORNO DE ERRO DA FERRAMENTA ---
def buscar_google_jurisprudencia(query: str) -> str:
    """Use para buscar jurisprudência, súmulas, artigos de lei e notícias jurídicas na internet."""
    print(f"--- Usando Ferramenta: buscando no Google por '{query}' ---")
    try:
        search_results = GoogleSearch(queries=[query])
        return json.dumps(search_results)
    except Exception as e:
        # A mensagem de erro agora é mais instrutiva para o agente
        return f"Erro ao usar a ferramenta BuscaGoogleJurisprudencia. O erro foi: {e}. Tente reformular sua busca ou use outra ferramenta."

def buscar_no_lexml(termo_da_lei: str) -> str:
    """Use para buscar o texto oficial de leis e decretos pelo nome ou número."""
    print(f"--- Usando Ferramenta Manual: buscando no LexML por '{termo_da_lei}' ---")
    return "Resultado simulado da LexML. Se não encontrar o que precisa, tente a BuscaGoogleJurisprudencia com o nome da lei."

def buscar_casos_similares(resumo_do_caso_atual: str) -> str:
    """Use esta ferramenta PRIMEIRO para pesquisar no banco de dados interno por casos anteriores similares."""
    print(f"--- Usando Ferramenta Interna: buscando casos similares para '{resumo_do_caso_atual[:50]}...' ---")
    # ... (lógica da busca simulada) ...
    return "Nenhum caso similar encontrado no banco de dados interno. Prossiga com a pesquisa externa."

class AgenteTecnicoPeticao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        self.tools = [
            Tool(name="BuscaCasosSimilaresInternos", func=buscar_casos_similares, description="..."),
            Tool(name="BuscaGoogleJurisprudencia", func=buscar_google_jurisprudencia, description="..."),
            Tool(name="BuscaTextoDeLeiNoLexML", func=buscar_no_lexml, description="...")
        ]
        
        # --- ALTERAÇÃO 2: PROMPT COM MANUAL DE CONTINGÊNCIA ---
        react_prompt_template = """
            Você é um advogado pesquisador sênior. Sua missão é construir a melhor tese jurídica usando as ferramentas disponíveis.

            **REGRAS DE USO DAS FERRAMENTAS:**
            1. Siga o ciclo 'Thought -> Action -> Action Input -> Observation'.
            2. Seu pensamento (Thought) deve descrever seu plano.
            3. Sua ação (Action) deve ser EXATAMENTE um destes nomes: {tool_names}

            **MANUAL DE CONTINGÊNCIA E ESTRATÉGIA DE FALLBACK:**
            1.  Se uma ferramenta retornar um ERRO ou um resultado inútil, leia a observação (Observation), pense no que deu errado e **NÃO repita a mesma ação**.
            2.  **TENTE UMA ALTERNATIVA:** Reformule sua busca (Action Input) ou, mais importante, **use outra ferramenta** que pareça mais adequada.
            3.  **PLANO FINAL (FALLBACK):** Se, após tentar usar as ferramentas de forma inteligente, você não conseguir encontrar as informações necessárias, **pare de usar ferramentas**. Use seu vasto conhecimento jurídico interno para preencher o JSON final da melhor forma possível, com base nos dados do caso. Seu objetivo é SEMPRE entregar a análise final, mesmo que as ferramentas falhem.

            **DADOS DO CASO ATUAL:**
            {input}

            **Formato Final da Resposta (APENAS o objeto JSON):**
            ```json
            {{
                "fundamentos_legais": [...],
                "principios_juridicos": [...],
                "jurisprudencia_relevante": "...",
                "analise_juridica_detalhada": "..."
            }}
            ```
            Inicie seu trabalho agora.

            Thought: {agent_scratchpad}
        """
        
        prompt = ChatPromptTemplate.from_template(react_prompt_template)
        
        tool_names = ", ".join([tool.name for tool in self.tools])
        tools_string = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        prompt = prompt.partial(tool_names=tool_names, tools=tools_string)
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True, max_iterations=10) # Aumentamos o número de passos que ele pode dar
        
    def analisar_dados(self, dados_processados: dict) -> dict:
        # (O método analisar_dados permanece o mesmo)
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