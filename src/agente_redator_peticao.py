# agente_redator_peticao.py - VERSÃO REFATORADA (O ESCRITOR)

import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

class AgenteRedatorPeticao:
    """
    Agente especialista em redigir o texto de uma petição com base
    nos dados do caso e na análise técnica recebida.
    """
    def __init__(self, llm_api_key: str):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.2)
        self.prompt_template = PromptTemplate(
            input_variables=["dados_estruturados", "analise_tecnica"],
            template="""
            Você é um advogado processualista sênior, um mestre na arte de escrever petições iniciais persuasivas e tecnicamente perfeitas.

            Sua tarefa é redigir o texto completo em HTML de uma petição com base no dossiê abaixo, que contém os dados do caso e a análise jurídica preparada pelo seu pesquisador.

            **DADOS DO CASO (fornecidos pelo cliente):**
            {dados_estruturados}

            **ANÁLISE JURÍDICA E FUNDAMENTAÇÃO (preparada pelo pesquisador):**
            {analise_tecnica}

            **REGRAS DE REDAÇÃO:**
            - Use a 'analise_juridica_detalhada' como o fio condutor da sua argumentação na seção DO DIREITO.
            - Incorpore os 'fundamentos_legais' e a 'jurisprudencia_relevante' de forma fluida no texto.
            - Siga a estrutura formal (Endereçamento, Qualificação, Fatos, Direito, Pedidos, Valor da Causa, etc.).
            - Adapte os termos (Autor/Réu, Reclamante/Reclamada) com base na natureza da ação.
            - Se alguma informação essencial não foi fornecida nos dados (ex: nome do advogado, OAB), use placeholders claros: [NOME DO ADVOGADO], [OAB/UF].
            - O resultado deve ser apenas o HTML, começando com <h1>.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def redigir_documento(self, dados_processados: dict, analise_tecnica: dict, documento_anterior: str = None) -> dict:
        """
        Executa o processo de redação. O loop de revisão foi simplificado por enquanto.
        """
        try:
            print("✍️ Etapa de Redação: Escrevendo a petição...")
            dados_formatados = json.dumps(dados_processados, indent=2, ensure_ascii=False)
            analise_formatada = json.dumps(analise_tecnica, indent=2, ensure_ascii=False)
            
            resposta_llm = self.chain.invoke({
                "dados_estruturados": dados_formatados,
                "analise_tecnica": analise_formatada
            })
            
            peticao_html = resposta_llm.get("text", "")
            return {"documento": peticao_html, "erro": None}

        except Exception as e:
            print(f"❌ Erro no Agente Redator de Petição: {e}")
            return {"documento": None, "erro": f"Falha na redação da petição: {str(e)}"}