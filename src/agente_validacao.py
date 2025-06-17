# Agente de Validação

"""
Este script implementa o Agente de Validação, responsável por verificar a coerência lógica,
estrutura e formato do documento jurídico gerado, além de identificar erros.
"""

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import json

class AgenteValidacao:
    def __init__(self, llm_api_key):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=llm_api_key, temperature=0)

        self.prompt_template = PromptTemplate(
            input_variables=["documento_gerado", "dados_processados", "analise_juridica"],
            template=
            """
            Você é um Agente de Validação Jurídica, com a tarefa de revisar e validar documentos jurídicos.
            Analise o `documento_gerado` com base nos `dados_processados` e na `analise_juridica`.

            Seu objetivo é verificar:
            1.  **Coerência Lógica:** Os fatos, fundamentos jurídicos e pedidos/cláusulas estão alinhados e fazem sentido?
            2.  **Estrutura e Formato:** O documento segue a estrutura esperada para uma petição ou contrato (cabeçalhos, numeração de cláusulas/itens, qualificação das partes)?
            3.  **Conformidade:** Todos os requisitos essenciais para o tipo de documento foram atendidos? As informações dos dados processados foram corretamente incorporadas?
            4.  **Erros:** Existem erros gramaticais, de digitação, inconsistências ou omissões?

            Documento Gerado:
            {documento_gerado}

            Dados Processados (para referência):
            {dados_processados}

            Análise Jurídica (para referência):
            {analise_juridica}

            Formato da Saída:
            Retorne um JSON com as seguintes chaves:
            {{
                "status": "aprovado" ou "revisar",
                "sugestoes_melhoria": [
                    {{"secao": "Seção do documento (ex: Fatos, Cláusula X)", "descricao": "Descrição da sugestão de melhoria ou erro encontrado."}}
                ]
            }}
            Se o status for "aprovado", a lista `sugestoes_melhoria` deve estar vazia.
            """
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def validar_documento(self, documento_gerado: str, dados_processados: dict, analise_juridica: dict) -> dict:
        """Valida o documento gerado e retorna sugestões de melhoria, se houver."""
        
        dados_processados_str = json.dumps(dados_processados, indent=2, ensure_ascii=False)
        analise_juridica_str = json.dumps(analise_juridica, indent=2, ensure_ascii=False)

        resultado_llm = self.chain.invoke({
            "documento_gerado": documento_gerado,
            "dados_processados": dados_processados_str,
            "analise_juridica": analise_juridica_str
        })
        
        texto_gerado = resultado_llm["text"]

        try:
            validacao_resultado = json.loads(texto_gerado)
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON da saída do LLM: {e}")
            print(f"Saída do LLM que causou o erro: {texto_gerado}")
            return {"erro": "Falha na validação", "detalhes": str(e), "saida_llm": texto_gerado}

        return validacao_resultado

# Exemplo de uso (requer uma chave de API da OpenAI configurada como variável de ambiente OPENAI_API_KEY)
if __name__ == '__main__':
    api_key = "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" # Substitua ou use variável de ambiente

    if not api_key or api_key == "sk-placeholder-key":
        print("Chave da API OpenAI não configurada. Defina a variável de ambiente OPENAI_API_KEY ou substitua no código.")
        exit()

    validador = AgenteValidacao(llm_api_key=api_key)

    # Simulação de um documento gerado (petição)
    documento_exemplo_peticao = """
EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO DA XXX VARA CÍVEL DA COMARCA DE CIDADE– ESTADO

Maria Joaquina, nacionalidade, estado civil, portador do RG nº xxx, inscrito no CPF sob nº xxx, domiciliada na cidade de xxx, Estado de xxx, vem, respeitosamente, à presença de Vossa Excelência, por seu advogado que ao final subscreve – procuração anexa (DOC. 01) –, com fulcro na Constituição Federal, nos artigos 5º, inciso V e X, pelos artigos 186, 927 e seguintes do Código Civil, artigos 282 do Código de Processo Civil, artigos 138, 139, 140 do Código Penal, com supedâneo na Lei 12.550 de 15 de Dezembro de 2011 e demais normas pertinentes, para propor a presente

AÇÃO DE REPARAÇÃO DE DANOS MORAIS

em face de João Liborio, nacionalidade, estado civil, portador do RG nº xxx, inscrito no CPF sob nº xxx, residente e domiciliado na cidade de xxx-xx pelos seguintes motivos de fato e de direito:

DOS FATOS
Em 30 de abril de 2021 a requerente, em comemoração a aprovação no concurso público de delegada da policia civil do estado do Ceará, estava com amigos e familiares em um restaurante.

Momentos depois, João Liborio, diante das pessoas presentes no local, sem motivo ou razão aparente, se aproximou de Maria Joaquina e proferiu insultos, alegando, que “ Maria Joaquina tinha passado em tal concurso pois fraudou a prova”.

Em alto tom de voz, João Liborio chamou a requerente de “exibida”, “charlatã”, “ladrona” e “discarada”.

Ocorre que, Maria constrangida com os insultos proferidos na frente de toda a sua família e de todo o restaurante, a mesma pagou a conta e se retirou do estabelecimento de forma discreta junto de seus familiares.

DOS DIREITOS
Na Constituição Federal de 1988, aplica-se a tutela do direito à indenização por dano material ou moral decorrente da violação de direitos fundamentais, tais como a honra e a imagem das pessoas:

"Art. 5º ( CF/88), X - São invioláveis a intimidade, a vida privada, a honra e a imagem das pessoas, assegurado o direito a indenização pelo dano material ou moral decorrente de sua violação;(...)".

O art. 186 do Código Civil trata da reparação do dano causado por ação agente:

"Art. 186 ( CC)- Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito".

O artigo 927 do Código Civil, retrata que aquele que causar dano a outrem é obrigado a repará-lo. Neste caso, é evidente que a requerente foi lesada, devido aos insultos proferidos pelo requerido publicamente.

“Art. 927 ( CC)- Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repara-lo."

Os artigos 138, 139 e 140 do Código Penal Brasileiro, que trata dos crimes de Calúnia, Difamação e Injúria, respectivamente, é sabido que houve, no ato em tela.

Calúnia, pois o requerido acusou o requerente de “fraude contra Concurso Público”, crime previsto na Lei 12.550 de 2011, Capitulo 5º, Título 10º do Código Penal, que trata de crimes contra a fé pública o artigo 311-A.

Difamação, pois o requerido palavras de baixo calão e incriminou a requerente em um ato que a mesma não cometeu, desonrando a imagem personalíssima da mesma.

Injúria, pois o requerido, proferiu palavras de baixo calão e incriminou a requerente por atos que não cometeu,.

Ademais, para que possa diminuir a dor e a vergonha imposta pelo insultos proferidos pelo requerido, o dinheiro trará a requerente uma satisfação e a certeza que o mesmo pagou pela ofensa proferida a ela.

DA QUANTIA DEVIDA
Sendo comprovada a conduta danosa do requerido, assim como o dano moral sofrido e o nexo causal, deverá ser apurado um valor para indenizar a requerente pelos atos de João Liborio.

Devendo tal indenização ser proporcional ao grau de culpa, á gravidade da ofensa e ao nível econômico do requerido, levando em consideração que a indenização tem o intuito de diminuir o efeito causado do dano que a requerente sofreu.

Assim, levando em consideração os para apuração bem como o grande ato lesivo e crimes em regime strictu sensu, entende-se que é razoável o valor R$ 16.000,00 (dezesseis mil reais).

DOS PEDIDOS
1. Que o réu seja citado, no endereço no qual foi inicialmente referido, para que o mesmo compareça a audiência de instrução e julgamento, para apresentação de resposta, sob pena de revelia e confissão quanto á mérito de fato;

2. Que Vossa Excelência considere como procedente o pedido com o intuito de condenar o réu a pagar indenização no valor de $ 16.000,00 (dezesseis mil reais) pelos danos morais;

3. Que o réu seja condenado a pagar as custa processuais e os honorário advocatícios;

DAS PROVAS
Protesta por todos os meios de prova em direito admitidos, depoimentos de testemunhas, bem como novas provas, documentais e outras, que eventualmente venham a surgir.

DO VALOR DA CAUSA
Dá-se à causa o valor de R$ xxxxx (Valor).

Termos em que

Pede Deferimento.

(Local, data, ano).

Advogado

OAB
"""

    # Dados processados simulados do Agente Coletor de Dados (exemplo de petição)
    dados_exemplo_peticao = {
        "tipo_documento": "peticao",
        "contratante_nome": "Maria Joaquina",
        "contratante_cpf": "123.456.789-00",
        "contratante_endereco": "Rua Exemplo, 123, Cidade, Estado",
        "contratado_nome": "João Liborio",
        "contratado_cpf": "000.987.654-32",
        "contratado_endereco": "Av. Teste, 456, Cidade, Estado",
        "objeto_contrato": "Reparação de danos morais",
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

    print("\n--- Validação da Petição ---")
    resultado_validacao = validador.validar_documento(
        documento_gerado=documento_exemplo_peticao,
        dados_processados=dados_exemplo_peticao,
        analise_juridica=analise_exemplo_peticao
    )
    print(json.dumps(resultado_validacao, indent=2, ensure_ascii=False))

    # Exemplo de documento com um erro simulado para testar sugestões de melhoria
    documento_com_erro = documento_exemplo_peticao.replace("João Liborio", "João Liborio (erro de digitação)", 1)
    print("\n--- Validação de Documento com Erro Simulado ---")
    resultado_validacao_erro = validador.validar_documento(
        documento_gerado=documento_com_erro,
        dados_processados=dados_exemplo_peticao,
        analise_juridica=analise_exemplo_peticao
    )
    print(json.dumps(resultado_validacao_erro, indent=2, ensure_ascii=False))


