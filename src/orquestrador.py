# orquestrador.py - Orquestrador Principal com Injeção de Dependência da API Key

import os
import json
import traceback
from typing import Dict, Any, List
from datetime import datetime

from agente_coletor_dados import AgenteColetorDados
from pesquisa_juridica import PesquisaJuridica
from agente_redator import AgenteRedator
from agente_validador import AgenteValidador

class OrquestradorPrincipal:
    def __init__(self):
        print("Inicializando Orquestrador Principal...")
        
        # COMENTÁRIO: A leitura da chave da API foi centralizada aqui.
        # O orquestrador agora é o único responsável por obter este segredo do ambiente.
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_api_key:
            # Este erro agora acontecerá aqui, de forma mais clara, se a chave não for encontrada.
            raise ValueError("ERRO CRÍTICO: DEEPSEEK_API_KEY não encontrada no ambiente do Orquestrador.")
        
        print("✅ Chave da API encontrada pelo Orquestrador.")

        self.agente_coletor = AgenteColetorDados()
        self.pesquisa_juridica = PesquisaJuridica()
        
        # COMENTÁRIO: Ao inicializar o AgenteRedator, agora passamos a chave da API diretamente para ele.
        # Isso é conhecido como "injeção de dependência" e é uma prática muito mais robusta.
        self.agente_redator = AgenteRedator(api_key=deepseek_api_key)
        
        self.agente_validador = AgenteValidador()
        
        print("Orquestrador Principal inicializado com todos os agentes configurados.")
    
    def processar_solicitacao_completa(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print("Iniciando processamento completo...")
            inicio_processamento = datetime.now()
            
            agentes_executados = []
            
            # ETAPA 1: COLETOR DE DADOS
            print("ETAPA 1: Agente Coletor de Dados")
            resultado_coletor = self.agente_coletor.coletar_e_processar(dados_entrada)
            agentes_executados.append("Coletor de Dados")
            
            if resultado_coletor.get("status") == "erro":
                return resultado_coletor # Retorna o erro do coletor diretamente

            dados_estruturados = resultado_coletor.get('dados_estruturados', {})
            print("Dados estruturados: OK")
            
            # ETAPA 2: PESQUISA JURIDICA
            print("ETAPA 2: Pesquisa Juridica")
            fundamentos = dados_estruturados.get('fundamentos_necessarios', [])
            tipo_acao = dados_estruturados.get('tipo_acao', '')
            
            resultado_pesquisa = self.pesquisa_juridica.pesquisar_fundamentacao_completa(
                fundamentos=fundamentos,
                tipo_acao=tipo_acao
            )
            agentes_executados.append("Pesquisa Juridica")
            print("Pesquisa concluida: OK")
            
            # ETAPA 3: REDATOR
            print("ETAPA 3: Agente Redator")
            resultado_redacao = self.agente_redator.redigir_peticao_completa(
                dados_estruturados=dados_estruturados,
                pesquisa_juridica=resultado_pesquisa
            )
            agentes_executados.append("Redator")
            
            if resultado_redacao.get("status") == "erro":
                return resultado_redacao

            documento_html = resultado_redacao.get('documento_html', '')
            print(f"Documento redigido: {len(documento_html)} caracteres")
            
            # ETAPA 4: VALIDADOR
            print("ETAPA 4: Agente Validador")
            resultado_validacao = self.agente_validador.validar_e_formatar(
                documento_html=documento_html,
                dados_originais=dados_estruturados
            )
            agentes_executados.append("Validador")
            
            documento_final = resultado_validacao.get('documento_validado', documento_html)
            score_qualidade = resultado_validacao.get('estatisticas', {}).get('score_qualidade', 0)
            
            print(f"Documento validado: {len(documento_final)} caracteres")
            print(f"Score de qualidade: {score_qualidade}%")
            
            # RESULTADO FINAL
            tempo_total = (datetime.now() - inicio_processamento).total_seconds()
            
            resultado_final = {
                "status": "sucesso",
                "documento_final": documento_final, # Mantido para consistência interna
                "dados_estruturados": dados_estruturados,
                "pesquisa_juridica": resultado_pesquisa,
                "agentes_executados": agentes_executados,
                "relatorio_validacao": resultado_validacao,
                "score_qualidade": score_qualidade,
                "tempo_processamento": f"{tempo_total:.1f}s",
                "timestamp": datetime.now().isoformat()
            }
            
            print("PROCESSAMENTO COMPLETO FINALIZADO!")
            return resultado_final
            
        except Exception as e:
            print(f"ERRO no orquestrador: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return self._gerar_resultado_emergencia(dados_entrada, agentes_executados)

    def _gerar_resultado_emergencia(self, dados_entrada: Dict[str, Any], agentes_executados: List[str]) -> Dict[str, Any]:
        # ... (código de emergência permanece o mesmo)
        print("Gerando resultado de emergencia...")
        nome_autor = dados_entrada.get('clienteNome', '[NOME A SER PREENCHIDO]')
        nome_reu = dados_entrada.get('nome_contrario_peticao', '[NOME DO REU A SER PREENCHIDO]')
        fatos = dados_entrada.get('fatos_peticao', '[FATOS A SEREM DETALHADOS]')
        pedidos = dados_entrada.get('verbas_pleiteadas_peticao', '[PEDIDOS A SEREM ESPECIFICADOS]')
        valor_causa = dados_entrada.get('valor_causa_peticao', '[VALOR A SER ARBITRADO]')
        
        documento_emergencia = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Peticao Inicial</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.8; }}
        h1 {{ text-align: center; font-size: 20px; margin: 30px 0; }}
        h2 {{ font-size: 16px; margin: 25px 0 15px 0; font-weight: bold; }}
        p {{ text-align: justify; margin-bottom: 15px; text-indent: 2em; }}
    </style>
</head>
<body>
    <h1>PETICAO INICIAL</h1>
    
    <h2>I - QUALIFICACAO DAS PARTES</h2>
    <p><strong>AUTOR:</strong> {nome_autor}</p>
    <p><strong>REU:</strong> {nome_reu}</p>
    
    <h2>II - DOS FATOS</h2>
    <p>{fatos}</p>
    
    <h2>III - DOS PEDIDOS</h2>
    <p>{pedidos}</p>
    
    <h2>IV - DO VALOR DA CAUSA</h2>
    <p>Valor da causa: R$ {valor_causa}</p>
    
    <p>Termos em que, pede deferimento.</p>
</body>
</html>"""
        
        return {
            "status": "emergencia_com_dados_reais",
            "documento_html": documento_emergencia,
            "documento_final": documento_emergencia,
            "pesquisa_juridica": {"status": "nao_realizada", "motivo": "erro_no_processamento"},
            "relatorio_validacao": {"status": "emergencia", "score_qualidade": 60},
            "agentes_executados": agentes_executados,
            "score_qualidade": 60,
            "timestamp": datetime.now().isoformat()
        }