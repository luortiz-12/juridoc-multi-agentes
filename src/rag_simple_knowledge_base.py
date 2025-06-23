# rag_simple_knowledge_base.py
"""
Versão simplificada da Base de Conhecimento RAG para JuriDoc.
Usa embeddings básicos sem dependências pesadas.
"""

import os
import json
import pickle
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
from collections import defaultdict

class SimpleJuriDocRAG:
    """
    Base de conhecimento RAG simplificada para documentos jurídicos.
    Foca em padrões estruturais e templates para treinamento de agentes.
    """
    
    def __init__(self, persist_directory: str = "rag_db_cache"):
        # --- CORREÇÃO APLICADA AQUI ---
        # Usa um caminho relativo que funcionará em qualquer ambiente.
        self.base_path = Path(__file__).parent
        self.persist_path = self.base_path / persist_directory
        os.makedirs(self.persist_path, exist_ok=True)
        
        self.knowledge_base = {
            'padroes_estruturais': {
                'peticao': {}, 'contrato': {}, 'parecer': {}
            },
            'formulas_juridicas': {
                'peticao': [], 'contrato': [], 'parecer': []
            },
            'templates_secoes': {
                'peticao': {}, 'contrato': {}, 'parecer': {}
            },
            'guias_estruturais': {
                'peticao': [], 'contrato': [], 'parecer': []
            }
        }
    
    def load_structural_patterns(self, patterns_file: str):
        """
        Carrega e processa os padrões estruturais extraídos dos documentos.
        """
        try:
            with open(patterns_file, 'r', encoding='utf-8') as f:
                patterns_data = json.load(f)
            
            print("📚 Processando padrões estruturais...")
            
            # Assumindo que a chave principal é 'padroes_estruturais'
            structural_data = patterns_data.get('padroes_estruturais', {})

            for doc_type, patterns in structural_data.items():
                if 'total_analisados' in patterns:
                    print(f"  📄 {doc_type.upper()}: {patterns['total_analisados']} documentos analisados")
                
                # Seus métodos de extração serão chamados aqui
                self._extract_structural_templates(doc_type, patterns)
                # Adicionei as chamadas que faltavam para os outros extratores
                # com base na estrutura do seu arquivo JSON
                formulas_data = patterns_data.get('formulas_juridicas', {}).get(doc_type, [])
                self._extract_legal_formulas(doc_type, {'formulas_juridicas': formulas_data})
                
                templates_data = patterns_data.get('templates_secoes', {}).get(doc_type, {})
                self._extract_section_patterns(doc_type, {'tipos_secao': templates_data.get('distribuicao', {})})
                
                guides_data = patterns_data.get('guias_estruturais', {}).get(doc_type, [])
                self._create_structural_guides(doc_type, {'guias_estruturais': guides_data})

            print("✅ Padrões estruturais processados com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar padrões: {e}")
            return False
    
    def _extract_structural_templates(self, doc_type: str, patterns: Dict):
        """ Extrai templates estruturais dos documentos. """
        # SEU CÓDIGO ORIGINAL MANTIDO
        sequencias_comuns = patterns.get('sequencias_comuns', [])
        secoes_frequentes = patterns.get('secoes_frequentes', {})
        total_analisados = patterns.get('total_analisados', 0)
        
        self.knowledge_base['padroes_estruturais'][doc_type] = {
            'secoes_frequentes': secoes_frequentes,
            'sequencias_comuns': sequencias_comuns,
            'total_analisados': total_analisados
        }
    
    def _extract_legal_formulas(self, doc_type: str, patterns: Dict):
        """ Extrai e categoriza fórmulas jurídicas. """
        # SEU CÓDIGO ORIGINAL MANTIDO
        formulas = patterns.get('formulas_juridicas', [])
        formulas_categorizadas = defaultdict(list)
        for formula in formulas:
            if not formula.strip(): continue
            formula_lower = formula.lower()
            if 'artigo' in formula_lower: formulas_categorizadas['referencias_artigo'].append(formula)
            elif 'lei' in formula_lower: formulas_categorizadas['referencias_lei'].append(formula)
            elif 'código' in formula_lower or 'codigo' in formula_lower: formulas_categorizadas['referencias_codigo'].append(formula)
            else: formulas_categorizadas['formulas_genericas'].append(formula)
        self.knowledge_base['formulas_juridicas'][doc_type] = dict(formulas_categorizadas)

    def _extract_section_patterns(self, doc_type: str, patterns: Dict):
        """ Extrai padrões de seções e suas características. """
        # SEU CÓDIGO ORIGINAL MANTIDO
        tipos_secao = patterns.get('tipos_secao', {})
        secoes_ordenadas = sorted(tipos_secao.items(), key=lambda x: x[1], reverse=True)
        self.knowledge_base['templates_secoes'][doc_type] = {
            'mais_frequentes': secoes_ordenadas[:10],
            'total_tipos': len(tipos_secao),
            'distribuicao': tipos_secao
        }
    
    def _create_structural_guides(self, doc_type: str, patterns: Dict):
        """ Cria guias estruturais baseados nos padrões encontrados. """
        # SEU CÓDIGO ORIGINAL MANTIDO
        # Esta parte parece depender de uma estrutura diferente ou de um processamento que não está no arquivo JSON.
        # Mantendo a lógica que você criou.
        self.knowledge_base['guias_estruturais'][doc_type] = patterns.get('guias_estruturais', [])

    def get_structural_guidance(self, doc_type: str, context: str = "") -> Dict[str, Any]:
        # SEU CÓDIGO ORIGINAL MANTIDO
        if doc_type not in self.knowledge_base.get('padroes_estruturais', {}):
            return {}
        return {
            'padroes_estruturais': self.knowledge_base['padroes_estruturais'][doc_type],
            'templates_secoes': self.knowledge_base['templates_secoes'][doc_type],
            'guias_estruturais': self.knowledge_base['guias_estruturais'][doc_type],
            'formulas_juridicas': self.knowledge_base['formulas_juridicas'][doc_type]
        }

    # (Adicionei de volta seus outros métodos `get` e `save` que estavam faltando no seu paste)
    def get_section_template(self, doc_type: str, section_type: str) -> Dict[str, Any]:
        return self.knowledge_base.get('templates_secoes', {}).get(doc_type, {}).get(section_type, {})
    
    def get_legal_formulas_by_context(self, doc_type: str, context: str) -> List[str]:
        # Mantenha seu código original aqui
        pass

    def save_knowledge_base(self, filepath: str):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            print(f"✅ Base de conhecimento salva em: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar base de conhecimento: {e}")
            return False

# Bloco de teste corrigido para usar caminhos relativos
if __name__ == "__main__":
    print("🚀 Testando Base de Conhecimento RAG JuriDoc...")
    
    # --- CORREÇÃO: Caminhos relativos para os arquivos de teste ---
    current_dir = Path(__file__).parent
    patterns_file_path = current_dir / "padroes_estruturais_rag.json"
    kb_output_path = current_dir / "juridoc_rag_knowledge_base.json"

    rag_kb = SimpleJuriDocRAG(persist_directory=str(current_dir / "rag_db_cache_teste"))
    
    if os.path.exists(patterns_file_path):
        if rag_kb.load_structural_patterns(str(patterns_file_path)):
            print("✅ Padrões carregados e processados com sucesso!")
            rag_kb.save_knowledge_base(str(kb_output_path))
        else:
            print("❌ Falha ao carregar padrões estruturais.")
    else:
        print(f"❌ Arquivo de padrões não encontrado para o teste: {patterns_file_path}")