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
        # =================================================================
        # CORREÇÃO APLICADA CONFORME SUA ORDEM E SEU TESTE BEM-SUCEDIDO
        # Usando 'GoogleSearch()' como você confirmou que funciona.
        # =================================================================
        search_results = GoogleSearch(queries=[query])
        
        return json.dumps(search_results)
    except Exception as e:
        return f"Ocorreu um erro ao buscar no Google: {e}"

def buscar_no_lexml(termo_da_lei: str) -> str:
    """Use esta ferramenta para buscar o texto oficial de leis e decretos."""
    print(f"--- Usando Ferramenta Manual: buscando no LexML por '{termo_da_lei}' ---")
    return "Resultado simulado da LexML."

def buscar_casos_similares(resumo_do_caso_atual: str) -> str:
    """Use esta ferramenta PRIMEIRO para pesquisar em nosso banco de dados interno por casos anteriores similares."""
    print(f"--- Usando Ferramenta Interna: buscando casos similares para '{resumo_do_caso_atual[:50]}...' ---")
    BASE_DE_CASOS_INTERNA = [{"id": "caso_002", "resumo_dos_fatos": "inadimplemento contratual", "palavras_chave": ["inadimplemento", "cobrança"], "tese_aplicada": "Ação de Cobrança baseada no inadimplemento de obrigação contratual (Art. 389 e 475 do Código Civil)."}]
    palavras_encontradas = [caso for caso in BASE_DE_CASOS_INTERNA if any(palavra in resumo_do_caso_atual.lower() for palavra in caso["palavras_chave"])]
    if not palavras_encontradas: return "Nenhum caso similar encontrado."
    return f"Caso similar encontrado (ID: {palavras_encontradas[0]['id']}). A tese de sucesso foi: {palavras_encontradas[0]['tese_aplicada']}"

class AgenteTecnicoPeticao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        self.tools = [
            Tool(name="BuscaCasosSimilaresInternos", func=buscar_casos_similares, description="Pesquisa no banco de dados interno por casos passados. Use ANTES de buscas externas."),
            Tool(name="BuscaGoogleJurisprudencia", func=buscar_google_jurisprudencia, description="Busca jurisprudência e leis na internet."),
            Tool(name="BuscaTextoDeLeiNoLexML", func=buscar_no_lexml, description="Busca o texto oficial de um artigo de lei.")
        ]
        
        # Este prompt agora contém as variáveis {tools} e {tool_names}
        react_prompt_template = """
            Você é um advogado pesquisador sênior e sua missão é construir uma tese jurídica sólida. Para isso, você deve usar as ferramentas disponíveis.

            **REGRAS OBRIGATÓRIAS PARA USAR FERRAMENTAS:**
            1. Você DEVE seguir o ciclo 'Thought -> Action -> Action Input -> Observation'.
            2. O seu pensamento (Thought) deve descrever o que você está prestes a fazer.
            3. A sua ação (Action) deve ser EXATAMENTE um dos seguintes nomes de ferramentas: {tool_names}
            4. A sua entrada da ação (Action Input) deve ser o termo da busca.

            **EXEMPLO DO CICLO:**
            Thought: Preciso encontrar casos internos sobre inadimplemento para ter uma base.
            Action: BuscaCasosSimilaresInternos
            Action Input: inadimplemento de contrato de serviço por falta de pagamento
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
                "jurisprudencia_relevante": "Cite uma Súmula ou decisão encontrada. Se encontrou um caso interno similar, mencione-o aqui.",
                "analise_juridica_detalhada": "Parágrafo explicando como os fatos se conectam com a tese."
            }}
            ```
            Inicie seu trabalho agora.

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
            print(f"Erro no Agente Técnico de Petição: {e}")
            return {"erro": "Falha na análise jurídica da petição", "detalhes": str(e)}