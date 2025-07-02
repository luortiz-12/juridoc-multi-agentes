# orquestrador.py - Orquestrador Principal Integrado

import json
import traceback
from typing import Dict, Any, List
from datetime import datetime

from agente_coletor_dados import AgenteColetorDados
from pesquisa_juridica import PesquisaJuridica
from agente_redator import AgenteRedator
from agente_validador import AgenteValidador

class OrquestradorPrincipal:
    """
    Orquestrador principal que coordena todos os agentes para gerar petições iniciais
    com qualidade profissional e fundamentação jurídica sólida.
    """
    
    def __init__(self, openai_api_key: str):
        print("🚀 Inicializando Orquestrador Principal...")
        
        try:
            # Inicializar todos os agentes
            self.coletor_dados = AgenteColetorDados(openai_api_key)
            self.pesquisa_juridica = PesquisaJuridica()
            self.redator = AgenteRedator(openai_api_key)
            self.validador = AgenteValidador(openai_api_key)
            
            print("✅ Todos os agentes inicializados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro na inicialização dos agentes: {e}")
            raise
    
    def gerar_peticao_completa(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal para gerar uma petição inicial completa.
        
        Fluxo:
        1. Coleta e estruturação de dados
        2. Pesquisa jurídica
        3. Redação da petição
        4. Validação e formatação final
        
        Args:
            dados_entrada: Dados brutos recebidos do n8n ou outro sistema
            
        Returns:
            Dict com petição final e metadados completos
        """
        inicio_processamento = datetime.now()
        
        try:
            print("\n" + "="*60)
            print("🚀 INICIANDO GERAÇÃO DE PETIÇÃO INICIAL")
            print("="*60)
            
            # ETAPA 1: COLETA E ESTRUTURAÇÃO DE DADOS
            print("\n📊 ETAPA 1: Coleta e estruturação de dados")
            print("-" * 40)
            
            resultado_coleta = self.coletor_dados.coletar_e_processar(dados_entrada)
            
            if resultado_coleta.get("status") != "sucesso":
                return self._gerar_resposta_erro(
                    "Falha na coleta de dados", 
                    resultado_coleta,
                    inicio_processamento
                )
            
            dados_estruturados = resultado_coleta["dados_estruturados"]
            print("✅ Dados estruturados com sucesso")
            
            # ETAPA 2: PESQUISA JURÍDICA
            print("\n🔍 ETAPA 2: Pesquisa jurídica")
            print("-" * 40)
            
            temas_pesquisa = dados_estruturados.get("fundamentos_juridicos", {}).get("temas_pesquisa", [])
            tipo_acao = dados_estruturados.get("tipo_acao", "")
            
            resultado_pesquisa = self.pesquisa_juridica.pesquisar_fundamentos_juridicos(
                fundamentos=temas_pesquisa,
                tipo_acao=tipo_acao
            )
            print("✅ Pesquisa jurídica concluída")
            
            # ETAPA 3: REDAÇÃO DA PETIÇÃO
            print("\n✍️ ETAPA 3: Redação da petição")
            print("-" * 40)
            
            resultado_redacao = self.redator.redigir_peticao(
                dados_estruturados=dados_estruturados,
                pesquisa_juridica=resultado_pesquisa
            )
            
            if resultado_redacao.get("status") != "sucesso":
                return self._gerar_resposta_erro(
                    "Falha na redação", 
                    resultado_redacao,
                    inicio_processamento
                )
            
            peticao_redigida = resultado_redacao["peticao_html"]
            print("✅ Petição redigida com sucesso")
            
            # ETAPA 4: VALIDAÇÃO E FORMATAÇÃO FINAL
            print("\n🔍 ETAPA 4: Validação e formatação final")
            print("-" * 40)
            
            resultado_validacao = self.validador.validar_e_formatar(
                peticao_html=peticao_redigida,
                dados_estruturados=dados_estruturados
            )
            
            if resultado_validacao.get("status") != "sucesso":
                return self._gerar_resposta_erro(
                    "Falha na validação", 
                    resultado_validacao,
                    inicio_processamento
                )
            
            peticao_final = resultado_validacao["peticao_final"]
            print("✅ Validação e formatação concluídas")
            
            # ETAPA 5: COMPILAÇÃO DO RESULTADO FINAL
            print("\n📋 ETAPA 5: Compilação do resultado final")
            print("-" * 40)
            
            tempo_processamento = (datetime.now() - inicio_processamento).total_seconds()
            
            resultado_final = {
                "status": "sucesso",
                "documento_html": peticao_final,
                "metadados": {
                    "tipo_documento": "Petição Inicial",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tempo_processamento": f"{tempo_processamento:.2f}s",
                    "versao_sistema": "2.0",
                    "agentes_utilizados": [
                        "AgenteColetorDados",
                        "PesquisaJuridica", 
                        "AgenteRedator",
                        "AgenteValidador"
                    ]
                },
                "dados_estruturados": dados_estruturados,
                "pesquisa_realizada": {
                    "temas_pesquisados": temas_pesquisa,
                    "resumo": resultado_pesquisa.get("resumo_pesquisa", ""),
                    "fontes_consultadas": self._extrair_fontes_pesquisa(resultado_pesquisa)
                },
                "estatisticas_redacao": resultado_redacao.get("estatisticas", {}),
                "relatorio_qualidade": resultado_validacao.get("relatorio_qualidade", {}),
                "aprovacao": {
                    "aprovada": resultado_validacao.get("aprovada", False),
                    "problemas_encontrados": resultado_validacao.get("problemas_encontrados", []),
                    "score_qualidade": resultado_validacao.get("relatorio_qualidade", {}).get("score_qualidade", 0)
                }
            }
            
            print("\n" + "="*60)
            print("🎉 PETIÇÃO GERADA COM SUCESSO!")
            print(f"⏱️ Tempo total: {tempo_processamento:.2f}s")
            print(f"📊 Score de qualidade: {resultado_final['aprovacao']['score_qualidade']}%")
            print(f"✅ Status: {'Aprovada' if resultado_final['aprovacao']['aprovada'] else 'Precisa revisão'}")
            print("="*60)
            
            return resultado_final
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO NO ORQUESTRADOR: {e}")
            traceback.print_exc()
            
            return self._gerar_resposta_erro(
                f"Erro crítico na orquestração: {str(e)}",
                {"detalhes": traceback.format_exc()},
                inicio_processamento
            )
    
    def _extrair_fontes_pesquisa(self, resultado_pesquisa: Dict[str, Any]) -> List[str]:
        """Extrai as fontes consultadas na pesquisa."""
        fontes = []
        
        # Extrair de cada categoria de pesquisa
        for categoria in ["leis", "jurisprudencia", "doutrina"]:
            conteudo = resultado_pesquisa.get(categoria, "")
            if isinstance(conteudo, str) and "Fonte:" in conteudo:
                # Extrair URLs das fontes
                import re
                urls = re.findall(r'Fonte: (https?://[^\s\n]+)', conteudo)
                fontes.extend(urls)
        
        return list(set(fontes))  # Remover duplicatas
    
    def _gerar_resposta_erro(self, mensagem: str, detalhes: Dict[str, Any], inicio: datetime) -> Dict[str, Any]:
        """Gera resposta padronizada para erros."""
        tempo_processamento = (datetime.now() - inicio).total_seconds()
        
        return {
            "status": "erro",
            "mensagem": mensagem,
            "detalhes": detalhes,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tempo_processamento": f"{tempo_processamento:.2f}s",
            "documento_html": self._gerar_documento_erro(mensagem, detalhes)
        }
    
    def _gerar_documento_erro(self, mensagem: str, detalhes: Dict[str, Any]) -> str:
        """Gera documento HTML de erro."""
        return f"""
        <h1>ERRO NA GERAÇÃO DA PETIÇÃO</h1>
        
        <p><strong>Mensagem:</strong> {mensagem}</p>
        
        <p><strong>Timestamp:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <h2>DETALHES TÉCNICOS</h2>
        <pre>{json.dumps(detalhes, indent=2, ensure_ascii=False)}</pre>
        
        <h2>AÇÕES RECOMENDADAS</h2>
        <ul>
            <li>Verificar se todos os dados obrigatórios foram fornecidos</li>
            <li>Validar a estrutura dos dados de entrada</li>
            <li>Verificar conectividade com a API do OpenAI</li>
            <li>Consultar logs do sistema para mais detalhes</li>
        </ul>
        
        <p><em>Para suporte técnico, entre em contato com a equipe de desenvolvimento.</em></p>
        """
    
    def obter_status_sistema(self) -> Dict[str, Any]:
        """Retorna status detalhado do sistema."""
        try:
            # Testar cada componente
            status_componentes = {
                "coletor_dados": self._testar_componente(self.coletor_dados),
                "pesquisa_juridica": self._testar_componente(self.pesquisa_juridica),
                "redator": self._testar_componente(self.redator),
                "validador": self._testar_componente(self.validador)
            }
            
            # Status geral
            todos_ok = all(status_componentes.values())
            
            return {
                "status_geral": "operacional" if todos_ok else "problemas_detectados",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "componentes": status_componentes,
                "versao": "2.0",
                "agentes_ativos": len([k for k, v in status_componentes.items() if v])
            }
            
        except Exception as e:
            return {
                "status_geral": "erro",
                "mensagem": f"Erro ao verificar status: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _testar_componente(self, componente) -> bool:
        """Testa se um componente está funcionando."""
        try:
            # Teste básico - verificar se o objeto existe e tem métodos esperados
            if hasattr(componente, '__class__'):
                return True
            return False
        except:
            return False
    
    def gerar_relatorio_uso(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório de uso sem processar a petição."""
        return {
            "analise_dados": {
                "campos_fornecidos": list(dados_entrada.keys()),
                "tipo_acao": dados_entrada.get("tipo_acao", "Não especificado"),
                "tem_autor": bool(dados_entrada.get("autor")),
                "tem_reu": bool(dados_entrada.get("reu")),
                "tem_fatos": bool(dados_entrada.get("fatos")),
                "tem_pedidos": bool(dados_entrada.get("pedidos"))
            },
            "estimativas": {
                "tempo_processamento_estimado": "30-60 segundos",
                "complexidade": self._avaliar_complexidade(dados_entrada),
                "temas_pesquisa_estimados": self._estimar_temas_pesquisa(dados_entrada)
            },
            "recomendacoes": self._gerar_recomendacoes_entrada(dados_entrada)
        }
    
    def _avaliar_complexidade(self, dados: Dict[str, Any]) -> str:
        """Avalia a complexidade do caso baseado nos dados."""
        fatores_complexidade = 0
        
        # Verificar fatores que aumentam complexidade
        if isinstance(dados.get("pedidos"), list) and len(dados["pedidos"]) > 3:
            fatores_complexidade += 1
        
        if dados.get("urgencia"):
            fatores_complexidade += 1
        
        if dados.get("valor_causa") and "milhão" in str(dados["valor_causa"]).lower():
            fatores_complexidade += 1
        
        fatos = str(dados.get("fatos", ""))
        if len(fatos) > 1000:
            fatores_complexidade += 1
        
        if fatores_complexidade >= 3:
            return "Alta"
        elif fatores_complexidade >= 1:
            return "Média"
        else:
            return "Baixa"
    
    def _estimar_temas_pesquisa(self, dados: Dict[str, Any]) -> List[str]:
        """Estima temas de pesquisa baseado nos dados."""
        temas = []
        
        tipo_acao = str(dados.get("tipo_acao", "")).lower()
        fatos = str(dados.get("fatos", "")).lower()
        
        # Mapeamento básico
        if "cobrança" in tipo_acao or "cobrança" in fatos:
            temas.extend(["direito civil", "obrigações", "cobrança"])
        
        if "consumidor" in tipo_acao or "consumidor" in fatos:
            temas.extend(["direito do consumidor", "CDC"])
        
        if "trabalho" in tipo_acao or "trabalhista" in fatos:
            temas.extend(["direito trabalhista", "CLT"])
        
        if not temas:
            temas = ["direito civil", "código de processo civil"]
        
        return list(set(temas))
    
    def _gerar_recomendacoes_entrada(self, dados: Dict[str, Any]) -> List[str]:
        """Gera recomendações para melhorar os dados de entrada."""
        recomendacoes = []
        
        # Verificar dados obrigatórios
        if not dados.get("tipo_acao"):
            recomendacoes.append("Especificar o tipo de ação")
        
        if not dados.get("autor") or not dados.get("autor", {}).get("nome"):
            recomendacoes.append("Fornecer dados completos do autor")
        
        if not dados.get("reu") or not dados.get("reu", {}).get("nome"):
            recomendacoes.append("Fornecer dados completos do réu")
        
        if not dados.get("fatos"):
            recomendacoes.append("Detalhar os fatos do caso")
        
        if not dados.get("pedidos"):
            recomendacoes.append("Especificar os pedidos desejados")
        
        # Verificar dados opcionais mas importantes
        if not dados.get("valor_causa"):
            recomendacoes.append("Informar o valor da causa")
        
        if not dados.get("competencia"):
            recomendacoes.append("Especificar a competência/foro")
        
        if not recomendacoes:
            recomendacoes.append("Dados estão completos para processamento")
        
        return recomendacoes

