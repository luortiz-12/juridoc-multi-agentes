# agente_redator_peticao.py
import os, json, sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedatorPeticao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        prompt_template_base = """
            Você é um advogado processualista sênior, especialista na redação de petições iniciais.
            {instrucoes_de_revisao}
            **Dados do Caso:**
            {dados_processados_formatados}
            **Análise Jurídica e Tese:**
            {analise_juridica_formatada}
            **SUA TAREFA:** Redija o texto completo de uma Petição Inicial em HTML, seguindo as regras abaixo.
            **REGRAS DE QUALIDADE OBRIGATÓRIAS:**
            1.  **USO INTELIGENTE DE PLACEHOLDERS:** Se uma informação essencial NÃO FOR FORNECIDA (ex: nº da vara, OAB), NÃO omita a seção. Gere o texto e insira um placeholder claro. Exemplos: `[NOME DO ADVOGADO]`, `[NÚMERO DA OAB/UF]`, `[Nº DA VARA]`, `____/____/______`.
            2.  **ESTRUTURA FORMAL:** Siga a estrutura: Endereçamento, Qualificação das Partes, Título da Ação, e as seções <h2>DOS FATOS</h2>, <h2>DO DIREITO</h2>, <h2>DOS PEDIDOS</h2>, etc. Adapte os termos (Autor/Réu, Reclamante/Reclamada) ao contexto.
            3.  **SEM PLACEHOLDERS GENÉRICOS:** NUNCA use placeholders vagos como '[data]' ou '[preencher]'.
            4.  **FORMATO DE SAÍDA:** HTML puro, começando com `<h1>`.
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
            print(f"Erro no Agente Redator de Petição: {e}")
            return {"documento": None, "erro": f"Falha na redação da petição: {e}"}