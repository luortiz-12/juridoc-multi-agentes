# agente_tecnico_peticao.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteTecnicoPeticao:
    """
    Agente especialista em analisar os fatos de um caso, identificar a área do
    direito aplicável (Cível, Trabalhista, Penal) e construir a tese jurídica.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)

        # Prompt 100% focado em análise e pesquisa para litígios.
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados"],
            template=
            """
            Você é um advogado pesquisador sênior, com vasta experiência em Direito Processual Cível, Trabalhista e Penal no Brasil.
            Sua missão é analisar os fatos de um caso e, a partir deles, identificar o tipo de ação cabível e construir a tese jurídica mais forte e completa possível para uma petição inicial.

            **DADOS DO CASO:**
            {dados_processados}

            **SUA TAREFA - Pense passo a passo:**
            1.  **Analise os Fatos:** Examine os campos 'fatos_peticao', 'pedido_peticao', e outros campos específicos como 'data_admissao_peticao' ou 'motivo_prisao_peticao' para entender a natureza do conflito.
            2.  **Identifique o Ramo do Direito:**
                - Se os dados contêm 'data_admissao', 'salario_peticao', 'verbas_pleiteadas_peticao', o caso é **Trabalhista**.
                - Se os dados contêm 'data_fato_peticao', 'nome_vitima_peticao', 'desejo_representar_peticao', o caso é **Penal (Queixa-Crime)**.
                - Se os dados contêm 'autoridade_coatora_peticao', 'motivo_prisao_peticao', é **Constitucional/Penal (Habeas Corpus)**.
                - Caso contrário, é provavelmente **Cível** ou **Consumidor**.
            3.  **Realize a Pesquisa Jurídica Específica:** Com base no ramo identificado, pesquise e defina os fundamentos legais mais pertinentes. Para casos trabalhistas, foque na CLT. Para casos penais, no Código Penal e de Processo Penal. Para cíveis, no Código Civil e CPC.
            4.  **Estruture a Análise:** Retorne sua pesquisa em um formato JSON estrito, conforme o modelo abaixo.

            **REGRA DE OURO PARA A SAÍDA:**
            Sua resposta DEVE ser um objeto JSON VÁLIDO e NADA MAIS, começando com `{{` e terminando com `}}`. NÃO use blocos de Markdown.

            **O JSON deve seguir estritamente este formato:**
            {{
                "fundamentos_legais": [
                    {{"lei": "Nome da Lei/Código", "artigos": "Artigos relevantes", "descricao": "Breve descrição da relevância desses artigos para o caso concreto."}}
                ],
                "principios_juridicos": ["Princípio Relevante 1", "Princípio Relevante 2"],
                "jurisprudencia_relevante": "Cite uma Súmula do TST (se trabalhista) ou do STJ/STF (se cível/penal) ou um entendimento jurisprudencial consolidado que se aplique diretamente ao caso.",
                "analise_juridica_detalhada": "Escreva um parágrafo conciso explicando como os fatos se conectam com os fundamentos legais e a jurisprudência, formando a tese central que será usada na petição."
            }}
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, dados_processados: dict) -> dict:
        """Analisa os dados de uma petição e retorna a base jurídica."""
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
            print(f"Erro no Agente Técnico de Petição: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na análise jurídica da petição", "detalhes": str(e), "saida_llm": texto_gerado}