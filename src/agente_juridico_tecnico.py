# Agente Jurídico Técnico

"""
Este script implementa o Agente Jurídico Técnico, responsável por identificar normas aplicáveis,
fundamentos legais, artigos e jurisprudência com base nos dados coletados.
"""

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.tools import tool
import json
import requests

# Simulação de uma base de dados jurídica (poderia ser um VectorStore real)
# Para fins de demonstração, usaremos um dicionário simples.
base_dados_juridica = {
    "responsabilidade civil": {
        "artigos": ["Art. 186 do Código Civil", "Art. 927 do Código Civil"],
        "principios": ["Tutela do direito à indenização por dano material ou moral"],
        "jurisprudencia_exemplo": "Súmula 37 do STJ: São cumuláveis as indenizações por dano material e dano moral oriundos do mesmo fato."
    },
    "calunia": {
        "artigos": ["Art. 138 do Código Penal"],
        "principios": ["Crime contra a honra"],
        "jurisprudencia_exemplo": "Acórdão TJSP sobre calúnia em redes sociais."
    },
    "difamacao": {
        "artigos": ["Art. 139 do Código Penal"],
        "principios": ["Crime contra a honra"],
        "jurisprudencia_exemplo": "Acórdão STJ sobre difamação de pessoa jurídica."
    },
    "injuria": {
        "artigos": ["Art. 140 do Código Penal"],
        "principios": ["Crime contra a honra"],
        "jurisprudencia_exemplo": "Acórdão TRF sobre injúria racial."
    },
    "contrato de prestacao de servicos": {
        "artigos": ["Art. 593 do Código Civil", "Art. 421 do Código Civil"],
        "principios": ["Função social do contrato", "Autonomia da vontade"],
        "jurisprudencia_exemplo": "Jurisprudência sobre rescisão de contrato de prestação de serviços."
    }
}

@tool
def buscar_legislacao_lexml(termo_busca: str) -> str:
    """Busca legislação e normas jurídicas na API LexML. Retorna um resumo dos resultados."""
    # Simulação de chamada à API LexML
    # Em um cenário real, você faria uma requisição HTTP para a API LexML.
    # Ex: response = requests.get(f"https://www.lexml.gov.br/busca/rest?format=json&q={termo_busca}")
    # Para este exemplo, vamos retornar dados simulados.
    
    print(f"Simulando busca na LexML para: {termo_busca}")
    if "código civil" in termo_busca.lower():
        return "Art. 186 do Código Civil: Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.\nArt. 927 do Código Civil: Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repara-lo."
    elif "código penal" in termo_busca.lower():
        return "Art. 138 do Código Penal: Calúnia.\nArt. 139 do Código Penal: Difamação.\nArt. 140 do Código Penal: Injúria."
    else:
        return "Nenhum resultado encontrado na LexML para o termo especificado."

class AgenteJuridicoTecnico:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=llm_api_key, temperature=0)
        self.tools = [
            buscar_legislacao_lexml
        ]

        self.prompt_template = PromptTemplate(
            input_variables=["tipo_documento", "dados_processados"],
            template=
            """
            Você é um especialista jurídico com conhecimento aprofundado do ordenamento jurídico brasileiro.
            Sua tarefa é identificar os fundamentos legais, artigos, princípios e jurisprudência relevantes
            para a criação de um {tipo_documento} com base nos seguintes dados processados:

            Dados Processados:
            {dados_processados}

            Considere os seguintes pontos:
            - Para 'contrato', foque em artigos do Código Civil relacionados a contratos, como função social e inadimplemento.
            - Para 'peticao', identifique artigos da Constituição Federal, Código Civil, Código de Processo Civil e Código Penal (se aplicável, como em casos de crimes contra a honra).
            - Utilize a ferramenta `buscar_legislacao_lexml` para pesquisar termos jurídicos específicos e obter informações detalhadas.
            - Sintetize as informações de forma clara e objetiva, apresentando os fundamentos jurídicos mais pertinentes.
            - Se for uma petição, identifique os crimes contra a honra (calúnia, difamação, injúria) se os fatos indicarem isso.

            Formato da Saída:
            Retorne um JSON com as seguintes chaves:
            {{
                "fundamentos_legais": [
                    {{"lei": "Nome da Lei/Código", "artigos": "Artigos relevantes", "descricao": "Breve descrição"}}
                ],
                "principios_juridicos": ["Princípio 1", "Princípio 2"],
                "jurisprudencia_relevante": "Exemplo de jurisprudência ou súmula relevante",
                "analise_juridica_detalhada": "Uma análise textual detalhada dos fundamentos e como eles se aplicam ao caso."
            }}
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, tipo_documento: str, dados_processados: dict) -> dict:
        """Analisa os dados processados e identifica os fundamentos jurídicos."""
        
        # Converter dados_processados para string para o prompt
        dados_processados_str = json.dumps(dados_processados, ensure_ascii=False)

        # Adicionar lógica para usar as ferramentas
        # Para este exemplo, vamos simular a chamada da ferramenta dentro do LLMChain
        # Em um agente Langchain completo, o LLM decidiria quando usar a ferramenta.
        
        # Exemplo de como o LLM pode decidir usar a ferramenta:
        # Se o tipo de documento for petição e houver menção a crimes contra a honra, buscar no Código Penal.
        if tipo_documento == "peticao" and any(keyword in dados_processados_str.lower() for keyword in ["calunia", "difamacao", "injuria"]):
            print("Detectado termos relacionados a crimes contra a honra. Buscando no Código Penal...")
            legislacao_penal = buscar_legislacao_lexml("código penal")
            dados_processados_str += f"\n\nInformações adicionais da LexML (Código Penal):\n{legislacao_penal}"
        
        if tipo_documento == "contrato":
            print("Detectado contrato. Buscando no Código Civil...")
            legislacao_civil = buscar_legislacao_lexml("código civil")
            dados_processados_str += f"\n\nInformações adicionais da LexML (Código Civil):\n{legislacao_civil}"

        resultado_llm = self.chain.invoke({"tipo_documento": tipo_documento, "dados_processados": dados_processados_str})
        
        # A saída do LLMChain é um dicionário, e o texto gerado está na chave 'text'
        texto_gerado = resultado_llm["text"]

        try:
            analise_juridica = json.loads(texto_gerado)
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON da saída do LLM: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na análise jurídica", "detalhes": str(e), "saida_llm": texto_gerado}

        return analise_juridica

# Exemplo de uso (requer uma chave de API da OpenAI configurada como variável de ambiente OPENAI_API_KEY)
if __name__ == '__main__':
    # Para testar, substitua "SUA_CHAVE_API_OPENAI" pela sua chave real ou configure a variável de ambiente
    # import os
    # api_key = os.environ.get("OPENAI_API_KEY") 
    api_key = "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" # Substitua ou use variável de ambiente

    if not api_key or api_key == "sk-placeholder-key":
        print("Chave da API OpenAI não configurada. Defina a variável de ambiente OPENAI_API_KEY ou substitua no código.")
        exit()

    # Dados processados simulados do Agente Coletor de Dados
    dados_exemplo_peticao = {
        "tipo_documento": "peticao",
        "contratante_nome": "Maria Joaquina",
        "objeto_contrato": "Reparação de danos morais",
        "dados_adicionais_peticao": {
            "historico": "Maria Joaquina foi aprovada em concurso público para delegada.",
            "fatos": "João Liborio proferiu insultos públicos, chamando-a de 'charlatã', 'ladrona', 'discarada' e acusando-a de fraude em concurso.",
            "pedido": "Indenização por danos morais no valor de R$ 16.000,00.",
            "baseLegal": "Constituição Federal, Art. 5º, V e X; Código Civil, Art. 186, 927; Código Penal, Art. 138, 139, 140; Lei 12.550/2011."
        }
    }

    dados_exemplo_contrato = {
        "tipo_documento": "contrato",
        "tipo_contrato": "Prestação de Serviços de Desenvolvimento de Software",
        "contratante_nome": "Empresa X Ltda.",
        "contratado_nome": "João Desenvolvedor",
        "objeto_contrato": "Desenvolvimento de um aplicativo mobile para gerenciamento de tarefas.",
        "valor_contrato": "R$ 25.000,00"
    }

    agente_juridico = AgenteJuridicoTecnico(llm_api_key=api_key)

    print("\n--- Análise Jurídica para Petição ---")
    analise_peticao = agente_juridico.analisar_dados(
        tipo_documento=dados_exemplo_peticao["tipo_documento"],
        dados_processados=dados_exemplo_peticao
    )
    print(json.dumps(analise_peticao, indent=2, ensure_ascii=False))

    print("\n--- Análise Jurídica para Contrato ---")
    analise_contrato = agente_juridico.analisar_dados(
        tipo_documento=dados_exemplo_contrato["tipo_documento"],
        dados_processados=dados_exemplo_contrato
    )
    print(json.dumps(analise_contrato, indent=2, ensure_ascii=False))


