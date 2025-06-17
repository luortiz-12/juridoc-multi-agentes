# Agente de Validação

"""
Este script implementa o Agente de Validação, responsável por verificar a coerência lógica,
estrutura e formato do documento jurídico gerado, além de identificar erros.
"""

import os # Importar os para acessar variáveis de ambiente
import json
import sys # Importar sys para sys.exit()
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteValidacao:
    def __init__(self, llm_api_key):
        # Mudei para gpt-4o-mini para melhor precisão na validação e aderência ao formato JSON
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0)

        # Inicio do PromptTemplate (a parte que você forneceu)
        self.prompt_template = PromptTemplate(
            input_variables=["documento_gerado", "dados_processados", "analise_juridica"],
            template=
            """
            Você é um Agente de Validação Jurídica, com a tarefa de revisar e validar documentos jurídicos.
            Analise o `documento_gerado` com base nos `dados_processados` (dados originais do formulário) e na `analise_juridica` (fundamentos legais).

            Seu objetivo é verificar, de forma minuciosa e crítica:
            1.  **Coerência Lógica e Jurídica:** Os fatos, fundamentos jurídicos e pedidos/cláusulas estão alinhados, fazem sentido e não há contradições? A argumentação é sólida e legalmente consistente?
            2.  **Estrutura e Formato:** O documento segue a estrutura esperada para o tipo de documento (petição, contrato, parecer, estudo de caso)? (Ex: cabeçalhos, qualificação das partes, numeração de cláusulas/itens, etc.). Ele está em formato HTML válido? (Verifique tags HTML abertas/fechadas e erros de sintaxe HTML).
            3.  **Completude e Elaboração:** O documento contém todas as seções essenciais e informações cruciais para o tipo de documento? As seções estão suficientemente detalhadas, bem elaboradas e com a profundidade necessária? O texto é coeso e profissional?
            4.  **Fundamentação Legal:** Foram incluídas citações de artigos legais, princípios jurídicos **e, OBRIGATORIAMENTE, jurisprudência relevante** onde aplicável? As referências são adequadas e suficientes para fundamentar a tese/cláusulas? (Verifique se a `analise_juridica` foi bem aplicada na redação).
            5.  **Erros:** Existem erros gramaticais, de digitação, inconsistências de dados ou omissões?

            **Documento Gerado (HTML):**
            {documento_gerado}

            **Dados Processados (para referência):**
            {dados_processados}

            **Análise Jurídica (para referência):**
            {analise_juridica}

            **Instruções para a Análise e Formato da Saída:**
            - Ignore campos vazios ou `None` nos `dados_processados` e `analise_juridica` que não são relevantes para a validação da estrutura ou do conteúdo principal do documento.
            - Avalie o `documento_gerado` como o texto final que será entregue.
            - Seja objetivo e direto nas sugestões de melhoria. Cada sugestão deve ser clara e acionável para o Agente de Redação Jurídica.
            - **Se um problema for identificado, descreva-o e indique qual seção do documento (ou aspecto geral) precisa de melhoria.**
            - **Se o documento for reprovado por falta de jurisprudência ou fundamentação, seja explícito na sugestão.**

            Retorne um JSON ESTRICTAMENTE VÁLIDO.
            **NÃO INCLUA VÍRGULAS PENDENTES (TRAILING_COMMAS) EM LISTAS OU OBJETOS JSON.**
            **O JSON deve seguir exatamente este formato:**
            ```json
            {{
                "status": "aprovado" ou "revisar", // "aprovado" se não houver problemas significativos; "revisar" caso contrário.
                "sugestoes_melhoria": [
                    {{"secao": "Seção do documento (ex: 'Dos Fatos', 'Cláusula Terceira', 'Conclusão', 'Formatação HTML', 'Fundamentação Legal')", "descricao": "Descrição clara e concisa da sugestão de melhoria ou erro encontrado. Ex: 'Expandir o detalhamento dos fatos, incluindo mais contexto.', 'Adicionar jurisprudência do STJ sobre o tema X para a seção Do Direito.', 'Corrigir a tag </div> mal fechada na seção X'."}}
                    // Adicione mais sugestões conforme necessário. Se aprovado, esta lista deve ser vazia.
                ]
            }}
            ```
            Se o status for "aprovado", a lista `sugestoes_melhoria` DEVE estar vazia.
            """
        ) # Fim do PromptTemplate

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def validar_documento(self, documento_gerado: str, dados_processados: dict, analise_juridica: dict) -> dict:
        """Valida o documento gerado e retorna sugestões de melhoria, se houver."""
        
        # Converter dicionários para strings JSON para o prompt
        dados_processados_str = json.dumps(dados_processados, indent=2, ensure_ascii=False)
        analise_juridica_str = json.dumps(analise_juridica, indent=2, ensure_ascii=False)

        try:
            resultado_llm = self.chain.invoke({
                "documento_gerado": documento_gerado,
                "dados_processados": dados_processados_str,
                "analise_juridica": analise_juridica_str
            })
            
            texto_gerado = resultado_llm["text"]

            validacao_resultado = json.loads(texto_gerado)
            return validacao_resultado
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON da saída do LLM no Agente de Validação: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            # Retornar um dicionário de erro explícito para o Orquestrador
            return {"erro": "Falha na validação (JSON inválido)", "detalhes": str(e), "saida_llm": texto_gerado}
        except Exception as e:
            print(f"Erro inesperado no Agente de Validação: {e}")
            return {"erro": "Falha inesperada na validação", "detalhes": str(e), "saida_llm": ""}


# Exemplo de uso (requer uma chave de API da OpenAI configurada como variável de ambiente OPENAI_API_KEY)
if __name__ == '__main__':
    # Para testar, obtenha a chave da API OpenAI da variável de ambiente
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("Erro: Chave da API OpenAI (OPENAI_API_KEY) não configurada.")
        print("Por favor, defina a variável de ambiente antes de executar (ex: export OPENAI_API_KEY='sua_chave_aqui').")
        sys.exit(1)

    validador = AgenteValidacao(llm_api_key=api_key)

    # --- SIMULAÇÃO DE DADOS PARA VALIDAÇÃO ---
    # Simulação de um documento gerado (petição) - EXEMPLO COM ERRO SIMULADO
    documento_exemplo_peticao_com_erro = """
    <h1>AÇÃO DE REPARAÇÃO DE DANOS MORAIS</h1>

    EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO DA XXX VARA CÍVEL DA COMARCA DE CIDADE– ESTADO

    <p>Maria Joaquina, nacionalidade, estado civil, portador do RG nº xxxx, inscrito no CPF sob nº xxx, domiciliada na cidade de xxx, Estado de xxx, vem, respeitosamente, à presença de Vossa Excelência, por seu advogado que ao final subscreve – procuração anexa (DOC. 01) –, com fulcro na Constituição Federal, nos artigos