# agente_tecnico_contrato.py
import os, json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteTecnicoContrato:
    """
    Agente especialista que usa seu conhecimento interno para definir a 
    base jurídica para um contrato.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados"],
            template="""
            Você é um advogado sênior, especialista em Direito Contratual. Sua missão é analisar os dados de um futuro contrato e, usando seu vasto conhecimento jurídico interno, construir a melhor tese e fundamentação jurídica. Você não tem acesso a ferramentas externas.

            DADOS DO FUTURO CONTRATO:
            {dados_processados}

            SUA TAREFA:
            1.  Analise os dados para entender o objeto, as partes e as condições do contrato.
            2.  Com base no seu conhecimento, identifique os artigos do Código Civil e os princípios contratuais mais importantes.
            3.  Cite uma jurisprudência ou súmula consolidada que seja relevante para este tipo de contrato.
            4.  Retorne sua análise completa no formato JSON abaixo.

            Formato Final da Resposta (DEVE ser um JSON válido):
            ```json
            {{
                "fundamentos_legais": [{{"lei": "Código Civil", "artigos": "Art. 421 e 422", "descricao": "Princípios da função social do contrato e da boa-fé objetiva."}}],
                "principios_juridicos": ["Pacta Sunt Servanda", "Boa-Fé Objetiva", "Autonomia da Vontade"],
                "jurisprudencia_relevante": "Súmulas do STJ sobre contratos de prestação de serviço ou o tema central do contrato.",
                "analise_juridica_detalhada": "Análise concisa explicando que o contrato será regido pelos princípios e leis identificados, garantindo segurança jurídica."
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
            print(f"Erro no Agente Técnico de Contrato: {e}")
            return {"erro": "Falha na análise jurídica do contrato", "detalhes": str(e), "saida_llm": texto_gerado}