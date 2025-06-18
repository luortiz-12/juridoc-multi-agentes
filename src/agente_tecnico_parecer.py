# agente_tecnico_parecer.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteTecnicoParecer:
    """
    Agente especialista em analisar uma consulta jurídica e pesquisar a
    legislação, doutrina e jurisprudência para fundamentar um parecer.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.0)

        # Prompt focado em pesquisa para resposta de consultas.
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados"],
            template=
            """
            Você é um jurista e parecerista renomado, conhecido por sua profundidade técnica e clareza ao responder consultas jurídicas.
            Sua missão é analisar a consulta jurídica apresentada e conduzir uma pesquisa aprofundada para encontrar a legislação, doutrina e jurisprudência aplicáveis que respondam objetivamente à questão.

            **DADOS DA CONSULTA:**
            {dados_processados}

            **SUA TAREFA:**
            1.  **Entenda a Questão Central:** Analise o campo 'consulta_parecer' para identificar as perguntas exatas que precisam ser respondidas.
            2.  **Pesquisa Jurídica Direcionada:** Pesquise artigos de lei, Súmulas do STJ/STF e posições doutrinárias que se apliquem diretamente ao 'assunto_parecer'.
            3.  **Estruture a Análise:** Retorne sua pesquisa em um formato JSON estrito, que servirá de base para a redação do parecer.

            **REGRA DE OURO PARA A SAÍDA:**
            Sua resposta DEVE ser um objeto JSON VÁLIDO e NADA MAIS, começando com `{{` e terminando com `}}`. NÃO use blocos de Markdown.

            **O JSON deve seguir estritamente este formato:**
            {{
                "fundamentos_legais": [
                    {{"lei": "Nome da Lei/Código (ex: Lei nº 13.709/2018 - LGPD)", "artigos": "Art. 7º, I e IX; Art. 9º", "descricao": "Descreve as bases legais do consentimento e do legítimo interesse, e o direito à informação do titular."}}
                ],
                "principios_juridicos": ["Princípio da Finalidade", "Princípio da Necessidade", "Princípio da Transparência"],
                "jurisprudencia_relevante": "Citar uma decisão recente e relevante de um tribunal superior (STJ, TST) ou órgão regulador (ANPD) sobre o tema da consulta.",
                "analise_juridica_detalhada": "Escreva um parágrafo técnico, mas claro, que conecte a legislação e a jurisprudência para formar o raciocínio central que responderá à consulta."
            }}
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, dados_processados: dict) -> dict:
        """Analisa os dados de um parecer e retorna a base jurídica."""
        dados_processados_str = json.dumps(dados_processados, ensure_ascii=False, indent=2)
        texto_gerado = ""

        try:
            resultado_llm = self.chain.invoke({
                "dados_processados": dados_processados_str
            })
            texto_gerado = resultado_llm["text"]

            # Limpeza defensiva do JSON
            texto_limpo = texto_gerado.strip()
            if '```json' in texto_limpo:
                texto_limpo = texto_limpo.split('```json', 1)[-1]
            if '```' in texto_limpo:
                texto_limpo = texto_limpo.split('```', 1)[0]
            texto_limpo = texto_limpo.strip()

            analise_juridica = json.loads(texto_limpo)
            return analise_juridica
        except Exception as e:
            print(f"Erro no Agente Técnico de Parecer: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na análise jurídica do parecer", "detalhes": str(e), "saida_llm": texto_gerado}