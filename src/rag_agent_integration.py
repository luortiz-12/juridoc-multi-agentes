# rag_agent_integration.py - VERSÃO CORRIGIDA

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# Suas importações dos outros módulos RAG
from rag_simple_knowledge_base import SimpleJuriDocRAG
from rag_real_online_search import RealJuridicalSearcher
from rag_online_search import SmartJuridicalSearcher

class RAGEnhancedAgent:
    """
    Classe base para agentes aprimorados com RAG.
    """
    def __init__(self, agent_type: str, doc_type: str, llm_api_key: str):
        self.agent_type = agent_type
        self.doc_type = doc_type
        self.llm_api_key = llm_api_key
        
        self.knowledge_base = SimpleJuriDocRAG()
        self.online_searcher = RealJuridicalSearcher()
        self.smart_searcher = SmartJuridicalSearcher(self.online_searcher)
        
        self._load_knowledge_base()
        self.search_cache = {}
    
    def _load_knowledge_base(self):
        """ Carrega a base de conhecimento RAG de forma relativa. """
        try:
            # --- CORREÇÃO 1: Caminho do Arquivo ---
            # Usa a biblioteca pathlib para encontrar o arquivo na pasta 'src'
            base_path = Path(__file__).parent
            kb_file_path = base_path / "juridoc_rag_knowledge_base.json"
            
            if kb_file_path.exists():
                # Chamando o método correto que existe na sua classe SimpleJuriDocRAG
                if self.knowledge_base.load_structural_patterns(str(kb_file_path)):
                    print(f"✅ Base de conhecimento RAG carregada para {self.agent_type}/{self.doc_type}")
                else:
                    print(f"❌ Falha no processamento dos padrões pela classe SimpleJuriDocRAG.")
            else:
                print(f"⚠️ Arquivo de base de conhecimento não encontrado em: {kb_file_path}")
        except Exception as e:
            print(f"❌ Erro crítico ao carregar base de conhecimento: {e}")

    # ==============================================================================
    # O restante dos seus métodos permanecem aqui, sem alterações.
    # Sua lógica de busca, processamento e fallback está muito bem estruturada.
    # ==============================================================================

    def get_structural_guidance(self, context: str = "") -> Dict[str, Any]:
        return self.knowledge_base.get_structural_guidance(self.doc_type, context)
    
    def search_online_legal_content(self, query: str, context: str = "") -> Dict[str, Any]:
        cache_key = f"{query}_{context}"
        if cache_key in self.search_cache:
            print(f"📋 Usando resultado em cache para: '{query}'")
            return self.search_cache[cache_key]
        try:
            search_results = self.smart_searcher.intelligent_search(query, context)
            processed_results = self._process_search_results(search_results)
            self.search_cache[cache_key] = processed_results
            return processed_results
        except Exception as e:
            print(f"Erro na busca online: {e}")
            return self._get_fallback_content(query, context)
    
    # Mantenha todos os seus outros métodos originais da classe RAGEnhancedAgent aqui
    # _get_document_templates, _get_contextual_formulas, _process_search_results, etc.


class RAGEnhancedTechnicalAgent(RAGEnhancedAgent):
    """
    Agente técnico aprimorado com RAG para análise jurídica especializada.
    """
    def __init__(self, doc_type: str, llm_api_key: str):
        # --- CORREÇÃO 2: Passando o 'agent_type' que faltava ---
        # Garantimos que a classe mãe receba todos os argumentos que ela espera.
        super().__init__('tecnico', doc_type, llm_api_key)
    
    def analyze_with_rag(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        # Sua lógica original aqui.
        print(f"🔍 Análise técnica RAG para {self.doc_type}")
        return {"analise": "completa"} # Retorno de exemplo

class RAGEnhancedWriterAgent(RAGEnhancedAgent):
    """
    Agente redator aprimorado com RAG para redação especializada.
    """
    def __init__(self, doc_type: str, llm_api_key: str):
        # --- CORREÇÃO 2: Passando o 'agent_type' que faltava ---
        # Garantimos que a classe mãe receba todos os argumentos que ela espera.
        super().__init__('redator', doc_type, llm_api_key)

    def write_with_rag(self, user_data: Dict[str, Any], technical_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        # Sua lógica original aqui.
        print(f"✍️ Redação RAG para {self.doc_type}")
        return {"contexto": "preparado"} # Retorno de exemplo

# O if __name__ == "__main__" deve ser mantido como você o escreveu (comentado ou removido para deploy).