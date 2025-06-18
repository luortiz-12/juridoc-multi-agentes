# Agente de Redação Jurídica

"""
Este script implementa o Agente de Redação Jurídica, responsável por elaborar o texto
da petição ou contrato com base nos dados processados e fundamentos jurídicos.
"""

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedacaoJuridica:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0.2)

        # O prompt e o chain são criados UMA VEZ no construtor para máxima eficiência.
        prompt_template_base = """
            Você é um redator jurídico altamente qualificado, com vasta experiência na elaboração de documentos jurídicos no Brasil.
            Sua tarefa é redigir um documento jurídico completo e formal, utilizando os dados fornecidos e os fundamentos jurídicos identificados.

            **Dados Processados (do Agente Coletor):**
            {dados_processados_formatados}

            **Análise Jurídica (do Agente Jurídico Técnico):**
            {analise_juridica_formatada}

            **Instruções Gerais para Redação:**
            - Mantenha a linguagem formal, técnica e jurídica.
            - Evite repetições e seja conciso.
            - **IMPORTANTE:** Ao referenciar dados, inclua APENAS os campos que têm valor. Se um dado não estiver disponível, omita-o.
            - **Formato de Saída:** O documento deve ser retornado como HTML puro, sem tags `<html>`, `<body>`, ou blocos de código markdown (e.g., ```html`). O conteúdo deve começar diretamente pelo título `<h1>`.

            {instrucoes_especificas_tipo}
        """

        prompt = PromptTemplate(
            input_variables=[
                "dados_processados_formatados",
                "analise_juridica_formatada",
                "instrucoes_especificas_tipo"
            ],
            template=prompt_template_base
        )

        self.chain = LLMChain(llm=self.llm, prompt=prompt)

        # As instruções específicas agora são apenas atributos de string da classe
        self.instrucoes_peticao = """
            **Instruções Específicas para a Petição Inicial:**
            1.  **Cabeçalho:** Inicie com "EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO DA [NÚMERO] VARA [TIPO DE VARA, ex: CÍVEL] DA COMARCA DE [CIDADE]– [ESTADO]".
            2.  **Qualificação das Partes:** Qualifique completamente o Requerente e o Requerido.
            3.  **Fundamentação Legal (com fulcro):** Cite artigos e leis relevantes usando "com fulcro na..." conforme a análise jurídica.
            4.  **Título da Ação:** Defina o título da ação (ex: AÇÃO DE REPARAÇÃO DE DANOS MORAIS).
            5.  **Dos Fatos:** Descreva os fatos de forma clara, concisa e cronológica.
            6.  **Do Direito:** Desenvolva a argumentação jurídica, aplicando os fundamentos legais aos fatos.
            7.  **Dos Danos (se aplicável):** Detalhe os danos sofridos (morais, materiais).
            8.  **Da Quantia Devida (se aplicável):** Justifique o valor da indenização.
            9.  **Dos Pedidos:** Liste os pedidos de forma clara e numerada (1., 2., etc.). Inclua citação, condenação (se for o caso), custas e honorários.
            10. **Das Provas:** Cláusula padrão de protesto por todos os meios de prova.
            11. **Do Valor da Causa:** Indique o valor da causa.
            12. **Fechamento:** "Termos em que Pede Deferimento. [Local, data, ano]. Advogado OAB".
        """
        self.instrucoes_contrato = """
            **Instruções Específicas para o Contrato:**
            1.  **Título:** O título do contrato deve ser o 'tipo_contrato' dos dados processados, em maiúsculas (ex: CONTRATO DE PRESTAÇÃO DE SERVIÇOS).
            2.  **Qualificação das Partes:** Qualifique completamente o CONTRATANTE e o CONTRATADO.
            3.  **Cláusulas:** Use "CLÁUSULA" para seções principais (CLÁUSULA PRIMEIRA), e numeração hierárquica para subcláusulas (1.1, 1.2).
            4.  **Objeto do Contrato:** Descreva detalhadamente.
            5.  **Valor e Forma de Pagamento:** Detalhe o valor e as condições.
            6.  **Prazos de Vigência:** Especifique prazos.
            7.  **Responsabilidades das Partes:** Descreva as responsabilidades.
            8.  **Penalidades por Descumprimento:** Inclua penalidades.
            9.  **Foro de Eleição:** Adicione cláusula final para o foro.
            10. **Referências Legais:** Inclua referências legais específicas (ex.: artigos do Código Civil) sempre que aplicável, conforme a análise jurídica.
        """
        self.instrucoes_parecer = """
            **Instruções Específicas para o Parecer Jurídico:**
            - **Título:** PARECER JURÍDICO.
            - **Estrutura:** Identificação do Documento (SOLICITANTE, ASSUNTO), Consulta, Legislação Aplicável, Análise Jurídica, Conclusão.
            - **Linguagem:** Formal e técnica.
            - Inclua fundamentação jurídica (lei, doutrina, jurisprudência) de forma coesa.
            - Não inclua "Observação" no final.
        """
        self.instrucoes_estudo = """
            **Instruções Específicas para o Estudo de Caso Jurídico:**
            - **Título:** ESTUDO DE CASO JURÍDICO.
            - **Estrutura:** Título do Caso, Descrição do Caso, Contexto Jurídico, Pontos Relevantes, Análise do Caso, Conclusão (mínimo 3 parágrafos, com jurisprudência).
            - **Linguagem:** Formal, objetiva, com destaque para termos jurídicos em MAIÚSCULAS e Negrito (se o LLM suportar).
            - Inclua citações de leis, artigos, princípios, jurisprudência e doutrina.
        """

    def _format_data_for_prompt(self, data: dict) -> str:
        """Formata um dicionário para uma string legível pelo LLM, ignorando valores None/vazios."""
        formatted_parts = []
        for key, value in data.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            if isinstance(value, (dict, list)):
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {json.dumps(value, ensure_ascii=False, indent=2)}")
            else:
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted_parts)

    def redigir_documento(self, tipo_documento: str, dados_processados: dict, analise_juridica: dict) -> dict:
        """Redige o documento jurídico. Retorna um dicionário com 'documento' ou 'erro'."""
        instrucoes_map = {
            "peticao": self.instrucoes_peticao,
            "contrato": self.instrucoes_contrato,
            "parecer": self.instrucoes_parecer,
            "estudo": self.instrucoes_estudo
        }
        instrucoes_especificas = instrucoes_map.get(tipo_documento.lower())

        if not instrucoes_especificas:
            return {"documento": None, "erro": f"Tipo de documento '{tipo_documento}' não suportado para redação."}

        dados_processados_formatados = self._format_data_for_prompt(dados_processados)
        analise_juridica_formatada = self._format_data_for_prompt(analise_juridica)

        try:
            resultado_llm = self.chain.invoke({
                "dados_processados_formatados": dados_processados_formatados,
                "analise_juridica_formatada": analise_juridica_formatada,
                "instrucoes_especificas_tipo": instrucoes_especificas
            })
            
            texto_gerado = resultado_llm["text"]

            texto_limpo = texto_gerado.strip()
            if texto_limpo.startswith("```html"):
                texto_limpo = texto_limpo[7:]
            if texto_limpo.endswith("```"):
                texto_limpo = texto_limpo[:-3]
            texto_limpo = texto_limpo.strip()
            
            return {"documento": texto_limpo, "erro": None}

        except Exception as e:
            print(f"Erro ao invocar LLM na Redação Jurídica: {e}")
            return {"documento": None, "erro": f"Falha na invocação do LLM para redação: {e}"}

# (O bloco 'if __name__ == "__main__":' permanece o mesmo, mas lembre-se que ele precisa
# ser ajustado para lidar com o dicionário retornado, como fizemos no script de teste completo)