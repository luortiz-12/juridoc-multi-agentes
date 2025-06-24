# rag_agent_integration.py
"""
Integração do sistema RAG com os agentes especializados do JuriDoc.
Combina conhecimento estrutural, busca online e templates para cada tipo de agente.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

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
        try:
            base_path = Path(__file__).parent
            kb_file = base_path / "juridoc_rag_knowledge_base.json"
            if kb_file.exists():
                self.knowledge_base.load_knowledge_base(str(kb_file))
                print(f"✅ Base de conhecimento carregada para {self.agent_type} {self.doc_type}")
            else:
                print(f"⚠️ Base de conhecimento não encontrada: {kb_file}")
        except Exception as e:
            print(f"❌ Erro ao carregar base de conhecimento: {e}")

    # ... (O restante dos seus métodos de RAGEnhancedAgent permanecem aqui) ...
    # ... (get_structural_guidance, search_online_legal_content, etc.) ...


class RAGEnhancedTechnicalAgent(RAGEnhancedAgent):
    """
    Agente técnico aprimorado com RAG para análise jurídica especializada.
    """
    def __init__(self, doc_type: str, llm_api_key: str):
        # --- CORREÇÃO AQUI ---
        # Garantimos que o 'agent_type' ('tecnico') seja passado para a classe mãe.
        super().__init__('tecnico', doc_type, llm_api_key)
    
    # ... (O restante dos seus métodos de RAGEnhancedTechnicalAgent permanecem aqui) ...


class RAGEnhancedWriterAgent(RAGEnhancedAgent):
    """
    Agente redator aprimorado com RAG para redação especializada.
    """
    def __init__(self, doc_type: str, llm_api_key: str):
        # --- CORREÇÃO AQUI ---
        # Garantimos que o 'agent_type' ('redator') seja passado para a classe mãe.
        super().__init__('redator', doc_type, llm_api_key)

    # ... (O restante dos seus métodos de RAGEnhancedWriterAgent permanecem aqui) ...

# (O bloco if __name__ == "__main__" permanece o mesmo, de preferência comentado para o deploy)