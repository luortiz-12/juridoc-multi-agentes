# Agente Jurídico Técnico

"""
Este script implementa o Agente Jurídico Técnico, responsável por identificar normas aplicáveis,
fundamentos legais, artigos e jurisprudência com base nos dados coletados.
"""

import os
import json
import requests
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.tools import tool

# (As ferramentas e a base de dados jurídica permanecem as mesmas)
# ...

class AgenteJuridicoTecnico:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0)
        
        self.tools = [
            # ... (lista de ferramentas) ...
        ]

        self.prompt_template = PromptTemplate(
            input_variables=["tipo_documento", "dados_processados"],
            template=
            """
            Você é um especialista jurídico com conhecimento aprofundado do ordenamento jurídico brasileiro.
            Sua tarefa é identificar os fundamentos legais, artigos, princípios e jurisprudência relevantes
            para a criação de um {tipo_documento} com base nos seguintes dados processados.

            Dados Processados (JSON e contexto adicional):
            {dados_processados}

            Considere os seguintes pontos:
            - **Robustez a dados vazios:** Se um campo nos 'Dados Processados' estiver vazio, nulo ou não aplicável, ignore-o.
            - Para 'contrato', foque em artigos do Código Civil relacionados a contratos.
            - Para 'peticao', identifique artigos da Constituição, Código Civil, CPC e Código Penal (se aplicável).
            - Sintetize as informações de forma clara e objetiva, apresentando os fundamentos jurídicos mais pertinentes.

            ---
            **REGRA DE OURO PARA A SAÍDA:**
            Sua resposta DEVE ser um objeto JSON VÁLIDO e NADA MAIS.
            NÃO escreva nenhum texto explicativo antes ou depois do JSON.
            NÃO envolva o JSON em blocos de código Markdown como ```json.
            Sua resposta deve começar DIRETAMENTE com o caractere `{{` e terminar DIRETAMENTE com o caractere `}}`.
            
            O JSON deve seguir estritamente este formato:
            {{
                "fundamentos_legais": [
                    {{"lei": "Nome da Lei/Código", "artigos": "Artigos relevantes", "descricao": "Breve descrição"}}
                ],
                "principios_juridicos": ["Princípio 1", "Princípio 2"],
                "jurisprudencia_relevante": "Exemplo de jurisprudência ou súmula relevante",
                "analise_juridica_detalhada": "Uma análise textual detalhada dos fundamentos e como eles se aplicam ao caso."
            }}
            
            NÃO inclua vírgulas pendentes (trailing commas).
            ---
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, tipo_documento: str, dados_processados: dict) -> dict:
        dados_processados_str = json.dumps(dados_processados, ensure_ascii=False)
        informacoes_ferramentas = ""
        # ... (lógica de simulação de ferramentas) ...
        dados_para_prompt = f"{dados_processados_str}{informacoes_ferramentas}"
        
        texto_gerado = ""

        try:
            resultado_llm = self.chain.invoke({
                "tipo_documento": tipo_documento,
                "dados_processados": dados_para_prompt
            })
            
            texto_gerado = resultado_llm["text"]

            texto_limpo = texto_gerado.strip()
            if '```json' in texto_limpo:
                texto_limpo = texto_limpo.split('```json', 1)[-1]
            if '```' in texto_limpo:
                texto_limpo = texto_limpo.split('```', 1)[0]
            texto_limpo = texto_limpo.strip()
            
            analise_juridica = json.loads(texto_limpo)
            return analise_juridica
            
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON da saída do LLM no Agente Jurídico Técnico: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na análise jurídica", "detalhes": str(e), "saida_llm": texto_gerado}
        
        except Exception as e:
            print(f"Erro inesperado no Agente Jurídico Técnico: {e}")
            return {"erro": "Falha inesperada na análise jurídica", "detalhes": str(e), "saida_llm": texto_gerado}

# (O bloco 'if __name__ == "__main__":' permanece o mesmo)