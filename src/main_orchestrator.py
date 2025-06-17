# Orquestrador Principal do Sistema Multi-Agentes

"""
Este script orquestra a execução dos agentes especializados para a geração de documentos jurídicos.
Ele coordena o fluxo de dados entre o Agente Coletor de Dados, Agente Jurídico Técnico,
Agente de Redação Jurídica, Agente de Validação e Agente de Formatação Final.
"""

import os
import json
import sys # Importar sys para manipulação do path

# Adicionar o diretório raiz 'src' ao path para garantir que as importações dos agentes funcionem
# Se este arquivo (main_orchestrator.py) está em 'src/', então os agentes estão no mesmo nível.
# Se os agentes estão em 'src/agentes/', esta linha pode precisar de ajuste.
# Dado que juridoc.py (em src/routes/) importa main_orchestrator, e main_orchestrator importa os agentes,
# o sys.path.insert no juridoc.py (que aponta para '../') deve ser suficiente.
# Mas vamos manter uma adição defensiva aqui caso a estrutura de importação mude ou seja executado diretamente.
# Se os agentes estão na mesma pasta que este orquestrador, não é estritamente necessário.
# Vamos assumir que os agentes estão no mesmo nível de diretório ou que o sys.path já foi configurado por start.py/main.py
# (que ele é via juridoc.py). Se der erro de importação, vamos revisar os paths.

from agente_coletor_dados import AgenteColetorDados
from agente_juridico_tecnico import AgenteJuridicoTecnico
from agente_redacao_juridica import AgenteRedacaoJuridica
from agente_validacao import AgenteValidacao
from agente_formatacao_final import AgenteFormatacaoFinal

class Orquestrador:
    def __init__(self, openai_api_key):
        # A chave da API é passada aqui. Agora, é o AGENTE quem deve usá-la corretamente.
        # Ele não deve ter a chave hardcoded dentro de si.
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.juridico = AgenteJuridicoTecnico(llm_api_key=openai_api_key)
        self.redator = AgenteRedacaoJuridica(llm_api_key=openai_api_key)
        self.validador = AgenteValidacao(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal() # O formatador geralmente não precisa de LLM API Key

    def gerar_documento(self, raw_input_data: dict) -> dict:
        print("\n--- Iniciando Geração de Documento ---")

        # 1. Agente Coletor de Dados
        print("Executando Agente Coletor de Dados...")
        dados_processados = self.coletor.coletar_e_processar(raw_input_data)
        if "erro" in dados_processados:
            return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
        print("Dados coletados e processados com sucesso.")
        # print(json.dumps(dados_processados, indent=2, ensure_ascii=False))

        # 2. Agente Jurídico Técnico
        print("Executando Agente Jurídico Técnico...")
        tipo_documento = dados_processados.get("tipo_documento", "") # Assumimos que 'tipo_documento' vem aqui
        analise_juridica = self.juridico.analisar_dados(tipo_documento, dados_processados)
        if "erro" in analise_juridica:
            # Captura o erro da vírgula pendente aqui se o agente retornar
            return {"status": "erro", "mensagem": "Falha na análise jurídica", "detalhes": analise_juridica}
        print("Análise jurídica concluída com sucesso.")
        # print(json.dumps(analise_juridica, indent=2, ensure_ascii=False))

        # 3. Agente de Redação Jurídica (com loop de validação)
        documento_gerado = ""
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            print(f"Executando Agente de Redação Jurídica (Tentativa {tentativa + 1}/{max_tentativas})...")
            # Adicione 'analise_juridica.get("sugestoes_revisao", [])' se o redator precisar delas para correção
            documento_gerado = self.redator.redigir_documento(tipo_documento, dados_processados, analise_juridica)
            if isinstance(documento_gerado, dict) and "erro" in documento_gerado:
                return {"status": "erro", "mensagem": "Falha na redação do documento", "detalhes": documento_gerado}
            if "Tipo de documento não suportado" in documento_gerado: # Se o redator retornar esta string específica
                return {"status": "erro", "mensagem": "Tipo de documento não suportado para redação.", "detalhes": documento_gerado}
            print("Documento preliminar redigido.")
            # print(documento_gerado)

            # 4. Agente de Validação
            print("Executando Agente de Validação...")
            resultado_validacao = self.validador.validar_documento(documento_gerado, dados_processados, analise_juridica)
            if "erro" in resultado_validacao:
                return {"status": "erro", "mensagem": "Falha na validação do documento", "detalhes": resultado_validacao}
            print("Validação concluída.")
            # print(json.dumps(resultado_validacao, indent=2, ensure_ascii=False))

            if resultado_validacao.get("status") == "aprovado":
                print("Documento aprovado pelo Agente de Validação.")
                break
            else:
                print("Documento requer revisão. Sugestões:")
                for sugestao in resultado_validacao.get("sugestoes_melhoria", []):
                    print(f"  - Seção: {sugestao.get('secao')}, Descrição: {sugestao.get('descricao')}")

                # Adicionar sugestões de melhoria à análise jurídica para o redator tentar corrigir
                analise_juridica["sugestoes_revisao"] = resultado_validacao.get("sugestoes_melhoria", [])
                if tentativa == max_tentativas - 1:
                    return {"status": "erro", "mensagem": "Documento não aprovado após múltiplas tentativas de revisão.", "detalhes": resultado_validacao}

        # Verificação final caso o loop termine sem aprovação
        if resultado_validacao.get("status") != "aprovado":
            return {"status": "erro", "mensagem": "Documento não foi aprovado pelo validador.", "detalhes": resultado_validacao}


        # 5. Agente de Formatação Final
        print("Executando Agente de Formatação Final...")
        documento_final_html = self.formatador.formatar_documento(documento_gerado, dados_processados)
        print("Documento formatado com sucesso.")

        print("--- Geração de Documento Concluída ---")
        return {"status": "sucesso", "documento_html": documento_final_html}

# Exemplo de uso (apenas para testes LOCAIS)
if __name__ == '__main__':
    # Configurar a chave da API OpenAI LENDO DA VARIÁVEL DE AMBIENTE
    # VOCÊ DEVE TER EXPORT OPENAI_API_KEY="sua_chave_aqui" ANTES DE EXECUTAR LOCALMENTE
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if not openai_api_key:
        print("Erro: Chave da API OpenAI (OPENAI_API_KEY) não encontrada nas variáveis de ambiente.")
        print("Por favor, defina-a antes de executar o script (ex: export OPENAI_API_KEY='sua_chave_aqui').")
        sys.exit(1) # Importar sys no topo se for usar exit()

    orquestrador = Orquestrador(openai_api_key=openai_api_key)

    # --- SIMULAÇÃO DE ENTRADAS DE DADOS (PARA TESTE LOCAL) ---
    raw_input_data_peticao = {
        "tipo_documento": "peticao", # Alterado de tipoDocumento para tipo_documento para consistência
        "contratante": "Maria Joaquina",
        "cpfContratante": "123.456.789-00",
        "cnpjContratante": None,
        "enderecoContratante": "Rua Exemplo, 123, Cidade, Estado",
        "contratado": "João Liborio",
        "cpfContratado": "000.987.654-32",
        "cnpjContratado": None,
        "enderecoContratado": "Av. Teste, 4056, Cidade, Estado",
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

    raw_input_data_contrato = {
        "tipo_documento": "contrato", # Alterado de tipoDocumento para tipo_documento para consistência
        "tipoContrato": "Prestação de Serviços de Desenvolvimento de Software", # Manter este nome se o prompt LLM o usa
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
        "rgContratado": "98765432-1"
    }

    # Gerar a petição
    print("----- TESTE: GERANDO PETIÇÃO -----")
    resultado_peticao = orquestrador.gerar_documento(raw_input_data_peticao)
    if resultado_peticao["status"] == "sucesso":
        with open("peticao_final.html", "w", encoding="utf-8") as f:
            f.write(resultado_peticao["documento_html"])
        print("Petição HTML salva em: peticao_final.html")
    else:
        print(f"Erro ao gerar petição: {resultado_peticao['mensagem']}")
        print(f"Detalhes: {json.dumps(resultado_peticao['detalhes'], indent=2, ensure_ascii=False)}") # Para ver detalhes JSON

    print("\n" + "="*50 + "\n")

    # Gerar o contrato
    print("----- TESTE: GERANDO CONTRATO -----")
    resultado_contrato = orquestrador.gerar_documento(raw_input_data_contrato)
    if resultado_contrato["status"] == "sucesso":
        with open("contrato_final.html", "w", encoding="utf-8") as f:
            f.write(resultado_contrato["documento_html"])
        print("Contrato HTML salvo em: contrato_final.html")
    else:
        print(f"Erro ao gerar contrato: {resultado_contrato['mensagem']}")
        print(f"Detalhes: {json.dumps(resultado_contrato['detalhes'], indent=2, ensure_ascii=False)}") # Para ver detalhes JSON