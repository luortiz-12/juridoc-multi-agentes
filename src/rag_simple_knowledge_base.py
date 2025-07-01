# rag_simple_knowledge_base.py - VERSÃO CORRIGIDA COM MÉTODO FALTANTE
"""
Versão corrigida da Base de Conhecimento RAG para JuriDoc.
ADICIONADO: método get_relevant_context que estava faltando.
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
    VERSÃO CORRIGIDA - Inclui método get_relevant_context.
    """
    
    def __init__(self, persist_directory: str = "rag_db_cache"):
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
        
        # Cache para otimização
        self._context_cache = {}
        self._loaded = False
    
    def load_structural_patterns(self, patterns_file: str) -> bool:
        """
        Carrega e processa os padrões estruturais extraídos dos documentos.
        """
        try:
            print(f"📚 Carregando padrões estruturais de: {patterns_file}")
            
            with open(patterns_file, 'r', encoding='utf-8') as f:
                patterns_data = json.load(f)
            
            print("📚 Processando padrões estruturais...")
            
            # Processar cada tipo de documento
            for doc_type in ['peticao', 'contrato', 'parecer']:
                if doc_type in patterns_data:
                    doc_data = patterns_data[doc_type]
                    
                    # Contar documentos
                    count = len(doc_data.get('documentos', []))
                    print(f"  📄 {doc_type.upper()}: {count} documentos analisados")
                    
                    # Extrair padrões estruturais
                    self.knowledge_base['padroes_estruturais'][doc_type] = doc_data.get('padroes_estruturais', {})
                    
                    # Extrair fórmulas jurídicas
                    self.knowledge_base['formulas_juridicas'][doc_type] = doc_data.get('formulas_juridicas', [])
                    
                    # Extrair templates de seções
                    self.knowledge_base['templates_secoes'][doc_type] = doc_data.get('templates_secoes', {})
                    
                    # Extrair guias estruturais
                    self.knowledge_base['guias_estruturais'][doc_type] = doc_data.get('guias_estruturais', [])
            
            self._loaded = True
            print("✅ Padrões estruturais processados com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar padrões estruturais: {e}")
            return False
    
    def get_relevant_context(self, doc_type: str, user_data: dict) -> str:
        """
        MÉTODO ADICIONADO - Obtém contexto relevante da base RAG.
        Este método estava faltando e causava erros nos agentes.
        """
        try:
            # Normalizar tipo de documento
            doc_type = doc_type.lower().strip()
            if doc_type not in ['peticao', 'contrato', 'parecer']:
                doc_type = 'peticao'  # fallback
            
            # Verificar cache
            cache_key = f"{doc_type}_{hash(str(user_data))}"
            if cache_key in self._context_cache:
                return self._context_cache[cache_key]
            
            # Se não carregou ainda, tentar carregar
            if not self._loaded:
                kb_file = self.base_path / "juridoc_rag_knowledge_base.json"
                if kb_file.exists():
                    self.load_structural_patterns(str(kb_file))
            
            # Construir contexto relevante
            context_parts = []
            
            # 1. Padrões estruturais
            padroes = self.knowledge_base['padroes_estruturais'].get(doc_type, {})
            if padroes:
                context_parts.append(f"PADRÕES ESTRUTURAIS PARA {doc_type.upper()}:")
                for secao, detalhes in padroes.items():
                    if isinstance(detalhes, dict) and detalhes.get('frequencia', 0) > 0:
                        context_parts.append(f"- {secao}: {detalhes.get('descricao', 'N/A')}")
            
            # 2. Templates de seções
            templates = self.knowledge_base['templates_secoes'].get(doc_type, {})
            if templates:
                context_parts.append(f"\nTEMPLATES DE SEÇÕES PARA {doc_type.upper()}:")
                for secao, template in templates.items():
                    if template and len(str(template)) > 10:
                        context_parts.append(f"- {secao}: {str(template)[:200]}...")
            
            # 3. Fórmulas jurídicas
            formulas = self.knowledge_base['formulas_juridicas'].get(doc_type, [])
            if formulas:
                context_parts.append(f"\nFÓRMULAS JURÍDICAS PARA {doc_type.upper()}:")
                for i, formula in enumerate(formulas[:5]):  # Limitar a 5
                    if isinstance(formula, dict):
                        context_parts.append(f"- {formula.get('tipo', 'N/A')}: {formula.get('texto', 'N/A')}")
                    else:
                        context_parts.append(f"- Fórmula {i+1}: {str(formula)[:100]}...")
            
            # 4. Guias estruturais
            guias = self.knowledge_base['guias_estruturais'].get(doc_type, [])
            if guias:
                context_parts.append(f"\nGUIAS ESTRUTURAIS PARA {doc_type.upper()}:")
                for guia in guias[:3]:  # Limitar a 3
                    context_parts.append(f"- {str(guia)[:150]}...")
            
            # 5. Contexto específico baseado nos dados do usuário
            context_parts.append(f"\nCONTEXTO ESPECÍFICO:")
            context_parts.append(f"- Tipo de documento solicitado: {doc_type}")
            context_parts.append(f"- Dados fornecidos: {len(user_data)} campos preenchidos")
            
            # Identificar tipo específico baseado nos dados
            tipo_especifico = self._identificar_tipo_especifico(user_data, doc_type)
            if tipo_especifico:
                context_parts.append(f"- Subtipo identificado: {tipo_especifico}")
            
            # Juntar tudo
            full_context = "\n".join(context_parts)
            
            # Limitar tamanho (máximo 2000 caracteres)
            if len(full_context) > 2000:
                full_context = full_context[:1997] + "..."
            
            # Salvar no cache
            self._context_cache[cache_key] = full_context
            
            return full_context
            
        except Exception as e:
            print(f"⚠️ Erro ao obter contexto RAG: {e}")
            return f"Contexto RAG para {doc_type} - Sistema em modo fallback devido a erro: {str(e)}"
    
    def _identificar_tipo_especifico(self, user_data: dict, doc_type: str) -> str:
        """
        Identifica subtipo específico baseado nos dados do usuário.
        """
        try:
            data_str = json.dumps(user_data, ensure_ascii=False).lower()
            
            if doc_type == 'peticao':
                if 'trabalh' in data_str or 'clt' in data_str:
                    return "Petição Trabalhista"
                elif 'dano' in data_str and 'moral' in data_str:
                    return "Petição de Danos Morais"
                elif 'acident' in data_str:
                    return "Petição de Acidente"
                elif 'previdenc' in data_str:
                    return "Petição Previdenciária"
                else:
                    return "Petição Cível Geral"
            
            elif doc_type == 'contrato':
                if 'locação' in data_str or 'aluguel' in data_str:
                    return "Contrato de Locação"
                elif 'compra' in data_str or 'venda' in data_str:
                    return "Contrato de Compra e Venda"
                elif 'serviço' in data_str or 'prestação' in data_str:
                    return "Contrato de Prestação de Serviços"
                else:
                    return "Contrato Geral"
            
            elif doc_type == 'parecer':
                if 'constitucional' in data_str:
                    return "Parecer Constitucional"
                elif 'administrativo' in data_str:
                    return "Parecer Administrativo"
                else:
                    return "Parecer Jurídico Geral"
            
            return ""
            
        except:
            return ""
    
    def get_structural_guidance(self, doc_type: str, context: str = "") -> Dict[str, Any]:
        """
        Obtém orientação estrutural específica para um tipo de documento.
        """
        try:
            doc_type = doc_type.lower().strip()
            if doc_type not in ['peticao', 'contrato', 'parecer']:
                doc_type = 'peticao'
            
            guidance = {
                'templates': self.knowledge_base['templates_secoes'].get(doc_type, {}),
                'padroes': self.knowledge_base['padroes_estruturais'].get(doc_type, {}),
                'formulas': self.knowledge_base['formulas_juridicas'].get(doc_type, []),
                'guias': self.knowledge_base['guias_estruturais'].get(doc_type, [])
            }
            
            return guidance
            
        except Exception as e:
            print(f"⚠️ Erro ao obter orientação estrutural: {e}")
            return {'templates': {}, 'padroes': {}, 'formulas': [], 'guias': []}
    
    def get_writing_templates(self, doc_type: str, section_type: str = "") -> List[str]:
        """
        Obtém templates de redação para um tipo específico de documento/seção.
        """
        try:
            doc_type = doc_type.lower().strip()
            templates = self.knowledge_base['templates_secoes'].get(doc_type, {})
            
            if section_type:
                section_templates = templates.get(section_type, [])
                if isinstance(section_templates, list):
                    return section_templates
                else:
                    return [str(section_templates)]
            else:
                # Retornar todos os templates
                all_templates = []
                for section, template_data in templates.items():
                    if isinstance(template_data, list):
                        all_templates.extend(template_data)
                    else:
                        all_templates.append(str(template_data))
                return all_templates
                
        except Exception as e:
            print(f"⚠️ Erro ao obter templates de redação: {e}")
            return []
    
    def get_legal_formulas(self, doc_type: str, formula_type: str = "") -> List[Dict]:
        """
        Obtém fórmulas jurídicas específicas.
        """
        try:
            doc_type = doc_type.lower().strip()
            formulas = self.knowledge_base['formulas_juridicas'].get(doc_type, [])
            
            if formula_type:
                filtered_formulas = []
                for formula in formulas:
                    if isinstance(formula, dict) and formula_type.lower() in formula.get('tipo', '').lower():
                        filtered_formulas.append(formula)
                return filtered_formulas
            else:
                return formulas
                
        except Exception as e:
            print(f"⚠️ Erro ao obter fórmulas jurídicas: {e}")
            return []

