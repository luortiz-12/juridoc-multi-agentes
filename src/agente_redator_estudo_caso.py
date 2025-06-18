# agente_redator_estudo_caso.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedatorEstudoCaso:
    """
    Agente especialista em redigir o texto completo de um Estudo de Caso Jurídico,
    com estrutura clara, analítica e com capacidade de auto-revisão.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.2)

        prompt_template_base = """
            Você é um escritor acadêmico e jurista, especialista em transformar análises jurídicas complexas em estudos de caso claros, bem estruturados e didáticos.

            {instrucoes_de_revisao}

            **Dados do Caso:**
            {dados_processados_formatados}

            **Pesquisa Jurídica para Análise:**
            {analise_juridica_formatada}

            **SUA TAREFA:**
            Redija o texto completo de um Estudo de Caso Jurídico em HTML, seguindo RIGOROSAMENTE a estrutura e as regras abaixo.

            **REGRAS DE ESTRUTURA E QUALIDADE:**
            1.  **Título Principal:** Comece com `<h1>ESTUDO DE CASO: [Use o campo 'titulo_caso']</h1>`.
            2.  **Apresentação do Caso:** Crie a seção `<h2>I - APRESENTAÇÃO DO CASO</h2>`. Nesta seção, narre os fatos e o contexto do caso, conforme descrito nos dados processados.
            3.  **Análise Jurídica:** Crie a seção `<h2>II - ANÁLISE JURÍDICA</h2>`. Esta é a parte central. Desenvolva a análise de forma organizada e didática, discutindo a legislação, os princípios e a jurisprudência da pesquisa fornecida.
            4.  **Conclusão:** Crie a seção `<h2>III - CONCLUSÃO</h2>`. Sintetize os achados da análise e apresente a solução ou o entendimento jurídico mais provável para o caso estudado.
            5.  **Linguagem:** Use uma linguagem formal e objetiva, apropriada para um texto analítico.
            6.  **Formato de Saída:** O documento deve ser retornado como HTML puro, começando diretamente pelo `<h1>`.
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
        """Redige ou REVISA o estudo de caso."""
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
            print(f"Erro no Agente Redator de Estudo de Caso: {e}")
            return {"documento": None, "erro": f"Falha na redação do estudo de caso: {e}"}