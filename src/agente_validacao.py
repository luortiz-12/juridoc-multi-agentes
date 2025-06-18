# agente_validacao.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteValidacao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0)

        # Prompt aprimorado para validar com base no tipo de documento
        self.prompt_template = PromptTemplate(
            input_variables=["documento_gerado", "dados_processados", "analise_juridica", "tipo_documento"],
            template="""
            Você é um Agente de Validação Jurídica extremamente crítico e detalhista. Sua tarefa é revisar o `documento_gerado` e identificar qualquer inconsistência, erro ou ponto de melhoria.

            **DADOS PARA ANÁLISE:**
            - Tipo do Documento: {tipo_documento}
            - Documento Gerado (HTML): {documento_gerado}
            - Dados Originais do Formulário: {dados_processados}
            - Análise Jurídica Usada na Redação: {analise_juridica}

            **INSTRUÇÕES DE VALIDAÇÃO GERAL (Aplicar a todos):**
            1.  **Coerência:** Os fatos, fundamentos e pedidos/cláusulas estão alinhados?
            2.  **Completude:** Todas as informações essenciais dos dados originais foram incluídas no documento?
            3.  **Placeholders:** O documento contém placeholders como '[data]', '[nome]' ou seções vazias que deveriam ter sido preenchidas? (Isto é um erro grave).
            4.  **Formato HTML:** O HTML parece ser válido? (Não precisa ser uma análise profunda).

            **INSTRUÇÕES DE VALIDAÇÃO ESPECÍFICA (Aplicar conforme o tipo):**
            - **Se for um CONTRATO:** Verifique se as cláusulas essenciais (Objeto, Valor, Partes, Prazos, Foro) estão presentes, claras e bem definidas.
            - **Se for uma PETIÇÃO:** Verifique se a estrutura (Endereçamento, Qualificação, Fatos, Direito, Pedidos) está correta e se os pedidos são uma consequência lógica da argumentação. O pedido de honorários está bem fundamentado?
            - **Se for um PARECER:** Verifique se a estrutura (Ementa, Relatório, Fundamentação, Conclusão) foi seguida e se a conclusão responde objetivamente à consulta.
            - **Se for um ESTUDO DE CASO:** Verifique se a análise é coerente e se a conclusão se baseia nos fatos e na análise jurídica apresentada.

            **REGRA DE OURO PARA A SAÍDA:**
            Sua resposta DEVE ser um objeto JSON VÁLIDO e NADA MAIS, começando com `{{` e terminando com `}}`. NÃO use blocos de Markdown.
            O formato deve ser:
            {{
                "status": "aprovado" ou "revisar",
                "sugestoes_melhoria": [
                    {{"secao": "Seção ou Aspecto a Melhorar", "descricao": "Descrição clara e acionável da sugestão ou erro encontrado."}}
                ]
            }}
            Se o status for "aprovado", a lista `sugestoes_melhoria` DEVE ser vazia.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def validar_documento(self, documento_gerado: str, dados_processados: dict, analise_juridica: dict, tipo_documento: str) -> dict:
        dados_processados_str = json.dumps(dados_processados, indent=2, ensure_ascii=False)
        analise_juridica_str = json.dumps(analise_juridica, indent=2, ensure_ascii=False)
        texto_gerado = ""
        try:
            resultado_llm = self.chain.invoke({
                "documento_gerado": documento_gerado,
                "dados_processados": dados_processados_str,
                "analise_juridica": analise_juridica_str,
                "tipo_documento": tipo_documento
            })
            texto_gerado = resultado_llm["text"]
            texto_limpo = texto_gerado.strip()
            if '```json' in texto_limpo:
                texto_limpo = texto_limpo.split('```json', 1)[-1]
            if '```' in texto_limpo:
                texto_limpo = texto_limpo.split('```', 1)[0]
            texto_limpo = texto_limpo.strip()
            validacao_resultado = json.loads(texto_limpo)
            return validacao_resultado
        except Exception as e:
            print(f"Erro no Agente de Validação: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na validação do documento", "detalhes": str(e), "saida_llm": texto_gerado}