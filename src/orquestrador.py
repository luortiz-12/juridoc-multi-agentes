# orquestrador.py - Orquestrador que SEMPRE executa todos os 4 agentes

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
    Orquestrador que SEMPRE executa todos os 4 agentes em sequência:
    1. Coletor de Dados
    2. Pesquisa Jurídica
    3. Redator
    4. Validador
    
    NUNCA usa fallback com dados simulados.
    """
    
    def __init__(self):
        print("🎯 Inicializando Orquestrador Principal COMPLETO...")
        
        # Inicializar todos os agentes
        self.agente_coletor = AgenteColetorDados()
        self.pesquisa_juridica = PesquisaJuridica()
        self.agente_redator = AgenteRedator()
        self.agente_validador = AgenteValidador()
        
        print("✅ Orquestrador Principal COMPLETO inicializado")
    
    def processar_solicitacao_completa(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa solicitação executando TODOS os 4 agentes obrigatoriamente.
        """
        try:
            print("🚀 Iniciando processamento COMPLETO com todos os agentes...")
            inicio_processamento = datetime.now()
            
            agentes_executados = []
            
            # ========================================
            # ETAPA 1: AGENTE COLETOR DE DADOS
            # ========================================
            print("\n" + "="*50)
            print("📊 ETAPA 1: Agente Coletor de Dados")
            print("="*50)
            
            resultado_coletor = self.agente_coletor.estruturar_dados(dados_entrada)
            agentes_executados.append("Coletor de Dados")
            
            if resultado_coletor.get('status') != 'sucesso':
                print("⚠️ Coletor com problemas, mas continuando...")
            
            dados_estruturados = resultado_coletor.get('dados_estruturados', {})
            print(f"📊 Dados estruturados: {len(str(dados_estruturados))} caracteres")
            
            # ========================================
            # ETAPA 2: PESQUISA JURÍDICA
            # ========================================
            print("\n" + "="*50)
            print("🔍 ETAPA 2: Pesquisa Jurídica")
            print("="*50)
            
            # Extrair fundamentos para pesquisa
            fundamentos = dados_estruturados.get('fundamentos_necessarios', [])
            tipo_acao = dados_estruturados.get('tipo_acao', '')
            
            print(f"🔍 Pesquisando fundamentos: {fundamentos}")
            print(f"📋 Tipo de ação: {tipo_acao}")
            
            resultado_pesquisa = self.pesquisa_juridica.pesquisar_fundamentacao_completa(
                fundamentos=fundamentos,
                tipo_acao=tipo_acao
            )
            agentes_executados.append("Pesquisa Jurídica")
            
            print(f"📚 Pesquisa concluída: {len(str(resultado_pesquisa))} caracteres de fundamentação")
            
            # ========================================
            # ETAPA 3: AGENTE REDATOR
            # ========================================
            print("\n" + "="*50)
            print("✍️ ETAPA 3: Agente Redator")
            print("="*50)
            
            resultado_redacao = self.agente_redator.redigir_peticao_completa(
                dados_estruturados=dados_estruturados,
                pesquisa_juridica=resultado_pesquisa
            )
            agentes_executados.append("Redator")
            
            documento_html = resultado_redacao.get('documento_html', '')
            print(f"📄 Documento redigido: {len(documento_html)} caracteres")
            
            # ========================================
            # ETAPA 4: AGENTE VALIDADOR
            # ========================================
            print("\n" + "="*50)
            print("✅ ETAPA 4: Agente Validador")
            print("="*50)
            
            resultado_validacao = self.agente_validador.validar_e_formatar(
                documento_html=documento_html,
                dados_originais=dados_estruturados
            )
            agentes_executados.append("Validador")
            
            documento_final = resultado_validacao.get('documento_validado', documento_html)
            score_qualidade = resultado_validacao.get('estatisticas', {}).get('score_qualidade', 0)
            
            print(f"✅ Documento validado: {len(documento_final)} caracteres")
            print(f"📊 Score de qualidade: {score_qualidade}%")
            
            # ========================================
            # ETAPA 5: COMPILAÇÃO DO RESULTADO FINAL
            # ========================================
            print("\n" + "="*50)
            print("📋 ETAPA 5: Compilação do Resultado Final")
            print("="*50)
            
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
                    "dados_reais_utilizados": self._contar_dados_reais(dados_estruturados),
                    "pesquisas_realizadas": len(fundamentos),
                    "agentes_executados": len(agentes_executados)
                },
                "relatorio_qualidade": {
                    "score_qualidade": score_qualidade,
                    "status": "completo",
                    "agentes_executados": agentes_executados,
                    "validacao": resultado_validacao.get('relatorio_validacao', '')
                },
                "timestamp": datetime.now().isoformat(),
                "tempo_processamento": f"{tempo_total:.1f}s",
                "score_qualidade": score_qualidade
            }
            
            print("\n" + "="*80)
            print("🎉 PROCESSAMENTO COMPLETO FINALIZADO!")
            print(f"⏱️ Tempo total: {tempo_total:.1f} segundos")
            print(f"🤖 Agentes executados: {', '.join(agentes_executados)}")
            print(f"📊 Score de qualidade: {score_qualidade}%")
            print("="*80)
            
            return resultado_final
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO no orquestrador: {e}")
            print(f"📋 Traceback: {traceback.format_exc()}")
            
            # NUNCA retornar fallback com dados simulados
            # Sempre tentar gerar algo com os dados reais disponíveis
            return self._gerar_resultado_emergencia_com_dados_reais(dados_entrada, agentes_executados)
    
    def _resumir_pesquisa(self, resultado_pesquisa: Dict[str, Any], fundamentos: List[str]) -> str:
        """Gera resumo da pesquisa realizada."""
        
        area_direito = resultado_pesquisa.get('area_direito', 'não identificada')
        total_fontes = resultado_pesquisa.get('total_fontes', 0)
        
        return f"Pesquisa realizada para {area_direito} com {total_fontes} fontes. Fundamentos: {', '.join(fundamentos)}"
    
    def _contar_dados_reais(self, dados_estruturados: Dict[str, Any]) -> int:
        """Conta quantos dados reais foram utilizados."""
        
        dados_reais = 0
        
        # Verificar dados do autor
        autor = dados_estruturados.get('autor', {})
        if autor.get('nome') and not autor.get('nome', '').startswith('['):
            dados_reais += 1
        if autor.get('qualificacao') and not autor.get('qualificacao', '').startswith('['):
            dados_reais += 1
            
        # Verificar dados do réu
        reu = dados_estruturados.get('reu', {})
        if reu.get('nome') and not reu.get('nome', '').startswith('['):
            dados_reais += 1
        if reu.get('qualificacao') and not reu.get('qualificacao', '').startswith('['):
            dados_reais += 1
            
        # Verificar outros dados
        if dados_estruturados.get('fatos') and not dados_estruturados.get('fatos', '').startswith('['):
            dados_reais += 1
        if dados_estruturados.get('pedidos') and not dados_estruturados.get('pedidos', '').startswith('['):
            dados_reais += 1
        if dados_estruturados.get('valor_causa') and not dados_estruturados.get('valor_causa', '').startswith('['):
            dados_reais += 1
            
        return dados_reais
    
    def _gerar_resultado_emergencia_com_dados_reais(self, dados_entrada: Dict[str, Any], agentes_executados: List[str]) -> Dict[str, Any]:
        """
        Gera resultado de emergência usando APENAS dados reais.
        NUNCA usa dados simulados.
        """
        print("🚨 Gerando resultado de emergência com dados REAIS...")
        
        # Extrair dados reais básicos
        nome_autor = dados_entrada.get('clienteNome', '[NOME A SER PREENCHIDO]')
        nome_reu = dados_entrada.get('nome_contrario_peticao', '[NOME DO RÉU A SER PREENCHIDO]')
        fatos = dados_entrada.get('fatos_peticao', '[FATOS A SEREM DETALHADOS]')
        pedidos = dados_entrada.get('verbas_pleiteadas_peticao', '[PEDIDOS A SEREM ESPECIFICADOS]')
        valor_causa = dados_entrada.get('valor_causa_peticao', '[VALOR A SER ARBITRADO]')
        
        # Gerar documento básico com dados reais
        documento_emergencia = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Petição Inicial</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.8; }}
        h1 {{ text-align: center; font-size: 20px; margin: 30px 0; }}
        h2 {{ font-size: 16px; margin: 25px 0 15px 0; font-weight: bold; }}
        p {{ text-align: justify; margin-bottom: 15px; text-indent: 2em; }}
    </style>
</head>
<body>
    <h1>PETIÇÃO INICIAL</h1>
    
    <h2>I - QUALIFICAÇÃO DAS PARTES</h2>
    <p><strong>AUTOR:</strong> {nome_autor}</p>
    <p><strong>RÉU:</strong> {nome_reu}</p>
    
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
            "score_qualidade": 60,  # Score reduzido por ser emergência
            "timestamp": datetime.now().isoformat(),
            "observacao": "Resultado de emergência gerado com dados reais disponíveis"
        }



ao vivo
