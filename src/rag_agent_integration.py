# rag_agent_integration.py
"""
Integração do sistema RAG com os agentes especializados do JuriDoc.
Combina conhecimento estrutural, busca online e templates para cada tipo de agente.
"""

import os
import json
from typing import Dict, List, Any, Optional
from rag_simple_knowledge_base import SimpleJuriDocRAG
from rag_real_online_search import RealJuridicalSearcher
from rag_online_search import SmartJuridicalSearcher

class RAGEnhancedAgent:
    """
    Classe base para agentes aprimorados com RAG.
    Fornece conhecimento estrutural e busca online para agentes especializados.
    """
    
    def __init__(self, agent_type: str, doc_type: str, llm_api_key: str):
        self.agent_type = agent_type  # 'tecnico' ou 'redator'
        self.doc_type = doc_type      # 'peticao', 'contrato', 'parecer'
        self.llm_api_key = llm_api_key
        
        # Inicializar componentes RAG
        self.knowledge_base = SimpleJuriDocRAG()
        self.online_searcher = RealJuridicalSearcher()
        self.smart_searcher = SmartJuridicalSearcher(self.online_searcher)
        
        # Carregar base de conhecimento
        self._load_knowledge_base()
        
        # Cache para evitar buscas repetidas
        self.search_cache = {}
    
    def _load_knowledge_base(self):
        """
        Carrega a base de conhecimento RAG.
        """
        try:
            kb_file = "/home/ubuntu/juridoc_rag_knowledge_base.json"
            if os.path.exists(kb_file):
                self.knowledge_base.load_knowledge_base(kb_file)
                print(f"✅ Base de conhecimento carregada para {self.agent_type} {self.doc_type}")
            else:
                print(f"⚠️ Base de conhecimento não encontrada: {kb_file}")
        except Exception as e:
            print(f"❌ Erro ao carregar base de conhecimento: {e}")
    
    def get_structural_guidance(self, context: str = "") -> Dict[str, Any]:
        """
        Obtém orientação estrutural da base RAG para o tipo de documento.
        """
        try:
            guidance = self.knowledge_base.get_structural_guidance(self.doc_type, context)
            
            # Enriquecer com templates específicos
            if guidance:
                guidance['templates'] = self._get_document_templates()
                guidance['formulas_context'] = self._get_contextual_formulas(context)
            
            return guidance
        except Exception as e:
            print(f"Erro ao obter orientação estrutural: {e}")
            return {}
    
    def search_online_legal_content(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Busca conteúdo jurídico online relevante para a consulta.
        """
        # Verificar cache primeiro
        cache_key = f"{query}_{context}"
        if cache_key in self.search_cache:
            print(f"📋 Usando resultado em cache para: '{query}'")
            return self.search_cache[cache_key]
        
        try:
            # Busca inteligente com fallback
            search_results = self.smart_searcher.intelligent_search(query, context)
            
            # Processar e filtrar resultados
            processed_results = self._process_search_results(search_results)
            
            # Armazenar em cache
            self.search_cache[cache_key] = processed_results
            
            return processed_results
            
        except Exception as e:
            print(f"Erro na busca online: {e}")
            return self._get_fallback_content(query, context)
    
    def _get_document_templates(self) -> Dict[str, Any]:
        """
        Obtém templates específicos para o tipo de documento.
        """
        templates = {}
        
        if self.doc_type == 'peticao':
            templates = {
                'cabecalho': self.knowledge_base.get_section_template('peticao', 'cabecalho_autoridade'),
                'preambulo': self.knowledge_base.get_section_template('peticao', 'preambulo'),
                'fatos': self.knowledge_base.get_section_template('peticao', 'fatos'),
                'fundamentacao': self.knowledge_base.get_section_template('peticao', 'fundamentacao_juridica'),
                'pedidos': self.knowledge_base.get_section_template('peticao', 'pedidos')
            }
        elif self.doc_type == 'contrato':
            templates = {
                'qualificacao': self.knowledge_base.get_section_template('contrato', 'qualificacao_partes'),
                'objeto': self.knowledge_base.get_section_template('contrato', 'objeto_contrato'),
                'clausulas': self.knowledge_base.get_section_template('contrato', 'clausula_contratual')
            }
        elif self.doc_type == 'parecer':
            templates = {
                'consulta': self.knowledge_base.get_section_template('parecer', 'questao_consultada'),
                'analise': self.knowledge_base.get_section_template('parecer', 'analise_juridica'),
                'conclusao': self.knowledge_base.get_section_template('parecer', 'conclusao')
            }
        
        return templates
    
    def _get_contextual_formulas(self, context: str) -> List[str]:
        """
        Obtém fórmulas jurídicas relevantes para o contexto.
        """
        try:
            return self.knowledge_base.get_legal_formulas_by_context(self.doc_type, context)
        except Exception as e:
            print(f"Erro ao obter fórmulas contextuais: {e}")
            return []
    
    def _process_search_results(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa e filtra resultados de busca para relevância.
        """
        processed = {
            'query': search_results.get('original_query', ''),
            'used_fallback': search_results.get('used_fallback', False),
            'recommendation': search_results.get('recommendation', ''),
            'legislation': [],
            'jurisprudence': [],
            'summary': {
                'total_results': 0,
                'legislation_count': 0,
                'jurisprudence_count': 0
            }
        }
        
        final_results = search_results.get('final_results', {})
        
        # Processar legislação
        if 'legislation' in final_results:
            for source, results in final_results['legislation'].items():
                if isinstance(results, list):
                    processed['legislation'].extend(results)
                elif isinstance(results, dict) and 'results' in results:
                    processed['legislation'].extend(results['results'])
        
        # Processar jurisprudência
        if 'jurisprudence' in final_results:
            for source, results in final_results['jurisprudence'].items():
                if isinstance(results, list):
                    processed['jurisprudence'].extend(results)
                elif isinstance(results, dict) and 'results' in results:
                    processed['jurisprudence'].extend(results['results'])
        
        # Atualizar contadores
        processed['summary']['legislation_count'] = len(processed['legislation'])
        processed['summary']['jurisprudence_count'] = len(processed['jurisprudence'])
        processed['summary']['total_results'] = processed['summary']['legislation_count'] + processed['summary']['jurisprudence_count']
        
        return processed
    
    def _get_fallback_content(self, query: str, context: str) -> Dict[str, Any]:
        """
        Conteúdo de fallback quando busca online falha.
        """
        return {
            'query': query,
            'used_fallback': True,
            'recommendation': 'Busca online indisponível. Usando conhecimento interno da LLM.',
            'legislation': [
                {
                    'title': f'Conhecimento Interno sobre {query}',
                    'description': f'Baseado no conhecimento da LLM sobre {query} no contexto de {self.doc_type}',
                    'source': 'LLM Knowledge',
                    'type': 'conhecimento_interno'
                }
            ],
            'jurisprudence': [],
            'summary': {
                'total_results': 1,
                'legislation_count': 1,
                'jurisprudence_count': 0
            }
        }
    
    def generate_enhanced_context(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera contexto enriquecido combinando dados do usuário, conhecimento estrutural e busca online.
        """
        enhanced_context = {
            'user_data': user_data,
            'structural_guidance': {},
            'online_content': {},
            'templates': {},
            'recommendations': []
        }
        
        # Extrair contexto dos dados do usuário
        context_query = self._extract_context_from_user_data(user_data)
        
        # Obter orientação estrutural
        enhanced_context['structural_guidance'] = self.get_structural_guidance(context_query)
        
        # Buscar conteúdo online relevante
        if context_query:
            enhanced_context['online_content'] = self.search_online_legal_content(context_query)
        
        # Adicionar templates
        enhanced_context['templates'] = self._get_document_templates()
        
        # Gerar recomendações
        enhanced_context['recommendations'] = self._generate_recommendations(enhanced_context)
        
        return enhanced_context
    
    def _extract_context_from_user_data(self, user_data: Dict[str, Any]) -> str:
        """
        Extrai contexto relevante dos dados do usuário para busca.
        """
        context_parts = []
        
        # Campos comuns que podem indicar contexto jurídico
        relevant_fields = [
            'tipo_documento', 'assunto', 'materia', 'objeto',
            'natureza_acao', 'fundamento_legal', 'causa_pedir'
        ]
        
        for field in relevant_fields:
            if field in user_data and user_data[field]:
                value = str(user_data[field]).strip()
                if value and value.lower() != 'null':
                    context_parts.append(value)
        
        return ' '.join(context_parts[:3])  # Limitar a 3 termos principais
    
    def _generate_recommendations(self, enhanced_context: Dict[str, Any]) -> List[str]:
        """
        Gera recomendações baseadas no contexto enriquecido.
        """
        recommendations = []
        
        # Recomendações estruturais
        structural = enhanced_context.get('structural_guidance', {})
        if structural.get('guias_estruturais'):
            recommendations.append("Seguir estrutura padrão identificada nos modelos analisados")
        
        # Recomendações de busca online
        online = enhanced_context.get('online_content', {})
        if online.get('used_fallback'):
            recommendations.append("Verificar legislação atualizada em fontes oficiais")
        elif online.get('summary', {}).get('total_results', 0) > 0:
            recommendations.append("Considerar legislação e jurisprudência encontradas")
        
        # Recomendações por tipo de documento
        if self.doc_type == 'peticao':
            recommendations.append("Incluir fundamentação jurídica sólida e pedidos claros")
        elif self.doc_type == 'contrato':
            recommendations.append("Definir claramente objeto, partes e obrigações")
        elif self.doc_type == 'parecer':
            recommendations.append("Apresentar análise fundamentada e conclusão objetiva")
        
        return recommendations

class RAGEnhancedTechnicalAgent(RAGEnhancedAgent):
    """
    Agente técnico aprimorado com RAG para análise jurídica especializada.
    """
    
    def __init__(self, doc_type: str, llm_api_key: str):
        super().__init__('tecnico', doc_type, llm_api_key)
    
    def analyze_with_rag(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise jurídica aprimorada com RAG.
        """
        print(f"🔍 Análise técnica RAG para {self.doc_type}")
        
        # Gerar contexto enriquecido
        enhanced_context = self.generate_enhanced_context(user_data)
        
        # Extrair elementos para análise
        context_query = self._extract_context_from_user_data(user_data)
        
        # Buscar fundamentação legal específica
        legal_foundation = self.search_online_legal_content(
            f"{context_query} fundamentação legal",
            f"análise jurídica {self.doc_type}"
        )
        
        # Buscar jurisprudência relevante
        jurisprudence = self.search_online_legal_content(
            f"{context_query} jurisprudência",
            f"precedentes {self.doc_type}"
        )
        
        # Compilar análise técnica
        technical_analysis = {
            'enhanced_context': enhanced_context,
            'legal_foundation': legal_foundation,
            'jurisprudence': jurisprudence,
            'structural_recommendations': self._get_structural_recommendations(),
            'legal_formulas': enhanced_context['structural_guidance'].get('formulas_context', []),
            'analysis_summary': self._generate_analysis_summary(enhanced_context, legal_foundation, jurisprudence)
        }
        
        return technical_analysis
    
    def _get_structural_recommendations(self) -> List[str]:
        """
        Recomendações estruturais específicas para agente técnico.
        """
        recommendations = []
        
        if self.doc_type == 'peticao':
            recommendations.extend([
                "Identificar tipo específico de petição (cível, trabalhista, penal)",
                "Verificar competência do juízo",
                "Fundamentar juridicamente cada pedido",
                "Citar legislação aplicável e jurisprudência consolidada"
            ])
        elif self.doc_type == 'contrato':
            recommendations.extend([
                "Analisar natureza jurídica do contrato",
                "Verificar requisitos de validade",
                "Identificar obrigações principais e acessórias",
                "Considerar legislação específica aplicável"
            ])
        elif self.doc_type == 'parecer':
            recommendations.extend([
                "Delimitar precisamente a questão jurídica",
                "Pesquisar doutrina e jurisprudência atualizadas",
                "Analisar diferentes correntes interpretativas",
                "Apresentar conclusão fundamentada"
            ])
        
        return recommendations
    
    def _generate_analysis_summary(self, context: Dict, legal: Dict, jurisprudence: Dict) -> str:
        """
        Gera resumo da análise técnica.
        """
        summary_parts = []
        
        # Contexto estrutural
        structural = context.get('structural_guidance', {})
        if structural:
            summary_parts.append(f"Estrutura baseada em {structural.get('padroes_estruturais', {}).get('total_analisados', 0)} modelos analisados")
        
        # Fundamentação legal
        legal_count = legal.get('summary', {}).get('total_results', 0)
        if legal_count > 0:
            summary_parts.append(f"{legal_count} fontes legais identificadas")
        
        # Jurisprudência
        jur_count = jurisprudence.get('summary', {}).get('total_results', 0)
        if jur_count > 0:
            summary_parts.append(f"{jur_count} precedentes jurisprudenciais encontrados")
        
        # Fallback
        if legal.get('used_fallback') or jurisprudence.get('used_fallback'):
            summary_parts.append("Recomenda-se verificação em fontes oficiais atualizadas")
        
        return ". ".join(summary_parts) if summary_parts else "Análise baseada em conhecimento interno"

class RAGEnhancedWriterAgent(RAGEnhancedAgent):
    """
    Agente redator aprimorado com RAG para redação especializada.
    """
    
    def __init__(self, doc_type: str, llm_api_key: str):
        super().__init__('redator', doc_type, llm_api_key)
    
    def write_with_rag(self, user_data: Dict[str, Any], technical_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Redação aprimorada com RAG.
        """
        print(f"✍️ Redação RAG para {self.doc_type}")
        
        # Gerar contexto enriquecido (se não fornecido via análise técnica)
        if technical_analysis:
            enhanced_context = technical_analysis.get('enhanced_context', {})
        else:
            enhanced_context = self.generate_enhanced_context(user_data)
        
        # Obter templates de redação
        writing_templates = self._get_writing_templates()
        
        # Obter padrões linguísticos
        linguistic_patterns = self._get_linguistic_patterns()
        
        # Compilar contexto de redação
        writing_context = {
            'enhanced_context': enhanced_context,
            'technical_analysis': technical_analysis,
            'writing_templates': writing_templates,
            'linguistic_patterns': linguistic_patterns,
            'style_guide': self._get_style_guide(),
            'writing_recommendations': self._get_writing_recommendations()
        }
        
        return writing_context
    
    def _get_writing_templates(self) -> Dict[str, Any]:
        """
        Templates específicos para redação.
        """
        return self._get_document_templates()
    
    def _get_linguistic_patterns(self) -> Dict[str, List[str]]:
        """
        Padrões linguísticos específicos para o tipo de documento.
        """
        patterns = {
            'peticao': {
                'formulas_abertura': [
                    "vem respeitosamente à presença de Vossa Excelência",
                    "tem a honra de dirigir-se a este Egrégio Tribunal",
                    "comparece perante este Juízo"
                ],
                'formulas_narrativa': [
                    "Narra o requerente que",
                    "Ocorre que",
                    "Acontece que"
                ],
                'formulas_fundamentacao': [
                    "O direito do requerente encontra amparo em",
                    "A pretensão está fundamentada em",
                    "Assiste razão ao requerente, pois"
                ],
                'formulas_pedidos': [
                    "Diante do exposto, requer",
                    "Pelos fundamentos expostos, pleiteia",
                    "Ante o exposto, pugna"
                ]
            },
            'contrato': {
                'formulas_abertura': [
                    "Pelo presente instrumento particular",
                    "Por este contrato",
                    "Através do presente instrumento"
                ],
                'formulas_clausulas': [
                    "Fica estabelecido que",
                    "As partes convencionam que",
                    "É condição deste contrato"
                ]
            },
            'parecer': {
                'formulas_abertura': [
                    "Trata-se de consulta sobre",
                    "Foi-nos apresentada questão relativa a",
                    "Submeteu-se à nossa análise"
                ],
                'formulas_analise': [
                    "Examinando a questão sob o prisma legal",
                    "Do ponto de vista jurídico",
                    "Analisando a matéria"
                ],
                'formulas_conclusao': [
                    "Diante do exposto, conclui-se que",
                    "Face ao examinado, entendemos que",
                    "Pelo exposto, é nosso parecer que"
                ]
            }
        }
        
        return patterns.get(self.doc_type, {})
    
    def _get_style_guide(self) -> Dict[str, str]:
        """
        Guia de estilo para o tipo de documento.
        """
        style_guides = {
            'peticao': {
                'tom': 'formal e respeitoso',
                'pessoa': 'terceira pessoa',
                'tempo_verbal': 'presente e pretérito perfeito',
                'tratamento': 'Vossa Excelência, Meritíssimo',
                'estrutura': 'cronológica e lógica'
            },
            'contrato': {
                'tom': 'formal e preciso',
                'pessoa': 'terceira pessoa',
                'tempo_verbal': 'presente',
                'linguagem': 'clara e objetiva',
                'estrutura': 'clausular e sistemática'
            },
            'parecer': {
                'tom': 'técnico e analítico',
                'pessoa': 'primeira pessoa do plural',
                'tempo_verbal': 'presente',
                'linguagem': 'técnica e fundamentada',
                'estrutura': 'problema-análise-conclusão'
            }
        }
        
        return style_guides.get(self.doc_type, {})
    
    def _get_writing_recommendations(self) -> List[str]:
        """
        Recomendações específicas para redação.
        """
        recommendations = []
        
        if self.doc_type == 'peticao':
            recommendations.extend([
                "Usar linguagem formal e respeitosa",
                "Manter cronologia clara dos fatos",
                "Fundamentar juridicamente cada alegação",
                "Ser específico nos pedidos",
                "Evitar prolixidade desnecessária"
            ])
        elif self.doc_type == 'contrato':
            recommendations.extend([
                "Definir claramente termos e conceitos",
                "Especificar direitos e obrigações",
                "Prever situações de inadimplemento",
                "Usar linguagem precisa e inequívoca",
                "Organizar em cláusulas numeradas"
            ])
        elif self.doc_type == 'parecer':
            recommendations.extend([
                "Delimitar precisamente a questão",
                "Apresentar análise fundamentada",
                "Citar fontes doutrinárias e jurisprudenciais",
                "Manter imparcialidade técnica",
                "Concluir de forma objetiva"
            ])
        
        return recommendations

if __name__ == "__main__":
    # Teste da integração RAG com agentes
    print("🚀 Testando Integração RAG com Agentes Especializados...")
    
    # Dados de teste
    test_user_data = {
        'tipo_documento': 'peticao',
        'assunto': 'danos morais',
        'natureza_acao': 'indenização',
        'causa_pedir': 'negativação indevida'
    }
    
    # Teste agente técnico
    print("\n🔍 Teste: Agente Técnico RAG")
    technical_agent = RAGEnhancedTechnicalAgent('peticao', 'test-key')
    technical_analysis = technical_agent.analyze_with_rag(test_user_data)
    
    print(f"Análise técnica concluída:")
    print(f"  - Contexto estrutural: {len(technical_analysis['enhanced_context'])} elementos")
    print(f"  - Fundamentação legal: {technical_analysis['legal_foundation']['summary']['total_results']} resultados")
    print(f"  - Jurisprudência: {technical_analysis['jurisprudence']['summary']['total_results']} resultados")
    
    # Teste agente redator
    print("\n✍️ Teste: Agente Redator RAG")
    writer_agent = RAGEnhancedWriterAgent('peticao', 'test-key')
    writing_context = writer_agent.write_with_rag(test_user_data, technical_analysis)
    
    print(f"Contexto de redação preparado:")
    print(f"  - Templates: {len(writing_context['writing_templates'])} seções")
    print(f"  - Padrões linguísticos: {len(writing_context['linguistic_patterns'])} categorias")
    print(f"  - Recomendações: {len(writing_context['writing_recommendations'])} itens")
    
    # Salvar resultados de teste
    with open('/home/ubuntu/rag_integration_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'technical_analysis': technical_analysis,
            'writing_context': writing_context
        }, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Teste de integração RAG concluído!")
    print("📁 Resultados salvos em: /home/ubuntu/rag_integration_test_results.json")

