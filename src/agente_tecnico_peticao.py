# agente_tecnico_peticao.py
import os, json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteTecnicoPeticao:
    """
    Agente especialista que usa seu conhecimento interno para construir
    a tese jurídica para uma petição.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados"],
            template="""
            Você é um advogado pesquisador sênior com vasto conhecimento do direito brasileiro. Sua missão é analisar os fatos de um caso e, usando seu conhecimento interno, construir a melhor tese jurídica para uma petição. Você não tem acesso à internet.

            DADOS DO CASO:
            {dados_processados}

            SUA TAREFA:
            1.  Analise os fatos e o pedido do cliente.
            2.  Identifique o ramo do direito (Cível, Consumidor, Trabalhista, etc.).
            3.  Com base no seu conhecimento, formule a fundamentação jurídica, citando as leis, artigos e jurisprudência consolidada (Súmulas) mais relevantes.
            4.  Retorne sua análise completa no formato JSON abaixo.

            Formato Final da Resposta (DEVE ser um JSON válido):
            ```json
            {{
                "fundamentos_legais": [{{"lei": "Nome da Lei/Código", "artigos": "Artigos aplicáveis", "descricao": "Explicação da relevância do artigo para o caso."}}],
                "principios_juridicos": ["Princípios jurídicos que se aplicam."],
                "jurisprudencia_relevante": "Cite uma Súmula do STJ/STF/TST ou um entendimento pacificado relevante.",
                "analise_juridica_detalhada": "Um parágrafo explicando como os fatos se conectam com a lei e a jurisprudência para formar a tese da petição."
            }}
            ```
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, dados_processados: dict) -> dict:
        dados_processados_str = json.dumps(dados_processados, ensure_ascii=False, indent=2)
        texto_gerado = ""
        try:
            resultado_llm = self.chain.invoke({"dados_processados": dados_processados_str})
            texto_gerado = resultado_llm['text']
            texto_limpo = texto_gerado.strip()
            if '```json' in texto_limpo: texto_limpo = texto_limpo.split('```json', 1)[-1]
            if '```' in texto_limpo: texto_limpo = texto_limpo.split('```', 1)[0]
            analise_juridica = json.loads(texto_limpo.strip())
            return analise_juridica
        except Exception as e:
            print(f"Erro no Agente Técnico de Petição: {e}")
            return {"erro": "Falha na análise jurídica da petição", "detalhes": str(e), "saida_llm": texto_gerado}