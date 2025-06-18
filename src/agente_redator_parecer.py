# agente_redator_parecer.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedatorParecer:
    """
    Agente especialista em redigir o texto completo de um Parecer Jurídico,
    seguindo a estrutura formal (Ementa, Relatório, Fundamentação, Conclusão).
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)

        # Prompt 100% focado na estrutura de um parecer.
        prompt_template_base = """
            Você é um advogado parecerista sênior, com estilo de escrita formal, objetivo e didático.

            **INSTRUÇÃO MAIS IMPORTANTE:** Se o campo 'sugestoes_revisao' for fornecido, sua tarefa principal é REVISAR o parecer anterior aplicando OBRIGATORIAMENTE todas as sugestões listadas. A revisão tem prioridade máxima. Se não, redija um novo parecer.

            **Dados da Consulta:**
            {dados_processados_formatados}

            **Pesquisa Jurídica para Fundamentação:**
            {analise_juridica_formatada}

            **SUA TAREFA:**
            Redija o texto completo de um Parecer Jurídico em HTML, seguindo RIGOROSAMENTE a estrutura e as regras abaixo.

            **REGRAS DE ESTRUTURA E QUALIDADE:**
            1.  **Título:** Comece com `<h1>PARECER JURÍDICO</h1>`.
            2.  **Identificação:** Crie uma seção de identificação com: "PARECER Nº [INSIRA UM NÚMERO GENÉRICO COMO 001/2025]", "INTERESSADO: [Use o campo 'solicitante_parecer']", e "ASSUNTO: [Use o campo 'assunto_parecer']".
            3.  **Ementa:** Crie uma seção `<h2>EMENTA</h2>`. A ementa deve ser um resumo curto e estruturado em tópicos dos pontos principais do parecer. Finalize com palavras-chave em maiúsculas (ex: "PALAVRAS-CHAVE: DIREITO DIGITAL. PROTEÇÃO DE DADOS. LGPD. MARKETING.").
            4.  **Relatório:** Crie a seção `<h2>I - RELATÓRIO</h2>`. Nesta seção, transcreva ou resuma de forma clara e objetiva a consulta feita pelo interessado (campo 'consulta_parecer').
            5.  **Fundamentação:** Crie a seção `<h2>II - DA FUNDAMENTAÇÃO</h2>`. Esta é a parte principal. Desenvolva a análise jurídica de forma lógica, explicando a legislação, os princípios e a jurisprudência encontrados na pesquisa jurídica fornecida. Use a 'analise_juridica_detalhada' como guia para sua argumentação.
            6.  **Conclusão:** Crie a seção `<h2>III - DA CONCLUSÃO</h2>`. Responda diretamente às perguntas da consulta, de forma clara e sem ambiguidades, com base na fundamentação. Comece com "Diante do exposto, e em resposta à consulta formulada, este parecerista conclui que...".
            7.  **Fechamento:** Finalize com a frase "É o parecer, salvo melhor juízo.", e em seguida, os campos para Local, Data, Nome do Advogado e OAB.
            8.  **Formato de Saída:** O documento deve ser retornado como HTML puro, começando diretamente pelo `<h1>`.
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
        """Redige o parecer. Retorna um dicionário com 'documento' ou 'erro'."""
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
            print(f"Erro no Agente Redator de Parecer: {e}")
            return {"documento": None, "erro": f"Falha na redação do parecer: {e}"}