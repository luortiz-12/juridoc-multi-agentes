# orquestrador.py - Orquestrador Principal sem erros de sintaxe

import os
import json
import traceback
from typing import Dict, Any, List
from datetime import datetime

# Imports dos agentes
from agente_coletor_dados import AgenteColetorDados
from pesquisa_juridica import PesquisaJuridica
from agente_redator import AgenteRedator
from agente_validador import AgenteValidador

class OrquestradorPrincipal:
    """
    Orquestrador que executa todos os 4 agentes em sequencia.
    """
    
    def __init__(self):
        print("🎯 Inicializando Orquestrador Principal...")
        
        # Inicializar todos os agentes
        self.agente_coletor = AgenteColetorDados()
        self.pesquisa_juridica = PesquisaJuridica()
        self.agente_redator = AgenteRedator()
        self.agente_validador = AgenteValidador()
        
        print("✅ Orquestrador Principal inicializado")
    
    def processar_solicitacao_completa(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa solicitacao executando todos os 4 agentes.
        """
        try:
            print("🚀 Iniciando processamento completo...")
            inicio_processamento = datetime.now()
            
            agentes_executados = []
            
            # ETAPA 1: COLETOR DE DADOS
            print("📊 ETAPA 1: Agente Coletor de Dados")
            resultado_coletor = self.agente_coletor.estruturar_dados(dados_entrada)
            agentes_executados.append("Coletor de Dados")
            
            dados_estruturados = resultado_coletor.get('dados_estruturados', {})
            print(f"📊 Dados estruturados: OK")
            
            # ETAPA 2: PESQUISA JURIDICA
            print("🔍 ETAPA 2: Pesquisa Juridica")
            fundamentos = dados_estruturados.get('fundamentos_necessarios', [])
            tipo_acao = dados_estruturados.get('tipo_acao', '')
            
            resultado_pesquisa = self.pesquisa_juridica.pesquisar_fundamentacao_completa(
                fundamentos=fundamentos,
                tipo_acao=tipo_acao
            )
            agentes_executados.append("Pesquisa Juridica")
            print(f"📚 Pesquisa concluida: OK")
            
            # ETAPA 3: REDATOR
            print("✍️ ETAPA 3: Agente Redator")
            resultado_redacao = self.agente_redator.redigir_peticao_completa(
                dados_estruturados=dados_estruturados,
                pesquisa_juridica=resultado_pesquisa
            )
            agentes_executados.append("Redator")
            
            documento_html = resultado_redacao.get('documento_html', '')
            print(f"📄 Documento redigido: {len(documento_html)} caracteres")
            
            # ETAPA 4: VALIDADOR
            print("✅ ETAPA 4: Agente Validador")
            resultado_validacao = self.agente_validador.validar_e_formatar(
                documento_html=documento_html,
                dados_originais=dados_estruturados
            )
            agentes_executados.append("Validador")
            
            documento_final = resultado_validacao.get('documento_validado', documento_html)
            score_qualidade = resultado_validacao.get('estatisticas', {}).get('score_qualidade', 0)
            
            print(f"✅ Documento validado: {len(documento_final)} caracteres")
            print(f"📊 Score de qualidade: {score_qualidade}%")
            
            # RESULTADO FINAL
            tempo_total = (datetime.now() - inicio_processamento).total_seconds()
            
            resultado_final = {
                "status": "sucesso",
                "documento_html": documento_final,
                "dados_estruturados": dados_estruturados,
                "pesquisa_realizada": self._resumir_pesquisa(resultado_pesquisa, fundamentos),
                "agentes_executados": agentes_executados,
                "estatisticas_completas": {
                    "tempo_processamento": f"{tempo_total:.1f}s",
                    "tamanho_documento": len(documento_final),
                    "score_qualidade": score_qualidade,
                    "agentes_executados": len(agentes_executados)
                },
                "relatorio_qualidade": {
                    "score_qualidade": score_qualidade,
                    "status": "completo",
                    "agentes_executados": agentes_executados
                },
                "timestamp": datetime.now().isoformat(),
                "tempo_processamento": f"{tempo_total:.1f}s",
                "score_qualidade": score_qualidade
            }
            
            print(f"🎉 PROCESSAMENTO COMPLETO FINALIZADO!")
            print(f"⏱️ Tempo total: {tempo_total:.1f} segundos")
            print(f"🤖 Agentes executados: {', '.join(agentes_executados)}")
            print(f"📊 Score de qualidade: {score_qualidade}%")
            
            return resultado_final
            
        except Exception as e:
            print(f"❌ ERRO no orquestrador: {e}")
            return self._gerar_resultado_emergencia(dados_entrada, agentes_executados)
    
    def _resumir_pesquisa(self, resultado_pesquisa: Dict[str, Any], fundamentos: List[str]) -> str:
        """Gera resumo da pesquisa realizada."""
        area_direito = resultado_pesquisa.get('area_direito', 'nao identificada')
        return f"Pesquisa realizada para {area_direito}. Fundamentos: {', '.join(fundamentos)}"
    
    def _gerar_resultado_emergencia(self, dados_entrada: Dict[str, Any], agentes_executados: List[str]) -> Dict[str, Any]:
        """Gera resultado de emergencia com dados reais."""
        print("🚨 Gerando resultado de emergencia...")
        
        nome_autor = dados_entrada.get('clienteNome', '[NOME A SER PREENCHIDO]')
        nome_reu = dados_entrada.get('nome_contrario_peticao', '[NOME DO REU A SER PREENCHIDO]')
        fatos = dados_entrada.get('fatos_peticao', '[FATOS A SEREM DETALHADOS]')
        pedidos = dados_entrada.get('verbas_pleiteadas_peticao', '[PEDIDOS A SEREM ESPECIFICADOS]')
        valor_causa = dados_entrada.get('valor_causa_peticao', '[VALOR A SER ARBITRADO]')
        
        documento_emergencia = f"""
<!DOCTYPE html>
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
</html>
        """
        
        return {
            "status": "emergencia_com_dados_reais",
            "documento_html": documento_emergencia,
            "agentes_executados": agentes_executados,
            "score_qualidade": 60,
            "timestamp": datetime.now().isoformat()
        }