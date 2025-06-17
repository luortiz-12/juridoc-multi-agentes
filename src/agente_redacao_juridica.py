# Agente de Redação Jurídica

"""
Este script implementa o Agente de Redação Jurídica, responsável por elaborar o texto
da petição ou contrato com base nos dados processados e fundamentos jurídicos.
"""

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedacaoJuridica:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0.2)

        # <-- ALTERAÇÃO 1: Otimização e Refatoração ---
        # O prompt e o chain são criados UMA VEZ no construtor para máxima eficiência.
        prompt_template_base = """
            Você é um redator jurídico altamente qualificado, com vasta experiência na elaboração de documentos jurídicos no Brasil.
            Sua tarefa é redigir um documento jurídico completo e formal, utilizando os dados fornecidos e os fundamentos jurídicos identificados.

            **Dados Processados (do Agente Coletor):**
            {dados_processados_formatados}

            **Análise Jurídica (do Agente Jurídico Técnico):**
            {analise_juridica_formatada}

            **Instruções Gerais para Redação:**
            - Mantenha a linguagem formal, técnica e jurídica.
            - Evite repetições e seja conciso.
            - **IMPORTANTE:** Ao referenciar dados, inclua APENAS os campos que têm valor. Se um dado não estiver disponível, omita-o.
            - **Formato de Saída:** O documento deve ser retornado como HTML puro, sem tags `<html>`, `<body>`, ou blocos de código markdown (e.g., ```html`). O conteúdo deve começar diretamente pelo título `<h1>`.

            {instrucoes_especificas_tipo}
        """

        prompt = PromptTemplate(
            input_variables=[
                "dados_processados_formatados",
                "analise_juridica_formatada",
                "instrucoes_especificas_tipo"
            ],
            template=prompt_template_base
        )

        self.chain = LLMChain(llm=self.llm, prompt=prompt)
        # --- FIM DA ALTERAÇÃO 1 ---

        # As instruções específicas agora são apenas atributos de string da classe
        self.instrucoes_peticao = """
            **Instruções Específicas para a Petição Inicial:**
            1.  **Cabeçalho:** Inicie com "EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO DA ... VARA ... DA COMARCA DE ...".
            2.  **Qualificação das Partes:** Qualifique completamente o Requerente e o Requerido.
            ... (restante das instruções) ...
        """
        self.instrucoes_contrato = """
            **Instruções Específicas para o Contrato:**
            1.  **Título:** O título do contrato deve ser o 'tipo_contrato', em maiúsculas.
            2.  **Qualificação das Partes:** Qualifique completamente o CONTRATANTE e o CONTRATADO.
            ... (restante das instruções) ...
        """
        self.instrucoes_parecer = "..." # Mantenha as instruções aqui
        self.instrucoes_estudo = "..." # Mantenha as instruções aqui

    def _format_data_for_prompt(self, data: dict) -> str:
        """Formata um dicionário para uma string legível pelo LLM, ignorando valores None/vazios."""
        # Este método auxiliar já estava bom e foi mantido.
        formatted_parts = []
        for key, value in data.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            if isinstance(value, (dict, list)):
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {json.dumps(value, ensure_ascii=False, indent=2)}")
            else:
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted_parts)

    def redigir_documento(self, tipo_documento: str, dados_processados: dict, analise_juridica: dict) -> dict:
        """Redige o documento jurídico. Retorna um dicionário com 'documento' ou 'erro'."""
        
        # <-- ALTERAÇÃO 2: Lógica simplificada ---
        # Apenas seleciona as instruções corretas. Não recria o chain.
        instrucoes_map = {
            "peticao": self.instrucoes_peticao,
            "contrato": self.instrucoes_contrato,
            "parecer": self.instrucoes_parecer,
            "estudo": self.instrucoes_estudo
        }
        instrucoes_especificas = instrucoes_map.get(tipo_documento.lower())

        if not instrucoes_especificas:
            return {"documento": None, "erro": f"Tipo de documento '{tipo_documento}' não suportado para redação."}
        # --- FIM DA ALTERAÇÃO 2 ---

        dados_processados_formatados = self._format_data_for_prompt(dados_processados)
        analise_juridica_formatada = self._format_data_for_prompt(analise_juridica)

        try:
            resultado_llm = self.chain.invoke({
                "dados_processados_formatados": dados_processados_formatados,
                "analise_juridica_formatada": analise_juridica_formatada,
                "instrucoes_especificas_tipo": instrucoes_especificas
            })
            
            texto_gerado = resultado_llm["text"]

            # --- ALTERAÇÃO 3: Pós-processamento defensivo para HTML ---
            texto_limpo = texto_gerado.strip()
            if texto_limpo.startswith("```html"):
                texto_limpo = texto_limpo[7:]
            if texto_limpo.endswith("```"):
                texto_limpo = texto_limpo[:-3]
            texto_limpo = texto_limpo.strip()
            # --- FIM DA ALTERAÇÃO 3 ---
            
            return {"documento": texto_limpo, "erro": None}

        except Exception as e:
            print(f"Erro ao invocar LLM na Redação Jurídica: {e}")
            return {"documento": None, "erro": f"Falha na invocação do LLM para redação: {e}"}

# (O bloco 'if __name__ == "__main__":' precisará de um pequeno ajuste para lidar com o novo formato de retorno)
if __name__ == '__main__':
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Erro: Chave da API OpenAI (OPENAI_API_KEY) não configurada.")
        sys.exit(1)

    redator = AgenteRedacaoJuridica(llm_api_key=api_key)
    # ... (dados de exemplo permanecem os mesmos) ...

    print("\n--- Redação da Petição ---")
    resultado_peticao = redator.redigir_documento(
        # ... (argumentos) ...
    )
    if resultado_peticao["erro"]:
        print(f"Erro ao gerar petição: {resultado_peticao['erro']}")
    else:
        print(resultado_peticao["documento"])