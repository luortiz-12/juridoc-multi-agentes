# main_orchestrator.py
import os, json, sys
# (Suas importações de agentes aqui)
from agente_coletor_dados import AgenteColetorDados
# ...e todos os outros...

class Orquestrador:
    def __init__(self, openai_api_key):
        # (Sua instanciação de todos os 11 agentes aqui)
        # ...

    def gerar_documento(self, raw_input_data: dict) -> dict:
        print("\n--- Iniciando Geração de Documento com Arquitetura de Especialistas ---")
        dados_processados = self.coletor.coletar_e_processar(raw_input_data)
        if dados_processados.get("erro"):
            return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
        print("Dados coletados e processados com sucesso.")

        tipo_documento = dados_processados.get("tipo_documento", "").lower().strip()
        agente_tecnico_usado, agente_redator_usado = None, None
        
        # (Seu bloco if/elif para roteamento aqui)
        # ...
        
        if not agente_tecnico_usado:
            return {"status": "erro", "mensagem": f"Tipo de documento '{tipo_documento}' não suportado."}
        
        print(f"Roteado para especialistas de '{tipo_documento}'.")
        print("Executando Agente Técnico Especialista...")
        analise_juridica = agente_tecnico_usado.analisar_dados(dados_processados)
        if analise_juridica.get("erro"):
            return {"status": "erro", "mensagem": "Falha na análise jurídica especialista", "detalhes": analise_juridica}
        print("Análise jurídica especialista concluída.")

        # --- LÓGICA DE REVISÃO COM MEMÓRIA ---
        documento_gerado = None
        resultado_validacao = {}
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            print(f"Executando Agente Redator Especialista (Tentativa {tentativa + 1}/{max_tentativas})...")
            
            resultado_redacao = agente_redator_usado.redigir_documento(
                dados_processados=dados_processados,
                analise_juridica=analise_juridica,
                documento_anterior=documento_gerado # Passa o documento da iteração anterior (será None na primeira)
            )
            
            if resultado_redacao.get("erro"):
                return {"status": "erro", "mensagem": "Falha na redação especialista", "detalhes": resultado_redacao}
            
            documento_gerado = resultado_redacao.get("documento", "") # Atualiza o documento com a nova versão
            print("Documento preliminar redigido pelo especialista.")

            print("Executando Agente de Validação...")
            resultado_validacao = self.validador.validar_documento(documento_gerado, dados_processados, analise_juridica, tipo_documento)
            
            if resultado_validacao.get("erro"):
                return {"status": "erro", "mensagem": "Falha na validação do documento", "detalhes": resultado_validacao}
            
            if resultado_validacao.get("status") == "aprovado":
                print("Documento APROVADO pelo Agente de Validação.")
                break
            else:
                sugestoes = resultado_validacao.get("sugestoes_melhoria", [])
                print(f"Documento requer revisão. Sugestões: {sugestoes}")
                analise_juridica["sugestoes_revisao"] = sugestoes
                if tentativa == max_tentativas - 1:
                    print("Documento não aprovado após múltiplas tentativas.")
        
        # --- FIM DA LÓGICA DE REVISÃO ---

        if resultado_validacao.get("status") != "aprovado":
            return {"status": "erro", "mensagem": "Documento não aprovado após múltiplas tentativas de revisão.", "detalhes": resultado_validacao}

        print("Executando Agente de Formatação Final...")
        documento_final_html = self.formatador.formatar_documento(documento_gerado, dados_processados)
        print("Documento final formatado com sucesso.")

        print("--- Geração de Documento Concluída ---")
        return {"status": "sucesso", "documento_html": documento_final_html}