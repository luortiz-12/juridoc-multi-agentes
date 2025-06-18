# agente_coletor_dados.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers.structured import StructuredOutputParser, ResponseSchema
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteColetorDados:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0)

        # Esquema de resposta com todos os campos possíveis dos formulários
        # A linha "base_legal_peticao" foi removida conforme a nova arquitetura.
        response_schemas = [
            # ... (todas as outras 60+ linhas de ResponseSchema que você tem, exceto a de 'base_legal_peticao') ...
            ResponseSchema(name="tipo_documento", description="Tipo do documento a ser gerado", type="string"),
            ResponseSchema(name="contratante_nome", description="Nome completo ou Razão Social da primeira parte", type="string"),
            # etc...
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()

        self.prompt_template = PromptTemplate(
            input_variables=["dados_brutos"],
            partial_variables={"format_instructions": self.format_instructions},
            template="""
            Você é um assistente especializado em extrair e estruturar informações de dados brutos para a criação de documentos jurídicos.
            Analise os seguintes dados brutos e extraia TODAS as informações relevantes conforme as instruções de formato abaixo.
            Se uma informação específica não estiver presente nos dados brutos, omita o campo correspondente na saída JSON final.
            Dados Brutos:\n{dados_brutos}\n
            Instruções de Formato Geradas Automaticamente:\n{format_instructions}\n
            ---
            **REGRA DE OURO PARA A SAÍDA FINAL:**
            Sua resposta DEVE ser um objeto JSON VÁLIDO e NADA MAIS.
            NÃO escreva nenhum texto explicativo antes ou depois do JSON.
            NÃO envolva o JSON em blocos de código Markdown como ```json.
            Sua resposta deve começar DIRETAMENTE com o caractere `{{` e terminar DIRETAMENTE com o caractere `}}`.
            NÃO inclua vírgulas pendentes (trailing commas).
            ---
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def coletar_e_processar(self, dados_brutos: dict) -> dict:
        dados_para_processar = dados_brutos.get("body", dados_brutos)
        raw_json_string = json.dumps(dados_para_processar, ensure_ascii=False)
        texto_gerado = ""
        try:
            resultado_llm = self.chain.invoke({"dados_brutos": raw_json_string})
            texto_gerado = resultado_llm['text']
            texto_limpo = texto_gerado.strip()
            if '```json' in texto_limpo:
                texto_limpo = texto_limpo.split('```json', 1)[-1]
            if '```' in texto_limpo:
                texto_limpo = texto_limpo.split('```', 1)[0]
            texto_limpo = texto_limpo.strip()
            dados_estruturados = self.output_parser.parse(texto_limpo)
            return dados_estruturados
        except Exception as e:
            print(f"Erro ao fazer o parse da saída do LLM no Agente Coletor: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha ao processar dados de entrada pelo LLM", "detalhes": str(e), "saida_llm": texto_gerado}