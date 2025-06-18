# agente_redator_contrato.py
import os, json, sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedatorContrato:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        prompt_template_base = """
            Você é um advogado especialista na redação de contratos.
            {instrucoes_de_revisao}
            **Dados do Contrato:**
            {dados_processados_formatados}
            **Análise Jurídica e Fundamentação:**
            {analise_juridica_formatada}
            **SUA TAREFA:**
            Redija o texto completo de um contrato em HTML, seguindo as regras abaixo.
            **REGRAS:**
            1. Título: Comece com <h1>TÍTULO DO CONTRATO</h1>.
            2. Qualificação das Partes: Apresente as partes usando o jargão 'Por este instrumento particular...'.
            3. Cláusulas: Estruture em cláusulas numeradas: <h2>CLÁUSULA PRIMEIRA - DO OBJETO</h2>, etc.
            4. Fechamento: Inclua parágrafo de fechamento e campos para assinaturas.
            5. SEM PLACEHOLDERS.
            6. Formato de Saída: HTML puro, começando com <h1>.
        """
        self.prompt = PromptTemplate(input_variables=["instrucoes_de_revisao", "dados_processados_formatados", "analise_juridica_formatada"], template=prompt_template_base)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def _format_data_for_prompt(self, data: dict) -> str:
        # (O código deste método é o mesmo do agente de petição)
        # ...
        return "" # Mantenha seu código aqui.

    def redigir_documento(self, dados_processados: dict, analise_juridica: dict, documento_anterior: str = None) -> dict:
        # (A lógica deste método é a mesma do agente de petição)
        # ...
        return {} # Mantenha seu código aqui.