# agente_redator_peticao.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedatorPeticao:
    """
    Agente especialista em redigir o texto completo de uma Petição Inicial,
    adaptando a terminologia e estrutura conforme a área do direito.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.2)

        # Prompt 100% focado em redação de petições.
        prompt_template_base = """
            Você é um advogado processualista sênior, com excepcional habilidade para redigir peças processuais claras, persuasivas e tecnicamente perfeitas.

            **INSTRUÇÃO MAIS IMPORTANTE:** Se o campo 'sugestoes_revisao' for fornecido, sua tarefa principal é REVISAR o documento anterior aplicando OBRIGATORIAMENTE todas as sugestões listadas. A revisão tem prioridade máxima. Se não, redija uma nova petição.

            **Dados do Caso:**
            {dados_processados_formatados}

            **Análise Jurídica e Tese (pode conter sugestões de revisão):**
            {analise_juridica_formatada}

            **SUA TAREFA:**
            Redija o texto completo de uma Petição Inicial em HTML, seguindo rigorosamente a estrutura e as regras abaixo.

            **REGRAS DE ESTRUTURA E QUALIDADE:**
            1.  **Endereçamento:** Comece com o endereçamento ao juízo competente em `<h1>`. Ex: "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DO TRABALHO DA __ VARA DO TRABALHO DE [CIDADE]".
            2.  **Qualificação das Partes:** Qualifique de forma completa as partes. **Adapte os termos**: use "Requerente/Requerido" ou "Autor/Réu" para casos cíveis; "Reclamante/Reclamado(a)" para trabalhistas; "Querelante/Querelado" para queixa-crime; "Paciente/Autoridade Coatora" para Habeas Corpus.
            3.  **Título da Ação:** Crie um título apropriado em `<h2>` (Ex: "AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS", "RECLAMAÇÃO TRABALHISTA", "QUEIXA-CRIME", "ORDEM DE HABEAS CORPUS").
            4.  **Seções Estruturais:** Crie as seções usando `<h2>`: `DOS FATOS` (narre a história de forma clara e cronológica), `DO DIREITO` (desenvolva a argumentação usando a 'analise_juridica_detalhada' como guia e citando os artigos e jurisprudência), e `DOS PEDIDOS` (liste todos os pedidos de forma clara e numerada).
            5.  **Seções Finais:** Inclua as seções `DO VALOR DA CAUSA`, `DAS PROVAS` e o fecho de encerramento ('Termos em que, Pede deferimento.').
            6.  **SEM PLACEHOLDERS:** O texto deve ser final, sem placeholders como '[data]' ou '[local]'.
            7.  **Formato de Saída:** O documento deve ser retornado como HTML puro, começando diretamente pelo `<h1>`. Não inclua `<html>` ou `<body>`.
        """

        prompt = PromptTemplate(
            input_variables=[
                "dados_processados_formatados",
                "analise_juridica_formatada"
            ],
            template=prompt_template_base
        )
        self.chain = LLMChain(llm=self.llm, prompt=prompt)

    def _format_data_for_prompt(self, data: dict) -> str:
        """Formata um dicionário para uma string legível pelo LLM."""
        formatted_parts = []
        for key, value in data.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            if isinstance(value, (dict, list)):
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {json.dumps(value, ensure_ascii=False, indent=2)}")
            else:
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted_parts)

    def redigir_documento(self, dados_processados: dict, analise_juridica: dict) -> dict:
        """Redige a petição. Retorna um dicionário com 'documento' ou 'erro'."""
        dados_processados_formatados = self._format_data_for_prompt(dados_processados)
        analise_juridica_formatada = self._format_data_for_prompt(analise_juridica)

        try:
            resultado_llm = self.chain.invoke({
                "dados_processados_formatados": dados_processados_formatados,
                "analise_juridica_formatada": analise_juridica_formatada
            })
            
            texto_gerado = resultado_llm["text"]

            # Limpeza defensiva do HTML
            texto_limpo = texto_gerado.strip()
            if texto_limpo.startswith("```html"):
                texto_limpo = texto_limpo[7:]
            if texto_limpo.endswith("```"):
                texto_limpo = texto_limpo[:-3]
            texto_limpo = texto_limpo.strip()
            
            return {"documento": texto_limpo, "erro": None}

        except Exception as e:
            print(f"Erro no Agente Redator de Petição: {e}")
            return {"documento": None, "erro": f"Falha na redação da petição: {e}"}