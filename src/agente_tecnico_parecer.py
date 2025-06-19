# agente_tecnico_parecer.py
import os, json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteTecnicoParecer:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.0)
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados"],
            template="""
            Você é um jurista parecerista renomado. Sua missão é analisar uma consulta jurídica e, com base no seu profundo conhecimento, fornecer uma resposta técnica e fundamentada. Você não tem acesso a ferramentas de busca em tempo real.

            DADOS DA CONSULTA:
            {dados_processados}

            SUA TAREFA:
            1.  Entenda a questão central da consulta.
            2.  Busque em seu conhecimento a legislação, doutrina e jurisprudência consolidada sobre o tema.
            3.  Estruture uma análise clara e objetiva para responder à consulta.
            4.  Retorne sua análise completa no formato JSON abaixo.

            Formato Final da Resposta (DEVE ser um JSON válido):
            ```json
            {{
                "fundamentos_legais": [{{"lei": "...", "artigos": "...", "descricao": "..."}}],
                "principios_juridicos": ["..."],
                "jurisprudencia_relevante": "...",
                "analise_juridica_detalhada": "..."
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
            print(f"Erro no Agente Técnico de Parecer: {e}")
            return {"erro": "Falha na análise jurídica do parecer", "detalhes": str(e), "saida_llm": texto_gerado}