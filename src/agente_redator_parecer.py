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
    seguindo a estrutura formal e com capacidade de auto-revisão.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)

        prompt_template_base = """
            Você é um advogado parecerista sênior, com estilo de escrita formal, objetivo e didático.

            {instrucoes_de_revisao}

            **Dados da Consulta:**
            {dados_processados_formatados}

            **Pesquisa Jurídica para Fundamentação:**
            {analise_juridica_formatada}

            **SUA TAREFA:**
            Redija o texto completo de um Parecer Jurídico em HTML, seguindo RIGOROSAMENTE a estrutura e as regras abaixo.

            **REGRAS DE ESTRUTURA E QUALIDADE:**
            1.  **Título:** Comece com `<h1>PARECER JURÍDICO</h1>`.
            2.  **Identificação:** Crie uma seção de identificação com: "PARECER Nº [INSIRA UM NÚMERO GENÉRICO COMO 001/2025]", "INTERESSADO: [Use o campo 'solicitante_parecer']", e "ASSUNTO: [Use o campo 'assunto_parecer']".
            3.  **Ementa:** Crie uma seção `<h2>EMENTA</h2>`. A ementa deve ser um resumo curto em tópicos dos pontos principais do parecer, finalizando com palavras-chave.
            4.  **Relatório:** Crie a seção `<h2>I - RELATÓRIO</h2>`. Resuma a consulta feita pelo interessado (campo 'consulta_parecer').
            5.  **Fundamentação:** Crie a seção `<h2>II - DA FUNDAMENTAÇÃO</h2>`. Desenvolva a análise jurídica de forma lógica, usando a pesquisa fornecida.
            6.  **Conclusão:** Crie a seção `<h2>III - DA CONCLUSÃO</h2>`. Responda diretamente às perguntas da consulta. Comece com "Diante do exposto, conclui-se que...".
            7.  **Fechamento:** Finalize com "É o parecer, salvo melhor juízo.", seguido de Local, Data, Nome do Advogado e OAB.
            8.  **Formato de Saída:** HTML puro, começando com `<h1>`.
        """

        self.prompt = PromptTemplate(
            input_variables=[
                "instrucoes_de_revisao",
                "dados_processados_formatados",
                "analise_juridica_formatada"
            ],
            template=prompt_template_base
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def _format_data_for_prompt(self, data: dict) -> str:
        formatted_parts = []
        for key, value in data.items():
            if value is None or (isinstance(value, str) and not value.strip()): continue
            if isinstance(value, (dict, list)):
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {json.dumps(value, ensure_ascii=False, indent=2)}")
            else:
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted_parts)

    def redigir_documento(self, dados_processados: dict, analise_juridica: dict, documento_anterior: str = None) -> dict:
        """Redige ou REVISA o parecer."""
        instrucoes_de_revisao_str = ""
        sugestoes_revisao = analise_juridica.get("sugestoes_revisao")
        if documento_anterior and sugestoes_revisao:
            sugestoes_formatadas = "\n".join([f"- Na seção '{s.get('secao', 'Geral')}': {s.get('descricao')}" for s in sugestoes_revisao])
            instrucoes_de_revisao_str = f"""**MODO DE REVISÃO ATIVADO. SUA TAREFA É CORRIGIR O DOCUMENTO ABAIXO.**\nA sua versão anterior falhou na validação. Você DEVE aplicar as seguintes correções OBRIGATÓRIAS:\n{sugestoes_formatadas}\n\n**DOCUMENTO ANTERIOR PARA CORRIGIR:**\n```html\n{documento_anterior}\n```\n**REDIJA A VERSÃO COMPLETA E CORRIGIDA DO DOCUMENTO ABAIXO, SEM OS MESMOS ERROS.**\n---"""
        
        analise_juridica_sem_sugestoes = analise_juridica.copy()
        analise_juridica_sem_sugestoes.pop("sugestoes_revisao", None)
        
        dados_processados_formatados = self._format_data_for_prompt(dados_processados)
        analise_juridica_formatada = self._format_data_for_prompt(analise_juridica_sem_sugestoes)

        try:
            resultado_llm = self.chain.invoke({"instrucoes_de_revisao": instrucoes_de_revisao_str, "dados_processados_formatados": dados_processados_formatados, "analise_juridica_formatada": analise_juridica_formatada})
            texto_gerado = resultado_llm["text"]
            texto_limpo = texto_gerado.strip()
            if texto_limpo.startswith("```html"): texto_limpo = texto_limpo[7:]
            if texto_limpo.endswith("```"): texto_limpo = texto_limpo[:-3]
            return {"documento": texto_limpo.strip(), "erro": None}
        except Exception as e:
            print(f"Erro no Agente Redator de Parecer: {e}")
            return {"documento": None, "erro": f"Falha na redação do parecer: {e}"}