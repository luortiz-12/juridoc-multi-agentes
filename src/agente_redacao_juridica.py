# Agente de Redação Jurídica

"""
Este script implementa o Agente de Redação Jurídica, responsável por elaborar o texto
da petição ou contrato com base nos dados processados e fundamentos jurídicos.
"""

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import json

class AgenteRedacaoJuridica:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=llm_api_key, temperature=0.2) # Temperatura um pouco maior para criatividade na redação

        self.prompt_template_peticao = PromptTemplate(
            input_variables=["dados_processados", "analise_juridica"],
            template=
            """
            Você é um redator jurídico altamente qualificado, com vasta experiência na elaboração de petições iniciais.
            Sua tarefa é redigir uma petição inicial completa e formal, utilizando os dados fornecidos e os fundamentos jurídicos identificados.

            Dados Processados (do Agente Coletor):
            {dados_processados}

            Análise Jurídica (do Agente Jurídico Técnico):
            {analise_juridica}

            Instruções para a Redação da Petição:
            1.  **Cabeçalho:** Inicie com "EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO DA XXX VARA CÍVEL DA COMARCA DE CIDADE– ESTADO".
            2.  **Qualificação das Partes:** Inclua a qualificação completa do requerente e do requerido, utilizando os dados processados. Se algum dado (RG, CPF, CNPJ, endereço) não estiver disponível, omita-o, mas mantenha a estrutura.
            3.  **Fundamentação Legal (com fulcro):** Cite os artigos e leis relevantes conforme a análise jurídica, utilizando a expressão "com fulcro na...".
            4.  **Título da Ação:** Defina o título da ação (ex: AÇÃO DE REPARAÇÃO DE DANOS MORAIS).
            5.  **Dos Fatos:** Descreva os fatos de forma clara, concisa e cronológica, baseando-se nos dados processados, especialmente em `dados_adicionais_peticao.fatos` e `historico`.
            6.  **Do Direito:** Desenvolva a argumentação jurídica, explicando como os fundamentos legais (artigos, princípios, jurisprudência) se aplicam aos fatos. Utilize a `analise_juridica_detalhada` e os `fundamentos_legais` fornecidos.
            7.  **Dos Danos (se aplicável):** Detalhe os danos sofridos (morais, materiais), se houver, com base nos fatos e na análise jurídica.
            8.  **Da Quantia Devida (se aplicável):** Se houver pedido de indenização, justifique o valor com base nos princípios de proporcionalidade e gravidade da ofensa.
            9.  **Dos Pedidos:** Liste os pedidos de forma clara e numerada (ex: 1. Que o réu seja citado...). Inclua citação, condenação (se for o caso), custas processuais e honorários advocatícios.
            10. **Das Provas:** Inclua a cláusula padrão de protesto por todos os meios de prova.
            11. **Do Valor da Causa:** Indique o valor da causa.
            12. **Fechamento:** "Termos em que Pede Deferimento. (Local, data, ano). Advogado OAB".

            Formato:
            - Use parágrafos bem estruturados.
            - Mantenha a linguagem formal e técnica.
            - Evite repetições.
            - Não inclua tags HTML ou Markdown de bloco de código no início ou fim do documento.
            - Não inclua o rodapé HTML/CSS que estava no workflow do n8n, isso será tratado pelo Agente de Formatação Final.
            """
        )

        self.prompt_template_contrato = PromptTemplate(
            input_variables=["dados_processados", "analise_juridica"],
            template=
            """
            Você é um redator jurídico altamente qualificado, com vasta experiência na elaboração de contratos.
            Sua tarefa é redigir um contrato completo e formal, utilizando os dados fornecidos e os fundamentos jurídicos identificados.

            Dados Processados (do Agente Coletor):
            {dados_processados}

            Análise Jurídica (do Agente Jurídico Técnico):
            {analise_juridica}

            Instruções para a Redação do Contrato:
            1.  **Título:** O título do contrato deve ser o `tipo_contrato` dos dados processados, em maiúsculas.
            2.  **Qualificação das Partes:** Inclua a qualificação completa do CONTRATANTE e do CONTRATADO, utilizando os dados processados. Se algum dado (RG, CPF, CNPJ, endereço) não estiver disponível, omita-o, mas mantenha a estrutura.
            3.  **Cláusulas:** Utilize numeração e a palavra "CLÁUSULA" para cada seção principal do contrato (ex.: CLÁUSULA PRIMEIRA, CLÁUSULA SEGUNDA). Para subcláusulas, use classificação hierárquica com numeração (ex: 1.1, 1.2, 1.3 na CLÁUSULA PRIMEIRA).
            4.  **Objeto do Contrato:** Descreva detalhadamente o objeto do contrato.
            5.  **Valor e Forma de Pagamento:** Detalhe o valor e as condições de pagamento.
            6.  **Prazos de Vigência:** Especifique os prazos de execução e vigência.
            7.  **Responsabilidades das Partes:** Descreva as responsabilidades de cada parte.
            8.  **Penalidades por Descumprimento:** Inclua as penalidades aplicáveis em caso de descumprimento.
            9.  **Foro de Eleição:** Adicione uma cláusula final para o foro de eleição.
            10. **Referências Legais:** Inclua referências legais específicas (ex.: artigos do Código Civil) sempre que aplicável, conforme a `analise_juridica`.

            Formato:
            - Use parágrafos bem estruturados.
            - Mantenha a linguagem formal e técnica.
            - Evite repetições.
            - Não inclua tags HTML ou Markdown de bloco de código no início ou fim do documento.
            - Não inclua o rodapé HTML/CSS que estava no workflow do n8n, isso será tratado pelo Agente de Formatação Final.
            """
        )

        self.chain_peticao = LLMChain(llm=self.llm, prompt=self.prompt_template_peticao)
        self.chain_contrato = LLMChain(llm=self.llm, prompt=self.prompt_template_contrato)

    def redigir_documento(self, tipo_documento: str, dados_processados: dict, analise_juridica: dict) -> str:
        """Redige o documento jurídico com base nos dados e análise jurídica."""
        
        # Converter dicionários para strings formatadas para o prompt
        dados_processados_str = json.dumps(dados_processados, indent=2, ensure_ascii=False)
        analise_juridica_str = json.dumps(analise_juridica, indent=2, ensure_ascii=False)

        if tipo_documento.lower() == "peticao":
            resultado_llm = self.chain_peticao.invoke({
                "dados_processados": dados_processados_str,
                "analise_juridica": analise_juridica_str
            })
        elif tipo_documento.lower() == "contrato":
            resultado_llm = self.chain_contrato.invoke({
                "dados_processados": dados_processados_str,
                "analise_juridica": analise_juridica_str
            })
        else:
            return "Tipo de documento não suportado para redação."

        return resultado_llm["text"]

# Exemplo de uso (requer uma chave de API da OpenAI configurada como variável de ambiente OPENAI_API_KEY)
if __name__ == '__main__':
    # Para testar, substitua "SUA_CHAVE_API_OPENAI" pela sua chave real ou configure a variável de ambiente
    # import os
    # api_key = os.environ.get("OPENAI_API_KEY") 
    api_key = "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" # Substitua ou use variável de ambiente

    if not api_key or api_key == "sk-placeholder-key":
        print("Chave da API OpenAI não configurada. Defina a variável de ambiente OPENAI_API_KEY ou substitua no código.")
        exit()

    redator = AgenteRedacaoJuridica(llm_api_key=api_key)

    # Dados processados simulados do Agente Coletor de Dados (exemplo de petição)
    dados_exemplo_peticao = {
        "tipo_documento": "peticao",
        "contratante_nome": "Maria Joaquina",
        "contratante_cpf": "123.456.789-00",
        "contratante_endereco": "Rua Exemplo, 123, Cidade, Estado",
        "contratado_nome": "João Liborio",
        "contratado_cpf": "000.987.654-32",
        "contratado_endereco": "Av. Teste, 456, Cidade, Estado",
        "objeto_contrato": "Reparação de danos morais", # Usado aqui para contextualizar o LLM, embora seja petição
        "dados_adicionais_peticao": {
            "historico": "Maria Joaquina foi aprovada em concurso público para delegada.",
            "fatos": "João Liborio proferiu insultos públicos, chamando-a de 'charlatã', 'ladrona', 'discarada' e acusando-a de fraude em concurso.",
            "pedido": "Indenização por danos morais no valor de R$ 16.000,00.",
            "valorCausa": "R$ 16.000,00"
        }
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


