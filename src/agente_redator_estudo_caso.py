# agente_redator_estudo_caso.py
import os, json, sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedatorEstudoCaso:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.2)
        prompt_template_base = """
            Você é um escritor acadêmico e jurista, especialista em transformar análises jurídicas complexas em estudos de caso claros e didáticos.
            {instrucoes_de_revisao}
            **Dados do Caso:**
            {dados_processados_formatados}
            **Pesquisa Jurídica para Análise:**
            {analise_juridica_formatada}
            **SUA TAREFA:** Redija um Estudo de Caso Jurídico em HTML.
            **REGRAS DE QUALIDADE OBRIGATÓRIAS:**
            1.  **USO INTELIGENTE DE PLACEHOLDERS:** Se informações estiverem faltando nos dados, utilize placeholders claros como `[INFORMAÇÃO PENDENTE]` ou `[DETALHE NÃO FORNECIDO]`.
            2.  **ESTRUTURA ACADÊMICA:** Siga a estrutura: `<h1>ESTUDO DE CASO: [TÍTULO]</h1>`, `<h2>I - APRESENTAÇÃO DO CASO</h2>`, `<h2>II - ANÁLISE JURÍDICA</h2>`, `<h2>III - CONCLUSÃO</h2>`.
            3.  **FORMATO DE SAÍDA:** HTML puro, começando com `<h1>`.
        """
        self.prompt = PromptTemplate(input_variables=["instrucoes_de_revisao", "dados_processados_formatados", "analise_juridica_formatada"], template=prompt_template_base)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def _format_data_for_prompt(self, data: dict) -> str:
        formatted_parts = []
        for key, value in data.items():
            if value is None or (isinstance(value, str) and not value.strip()): continue
            if isinstance(value, (dict, list)): formatted_parts.append(f"{key.replace('_', ' ').title()}: {json.dumps(value, ensure_ascii=False, indent=2)}")
            else: formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted_parts)

    def redigir_documento(self, dados_processados: dict, analise_juridica: dict, documento_anterior: str = None) -> dict:
        instrucoes_de_revisao_str = ""
        sugestoes_revisao = analise_juridica.get("sugestoes_revisao")
        if documento_anterior and sugestoes_revisao:
            sugestoes_formatadas = "\n".join([f"- Na seção '{s.get('secao', 'Geral')}': {s.get('descricao')}" for s in sugestoes_revisao])
            instrucoes_de_revisao_str = f"""**MODO DE REVISÃO ATIVADO. SUA PRIORIDADE MÁXIMA É CORRIGIR O DOCUMENTO ABAIXO.**\nA sua versão anterior falhou na validação. Pense passo a passo e aplique TODAS as seguintes correções obrigatórias:\n{sugestoes_formatadas}\n\n**DOCUMENTO ANTERIOR PARA CORRIGIR:**\n```html\n{documento_anterior}\n```\n**REDIJA A VERSÃO FINAL E CORRIGIDA, SEM OS MESMOS ERROS.**\n---"""
        
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