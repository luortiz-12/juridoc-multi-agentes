# Agente Jurídico Técnico

"""
Este script implementa o Agente Jurídico Técnico, responsável por identificar normas aplicáveis,
fundamentos legais, artigos e jurisprudência com base nos dados coletados.
"""

import os # Importar os para acessar variáveis de ambiente
import json
import requests
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.tools import tool # Mantido, mas lembre-se que LLMChain não os invoca automaticamente

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
    print(f"Simulando busca na LexML para: {termo_busca}")
    if "código civil" in termo_busca.lower():
        return "Art. 186 do Código Civil: Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.\nArt. 927 do Código Civil: Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repara-lo."
    elif "código penal" in termo_busca.lower():
        return "Art. 138 do Código Penal: Calúnia.\nArt. 139 do Código Penal: Difamação.\nArt. 140 do Código Penal: Injúria."
    else:
        return "Nenhum resultado encontrado na LexML para o termo especificado."

# --- Ferramentas adicionais (aqui você implementaria as APIs reais) ---
@tool
def buscar_jurisprudencia_jusbrasil(termo_busca: str) -> str:
    """Busca jurisprudência no JusBrasil. Retorna títulos e links relevantes."""
    print(f"Simulando busca no JusBrasil para: {termo_busca}")
    return f"Resultados JusBrasil para '{termo_busca}': Link1, Link2"

@tool
def buscar_jurisprudencia_stj(termo_busca: str) -> str:
    """Busca jurisprudência no STJ. Retorna títulos e links relevantes."""
    print(f"Simulando busca no STJ para: {termo_busca}")
    return f"Resultados STJ para '{termo_busca}': Decisao A, Decisao B"

@tool
def buscar_jurisprudencia_stf(termo_busca: str) -> str:
    """Busca jurisprudência no STF. Retorna títulos e links relevantes."""
    print(f"Simulando busca no STF para: {termo_busca}")
    return f"Resultados STF para '{termo_busca}': Acordao X, Acordao Y"

@tool
def buscar_leis_senado(termo_busca: str) -> str:
    """Busca leis no portal do Senado. Retorna dispositivos legais relevantes."""
    print(f"Simulando busca no Senado para: {termo_busca}")
    return f"Resultados Leis do Senado para '{termo_busca}': Lei Z, Artigo W"
# --- Fim das Ferramentas adicionais ---


class AgenteJuridicoTecnico:
    def __init__(self, llm_api_key):
        # Mudei para gpt-4o-mini para melhor aderência ao formato JSON
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=llm_api_key, temperature=0)
        
        # Estas ferramentas seriam passadas para um AgentExecutor, não para um LLMChain direto
        # No seu caso, o LLMChain não as invoca, a lógica no analisar_dados faz a "simulação" de uso.
        self.tools = [
            buscar_legislacao_lexml,
            buscar_jurisprudencia_jusbrasil,
            buscar_jurisprudencia_stj,
            buscar_jurisprudencia_stf,
            buscar_leis_senado
        ]

        self.prompt_template = PromptTemplate(
            input_variables=["tipo_documento", "dados_processados"],
            template=
            """
            Você é um especialista jurídico com conhecimento aprofundado do ordenamento jurídico brasileiro.
            Sua tarefa é identificar os fundamentos legais, artigos, princípios e jurisprudência relevantes
            para a criação de um {tipo_documento} com base nos seguintes dados processados.

            Dados Processados (JSON):
            {dados_processados}

            Considere os seguintes pontos:
            - **Robustez a dados vazios:** Se um campo nos 'Dados Processados' estiver vazio, nulo ou não aplicável para o tipo de documento, ignore-o e NÃO o mencione na sua análise ou no JSON de saída.
            - Para 'contrato', foque em artigos do Código Civil relacionados a contratos, como função social e inadimplemento.
            - Para 'peticao', identifique artigos da Constituição Federal, Código Civil, Código de Processo Civil e Código Penal (se aplicável, como em casos de crimes contra a honra, utilizando campos como 'fatos_peticao' ou 'historico_peticao').
            - **Utilização de Ferramentas (Simuladas):** As informações de ferramentas serão pré-adicionadas para sua análise. Use-as para enriquecer os fundamentos.
            - Sintetize as informações de forma clara e objetiva, apresentando os fundamentos jurídicos mais pertinentes.

            **Formato da Saída:**
            Retorne a sua análise como um objeto JSON ESTRICTAMENTE VÁLIDO.
            **NÃO INCLUA VÍRGULAS PENDENTES (TRAILING COMMAS) EM LISTAS OU OBJETOS JSON.**
            **O JSON deve seguir exatamente este formato:**
            ```json
            {{
                "fundamentos_legais": [
                    {{"lei": "Nome da Lei/Código", "artigos": "Artigos relevantes", "descricao": "Breve descrição"}}
                    // Adicione mais objetos de lei/artigo conforme necessário, SEM vírgula no último item
                ],
                "principios_juridicos": ["Princípio 1", "Princípio 2"],
                "jurisprudencia_relevante": "Exemplo de jurisprudência ou súmula relevante",
                "analise_juridica_detalhada": "Uma análise textual detalhada dos fundamentos e como eles se aplicam ao caso."
            }}
            ```
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, tipo_documento: str, dados_processados: dict) -> dict:
        """Analisa os dados processados e identifica os fundamentos jurídicos."""
        
        # Converter dados_processados para string para o prompt
        # Usar ensure_ascii=False para evitar problemas com caracteres especiais
        dados_processados_str = json.dumps(dados_processados, ensure_ascii=False)

        # Lógica para usar as ferramentas (simulação de como o LLM poderia invocá-las)
        # Em um agente Langchain completo (com AgentExecutor), o LLM decidiria isso sozinho.
        # Aqui, estamos pré-invocando com base no tipo de documento.
        informacoes_ferramentas = ""
        
        # Busca na LexML
        if "código civil" in dados_processados_str.lower() or tipo_documento == "contrato":
            legislacao_civil = buscar_legislacao_lexml("código civil")
            informacoes_ferramentas += f"\n\nInformações adicionais da LexML (Código Civil):\n{legislacao_civil}"
        
        if "código penal" in dados_processados_str.lower() or tipo_documento == "peticao": # Petição pode ser criminal
            legislacao_penal = buscar_legislacao_lexml("código penal")
            informacoes_ferramentas += f"\n\nInformações adicionais da LexML (Código Penal):\n{legislacao_penal}"

        # Exemplos de uso de outras ferramentas com base em termos nos dados
        if "danos morais" in dados_processados_str.lower():
            informacoes_ferramentas += f"\n\nJurisprudência JusBrasil (danos morais):\n{buscar_jurisprudencia_jusbrasil('danos morais')}"
            informacoes_ferramentas += f"\n\nJurisprudência STJ (danos morais):\n{buscar_jurisprudencia_stj('danos morais')}"
            
        if "constituição" in dados_processados_str.lower():
            informacoes_ferramentas += f"\n\nJurisprudência STF (Constituição):\n{buscar_jurisprudencia_stf('constituição')}"
            informacoes_ferramentas += f"\n\nLeis do Senado (Constituição):\n{buscar_leis_senado('constituição')}"
            
        dados_para_prompt = f"{dados_processados_str}{informacoes_ferramentas}"

        resultado_llm = self.chain.invoke({
            "tipo_documento": tipo_documento,
            "dados_processados": dados_para_prompt # Passa os dados e as infos das ferramentas
        })
        
        # A saída do LLMChain é um dicionário, e o texto gerado está na chave 'text'
        texto_gerado = resultado_llm["text"]

        try:
            analise_juridica = json.loads(texto_gerado)
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON da saída do LLM no Agente Jurídico Técnico: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            # Retornar um dicionário de erro explícito para o Orquestrador
            return {"erro": "Falha na análise jurídica", "detalhes": str(e), "saida_llm": texto_gerado}

        return analise_juridica

# Exemplo de uso (requer uma chave de API da OpenAI configurada como variável de ambiente OPENAI_API_KEY)
if __name__ == '__main__':
    import sys # Importar sys para sys.exit()
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("Erro: Chave da API OpenAI (OPENAI_API_KEY) não configurada.")
        print("Por favor, defina a variável de ambiente antes de executar (ex: export OPENAI_API_KEY='sua_chave_aqui').")
        sys.exit(1)

    agente_juridico = AgenteJuridicoTecnico(llm_api_key=api_key)

    # --- SIMULAÇÃO DE DADOS PROCESSADOS (vindo do Agente Coletor) ---
    # Este é o formato que o Agente Coletor deveria retornar
    dados_processados_peticao_exemplo = {
        "tipo_documento": "peticao",
        "contratante_nome": "Maria Joaquina",
        "cpfContratante": "123.456.789-00",
        "historico_peticao": "Maria Joaquina foi aprovada em concurso público para delegada.",
        "fatos_peticao": "João Liborio proferiu insultos públicos, chamando-a de 'charlatã', 'ladrona', 'discarada' e acusando-a de fraude em concurso.",
        "pedido_peticao": "Indenização por danos morais no valor de R$ 16.000,00.",
        "valor_causa_peticao": "R$ 16.000,00",
        "base_legal_peticao": "Constituição Federal, Art. 5º, V e X; Código Civil, Art. 186, 927; Código Penal, Art. 138, 139, 140; Lei 12.550/2011.",
        "nome_contrario_peticao": "João Liborio",
        # ... outros campos de petição conforme o AgenteColetorDados retorna
    }

    dados_processados_contrato_exemplo = {
        "tipo_documento": "contrato",
        "tipo_contrato": "Prestação de Serviços de Desenvolvimento de Software",
        "contratante_nome": "Empresa X Ltda.",
        "cnpjContratante": "12.345.678/0001-99",
        "contratado_nome": "João Desenvolvedor",
        "cpfContratado": "111.222.333-44",
        "objeto_contrato": "Desenvolvimento de um aplicativo mobile para gerenciamento de tarefas.",
        "valor_contrato": "R$ 25.000,00",
        # ... outros campos de contrato
    }
    
    print("\n--- Análise Jurídica para Petição ---")
    analise_peticao = agente_juridico.analisar_dados(
        tipo_documento=dados_processados_peticao_exemplo["tipo_documento"],
        dados_processados=dados_processados_peticao_exemplo
    )
    print(json.dumps(analise_peticao, indent=2, ensure_ascii=False))

    print("\n--- Análise Jurídica para Contrato ---")
    analise_contrato = agente_juridico.analisar_dados(
        tipo_documento=dados_processados_contrato_exemplo["tipo_documento"],
        dados_processados=dados_processados_contrato_exemplo
    )
    print(json.dumps(analise_contrato, indent=2, ensure_ascii=False))