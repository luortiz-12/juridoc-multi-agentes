# agente_validador.py - Versão 2.1 com Lógica de Aprovação Corrigida

import re
from typing import Dict, Any, List
from datetime import datetime

class AgenteValidador:
    """
    Agente Validador v2.1 que:
    - Analisa a qualidade do documento.
    - Retorna um status de "aprovado" ou "reprovado" de forma correta.
    - Gera recomendações claras para o Agente Redator em caso de reprovação.
    """
    
    def __init__(self):
        print("✅ Inicializando Agente Validador v2.1 (com Feedback)...")
        self.criterios_validacao = {
            'tamanho_minimo': 20000,
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
            
            # COMENTÁRIO: Lógica de aprovação corrigida.
            # O status agora é "reprovado" se qualquer problema for encontrado.
            status = "reprovado" if problemas else "aprovado"
            
            # A margem de 10% é aplicada aqui. Se o tamanho estiver dentro da margem,
            # o problema de tamanho não é adicionado, e o status pode ser "aprovado".
            tamanho_aceitavel = self.criterios_validacao['tamanho_minimo'] * 0.90
            if analise['tamanho'] >= tamanho_aceitavel:
                # Se o único problema era o tamanho e ele está dentro da margem, remove o problema.
                problemas = [p for p in problemas if p['tipo'] != 'tamanho_insuficiente']
                recomendacoes = [r for r in recomendacoes if "curto" not in r]
                if not problemas:
                    status = "aprovado"
            
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
        
        # COMENTÁRIO: A verificação de tamanho agora considera a margem de 10% antes de criar um problema.
        tamanho_aceitavel = self.criterios_validacao['tamanho_minimo'] * 0.90
        if analise['tamanho'] < tamanho_aceitavel:
            problema = {
                'tipo': 'tamanho_insuficiente',
                'descricao': f"Documento com {analise['tamanho']} caracteres (meta: {self.criterios_validacao['tamanho_minimo']})"
            }
            problemas.append(problema)
            recomendacoes.append("O documento está muito curto. Por favor, expanda todas as seções, adicionando mais detalhes, aprofundamento jurídico e exemplos práticos para enriquecer o conteúdo.")
            
        return problemas, recomendacoes

    def _calcular_score_qualidade(self, documento: str) -> float:
        """Calcula um score de qualidade mais rigoroso."""
        score = 0.0
        tamanho = len(documento)
        meta = self.criterios_validacao['tamanho_minimo']
        
        # O score agora só é alto se a meta for realmente atingida.
        if tamanho >= meta:
            score = 100.0
        elif tamanho >= meta * 0.9:
            score = 90.0 # Score alto, mas não perfeito, se estiver na margem.
        else:
            score = (tamanho / meta) * 80.0 # Penaliza mais se estiver abaixo da margem.
            
        return min(100.0, round(score, 2))
