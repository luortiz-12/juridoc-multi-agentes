# agente_tecnico_contrato.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteTecnicoContrato:
    """
    Agente especialista em analisar dados de um futuro contrato e definir
    a fundamentação jurídica e os princípios que regerão o acordo.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0.1)

        # Prompt 100% focado em análise contratual
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados"],
            template=
            """
            Você é um advogado sênior, especialista em Direito Contratual e Empresarial no Brasil.
            Sua missão é analisar os dados de um futuro contrato e, a partir deles, definir a fundamentação jurídica e os princípios que regerão este acordo.

            **DADOS DO FUTURO CONTRATO:**
            {dados_processados}

            **SUA TAREFA:**
            1.  **Analise os Dados:** Entenda o objeto do contrato, as partes envolvidas, os valores, prazos e penalidades.
            2.  **Pesquisa Jurídica:** Com base na sua análise, identifique os fundamentos legais mais fortes. Foque em artigos do Código Civil (Teoria Geral dos Contratos, Contratos em Espécie), e leis específicas se aplicável.
            3.  **Identifique Princípios:** Determine os princípios contratuais essenciais para este acordo, como 'Pacta Sunt Servanda', 'Boa-Fé Objetiva', 'Função Social do Contrato'.
            4.  **Estruture a Análise:** Retorne sua pesquisa em um formato JSON estrito.

            **REGRA DE OURO PARA A SAÍDA:**
            Sua resposta DEVE ser um objeto JSON VÁLIDO e NADA MAIS, começando com `{{` e terminando com `}}`.
            NÃO use blocos de Markdown.

            **O JSON deve seguir estritamente este formato:**
            {{
                "fundamentos_legais": [
                    {{"lei": "Código Civil", "artigos": "Art. 421 e 422", "descricao": "Princípios da função social do contrato e da boa-fé objetiva."}},
                    {{"lei": "Código Civil", "artigos": "Art. 593 a 609", "descricao": "Regras específicas sobre a prestação de serviços, se aplicável."}}
                ],
                "principios_juridicos": ["Pacta Sunt Servanda", "Boa-Fé Objetiva", "Autonomia da Vontade"],
                "jurisprudencia_relevante": "Citar uma súmula ou entendimento do STJ sobre o tipo de contrato em questão (ex: rescisão, multas, etc.).",
                "analise_juridica_detalhada": "Escreva um parágrafo conciso explicando que o contrato será regido pelos princípios da autonomia da vontade e da boa-fé, e que as cláusulas estão em conformidade com o Código Civil, garantindo segurança jurídica para ambas as partes."
            }}
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, dados_processados: dict) -> dict:
        """Analisa os dados de um contrato e retorna a base jurídica."""
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
            print(f"Erro no Agente Técnico de Contrato: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na análise jurídica do contrato", "detalhes": str(e), "saida_llm": texto_gerado}