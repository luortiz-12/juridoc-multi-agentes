# agente_tecnico_estudo_caso.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteTecnicoEstudoCaso:
    """
    Agente especialista em analisar um cenário fático (estudo de caso) e
    realizar uma pesquisa jurídica aprofundada sobre os temas envolvidos.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)

        # Prompt focado em pesquisa para análise de casos.
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados"],
            template=
            """
            Você é um professor de Direito e pesquisador sênior, mestre em analisar cenários complexos e identificar os múltiplos pontos de vista jurídicos.
            Sua missão é decompor um estudo de caso, identificar a(s) questão(ões) jurídica(s) central(is) e realizar uma pesquisa aprofundada para encontrar os fundamentos que iluminam o problema.

            **DADOS DO ESTUDO DE CASO:**
            {dados_processados}

            **SUA TAREFA:**
            1.  **Identifique a Questão Central:** Analise os campos 'descricao_caso' e 'contexto_juridico' para identificar o principal dilema ou conflito legal a ser estudado.
            2.  **Pesquisa Abrangente:** O objetivo não é 'vencer' um caso, mas explorá-lo. Pesquise a legislação, os princípios e a jurisprudência aplicáveis, considerando argumentos que poderiam ser usados por todas as partes envolvidas.
            3.  **Estruture a Análise:** Retorne sua pesquisa em um formato JSON estrito, que servirá de base para a redação do estudo de caso.

            **REGRA DE OURO PARA A SAÍDA:**
            Sua resposta DEVE ser um objeto JSON VÁLIDO e NADA MAIS, começando com `{{` e terminando com `}}`. NÃO use blocos de Markdown.

            **O JSON deve seguir estritamente este formato:**
            {{
                "fundamentos_legais": [
                    {{"lei": "Nome da Lei/Código", "artigos": "Artigos relevantes", "descricao": "Descrição de como estes artigos se aplicam aos fatos do caso."}}
                ],
                "principios_juridicos": ["Princípios relevantes que norteiam a discussão do caso"],
                "jurisprudencia_relevante": "Cite uma ou mais decisões de tribunais superiores que sejam análogas ou que definam o entendimento sobre a questão central do caso.",
                "analise_juridica_detalhada": "Escreva um parágrafo denso que resuma a tensão jurídica do caso, conectando os fatos aos fundamentos encontrados. Se houver teses conflitantes, mencione-as brevemente."
            }}
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, dados_processados: dict) -> dict:
        """Analisa os dados de um estudo de caso e retorna a base jurídica."""
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
            print(f"Erro no Agente Técnico de Estudo de Caso: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na análise jurídica do estudo de caso", "detalhes": str(e), "saida_llm": texto_gerado}