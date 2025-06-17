# Orquestrador Principal do Sistema Multi-Agentes

"""
Este script orquestra a execução dos agentes especializados para a geração de documentos jurídicos.
Ele coordena o fluxo de dados entre o Agente Coletor de Dados, Agente Jurídico Técnico,
Agente de Redação Jurídica, Agente de Validação e Agente de Formatação Final.
"""

import os
import json
import sys

# (Importações dos agentes permanecem as mesmas)
from agente_coletor_dados import AgenteColetorDados
from agente_juridico_tecnico import AgenteJuridicoTecnico
from agente_redacao_juridica import AgenteRedacaoJuridica
from agente_validacao import AgenteValidacao
from agente_formatacao_final import AgenteFormatacaoFinal

class Orquestrador:
    def __init__(self, openai_api_key):
        # A inicialização dos agentes está correta.
        self.coletor = AgenteColetorDados(llm_api_key=openai_api_key)
        self.juridico = AgenteJuridicoTecnico(llm_api_key=openai_api_key)
        self.redator = AgenteRedacaoJuridica(llm_api_key=openai_api_key)
        self.validador = AgenteValidacao(llm_api_key=openai_api_key)
        self.formatador = AgenteFormatacaoFinal()

    def gerar_documento(self, raw_input_data: dict) -> dict:
        print("\n--- Iniciando Geração de Documento ---")

        # 1. Agente Coletor de Dados
        print("Executando Agente Coletor de Dados...")
        dados_processados = self.coletor.coletar_e_processar(raw_input_data)
        # <-- ALTERAÇÃO 1: Padronização da verificação de erro
        if dados_processados.get("erro"):
            return {"status": "erro", "mensagem": "Falha na coleta de dados", "detalhes": dados_processados}
        print("Dados coletados e processados com sucesso.")

        # 2. Agente Jurídico Técnico
        print("Executando Agente Jurídico Técnico...")
        tipo_documento = dados_processados.get("tipo_documento", "")
        analise_juridica = self.juridico.analisar_dados(tipo_documento, dados_processados)
        # <-- ALTERAÇÃO 1: Padronização da verificação de erro
        if analise_juridica.get("erro"):
            return {"status": "erro", "mensagem": "Falha na análise jurídica", "detalhes": analise_juridica}
        print("Análise jurídica concluída com sucesso.")

        # 3. Agente de Redação Jurídica (com loop de validação)
        documento_gerado = ""
        resultado_validacao = {}
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            print(f"Executando Agente de Redação Jurídica (Tentativa {tentativa + 1}/{max_tentativas})...")
            
            # <-- ALTERAÇÃO 2: Lógica de chamada e verificação do Redator corrigida e simplificada
            resultado_redacao = self.redator.redigir_documento(tipo_documento, dados_processados, analise_juridica)
            
            if resultado_redacao.get("erro"):
                return {"status": "erro", "mensagem": "Falha na redação do documento", "detalhes": resultado_redacao}
            
            documento_gerado = resultado_redacao.get("documento", "")
            print("Documento preliminar redigido.")

            # 4. Agente de Validação
            print("Executando Agente de Validação...")
            resultado_validacao = self.validador.validar_documento(documento_gerado, dados_processados, analise_juridica)
            # <-- ALTERAÇÃO 1: Padronização da verificação de erro
            if resultado_validacao.get("erro"):
                return {"status": "erro", "mensagem": "Falha na validação do documento", "detalhes": resultado_validacao}
            print("Validação concluída.")

            if resultado_validacao.get("status") == "aprovado":
                print("Documento aprovado pelo Agente de Validação.")
                break # Sai do loop com sucesso
            else:
                print("Documento requer revisão. Sugestões:")
                sugestoes = resultado_validacao.get("sugestoes_melhoria", [])
                for sugestao in sugestoes:
                    print(f"  - Seção: {sugestao.get('secao')}, Descrição: {sugestao.get('descricao')}")
                
                # A lógica de feedback para o redator está ótima!
                analise_juridica["sugestoes_revisao"] = sugestoes
                # NOTA: Para um loop de revisão ainda mais eficaz, o prompt do AgenteRedacaoJuridica
                # poderia ser ajustado para explicitamente procurar e usar um campo "sugestoes_revisao".
                
                if tentativa == max_tentativas - 1:
                    print("Documento não aprovado após múltiplas tentativas.")
                    # A verificação final após o loop cuidará do retorno do erro.

        # Verificação final para garantir que o documento foi aprovado
        if resultado_validacao.get("status") != "aprovado":
            return {"status": "erro", "mensagem": "Documento não aprovado após múltiplas tentativas de revisão.", "detalhes": resultado_validacao}

        # 5. Agente de Formatação Final
        print("Executando Agente de Formatação Final...")
        documento_final_html = self.formatador.formatar_documento(documento_gerado, dados_processados)
        print("Documento formatado com sucesso.")

        print("--- Geração de Documento Concluída ---")
        return {"status": "sucesso", "documento_html": documento_final_html}

# (O bloco 'if __name__ == "__main__":' permanece o mesmo, a lógica de teste já é compatível)
# ... (código de teste) ...