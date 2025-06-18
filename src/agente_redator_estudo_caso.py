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
    com estrutura clara e analítica.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.2)

        # Prompt 100% focado na estrutura de um estudo de caso.
        prompt_template_base = """
            Você é um escritor acadêmico e jurista, especialista em transformar análises jurídicas complexas em estudos de caso claros, bem estruturados e didáticos.

            **INSTRUÇÃO MAIS IMPORTANTE:** Se o campo 'sugestoes_revisao' for fornecido, sua tarefa principal é REVISAR o estudo de caso anterior aplicando OBRIGATORIAMENTE todas as sugestões listadas. A revisão tem prioridade máxima. Se não, redija um novo estudo.

            **Dados do Caso:**
            {dados_processados_formatados}

            **Pesquisa Jurídica para Análise:**
            {analise_juridica_formatada}

            **SUA TAREFA:**
            Redija o texto completo de um Estudo de Caso Jurídico em HTML, seguindo RIGOROSAMENTE a estrutura e as regras abaixo.

            **REGRAS DE ESTRUTURA E QUALIDADE:**
            1.  **Título Principal:** Comece com `<h1>ESTUDO DE CASO: [Use o campo 'titulo_caso']</h1>`.
            2.  **Apresentação do Caso:** Crie a seção `<h2>I - APRESENTAÇÃO DO CASO</h2>`. Nesta seção, narre os fatos e o contexto do caso, conforme descrito nos dados processados.
            3.  **Análise Jurídica:** Crie a seção `<h2>II - ANÁLISE JURÍDICA</h2>`. Esta é a parte central. Desenvolva a análise de forma organizada e didática. Discuta a legislação, os princípios e a jurisprudência encontrados na pesquisa jurídica fornecida. Use a 'analise_juridica_detalhada' como o fio condutor da sua argumentação.
            4.  **Conclusão:** Crie a seção `<h2>III - CONCLUSÃO</h2>`. Sintetize os achados da análise e apresente a solução ou o entendimento jurídico mais provável ou recomendável para o caso estudado. Seja conclusivo e direto.
            5.  **Linguagem:** Use uma linguagem formal e objetiva, apropriada para um texto analítico.
            6.  **Formato de Saída:** O documento deve ser retornado como HTML puro, começando diretamente pelo `<h1>`.
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
        """Redige o estudo de caso. Retorna um dicionário com 'documento' ou 'erro'."""
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
            print(f"Erro no Agente Redator de Estudo de Caso: {e}")
            return {"documento": None, "erro": f"Falha na redação do estudo de caso: {e}"}