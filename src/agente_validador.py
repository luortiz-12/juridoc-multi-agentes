# agente_validador.py - Versão 2.3 com Recomendação de Formatação Aprimorada

import re
from typing import Dict, Any, List
from datetime import datetime

class AgenteValidador:
    """
    Agente Validador v2.3 que:
    - Analisa a qualidade do documento.
    - Gera recomendações claras, incluindo instruções de formatação para evitar HTML aninhado.
    """
    
    def __init__(self):
        print("✅ Inicializando Agente Validador v2.3 (com Feedback Aprimorado)...")
        self.criterios_validacao = {
            'tamanho_minimo': 30000,
        }
        print("✅ Agente Validador inicializado")
    
    def validar_e_formatar(self, documento_html: str, dados_originais: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Valida o documento e retorna um status e recomendações.
        """
        try:
            print("🔍 Iniciando validação de qualidade...")
            if not isinstance(documento_html, str): documento_html = ""
            
            analise = self._analisar_documento(documento_html)
            
            print(f"   -> Tamanho do Documento: {analise['tamanho']} caracteres (Meta: {self.criterios_validacao['tamanho_minimo']})")
            
            problemas, recomendacoes = self._identificar_problemas_e_recomendar(analise)
            
            status = "reprovado" if problemas else "aprovado"
            
            print(f"📊 Status da Validação: {status.upper()}")
            if recomendacoes:
                print(f"📋 Recomendações: {', '.join(recomendacoes)}")

            return {
                "status": status,
                "documento_validado": documento_html,
                "recomendacoes": recomendacoes,
                "score_qualidade": self._calcular_score_qualidade(documento_html),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return {"status": "erro", "erro": str(e)}
    
    def _analisar_documento(self, documento: str) -> Dict[str, Any]:
        """Analisa as métricas do documento."""
        return {'tamanho': len(documento)}

    def _identificar_problemas_e_recomendar(self, analise: Dict[str, Any]) -> (List[Dict], List[str]):
        """Identifica problemas e gera recomendações textuais para a IA."""
        problemas = []
        recomendacoes = []
        
        tamanho_aceitavel = self.criterios_validacao['tamanho_minimo'] * 0.80
        if analise['tamanho'] < tamanho_aceitavel:
            problema = {
                'tipo': 'tamanho_insuficiente',
                'descricao': f"Documento com {analise['tamanho']} caracteres (meta de 80%: {int(tamanho_aceitavel)})"
            }
            problemas.append(problema)
            
            # COMENTÁRIO: A recomendação agora inclui uma instrução de formatação explícita para a IA.
            # Isto deve resolver o problema do HTML aninhado na segunda tentativa.
            recomendacoes.append("O documento está muito curto. Expanda todas as seções com mais detalhes. IMPORTANTE: Ao reescrever, gere APENAS o conteúdo HTML da seção solicitada, sem incluir `<!DOCTYPE>`, `<html>`, `<head>`, ou `<body>` tags.")
            
        return problemas, recomendacoes

    def _calcular_score_qualidade(self, documento: str) -> float:
        """Calcula um score de qualidade com base no tamanho."""
        score = 0.0
        tamanho = len(documento)
        meta = self.criterios_validacao['tamanho_minimo']
        
        if meta == 0: return 100.0
        
        score = (tamanho / meta) * 100.0
            
        return min(100.0, round(score, 2))
