# Agente de Redação Jurídica

"""
Este script implementa o Agente de Redação Jurídica, responsável por elaborar o texto
da petição ou contrato com base nos dados processados e fundamentos jurídicos.
"""

import os # Importar os para acessar variáveis de ambiente
import json
import sys # Importar sys para sys.exit()
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class AgenteRedacaoJuridica:
    def __init__(self, llm_api_key):
        # Mudei para gpt-4o-mini para melhor aderência a instruções e nuances jurídicas
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0.2) 

        self.prompt_template_base = """
            Você é um redator jurídico altamente qualificado, com vasta experiência na elaboração de documentos jurídicos no Brasil.
            Sua tarefa é redigir um documento jurídico completo e formal, utilizando os dados fornecidos e os fundamentos jurídicos identificados.

            **Dados Processados (do Agente Coletor):**
            {dados_processados_formatados}

            **Análise Jurídica (do Agente Jurídico Técnico):**
            {analise_juridica_formatada}

            **Instruções Gerais para Redação:**
            - Mantenha a linguagem formal, técnica e jurídica.
            - Evite repetições e seja conciso.
            - **IMPORTANTE: Ao referenciar dados, inclua APENAS os campos que têm valor (não são None ou string vazia). Se um dado não estiver disponível ou não for relevante para o contexto, simplesmente omita-o no documento final.**
            - **Formato de Saída:** O documento deve ser retornado como HTML puro, sem tags `<html>`, `<body>`, ou blocos de código markdown (e.g., ```html`). O conteúdo deve começar diretamente pelo título `<h1>`.

            {instrucoes_especificas_tipo}
        """

        self.instrucoes_peticao = """
            **Instruções Específicas para a Petição Inicial:**
            1.  **Cabeçalho:** Inicie com "EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO DA [NÚMERO] VARA [TIPO DE VARA, ex: CÍVEL] DA COMARCA DE [CIDADE]– [ESTADO]".
            2.  **Qualificação das Partes:** Qualifique completamente o Requerente e o Requerido.
            3.  **Fundamentação Legal (com fulcro):** Cite artigos e leis relevantes usando "com fulcro na..." conforme a análise jurídica.
            4.  **Título da Ação:** Defina o título da ação (ex: AÇÃO DE REPARAÇÃO DE DANOS MORAIS).
            5.  **Dos Fatos:** Descreva os fatos de forma clara, concisa e cronológica.
            6.  **Do Direito:** Desenvolva a argumentação jurídica, aplicando os fundamentos legais aos fatos.
            7.  **Dos Danos (se aplicável):** Detalhe os danos sofridos (morais, materiais).
            8.  **Da Quantia Devida (se aplicável):** Justifique o valor da indenização.
            9.  **Dos Pedidos:** Liste os pedidos de forma clara e numerada (1., 2., etc.). Inclua citação, condenação (se for o caso), custas e honorários.
            10. **Das Provas:** Cláusula padrão de protesto por todos os meios de prova.
            11. **Do Valor da Causa:** Indique o valor da causa.
            12. **Fechamento:** "Termos em que Pede Deferimento. [Local, data, ano]. Advogado OAB".
        """

        self.instrucoes_contrato = """
            **Instruções Específicas para o Contrato:**
            1.  **Título:** O título do contrato deve ser o 'tipo_contrato' dos dados processados, em maiúsculas (ex: CONTRATO DE PRESTAÇÃO DE SERVIÇOS).
            2.  **Qualificação das Partes:** Qualifique completamente o CONTRATANTE e o CONTRATADO.
            3.  **Cláusulas:** Use "CLÁUSULA" para seções principais (CLÁUSULA PRIMEIRA), e numeração hierárquica para subcláusulas (1.1, 1.2).
            4.  **Objeto do Contrato:** Descreva detalhadamente.
            5.  **Valor e Forma de Pagamento:** Detalhe o valor e as condições.
            6.  **Prazos de Vigência:** Especifique prazos.
            7.  **Responsabilidades das Partes:** Descreva as responsabilidades.
            8.  **Penalidades por Descumprimento:** Inclua penalidades.
            9.  **Foro de Eleição:** Adicione cláusula final para o foro.
            10. **Referências Legais:** Inclua referências legais específicas (ex.: artigos do Código Civil) sempre que aplicável, conforme a análise jurídica.
        """
        # Adicione aqui templates para parecer e estudo de caso, se necessário.
        self.instrucoes_parecer = """
            **Instruções Específicas para o Parecer Jurídico:**
            - **Título:** PARECER JURÍDICO.
            - **Estrutura:** Identificação do Documento (SOLICITANTE, ASSUNTO), Consulta, Legislação Aplicável, Análise Jurídica, Conclusão.
            - **Linguagem:** Formal e técnica.
            - Inclua fundamentação jurídica (lei, doutrina, jurisprudência) de forma coesa.
            - Não inclua "Observação" no final.
        """
        self.instrucoes_estudo = """
            **Instruções Específicas para o Estudo de Caso Jurídico:**
            - **Título:** ESTUDO DE CASO JURÍDICO.
            - **Estrutura:** Título do Caso, Descrição do Caso, Contexto Jurídico, Pontos Relevantes, Análise do Caso, Conclusão (mínimo 3 parágrafos, com jurisprudência).
            - **Linguagem:** Formal, objetiva, com destaque para termos jurídicos em MAIÚSCULAS e Negrito (se o LLM suportar).
            - Inclua citações de leis, artigos, princípios, jurisprudência e doutrina.
        """


    def _format_data_for_prompt(self, data: dict) -> str:
        """Formata um dicionário para uma string legível pelo LLM, ignorando valores None/vazios."""
        formatted_parts = []
        for key, value in data.items():
            # Tenta ser mais inteligente sobre o que ignorar ou formatar
            if value is None or (isinstance(value, str) and not value.strip()):
                continue # Ignora campos None ou strings vazias/apenas espaços

            # Converte objetos aninhados em string JSON para o LLM
            if isinstance(value, dict):
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {json.dumps(value, ensure_ascii=False, indent=2)}")
            elif isinstance(value, list):
                 # Une a lista de strings ou representação de objetos se for uma lista de dicionários
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {json.dumps(value, ensure_ascii=False)}")
            else:
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted_parts)


    def redigir_documento(self, tipo_documento: str, dados_processados: dict, analise_juridica: dict) -> str:
        """Redige o documento jurídico com base nos dados e análise jurídica."""
        
        # Formatar os dados e a análise para o prompt, removendo campos vazios
        dados_processados_formatados = self._format_data_for_prompt(dados_processados)
        analise_juridica_formatada = self._format_data_for_prompt(analise_juridica)

        instrucoes_especificas = ""
        if tipo_documento.lower() == "peticao":
            instrucoes_especificas = self.instrucoes_peticao
            chain = LLMChain(llm=self.llm, prompt=PromptTemplate(input_variables=["dados_processados_formatados", "analise_juridica_formatada", "instrucoes_especificas_tipo"], template=self.prompt_template_base))
        elif tipo_documento.lower() == "contrato":
            instrucoes_especificas = self.instrucoes_contrato
            chain = LLMChain(llm=self.llm, prompt=PromptTemplate(input_variables=["dados_processados_formatados", "analise_juridica_formatada", "instrucoes_especificas_tipo"], template=self.prompt_template_base))
        elif tipo_documento.lower() == "parecer":
            instrucoes_especificas = self.instrucoes_parecer
            chain = LLMChain(llm=self.llm, prompt=PromptTemplate(input_variables=["dados_processados_formatados", "analise_juridica_formatada", "instrucoes_especificas_tipo"], template=self.prompt_template_base))
        elif tipo_documento.lower() == "estudo":
            instrucoes_especificas = self.instrucoes_estudo
            chain = LLMChain(llm=self.llm, prompt=PromptTemplate(input_variables=["dados_processados_formatados", "analise_juridica_formatada", "instrucoes_especificas_tipo"], template=self.prompt_template_base))
        else:
            return {"erro": "Tipo de documento não suportado para redação.", "tipo_solicitado": tipo_documento} # Retorna erro como dicionário

        try:
            resultado_llm = chain.invoke({
                "dados_processados_formatados": dados_processados_formatados,
                "analise_juridica_formatada": analise_juridica_formatada,
                "instrucoes_especificas_tipo": instrucoes_especificas
            })
            return resultado_llm["text"]
        except Exception as e:
            print(f"Erro ao invocar LLM na Redação Jurídica: {e}")
            return {"erro": "Falha na invocação do LLM para redação.", "detalhes": str(e)}


# Exemplo de uso (requer uma chave de API da OpenAI configurada como variável de ambiente OPENAI_API_KEY)
if __name__ == '__main__':
    # Para testar, obtenha a chave da API OpenAI da variável de ambiente
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("Erro: Chave da API OpenAI (OPENAI_API_KEY) não configurada.")
        print("Por favor, defina a variável de ambiente antes de executar (ex: export OPENAI_API_KEY='sua_chave_aqui').")
        sys.exit(1)

    redator = AgenteRedacaoJuridica(llm_api_key=api_key)

    # --- SIMULAÇÃO DE DADOS PROCESSADOS (vindo do Agente Coletor) ---
    # Usando dados do exemplo de petição do Agente Coletor (já corrigido para tipo_documento)
    dados_exemplo_peticao = {
        "tipo_documento": "peticao",
        "contratante_nome": "Maria Joaquina",
        "contratante_cpf": "123.456.789-00",
        "contratante_endereco": "Rua Exemplo, 123, Cidade, Estado",
        "contratado_nome": "João Liborio",
        "contratado_cpf": "000.987.654-32",
        "contratado_endereco": "Av. Teste, 456, Cidade, Estado",
        "objeto_contrato": "Reparação de danos morais",
        "historico_peticao": "Maria Joaquina foi aprovada em concurso público para delegada.",
        "fatos_peticao": "João Liborio proferiu insultos públicos, chamando-a de 'charlatã', 'ladrona', 'discarada' e acusando-a de fraude em concurso.",
        "pedido_peticao": "Indenização por danos morais no valor de R$ 16.000,00.",
        "valor_causa_peticao": "R$ 16.000,00"
    }

    # Análise jurídica simulada do Agente Jurídico Técnico (exemplo de petição)
    analise_exemplo_peticao = {
        "fundamentos_legais": [
            {"lei": "Constituição Federal", "artigos": "Art. 5º, V e X", "descricao": "Direito à honra e imagem, e indenização por sua violação."},
            {"lei": "Código Civil", "artigos": "Art. 186 e 927", "descricao": "Ato ilícito e obrigação de reparar o dano."},
            {"lei": "Código Penal", "artigos": "Art. 138, 139, 140", "descricao": "Crimes contra a honra: Calúnia, Difamação e Injúria."}
        ],
        "principios_juridicos": ["Responsabilidade Civil", "Dignidade da Pessoa Humana"],
        "jurisprudencia_relevante": "Súmula 37 do STJ: São cumuláveis as indenizações por dano material e dano moral oriundos do mesmo fato.",
        "analise_juridica_detalhada": "A conduta de João Liborio configura ato ilícito, violando a honra e imagem de Maria Joaquina, ensejando a reparação por danos morais com base nos artigos citados do Código Civil e da Constituição Federal. Os fatos também se enquadram nos crimes contra a honra previstos no Código Penal."
    }

    # Dados processados simulados do Agente Coletor de Dados (exemplo de contrato)
    dados_exemplo_contrato = {
        "tipo_documento": "contrato",
        "tipo_contrato": "Prestação de Serviços de Desenvolvimento de Software",
        "contratante_nome": "Empresa X Ltda.",
        "contratante_cnpj": "12.345.678/0001-99",
        "contratante_endereco": "Rua das Palmeiras, 123, São Paulo, SP",
        "contratado_nome": "João Desenvolvedor",
        "contratado_cpf": "111.222.333-44",
        "contratado_endereco": "Av. Principal, 456, Rio de Janeiro, RJ",
        "objeto_contrato": "Desenvolvimento de um aplicativo mobile para gerenciamento de tarefas.",
        "valor_contrato": "R$ 25.000,00",
        "pagamento": "50% na assinatura do contrato, 50% na entrega final.",
        "prazos_vigencia": "90 dias a partir da assinatura.",
        "responsabilidades_partes": "Contratante: fornecer todas as informações e materiais necessários. Contratado: entregar o software funcionando conforme especificações.",
        "penalidades_descumprimento": "Multa de 2% sobre o valor do contrato por dia de atraso na entrega.",
        "foro_eleicao": "São Paulo, SP"
    }

    # Análise jurídica simulada do Agente Jurídico Técnico (exemplo de contrato)
    analise_exemplo_contrato = {
        "fundamentos_legais": [
            {"lei": "Código Civil", "artigos": "Art. 421", "descricao": "Função social do contrato."},
            {"lei": "Código Civil", "artigos": "Art. 593", "descricao": "Contrato de prestação de serviços."}
        ],
        "principios_juridicos": ["Autonomia da Vontade", "Boa-fé Contratual"],
        "jurisprudencia_relevante": "Jurisprudência sobre validade de cláusulas contratuais.",
        "analise_juridica_detalhada": "O contrato de prestação de serviços deve observar os princípios da função social e da boa-fé, conforme o Código Civil. As cláusulas devem ser claras e equilibradas."
    }

    print("\n--- Redação da Petição ---")
    peticao_gerada = redator.redigir_documento(
        tipo_documento=dados_exemplo_peticao["tipo_documento"],
        dados_processados=dados_exemplo_peticao,
        analise_juridica=analise_exemplo_peticao
    )
    print(peticao_gerada)

    print("\n--- Redação do Contrato ---")
    contrato_gerado = redator.redigir_documento(
        tipo_documento=dados_exemplo_contrato["tipo_documento"],
        dados_processados=dados_exemplo_contrato,
        analise_juridica=analise_exemplo_contrato
    )
    print(contrato_gerado)