# agente_validador.py - Agente Validador Corrigido

import os
import json
import re
from typing import Dict, Any, List
from datetime import datetime

class AgenteValidador:
    """
    Agente Validador que:
    - Valida documentos HTML extensos
    - Corrige problemas de formatação
    - Garante qualidade profissional
    - NUNCA adiciona conteúdo de texto indesejado.
    """
    
    def __init__(self):
        print("✅ Inicializando Agente Validador...")
        self.criterios_validacao = {
            'tamanho_minimo': 10000, # Reduzido para um valor mais realista
            'secoes_obrigatorias': [
                'qualificação', 'fatos', 'direito', 'pedidos', 'valor'
            ],
            'formatacao_html': True,
            'dados_reais': True
        }
        print("✅ Agente Validador inicializado")
    
    def validar_e_formatar(self, documento_html: str, dados_originais: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Valida e formata documento HTML garantindo qualidade profissional.
        """
        try:
            print("🔍 Iniciando validação e formatação...")
            
            if not isinstance(documento_html, str):
                documento_html = str(documento_html)
            
            if dados_originais is None or not isinstance(dados_originais, dict):
                dados_originais = {}
            
            # ETAPA 1: ANÁLISE INICIAL
            analise_inicial = self._analisar_documento(documento_html)
            print(f"📊 Tamanho atual: {analise_inicial['tamanho']} caracteres")
            
            # ETAPA 2: IDENTIFICAR PROBLEMAS
            problemas = self._identificar_problemas(documento_html, analise_inicial)
            print(f"🔧 Corrigindo petição ({len(problemas)} problemas)")
            
            # ETAPA 3: CORRIGIR PROBLEMAS
            documento_corrigido = self._corrigir_problemas(documento_html, problemas)
            
            # COMENTÁRIO: A lógica de expansão que adicionava o texto indesejado foi REMOVIDA.
            # O agente não irá mais adicionar as seções "DA FUNDAMENTAÇÃO COMPLEMENTAR" etc.

            # ETAPA 4: FORMATAÇÃO FINAL
            documento_final = self._aplicar_formatacao_final(documento_corrigido)
            
            # ETAPA 5: CALCULAR SCORE
            score_qualidade = self._calcular_score_qualidade(documento_final)
            
            print(f"✅ Validação e formatação concluídas")
            print(f"📊 Score de qualidade: {score_qualidade}%")
            
            return {
                "status": "sucesso",
                "documento_validado": documento_final,
                "estatisticas": {
                    "tamanho_original": len(documento_html),
                    "tamanho_final": len(documento_final),
                    "problemas_corrigidos": len(problemas),
                    "score_qualidade": score_qualidade,
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return {
                "status": "erro_corrigido",
                "erro": str(e),
                "documento_validado": self._aplicar_validacao_emergencia(documento_html),
            }
    
    def _analisar_documento(self, documento: str) -> Dict[str, Any]:
        """Analisa documento para validação."""
        return {
            'tamanho': len(documento),
            'tem_html': '<html>' in documento.lower(),
            'tem_css': '<style>' in documento.lower(),
            'secoes_encontradas': len(re.findall(r'<h[123]>', documento, re.IGNORECASE)),
            'tem_dados_reais': '[ENDEREÇO A SER PREENCHIDO]' not in documento
        }

    def _identificar_problemas(self, documento: str, analise: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identifica problemas no documento."""
        problemas = []
        if analise['tamanho'] < self.criterios_validacao['tamanho_minimo']:
            problemas.append({'tipo': 'tamanho_insuficiente', 'descricao': f"Documento com {analise['tamanho']} caracteres", 'severidade': 'baixa'})
        if not analise['tem_html']:
            problemas.append({'tipo': 'html_incompleto', 'descricao': "Documento sem estrutura HTML completa", 'severidade': 'alta'})
        if not analise['tem_css']:
            problemas.append({'tipo': 'css_ausente', 'descricao': "Documento sem formatação CSS", 'severidade': 'media'})
        return problemas

    def _corrigir_problemas(self, documento: str, problemas: List[Dict[str, str]]) -> str:
        """Corrige problemas identificados."""
        documento_corrigido = documento
        for problema in problemas:
            tipo = problema['tipo']
            if tipo == 'html_incompleto':
                documento_corrigido = self._corrigir_html_incompleto(documento_corrigido)
            elif tipo == 'css_ausente':
                documento_corrigido = self._adicionar_css_profissional(documento_corrigido)
        return documento_corrigido

    def _corrigir_html_incompleto(self, documento: str) -> str:
        """Corrige HTML incompleto."""
        if not documento.strip().startswith('<!DOCTYPE'):
            css_basico = "<style>body{font-family:'Times New Roman',serif;margin:40px;line-height:1.8;}</style>"
            return f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>Documento Jurídico</title>{css_basico}</head><body>{documento}</body></html>'
        return documento

    def _adicionar_css_profissional(self, documento: str) -> str:
        """Adiciona CSS profissional."""
        css_profissional = """
        <style>
        body{font-family:'Times New Roman',serif;line-height:1.8;text-align:justify;margin:3cm}
        h1{text-align:center;font-size:16pt}
        h2{text-align:left;font-size:14pt;margin-top:30px;font-weight:bold}
        h3{text-align:left;font-size:12pt;margin-top:20px;font-weight:bold}
        p{text-indent:2em;margin-bottom:15px}
        .qualificacao p{text-indent:0}
        </style>
        """
        if '<head>' in documento:
            return documento.replace('</head>', f'{css_profissional}</head>')
        return css_profissional + documento

    def _aplicar_formatacao_final(self, documento: str) -> str:
        """Aplica formatação final profissional."""
        documento = re.sub(r'\n\s*\n\s*\n+', '\n\n', documento)
        if '</body>' not in documento:
            documento += '\n</body>\n</html>'
        return documento

    def _calcular_score_qualidade(self, documento: str) -> float:
        """Calcula score de qualidade do documento."""
        score = 0.0
        tamanho = len(documento)
        if tamanho >= self.criterios_validacao['tamanho_minimo']: score += 30.0
        else: score += (tamanho / self.criterios_validacao['tamanho_minimo']) * 30.0
        if '<html>' in documento.lower() and '</html>' in documento.lower(): score += 20.0
        if '<style>' in documento.lower(): score += 15.0
        if len(re.findall(r'<h[123]>', documento, re.IGNORECASE)) >= 5: score += 20.0
        if '[ENDEREÇO A SER PREENCHIDO]' not in documento: score += 15.0
        return min(100.0, score)

    def _aplicar_validacao_emergencia(self, documento: str) -> str:
        """Aplica validação de emergência em caso de erro."""
        if not isinstance(documento, str):
            documento = str(documento)
        if not documento.strip().startswith('<!DOCTYPE'):
            return f'<!DOCTYPE html><html><head><title>Documento</title></head><body>{documento}</body></html>'
        return documento
