# Agente Coletor de Dados

"""
Este script implementa o Agente Coletor de Dados, responsável por
extrair e pré-processar as informações de entrada para a geração de documentos jurídicos.
"""

import os # Importar os para acessar variáveis de ambiente
import json
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers.structured import StructuredOutputParser, ResponseSchema
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

# Simulação de uma entrada de dados (payload de um webhook, por exemplo)
# Mantenho aqui como exemplo para o bloco if __name__ == '__main__':
raw_input_data = {
    "body": {
        "tipo_documento": "contrato", # Altere para tipo_documento para consistência com o que a API espera
        "tipoContrato": "Prestação de Serviços de Desenvolvimento de Software",
        "contratante": "Empresa X Ltda.",
        "cpfContratante": None, # Exemplo de campo opcional não preenchido
        "cnpjContratante": "12.345.678/0001-99",
        "enderecoContratante": "Rua das Palmeiras, 123, São Paulo, SP",
        "contratado": "João Desenvolvedor",
        "cpfContratado": "111.222.333-44",
        "cnpjContratado": None,
        "enderecoContratado": "Av. Principal, 456, Rio de Janeiro, RJ",
        "objeto": "Desenvolvimento de um aplicativo mobile para gerenciamento de tarefas.",
        "valor": "R$ 25.000,00",
        "pagamento": "50% na assinatura do contrato, 50% na entrega final.",
        "prazos": "90 dias a partir da assinatura.",
        "responsabilidades ": "Contratante: fornecer todas as informações e materiais necessários. Contratado: entregar o software funcionando conforme especificações.",
        "penalidades": "Multa de 2% sobre o valor do contrato por dia de atraso na entrega.",
        "foro": "São Paulo, SP",
        "rgContratante": None,
        "rgContratado": "98765432-1",
        # Adicionando alguns campos de petição para o exemplo de coleta multi-documento
        "historico_peticao": "Breve histórico do caso para petição.",
        "fatos_peticao": "Detalhes dos fatos para petição."
    }
}


class AgenteColetorDados:
    def __init__(self, llm_api_key):
        # Usando gpt-4o-mini para melhor capacidade de aderência ao formato JSON
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0)

        # Definir o esquema de resposta para o parser
        # Garanta que todos os campos possíveis de TODOS os tipos de documento estejam aqui,
        # ou que o LLM tenha flexibilidade para retornar apenas os presentes.
        response_schemas = [
            ResponseSchema(name="tipo_documento", description="Tipo do documento a ser gerado (ex: contrato, peticao, parecer, estudo)", type="string"),
            ResponseSchema(name="tipo_contrato", description="Tipo específico do contrato, se aplicável (ex: Prestação de Serviços)", type="string"),
            ResponseSchema(name="contratante_nome", description="Nome completo ou Razão Social do contratante", type="string"),
            ResponseSchema(name="contratante_cpf", description="CPF do contratante (se pessoa física)", type="string"),
            ResponseSchema(name="contratante_cnpj", description="CNPJ do contratante (se pessoa jurídica)", type="string"),
            ResponseSchema(name="contratante_rg", description="RG do contratante", type="string"),
            ResponseSchema(name="contratante_endereco", description="Endereço completo do contratante", type="string"),
            ResponseSchema(name="contratado_nome", description="Nome completo ou Razão Social do contratado", type="string"),
            ResponseSchema(name="contratado_cpf", description="CPF do contratado (se pessoa física)", type="string"),
            ResponseSchema(name="contratado_cnpj", description="CNPJ do contratado (se pessoa jurídica)", type="string"),
            ResponseSchema(name="contratado_rg", description="RG do contratado", type="string"),
            ResponseSchema(name="contratado_endereco", description="Endereço completo do contratado", type="string"),
            ResponseSchema(name="objeto_contrato", description="Descrição detalhada do objeto do contrato", type="string"),
            ResponseSchema(name="valor_contrato", description="Valor total do contrato", type="string"),
            ResponseSchema(name="forma_pagamento", description="Condições e forma de pagamento", type="string"),
            ResponseSchema(name="prazos_vigencia", description="Prazos de execução e vigência do contrato", type="string"),
            ResponseSchema(name="responsabilidades_partes", description="Responsabilidades de cada parte envolvida", type="string"),
            ResponseSchema(name="penalidades_descumprimento", description="Penalidades em caso de descumprimento contratual", type="string"),
            ResponseSchema(name="foro_eleicao", description="Foro eleito para dirimir conflitos", type="string"),
            
            # --- CAMPOS ESPECÍFICOS DE PETIÇÃO ---
            ResponseSchema(name="historico_peticao", description="Histórico relevante para a petição", type="string"),
            ResponseSchema(name="fatos_peticao", description="Detalhamento dos fatos para a petição", type="string"),
            ResponseSchema(name="pedido_peticao", description="O que está sendo pedido na petição", type="string"),
            ResponseSchema(name="valor_causa_peticao", description="Valor da causa para a petição", type="string"),
            ResponseSchema(name="documentos_peticao", description="Documentos relacionados à petição", type="string"),
            ResponseSchema(name="base_legal_peticao", description="Base legal para a petição", type="string"),
            ResponseSchema(name="qualificacao_contrario_peticao", description="Qualificação da parte contrária na petição", type="string"),
            ResponseSchema(name="nome_contrario_peticao", description="Nome da parte contrária na petição", type="string"),
            ResponseSchema(name="qualificacao_cliente_peticao", description="Qualificação do cliente na petição", type="string"),
            ResponseSchema(name="info_extra_civel_peticao", description="Informações extras para petição cível", type="string"),
            ResponseSchema(name="info_extra_trabalhista_peticao", description="Informações extras para petição trabalhista", type="string"),
            ResponseSchema(name="data_admissao_peticao", description="Data de admissão para petição trabalhista", type="string"),
            ResponseSchema(name="data_demissao_peticao", description="Data de demissão para petição trabalhista", type="string"),
            ResponseSchema(name="salario_peticao", description="Salário para petição trabalhista", type="string"),
            ResponseSchema(name="jornada_peticao", description="Jornada de trabalho para petição trabalhista", type="string"),
            ResponseSchema(name="motivo_saida_peticao", description="Motivo de saída para petição trabalhista", type="string"),
            ResponseSchema(name="verbas_pleiteadas_peticao", description="Verbas pleiteadas para petição trabalhista", type="string"),
            ResponseSchema(name="data_fato_peticao", description="Data do fato para petição criminal", type="string"),
            ResponseSchema(name="hora_fato_peticao", description="Hora do fato para petição criminal", type="string"),
            ResponseSchema(name="local_fato_peticao", description="Local do fato para petição criminal", type="string"),
            ResponseSchema(name="nome_vitima_peticao", description="Nome da vítima para petição criminal", type="string"),
            ResponseSchema(name="qualificacao_vitima_peticao", description="Qualificação da vítima para petição criminal", type="string"),
            ResponseSchema(name="desejo_representar_peticao", description="Desejo de representar para petição criminal", type="string"),
            ResponseSchema(name="testemunhas_peticao", description="Testemunhas para petição criminal", type="string"),
            ResponseSchema(name="info_extra_criminal_peticao", description="Informações extras para petição criminal", type="string"),
            ResponseSchema(name="autoridade_coatora_peticao", description="Autoridade coatora para habeas corpus", type="string"),
            ResponseSchema(name="local_prisao_peticao", description="Local da prisão para habeas corpus", type="string"),
            ResponseSchema(name="motivo_prisao_peticao", description="Motivo da prisão para habeas corpus", type="string"),
            ResponseSchema(name="fundamento_liberdade_peticao", description="Fundamento para liberdade para habeas corpus", type="string"),
            ResponseSchema(name="info_extra_hc_peticao", description="Informações extras para habeas corpus", type="string"),
            ResponseSchema(name="data_prisao_peticao", description="Data da prisão para habeas corpus", type="string"),

            # --- CAMPOS ESPECÍFICOS DE PARECER ---
            ResponseSchema(name="solicitante_parecer", description="Solicitante do parecer jurídico", type="string"),
            ResponseSchema(name="assunto_parecer", description="Assunto do parecer jurídico", type="string"),
            ResponseSchema(name="consulta_parecer", description="Detalhes da consulta para o parecer", type="string"),
            ResponseSchema(name="legislacao_parecer", description="Legislação aplicável ao parecer", type="string"),
            ResponseSchema(name="analise_parecer", description="Análise jurídica para o parecer", type="string"),
            ResponseSchema(name="conclusao_parecer", description="Conclusão do parecer jurídico", type="string"),

            # --- CAMPOS ESPECÍFICOS DE ESTUDO DE CASO ---
            ResponseSchema(name="titulo_caso", description="Título do estudo de caso", type="string"),
            ResponseSchema(name="descricao_caso", description="Descrição do estudo de caso", type="string"),
            ResponseSchema(name="contexto_juridico", description="Contexto jurídico do estudo de caso", type="string"),
            ResponseSchema(name="pontos_relevantes", description="Pontos relevantes do estudo de caso", type="string"),
            ResponseSchema(name="analise_caso", description="Análise do estudo de caso", type="string"),
            ResponseSchema(name="conclusao_caso", description="Conclusão do estudo de caso", type="string")
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()

        # Template do prompt para extração e estruturação
        self.prompt_template = PromptTemplate(
            input_variables=["dados_brutos"],
            partial_variables={"format_instructions": self.format_instructions},
            template=
            """
            Você é um assistente especializado em extrair e estruturar informações de dados brutos para a criação de documentos jurídicos.
            Analise os seguintes dados brutos e extraia **TODAS** as informações relevantes conforme as instruções de formato abaixo.
            Se uma informação específica não estiver presente nos dados brutos, **omita o campo ou retorne None**, mas **não inclua o campo no JSON se o valor for None/vazio se não for explicitamente obrigatório**.

            **GARANTA QUE A SAÍDA SEJA UM JSON ESTRICTAMENTE VÁLIDO. NÃO INCLUA VÍRGULAS PENDENTES (TRAILING COMMAS) EM LISTAS OU OBJETOS.**

            Dados Brutos:
            {dados_brutos}

            Instruções de Formato:
            {format_instructions}
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def coletar_e_processar(self, dados_brutos: dict) -> dict:
        """Coleta os dados brutos e os processa para uma estrutura definida."""
        dados_para_processar = dados_brutos.get("body", dados_brutos)
        
        raw_json_string = json.dumps(dados_para_processar, ensure_ascii=False) # Garante que caracteres especiais funcionem

        try:
            resultado_llm = self.chain.invoke({"dados_brutos": raw_json_string})
            
            # A saída do LLMChain é um dicionário, e o texto gerado está na chave 'text'
            texto_gerado = resultado_llm['text']
            
            # Tentar fazer o parse do JSON
            dados_estruturados = self.output_parser.parse(texto_gerado)
            return dados_estruturados
        except Exception as e:
            print(f"Erro ao fazer o parse da saída do LLM no Agente Coletor: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            # Retornar um dicionário de erro explícito
            return {"erro": "Falha ao processar dados de entrada pelo LLM", "detalhes": str(e), "saida_llm": texto_gerado}

# Exemplo de uso (requer uma chave de API da OpenAI configurada como variável de ambiente OPENAI_API_KEY)
if __name__ == '__main__':
    # Obtém a chave da API OpenAI da variável de ambiente
    import sys # Importa sys para sys.exit()
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("Erro: Chave da API OpenAI (OPENAI_API_KEY) não configurada.")
        print("Por favor, defina a variável de ambiente antes de executar (ex: export OPENAI_API_KEY='sua_chave_aqui').")
        sys.exit(1)

    coletor = AgenteColetorDados(llm_api_key=api_key)

    # --- SIMULAÇÃO DE ENTRADA DE DADOS (Payload de um webhook) ---
    # Usando o exemplo de petição para testar a abrangência
    raw_input_data_completo = {
        "body": {
            "tipo_documento": "peticao", # Alterei para tipo_documento para consistência
            "tipoContrato": None,
            "contratante": "Maria Joaquina",
            "cpfContratante": "123.456.789-00",
            "cnpjContratante": None,
            "enderecoContratante": "Rua Exemplo, 123, Cidade, Estado",
            "contratado": "João Liborio",
            "cpfContratado": "000.987.654-32",
            "cnpjContratado": None,
            "enderecoContratado": "Av. Teste, 456, Cidade, Estado",
            "objeto": "Reparação de danos morais",
            "valor": "R$ 16.000,00",
            "pagamento": None,
            "prazos": None,
            "responsabilidades ": None,
            "penalidades": None,
            "foro": "Cidade, Estado",
            "rgContratante": None,
            "rgContratado": None,
            "historico_peticao": "Maria Joaquina foi aprovada em concurso público para delegada.",
            "fatos_peticao": "João Liborio proferiu insultos públicos, chamando-a de 'charlatã', 'ladrona', 'discarada' e acusando-a de fraude em concurso.",
            "pedido_peticao": "Indenização por danos morais no valor de R$ 16.000,00.",
            "valor_causa_peticao": "R$ 16.000,00",
            "documentos_peticao": "Procuração, Diário Oficial do Estado do Ceará.",
            "base_legal_peticao": "Constituição Federal, Art. 5º, V e X; Código Civil, Art. 186, 927; Código Penal, Art. 138, 139, 140; Lei 12.550/2011.",
            "qualificacao_contrario_peticao": "nacionalidade, estado civil, portador do RG nº xxx, inscrito no CPF sob nº xxx, residente e domiciliado na cidade de xxx-xx",
            "nome_contrario_peticao": "João Liborio",
            "qualificacao_cliente_peticao": "nacionalidade, estado civil, portador do RG nº xxx, inscrito no CPF sob nº xxx, domiciliada na cidade de xxx, Estado de xxx",
            "info_extra_civel_peticao": None,
            "info_extra_trabalhista_peticao": None,
            "data_admissao_peticao": None,
            "data_demissao_peticao": None,
            "salario_peticao": None,
            "jornada_peticao": None,
            "motivo_saida_peticao": None,
            "verbas_pleiteadas_peticao": None,
            "data_fato_peticao": None,
            "hora_fato_peticao": None,
            "local_fato_peticao": None,
            "nome_vitima_peticao": None,
            "qualificacao_vitima_peticao": None,
            "desejo_representar_peticao": None,
            "testemunhas_peticao": None,
            "info_extra_criminal_peticao": None,
            "autoridade_coatora_peticao": None,
            "local_prisao_peticao": None,
            "motivo_prisao_peticao": None,
            "fundamento_liberdade_peticao": None,
            "info_extra_hc_peticao": None,
            "data_prisao_peticao": None
        }
    }


    print("\n--- Dados Brutos de Entrada ---")
    print(json.dumps(raw_input_data_completo, indent=2, ensure_ascii=False))

    dados_processados = coletor.coletar_e_processar(raw_input_data_completo)

    print("\n--- Dados Processados pelo Agente Coletor ---")
    print(json.dumps(dados_processados, indent=2, ensure_ascii=False))

    # Exemplo de como acessar um campo específico:
    # print(f"\nTipo de Documento: {dados_processados.get('tipo_documento')}")
    # print(f"Nome do Contratante: {dados_processados.get('contratante_nome')}")