# Agente Coletor de Dados

"""
Este script implementa o Agente Coletor de Dados, responsável por 
extrair e pré-processar as informações de entrada para a geração de documentos jurídicos.
"""

from langchain_core.prompts import PromptTemplate
from langchain.output_parsers.structured import StructuredOutputParser, ResponseSchema
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import json

# Simulação de uma entrada de dados (payload de um webhook, por exemplo)
raw_input_data = {
    "body": {
        "tipoDocumento": "contrato",
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
        "rgContratado": "98765432-1"
    }
}

class AgenteColetorDados:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=llm_api_key, temperature=0)

        # Definir o esquema de resposta para o parser
        response_schemas = [
            ResponseSchema(name="tipo_documento", description="Tipo do documento a ser gerado (ex: contrato, peticao)", type="string"),
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
            ResponseSchema(name="dados_adicionais_peticao", description="Coletar todos os outros campos que podem ser relevantes para uma petição, como histórico, fatos, pedido, valor da causa, documentos, base legal, qualificação da parte contrária, etc.", type="object")
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
            Analise os seguintes dados brutos e extraia as informações relevantes conforme as instruções de formato abaixo.
            Se uma informação específica não estiver presente nos dados brutos, retorne None ou uma string vazia para o campo correspondente.
            Priorize a extração exata dos valores como fornecidos.

            Dados Brutos:
            {dados_brutos}

            Instruções de Formato:
            {format_instructions}
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def coletar_e_processar(self, dados_brutos: dict) -> dict:
        """Coleta os dados brutos e os processa para uma estrutura definida."""
        # O n8n passa os dados dentro de uma chave 'body', então acessamos ela diretamente.
        # Em um cenário real, essa lógica pode precisar ser mais robusta.
        dados_para_processar = dados_brutos.get("body", dados_brutos)
        
        raw_json_string = json.dumps(dados_para_processar)
        
        resultado_llm = self.chain.invoke({"dados_brutos": raw_json_string})
        
        # A saída do LLMChain é um dicionário, e o texto gerado está na chave 'text'
        texto_gerado = resultado_llm['text']
        
        # Tentar fazer o parse do JSON. Se falhar, pode ser necessário tratar o erro
        # ou ajustar o prompt para garantir que o LLM sempre retorne um JSON válido.
        try:
            dados_estruturados = self.output_parser.parse(texto_gerado)
        except Exception as e:
            print(f"Erro ao fazer o parse da saída do LLM: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            # Retornar os dados brutos ou um dicionário de erro como fallback
            return {"erro": "Falha ao processar dados", "detalhes": str(e), "saida_llm": texto_gerado}
            
        return dados_estruturados

# Exemplo de uso (requer uma chave de API da OpenAI configurada como variável de ambiente OPENAI_API_KEY)
if __name__ == '__main__':
    # Para testar, substitua "SUA_CHAVE_API_OPENAI" pela sua chave real ou configure a variável de ambiente
    # import os
    # api_key = os.environ.get("OPENAI_API_KEY") 
    api_key = "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" # Substitua ou use variável de ambiente

    if not api_key or api_key == "sk-placeholder-key":
        print("Chave da API OpenAI não configurada. Defina a variável de ambiente OPENAI_API_KEY ou substitua no código.")
        exit()

    coletor = AgenteColetorDados(llm_api_key=api_key)
    dados_processados = coletor.coletar_e_processar(raw_input_data)

    print("\n--- Dados Brutos de Entrada ---")
    print(json.dumps(raw_input_data, indent=2, ensure_ascii=False))
    print("\n--- Dados Processados pelo Agente Coletor ---")
    print(json.dumps(dados_processados, indent=2, ensure_ascii=False))

    # Exemplo de como acessar um campo específico:
    # print(f"\nTipo de Documento: {dados_processados.get('tipo_documento')}")
    # print(f"Nome do Contratante: {dados_processados.get('contratante_nome')}")


