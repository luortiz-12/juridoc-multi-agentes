# agente_validador.py - Versão 2.2 com Lógica de Aprovação de 80%

import re
from typing import Dict, Any, List
from datetime import datetime

class AgenteValidador:
    """
    Agente Validador v2.2 que:
    - Analisa a qualidade do documento.
    - Aprova documentos que atingem 80% da meta de tamanho.
    - Gera recomendações claras para o Agente Redator em caso de reprovação.
    - Fornece logs detalhados sobre o tamanho do documento.
    """
    
    def __init__(self):
        print("✅ Inicializando Agente Validador v2.2 (com Feedback)...")
        self.criterios_validacao = {
            'tamanho_minimo': 30000, # Meta de 30k
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
            
            # COMENTÁRIO: Adicionado log para informar o tamanho do documento.
            print(f"   -> Tamanho do Documento: {analise['tamanho']} caracteres (Meta: {self.criterios_validacao['tamanho_minimo']})")
            
            problemas, recomendacoes = self._identificar_problemas_e_recomendar(analise)
            
            # COMENTÁRIO: A lógica de aprovação foi ajustada para 80%.
            # Se não houver problemas (ou seja, se o tamanho for >= 80% da meta), o status é 'aprovado'.
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
        
        # COMENTÁRIO: A margem de aprovação foi alterada para 80% da meta.
        tamanho_aceitavel = self.criterios_validacao['tamanho_minimo'] * 0.80
        if analise['tamanho'] < tamanho_aceitavel:
            problema = {
                'tipo': 'tamanho_insuficiente',
                'descricao': f"Documento com {analise['tamanho']} caracteres (meta de 80%: {int(tamanho_aceitavel)})"
            }
            problemas.append(problema)
            recomendacoes.append("O documento está muito curto. Por favor, expanda todas as seções, adicionando mais detalhes, aprofundamento jurídico e exemplos práticos para enriquecer o conteúdo.")
            
        # Outras validações podem ser adicionadas aqui.
        
        return problemas, recomendacoes

    def _calcular_score_qualidade(self, documento: str) -> float:
        """Calcula um score de qualidade com base no tamanho."""
        score = 0.0
        tamanho = len(documento)
        meta = self.criterios_validacao['tamanho_minimo']
        
        if meta == 0: return 100.0 # Evita divisão por zero
        
        # O score é proporcional ao tamanho, até atingir 100% na meta.
        score = (tamanho / meta) * 100.0
            
        return min(100.0, round(score, 2))
