# agente_tecnico_peticao.py
import os
import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteTecnicoPeticao:
    """
    Agente especialista que analisa os fatos, identifica o tipo de petição
    (Cível, Trabalhista, Queixa-Crime, Habeas Corpus) e constrói a tese jurídica.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados"],
            template="""
            Você é um advogado pesquisador sênior, com profundo conhecimento do ordenamento jurídico brasileiro. Sua missão é analisar os fatos de um caso e construir a tese jurídica mais forte possível para uma petição inicial.

            **DADOS DO CASO (recebidos do formulário N8N):**
            {dados_processados}

            **SUA TAREFA:**

            **1. ANÁLISE E CLASSIFICAÇÃO (Instrução Obrigatória):**
            Sua primeira tarefa é identificar o tipo específico de petição com base nos campos preenchidos. Siga estas regras OBRIGATORIAMENTE:
            - Se algum campo contiver as palavras 'trabalho' ou 'trabalhista' (como 'InfoExtraTrabalhista', 'datadmissaoTrabalhista'), o caso é **TRABALHISTA**. Fundamente sua pesquisa na CLT.
            - Se algum campo contiver a palavra 'crime' ou 'criminal' (como 'datafatoCriminal'), o caso é **PENAL (QUEIXA-CRIME)**. Fundamente sua pesquisa no Código Penal e no Código de Processo Penal.
            - Se algum campo contiver a palavra 'habiesCorpus', o caso é **CONSTITUCIONAL (HABEAS CORPUS)**. Fundamente sua pesquisa no Art. 5º da Constituição Federal e no Código de Processo Penal.
            - Se nenhuma das condições acima for atendida, o caso é **CÍVEL**. Fundamente sua pesquisa no Código Civil e no Código de Processo Civil.
            - Ignore completamente todos os campos que vierem com valor 'null' ou vazios. Baseie sua análise apenas nos campos que contêm informação.

            **2. PESQUISA E FUNDAMENTAÇÃO:**
            Após classificar o caso, com base no seu vasto conhecimento interno, formule a fundamentação jurídica, citando as leis, artigos e jurisprudência consolidada (Súmulas) mais relevantes para a área do direito identificada.

            **3. ESTRUTURA DA RESPOSTA:**
            Retorne sua análise completa no formato JSON abaixo.

            **Formato Final da Resposta (DEVE ser um JSON válido):**
            ```json
            {{
                "fundamentos_legais": [{{"lei": "Nome do Código ou Lei", "artigos": "Artigos aplicáveis", "descricao": "Explicação da relevância do artigo para o caso."}}],
                "principios_juridicos": ["Princípios jurídicos que se aplicam ao caso específico."],
                "jurisprudencia_relevante": "Cite uma Súmula do STJ/STF/TST ou um entendimento pacificado relevante para a tese.",
                "analise_juridica_detalhada": "Um parágrafo completo e bem fundamentado explicando como os fatos se conectam com a lei e a jurisprudência para formar a tese da petição."
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

            # Limpeza defensiva do JSON
            texto_limpo = texto_gerado.strip()
            if '```json' in texto_limpo: texto_limpo = texto_limpo.split('```json', 1)[-1]
            if '```' in texto_limpo: texto_limpo = texto_limpo.split('```', 1)[0]
            analise_juridica = json.loads(texto_limpo.strip())
            return analise_juridica
        except Exception as e:
            print(f"Erro no Agente Técnico de Petição (LLMChain): {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na análise jurídica da petição", "detalhes": str(e), "saida_llm": texto_gerado}