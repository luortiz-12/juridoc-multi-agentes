# agente_tecnico_peticao.py

import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

def buscar_google_jurisprudencia(query: str) -> str:
    """Use esta ferramenta para buscar jurisprudência, súmulas, artigos de lei e notícias jurídicas na internet."""
    print(f"--- Usando Ferramenta: buscando no Google por '{query}' ---")
    try:
        # --- CORREÇÃO DE SINTAXE APLICADA ---
        # Trocado 'GoogleSearch(...)' pelo comando correto 'Google Search(...)'.
        search_results = Google Search(queries=[query])
        return json.dumps(search_results)
    except Exception as e:
        return f"Ocorreu um erro ao usar a ferramenta BuscaGoogleJurisprudencia. O erro foi: {e}. Tente reformular sua busca ou use outra ferramenta."

def buscar_no_lexml(termo_da_lei: str) -> str:
    """Use esta ferramenta para buscar o texto oficial de leis e decretos."""
    print(f"--- Usando Ferramenta Manual: buscando no LexML por '{termo_da_lei}' ---")
    return "Resultado simulado da LexML. Se não encontrar o que precisa, tente a BuscaGoogleJurisprudencia com o nome da lei."

def buscar_casos_similares(resumo_do_caso_atual: str) -> str:
    """Use esta ferramenta PRIMEIRO para pesquisar em nosso banco de dados interno por casos anteriores similares."""
    print(f"--- Usando Ferramenta Interna: buscando casos similares para '{resumo_do_caso_atual[:50]}...' ---")
    BASE_DE_CASOS_INTERNA = [{"id": "caso_002", "resumo_dos_fatos": "inadimplemento contratual", "palavras_chave": ["inadimplemento", "cobrança"], "tese_aplicada": "Ação de Cobrança baseada no inadimplemento de obrigação contratual (Art. 389 e 475 do Código Civil)."}]
    palavras_encontradas = [caso for caso in BASE_DE_CASOS_INTERNA if any(palavra in resumo_do_caso_atual.lower() for palavra in caso["palavras_chave"])]
    if not palavras_encontradas: return "Nenhum caso similar encontrado no banco de dados interno. Prossiga com a pesquisa externa."
    return f"Caso similar encontrado (ID: {palavras_encontradas[0]['id']}). A tese de sucesso foi: {palavras_encontradas[0]['tese_aplicada']}"

class AgenteTecnicoPeticao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        
        self.tools = [
            Tool(name="BuscaCasosSimilaresInternos", func=buscar_casos_similares, description="Pesquisa no banco de dados interno por casos passados com fatos similares. Use esta ferramenta ANTES de qualquer busca externa."),
            Tool(name="BuscaGoogleJurisprudencia", func=buscar_google_jurisprudencia, description="Busca jurisprudência, leis e notícias jurídicas na internet. Use para encontrar decisões recentes ou para complementar a tese encontrada nos casos internos."),
            Tool(name="BuscaTextoDeLeiNoLexML", func=buscar_no_lexml, description="Busca o texto oficial de um artigo de lei específico quando você já sabe qual é a lei e o artigo.")
        ]
        
        # --- PROMPT ReAct MAIS ROBUSTO ---
        # Inclui regras claras e um manual de contingência para evitar loops.
        react_prompt_template = """
            Você é um advogado pesquisador sênior e sua missão é construir uma tese jurídica sólida. Para isso, você deve usar as ferramentas disponíveis.

            **REGRAS OBRIGATÓRIAS PARA USAR FERRAMENTAS:**
            1. Você DEVE seguir o ciclo 'Thought -> Action -> Action Input -> Observation'.
            2. O seu pensamento (Thought) deve descrever seu plano de pesquisa.
            3. Sua ação (Action) deve ser EXATAMENTE um dos seguintes nomes de ferramentas: {tool_names}

            **MANUAL DE CONTINGÊNCIA E ESTRATÉGIA DE FALLBACK:**
            1. Se uma ferramenta retornar um ERRO ou um resultado inútil, leia a observação (Observation), pense no que deu errado e **NÃO repita a mesma ação**.
            2. **TENTE UMA ALTERNATIVA:** Reformule sua busca (Action Input) ou, mais importante, **use outra ferramenta** que pareça mais adequada.
            3. **PLANO FINAL (FALLBACK):** Se, após tentar usar as ferramentas de forma inteligente, você não conseguir encontrar as informações necessárias, **pare de usar ferramentas**. Use seu vasto conhecimento jurídico interno para preencher o JSON final da melhor forma possível. Seu objetivo é SEMPRE entregar a análise.

            **Você tem acesso às seguintes ferramentas:**
            {tools}

            **DADOS DO CASO ATUAL:**
            {input}

            **Formato Final da Resposta (APENAS o objeto JSON):**
            ```json
            {{
                "fundamentos_legais": [{{"lei": "...", "artigos": "...", "descricao": "..."}}],
                "principios_juridicos": ["..."],
                "jurisprudencia_relevante": "...",
                "analise_juridica_detalhada": "..."
            }}
            ```
            Inicie seu trabalho agora.

            Thought: {agent_scratchpad}
        """
        
        prompt = ChatPromptTemplate.from_template(react_prompt_template)
        
        # Usando o método .partial() para injetar as variáveis de forma segura
        tool_names = ", ".join([tool.name for tool in self.tools])
        tools_string = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        prompt = prompt.partial(tool_names=tool_names, tools=tools_string)
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True, max_iterations=10)

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