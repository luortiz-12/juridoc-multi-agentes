# agente_tecnico_peticao.py

import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

# --- FERRAMENTAS DO AGENTE ---

# Ferramenta 1: Busca no Google (Já existente)
def buscar_google_jurisprudencia(query: str) -> str:
    """Use para buscar jurisprudência, súmulas e notícias jurídicas recentes na internet."""
    print(f"--- Usando Ferramenta Externa: buscando no Google por '{query}' ---")
    try:
        search_results = Google Search(queries=[query])
        return json.dumps(search_results)
    except Exception as e:
        return f"Ocorreu um erro ao buscar no Google: {e}"

# Ferramenta 2: Busca em portal de legislação (Placeholder)
def buscar_no_lexml(termo_da_lei: str) -> str:
    """Use para buscar o texto oficial de leis e artigos específicos."""
    print(f"--- Usando Ferramenta Externa: buscando no LexML por '{termo_da_lei}' ---")
    return "Resultado simulado da LexML. (Implementação real necessária)."


# --- NOVA FERRAMENTA ESSENCIAL: BUSCA EM CASOS ANTERIORES (RAG) ---

# 1. Simulação da sua base de conhecimento interna
BASE_DE_CASOS_INTERNA = [
    {
        "id": "caso_001",
        "resumo_dos_fatos": "cliente comprou produto online, veio com defeito, loja se recusou a trocar alegando prazo expirado",
        "palavras_chave": ["consumidor", "vício do produto", "defeito", "troca negada"],
        "tese_aplicada": "Aplicou-se a teoria do vício oculto do Art. 18 do Código de Defesa do Consumidor (CDC), com pedido de inversão do ônus da prova (Art. 6º, VIII do CDC) e dano moral por desvio produtivo do consumidor."
    },
    {
        "id": "caso_002",
        "resumo_dos_fatos": "empresa prestou serviço de design, cliente aprovou a entrega mas não efetuou o pagamento da última parcela do contrato",
        "palavras_chave": ["inadimplemento contratual", "prestação de serviços", "falta de pagamento", "cobrança"],
        "tese_aplicada": "Ação de Cobrança baseada no inadimplemento de obrigação contratual (Art. 389 e 475 do Código Civil), combinada com enriquecimento sem causa (Art. 884 do CC). Pedido de pagamento do principal com juros e correção monetária."
    }
]

# 2. A função que o agente irá chamar
def buscar_casos_similares(resumo_do_caso_atual: str) -> str:
    """
    Use esta ferramenta PRIMEIRO para pesquisar em nosso banco de dados interno por casos anteriores
    que são similares ao caso atual. Isso ajuda a encontrar teses jurídicas que já foram validadas e usadas com sucesso.
    """
    print(f"--- Usando Ferramenta Interna: buscando casos similares para '{resumo_do_caso_atual[:50]}...' ---")
    resumo_do_caso_atual = resumo_do_caso_atual.lower()
    palavras_encontradas = [caso for caso in BASE_DE_CASOS_INTERNA if any(palavra in resumo_do_caso_atual for palavra in caso["palavras_chave"])]
    
    if not palavras_encontradas:
        return "Nenhum caso similar encontrado no banco de dados interno."
    
    # Em um sistema real, aqui entraria um cálculo de similaridade de vetores.
    # Para nossa simulação, retornamos o primeiro que encontrar.
    caso_encontrado = palavras_encontradas[0]
    return f"Caso similar encontrado (ID: {caso_encontrado['id']}). A tese de sucesso aplicada foi: {caso_encontrado['tese_aplicada']}"

# --- FIM DAS FERRAMENTAS ---


class AgenteTecnicoPeticao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        
        # Adicionamos a nova ferramenta à "caixa de ferramentas" do agente
        self.tools = [
            Tool(
                name="BuscaCasosSimilaresInternos",
                func=buscar_casos_similares,
                description="Pesquisa no banco de dados interno do escritório por casos passados com fatos similares. Use esta ferramenta ANTES de buscas externas."
            ),
            Tool(
                name="BuscaGoogleJurisprudencia",
                func=buscar_google_jurisprudencia,
                description="Busca jurisprudência, súmulas e notícias na internet. Use para encontrar decisões recentes ou para complementar a tese encontrada nos casos internos."
            ),
            Tool(
                name="BuscaTextoDeLeiNoLexML",
                func=buscar_no_lexml,
                description="Busca o texto oficial de um artigo de lei específico quando você já sabe qual é."
            )
        ]

        # O prompt é o mesmo, o agente aprenderá a usar a nova ferramenta pela sua descrição.
        react_prompt_template = """
            Você é um advogado pesquisador sênior. Sua missão é analisar os fatos de um caso e, usando as ferramentas disponíveis, construir a melhor tese jurídica.
            Sempre comece usando a ferramenta `BuscaCasosSimilaresInternos` para verificar se já temos uma solução para um problema parecido.
            Você tem acesso às seguintes ferramentas: {tools}
            Use o ciclo Thought/Action/Action Input/Observation. Quando tiver a resposta final, responda APENAS com o objeto JSON.

            DADOS DO CASO: {input}

            Formato Final da Resposta (JSON válido):
            ```json
            {{
                "fundamentos_legais": [{{"lei": "...", "artigos": "...", "descricao": "..."}}],
                "principios_juridicos": ["..."],
                "jurisprudencia_relevante": "Cite uma Súmula ou decisão encontrada. Se encontrou um caso interno similar, mencione-o aqui.",
                "analise_juridica_detalhada": "Parágrafo explicando como os fatos se conectam com a tese, idealmente partindo da tese encontrada no caso interno e complementada pela pesquisa externa."
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
            print(f"Erro no Agente Técnico de Petição: {e}")
            return {"erro": "Falha na análise jurídica da petição", "detalhes": str(e)}