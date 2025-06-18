# Agente Coletor de Dados

"""
Este script implementa o Agente Coletor de Dados, responsável por
extrair e pré-processar as informações de entrada para a geração de documentos jurídicos.
"""

import os
import json
import sys
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers.structured import StructuredOutputParser, ResponseSchema
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

# Simulação de uma entrada de dados (payload de um webhook, por exemplo)
# Mantenho aqui como exemplo para o bloco if __name__ == '__main__':
raw_input_data = {
    "body": {
        "tipo_documento": "contrato",
        "tipoContrato": "Prestação de Serviços de Desenvolvimento de Software",
        "contratante": "Empresa X Ltda.",
        "cpfContratante": None,
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
        "historico_peticao": "Breve histórico do caso para petição.",
        "fatos_peticao": "Detalhes dos fatos para petição."
    }
}


class AgenteColetorDados:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0)

        # A definição de 'response_schemas' é longa, então a omiti da visualização, mas ela deve estar aqui no seu código
        response_schemas = [
            ResponseSchema(name="tipo_documento", description="Tipo do documento a ser gerado (ex: contrato, peticao, parecer, estudo)", type="string"),
            # ... e todos os outros 60+ schemas que você definiu ...
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()

        self.prompt_template = PromptTemplate(
            input_variables=["dados_brutos"],
            partial_variables={"format_instructions": self.format_instructions},
            template=
            """
            Você é um assistente especializado em extrair e estruturar informações de dados brutos para a criação de documentos jurídicos.
            Analise os seguintes dados brutos e extraia TODAS as informações relevantes conforme as instruções de formato abaixo.
            Se uma informação específica não estiver presente nos dados brutos, omita o campo correspondente na saída JSON final.

            Dados Brutos:
            {dados_brutos}

            Instruções de Formato Geradas Automaticamente:
            {format_instructions}

            ---
            **REGRA DE OURO PARA A SAÍDA FINAL:**
            Apesar das instruções acima, sua resposta final DEVE ser um objeto JSON VÁLIDO e NADA MAIS.
            NÃO escreva nenhum texto explicativo antes ou depois do JSON.
            NÃO envolva o JSON em blocos de código Markdown como ```json.
            Sua resposta deve começar DIRETAMENTE com o caractere `{{` e terminar DIRETAMENTE com o caractere `}}`.
            NÃO inclua vírgulas pendentes (trailing commas).
            ---
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def coletar_e_processar(self, dados_brutos: dict) -> dict:
        """Coleta os dados brutos e os processa para uma estrutura definida."""
        dados_para_processar = dados_brutos.get("body", dados_brutos)
        
        raw_json_string = json.dumps(dados_para_processar, ensure_ascii=False)
        texto_gerado = ""

        try:
            resultado_llm = self.chain.invoke({"dados_brutos": raw_json_string})
            
            texto_gerado = resultado_llm['text']
            
            texto_limpo = texto_gerado.strip()
            
            if '```json' in texto_limpo:
                texto_limpo = texto_limpo.split('```json', 1)[-1]
            
            if '```' in texto_limpo:
                texto_limpo = texto_limpo.split('```', 1)[0]
                
            texto_limpo = texto_limpo.strip()
            
            dados_estruturados = self.output_parser.parse(texto_limpo)
            return dados_estruturados
            
        except Exception as e:
            print(f"Erro ao fazer o parse da saída do LLM no Agente Coletor: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha ao processar dados de entrada pelo LLM", "detalhes": str(e), "saida_llm": texto_gerado}

# (O bloco 'if __name__ == "__main__":' permanece o mesmo)