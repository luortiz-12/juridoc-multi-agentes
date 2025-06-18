# agente_redator_peticao.py
import os, json, sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedatorPeticao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        prompt_template_base = """
            Você é um advogado processualista sênior, especialista em redação de petições.
            {instrucoes_de_revisao}
            **Dados do Caso:**
            {dados_processados_formatados}
            **Análise Jurídica e Tese:**
            {analise_juridica_formatada}
            **SUA TAREFA:**
            Redija o texto completo de uma Petição Inicial em HTML, seguindo RIGOROSAMENTE as regras abaixo.
            **REGRAS DE ESTRUTURA E QUALIDADE:**
            1. Endereçamento: Comece com <h1>EXCELENTÍSSIMO SENHOR DOUTOR JUIZ...</h1>.
            2. Qualificação das Partes: Qualifique completamente as partes, adaptando os termos (Autor/Réu, Reclamante/Reclamada, etc.).
            3. Título da Ação: Crie um título apropriado em <h2>.
            4. Seções Estruturais: Crie as seções <h2>DOS FATOS</h2>, <h2>DO DIREITO</h2>, e <h2>DOS PEDIDOS</h2>.
            5. Seções Finais: Inclua DO VALOR DA CAUSA, DAS PROVAS e o fecho 'Termos em que, Pede deferimento.'.
            6. SEM PLACEHOLDERS: O texto deve ser final, sem placeholders como '[data]' ou '[local]'.
            7. Formato de Saída: HTML puro, começando com <h1>.
        """
        self.prompt = PromptTemplate(input_variables=["instrucoes_de_revisao", "dados_processados_formatados", "analise_juridica_formatada"], template=prompt_template_base)
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
            print(f"Erro no Agente Redator de Petição: {e}")
            return {"documento": None, "erro": f"Falha na redação da petição: {e}"}