# Agente de Validação

"""
Este script implementa o Agente de Validação, responsável por verificar a coerência lógica,
estrutura e formato do documento jurídico gerado, além de identificar erros.
"""

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteValidacao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0)

        self.prompt_template = PromptTemplate(
            input_variables=["documento_gerado", "dados_processados", "analise_juridica"],
            template=
            """
            Você é um Agente de Validação Jurídica, com a tarefa de revisar e validar documentos jurídicos.
            Analise o `documento_gerado` com base nos `dados_processados` (dados originais do formulário) e na `analise_juridica` (fundamentos legais).
            
            Seu objetivo é verificar, de forma minuciosa e crítica:
            1.  **Coerência Lógica e Jurídica:** ...
            2.  **Estrutura e Formato:** ...
            3.  **Completude e Elaboração:** ...
            4.  **Fundamentação Legal:** ...
            5.  **Erros:** ...

            **Documento Gerado (HTML):**
            {documento_gerado}

            **Dados Processados (para referência):**
            {dados_processados}

            **Análise Jurídica (para referência):**
            {analise_juridica}

            **Instruções para a Análise e Formato da Saída:**
            ... (resto das instruções de análise) ...

            **REGRA DE OURO PARA A SAÍDA:**
            Sua resposta DEVE ser um objeto JSON VÁLIDO e NADA MAIS.
            NÃO escreva nenhum texto explicativo antes ou depois do JSON.
            NÃO envolva o JSON em blocos de código Markdown como ```json.
            Sua resposta deve começar DIRETAMENTE com o caractere `{{` e terminar DIRETAMENTE com o caractere `}}`.
            
            O JSON deve seguir estritamente este formato:
            {{
                "status": "aprovado" ou "revisar",
                "sugestoes_melhoria": [
                    {{"secao": "Seção do documento", "descricao": "Descrição da sugestão de melhoria."}}
                ]
            }}
            
            Se o status for "aprovado", a lista `sugestoes_melhoria` DEVE estar vazia.
            NÃO inclua vírgulas pendentes (trailing commas).
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def validar_documento(self, documento_gerado: str, dados_processados: dict, analise_juridica: dict) -> dict:
        dados_processados_str = json.dumps(dados_processados, indent=2, ensure_ascii=False)
        analise_juridica_str = json.dumps(analise_juridica, indent=2, ensure_ascii=False)
        texto_gerado = ""

        try:
            resultado_llm = self.chain.invoke({
                "documento_gerado": documento_gerado,
                "dados_processados": dados_processados_str,
                "analise_juridica": analise_juridica_str
            })
            
            texto_gerado = resultado_llm["text"]

            texto_limpo = texto_gerado.strip()
            
            if '```json' in texto_limpo:
                texto_limpo = texto_limpo.split('```json', 1)[-1]
            
            if '```' in texto_limpo:
                texto_limpo = texto_limpo.split('```', 1)[0]
                
            texto_limpo = texto_limpo.strip()

            validacao_resultado = json.loads(texto_limpo)
            return validacao_resultado
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON da saída do LLM no Agente de Validação: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na validação (JSON inválido)", "detalhes": str(e), "saida_llm": texto_gerado}
        except Exception as e:
            print(f"Erro inesperado no Agente de Validação: {e}")
            return {"erro": "Falha inesperada na validação", "detalhes": str(e), "saida_llm": ""}

# (O bloco 'if __name__ == "__main__":' permanece o mesmo)