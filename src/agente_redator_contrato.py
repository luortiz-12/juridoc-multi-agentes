# agente_redator_contrato.py

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedatorContrato:
    """
    Agente especialista em redigir o texto completo e as cláusulas
    de um contrato, baseado nos dados e na análise jurídica.
    """
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0.2)

        # Este prompt é 100% focado em redação de contratos.
        prompt_template_base = """
            Você é um advogado especialista na redação de contratos, com notável atenção aos detalhes e ao jargão jurídico apropriado.

            **INSTRUÇÃO MAIS IMPORTANTE:** Se o campo 'sugestoes_revisao' for fornecido dentro da 'Análise Jurídica', sua tarefa principal é REVISAR o documento anterior aplicando OBRIGATORIAMENTE todas as sugestões listadas. A revisão tem prioridade máxima. Se não houver sugestões, sua tarefa é redigir um novo contrato do zero.

            **Dados do Contrato (formatados):**
            {dados_processados_formatados}

            **Análise Jurídica e Fundamentação (pode conter sugestões de revisão):**
            {analise_juridica_formatada}

            **SUA TAREFA:**
            Redija o texto completo de um contrato, em HTML, seguindo rigorosamente a estrutura e as regras abaixo.

            **REGRAS DE ESTRUTURA E QUALIDADE:**
            1.  **Título:** Comece com `<h1>TÍTULO DO CONTRATO EM MAIÚSCULAS</h1>`. O título deve vir do campo 'Tipo Contrato'.
            2.  **Qualificação das Partes:** Apresente as partes de forma completa, usando o jargão 'Por este instrumento particular, de um lado, [DADOS DO CONTRATANTE], doravante denominado CONTRATANTE, e, de outro lado, [DADOS DO CONTRATADO], doravante denominado CONTRATADO, têm entre si, justo e contratado, o que segue:'.
            3.  **Cláusulas:** Estruture o corpo do contrato em cláusulas numeradas, usando `<h2>CLÁUSULA PRIMEIRA - DO OBJETO</h2>`, `<h2>CLÁUSULA SEGUNDA - DO VALOR E PAGAMENTO</h2>`, e assim por diante. Crie cláusulas para todos os dados relevantes fornecidos (objeto, valor, pagamento, prazos, responsabilidades, penalidades, confidencialidade, foro, etc.).
            4.  **Linguagem Técnica:** Utilize termos jurídicos apropriados sempre que necessário.
            5.  **Fechamento:** Ao final, inclua um parágrafo de fechamento padrão ('E, por estarem assim justas e contratadas...') e os campos para assinatura das partes e de duas testemunhas.
            6.  **SEM PLACEHOLDERS:** Não utilize placeholders como '[data]' ou '[local]'. O texto deve ser final.
            7.  **Formato de Saída:** O documento deve ser retornado como HTML puro, começando diretamente pelo `<h1>`. Não inclua `<html>`, `<body>`, ou ````html`.
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
        """Redige o contrato. Retorna um dicionário com 'documento' ou 'erro'."""
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
            print(f"Erro no Agente Redator de Contrato: {e}")
            return {"documento": None, "erro": f"Falha na redação do contrato: {e}"}