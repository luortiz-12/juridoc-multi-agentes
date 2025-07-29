# agente_validador.py - Versão 2.0 com Lógica de Feedback

import re
from typing import Dict, Any, List
from datetime import datetime

class AgenteValidador:
    """
    Agente Validador v2.0 que:
    - Analisa a qualidade do documento em vez de apenas o corrigir.
    - Retorna um status de "aprovado" ou "reprovado".
    - Gera uma lista de recomendações claras para o Agente Redator em caso de reprovação.
    """
    
    def __init__(self):
        print("✅ Inicializando Agente Validador v2.0 (com Feedback)...")
        self.criterios_validacao = {
            'tamanho_minimo': 20000, # Meta de caracteres mais ambiciosa
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
            problemas, recomendacoes = self._identificar_problemas_e_recomendar(analise)
            
            # COMENTÁRIO: Lógica de aprovação com margem de 10%.
            tamanho_aceitavel = self.criterios_validacao['tamanho_minimo'] * 0.90
            status = "aprovado"
            if analise['tamanho'] < tamanho_aceitavel:
                status = "reprovado"

            print(f"📊 Status da Validação: {status.upper()}")
            if recomendacoes:
                print(f"📋 Recomendações: {', '.join(recomendacoes)}")

            return {
                "status": status,
                "documento_validado": documento_html, # Retorna o documento como está para o orquestrador decidir
                "recomendacoes": recomendacoes,
                "problemas_identificados": problemas,
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
        
        if analise['tamanho'] < self.criterios_validacao['tamanho_minimo']:
            problema = {
                'tipo': 'tamanho_insuficiente',
                'descricao': f"Documento com {analise['tamanho']} caracteres (meta: {self.criterios_validacao['tamanho_minimo']})"
            }
            problemas.append(problema)
            recomendacoes.append("O documento está muito curto. Por favor, expanda todas as seções, adicionando mais detalhes, aprofundamento jurídico e exemplos práticos para enriquecer o conteúdo.")
            
        # Outras validações e recomendações podem ser adicionadas aqui no futuro.
        
        return problemas, recomendacoes

    def _calcular_score_qualidade(self, documento: str) -> float:
        """Calcula um score de qualidade simples."""
        score = 0.0
        tamanho = len(documento)
        meta = self.criterios_validacao['tamanho_minimo']
        
        if tamanho >= meta:
            score = 100.0
        else:
            score = (tamanho / meta) * 100.0
            
        return min(100.0, round(score, 2))
