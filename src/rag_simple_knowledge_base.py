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
    
    def __init__(self, persist_directory: str = "/home/ubuntu/rag_simple_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.knowledge_base = {
            'padroes_estruturais': {
                'peticao': {},
                'contrato': {},
                'parecer': {}
            },
            'formulas_juridicas': {
                'peticao': [],
                'contrato': [],
                'parecer': []
            },
            'templates_secoes': {
                'peticao': {},
                'contrato': {},
                'parecer': {}
            },
            'guias_estruturais': {
                'peticao': [],
                'contrato': [],
                'parecer': []
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
            
            for doc_type, patterns in patterns_data.items():
                print(f"  📄 {doc_type.upper()}: {patterns['total_documentos']} documentos")
                
                # Processar estruturas comuns
                self._extract_structural_templates(doc_type, patterns)
                
                # Processar fórmulas jurídicas
                self._extract_legal_formulas(doc_type, patterns)
                
                # Processar tipos de seção
                self._extract_section_patterns(doc_type, patterns)
                
                # Criar guias estruturais
                self._create_structural_guides(doc_type, patterns)
            
            print("✅ Padrões estruturais processados com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar padrões: {e}")
            return False
    
    def _extract_structural_templates(self, doc_type: str, patterns: Dict):
        """
        Extrai templates estruturais dos documentos.
        """
        estruturas = patterns.get('estruturas_comuns', [])
        
        # Analisar padrões de estrutura
        secoes_frequentes = defaultdict(int)
        sequencias_comuns = []
        
        for estrutura in estruturas:
            secoes = estrutura.get('secoes', [])
            
            # Contar frequência de tipos de seção
            for secao in secoes:
                secoes_frequentes[secao['tipo']] += 1
            
            # Extrair sequências de seções
            if len(secoes) > 1:
                sequencia = [secao['tipo'] for secao in secoes]
                sequencias_comuns.append(sequencia)
        
        # Armazenar templates
        self.knowledge_base['padroes_estruturais'][doc_type] = {
            'secoes_frequentes': dict(secoes_frequentes),
            'sequencias_comuns': sequencias_comuns[:10],  # Top 10
            'total_analisados': len(estruturas)
        }
    
    def _extract_legal_formulas(self, doc_type: str, patterns: Dict):
        """
        Extrai e categoriza fórmulas jurídicas.
        """
        formulas = patterns.get('formulas_juridicas', [])
        
        formulas_categorizadas = {
            'referencias_artigo': [],
            'referencias_lei': [],
            'referencias_codigo': [],
            'formulas_genericas': []
        }
        
        for formula in formulas:
            if not formula.strip():
                continue
                
            formula_lower = formula.lower()
            
            if 'artigo' in formula_lower:
                formulas_categorizadas['referencias_artigo'].append(formula)
            elif 'lei' in formula_lower:
                formulas_categorizadas['referencias_lei'].append(formula)
            elif 'código' in formula_lower or 'codigo' in formula_lower:
                formulas_categorizadas['referencias_codigo'].append(formula)
            else:
                formulas_categorizadas['formulas_genericas'].append(formula)
        
        self.knowledge_base['formulas_juridicas'][doc_type] = formulas_categorizadas
    
    def _extract_section_patterns(self, doc_type: str, patterns: Dict):
        """
        Extrai padrões de seções e suas características.
        """
        tipos_secao = patterns.get('tipos_secao', {})
        
        # Ordenar por frequência
        secoes_ordenadas = sorted(tipos_secao.items(), key=lambda x: x[1], reverse=True)
        
        self.knowledge_base['templates_secoes'][doc_type] = {
            'mais_frequentes': secoes_ordenadas[:10],
            'total_tipos': len(tipos_secao),
            'distribuicao': tipos_secao
        }
    
    def _create_structural_guides(self, doc_type: str, patterns: Dict):
        """
        Cria guias estruturais baseados nos padrões encontrados.
        """
        guias = []
        
        if doc_type == 'peticao':
            guias = [
                {
                    'titulo': 'Estrutura Básica de Petição',
                    'descricao': 'Sequência padrão para petições iniciais',
                    'secoes_recomendadas': [
                        'cabecalho_autoridade',
                        'preambulo', 
                        'fatos',
                        'fundamentacao_juridica',
                        'pedidos'
                    ],
                    'formulas_sugeridas': self.knowledge_base['formulas_juridicas'][doc_type]['referencias_artigo'][:3]
                },
                {
                    'titulo': 'Petição de Danos Morais',
                    'descricao': 'Estrutura específica para ações de danos morais',
                    'secoes_recomendadas': [
                        'cabecalho_autoridade',
                        'preambulo',
                        'fatos',
                        'fundamentacao_juridica',
                        'pedidos'
                    ],
                    'elementos_especiais': ['valor_causa', 'provas_dano', 'nexo_causal']
                }
            ]
        
        elif doc_type == 'contrato':
            guias = [
                {
                    'titulo': 'Estrutura Básica de Contrato',
                    'descricao': 'Sequência padrão para contratos em geral',
                    'secoes_recomendadas': [
                        'qualificacao_partes',
                        'objeto_contrato',
                        'clausula_contratual'
                    ],
                    'elementos_obrigatorios': ['partes', 'objeto', 'valor', 'prazo']
                }
            ]
        
        elif doc_type == 'parecer':
            guias = [
                {
                    'titulo': 'Estrutura Básica de Parecer',
                    'descricao': 'Sequência padrão para pareceres jurídicos',
                    'secoes_recomendadas': [
                        'questao_consultada',
                        'analise_juridica',
                        'conclusao'
                    ],
                    'elementos_essenciais': ['fundamentacao', 'analise_legal', 'opiniao_conclusiva']
                }
            ]
        
        self.knowledge_base['guias_estruturais'][doc_type] = guias
    
    def get_structural_guidance(self, doc_type: str, context: str = "") -> Dict[str, Any]:
        """
        Obtém orientação estrutural para um tipo de documento.
        """
        if doc_type not in self.knowledge_base['padroes_estruturais']:
            return {}
        
        guidance = {
            'padroes_estruturais': self.knowledge_base['padroes_estruturais'][doc_type],
            'templates_secoes': self.knowledge_base['templates_secoes'][doc_type],
            'guias_estruturais': self.knowledge_base['guias_estruturais'][doc_type],
            'formulas_juridicas': self.knowledge_base['formulas_juridicas'][doc_type]
        }
        
        return guidance
    
    def get_section_template(self, doc_type: str, section_type: str) -> Dict[str, Any]:
        """
        Retorna template para um tipo específico de seção.
        """
        templates = {
            'peticao': {
                'cabecalho_autoridade': {
                    'formato': 'AO EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA [VARA] DE [COMARCA]',
                    'elementos': ['autoridade', 'vara', 'comarca'],
                    'estilo': 'formal_respeitoso'
                },
                'preambulo': {
                    'formato': '[NOME], [QUALIFICAÇÃO], vem respeitosamente à presença de Vossa Excelência...',
                    'elementos': ['qualificacao_requerente', 'verbo_respeitoso', 'tratamento'],
                    'estilo': 'formal_deferente'
                },
                'fatos': {
                    'formato': 'DOS FATOS\n\nNarra o requerente que...',
                    'elementos': ['titulo_secao', 'narrativa_cronologica', 'fatos_relevantes'],
                    'estilo': 'narrativo_objetivo'
                },
                'fundamentacao_juridica': {
                    'formato': 'DO DIREITO\n\nO direito do requerente encontra amparo em...',
                    'elementos': ['titulo_secao', 'base_legal', 'jurisprudencia'],
                    'estilo': 'tecnico_fundamentado'
                },
                'pedidos': {
                    'formato': 'DOS PEDIDOS\n\nDiante do exposto, requer...',
                    'elementos': ['titulo_secao', 'pedido_principal', 'pedidos_subsidiarios'],
                    'estilo': 'objetivo_claro'
                }
            },
            'contrato': {
                'qualificacao_partes': {
                    'formato': 'CONTRATANTE: [NOME], [QUALIFICAÇÃO]\nCONTRATADO: [NOME], [QUALIFICAÇÃO]',
                    'elementos': ['dados_contratante', 'dados_contratado'],
                    'estilo': 'formal_preciso'
                },
                'objeto_contrato': {
                    'formato': 'CLÁUSULA 1ª - DO OBJETO\nO presente contrato tem por objeto...',
                    'elementos': ['definicao_objeto', 'especificacoes'],
                    'estilo': 'claro_detalhado'
                }
            },
            'parecer': {
                'questao_consultada': {
                    'formato': 'CONSULTA\n\nFoi-nos apresentada a seguinte questão...',
                    'elementos': ['apresentacao_questao', 'contexto'],
                    'estilo': 'objetivo_contextual'
                },
                'analise_juridica': {
                    'formato': 'ANÁLISE JURÍDICA\n\nExaminando a questão sob o prisma legal...',
                    'elementos': ['analise_legal', 'fundamentacao', 'precedentes'],
                    'estilo': 'analitico_fundamentado'
                },
                'conclusao': {
                    'formato': 'CONCLUSÃO\n\nDiante do exposto, conclui-se que...',
                    'elementos': ['sintese_analise', 'opiniao_conclusiva'],
                    'estilo': 'conclusivo_assertivo'
                }
            }
        }
        
        return templates.get(doc_type, {}).get(section_type, {})
    
    def get_legal_formulas_by_context(self, doc_type: str, context: str) -> List[str]:
        """
        Retorna fórmulas jurídicas relevantes para um contexto.
        """
        formulas = self.knowledge_base['formulas_juridicas'].get(doc_type, {})
        
        context_lower = context.lower()
        relevant_formulas = []
        
        # Buscar por palavras-chave no contexto
        if 'artigo' in context_lower or 'art' in context_lower:
            relevant_formulas.extend(formulas.get('referencias_artigo', [])[:3])
        
        if 'lei' in context_lower:
            relevant_formulas.extend(formulas.get('referencias_lei', [])[:3])
        
        if 'código' in context_lower or 'codigo' in context_lower:
            relevant_formulas.extend(formulas.get('referencias_codigo', [])[:3])
        
        # Se não encontrou nada específico, retornar fórmulas genéricas
        if not relevant_formulas:
            relevant_formulas = formulas.get('formulas_genericas', [])[:3]
        
        return relevant_formulas
    
    def save_knowledge_base(self, filepath: str):
        """
        Salva a base de conhecimento em arquivo JSON.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            print(f"✅ Base de conhecimento salva em: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar base de conhecimento: {e}")
            return False
    
    def load_knowledge_base(self, filepath: str):
        """
        Carrega a base de conhecimento de arquivo JSON.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"✅ Base de conhecimento carregada de: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar base de conhecimento: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da base de conhecimento.
        """
        stats = {}
        
        for doc_type in ['peticao', 'contrato', 'parecer']:
            stats[doc_type] = {
                'padroes_estruturais': len(self.knowledge_base['padroes_estruturais'][doc_type]),
                'formulas_juridicas': sum(len(v) for v in self.knowledge_base['formulas_juridicas'][doc_type].values()),
                'guias_estruturais': len(self.knowledge_base['guias_estruturais'][doc_type]),
                'tipos_secao': len(self.knowledge_base['templates_secoes'][doc_type].get('distribuicao', {}))
            }
        
        return stats

if __name__ == "__main__":
    # Inicializar base de conhecimento RAG simplificada
    print("🚀 Inicializando Base de Conhecimento RAG JuriDoc (Versão Simplificada)...")
    
    rag_kb = SimpleJuriDocRAG()
    
    # Carregar padrões estruturais
    patterns_file = "/home/ubuntu/padroes_estruturais_rag.json"
    if rag_kb.load_structural_patterns(patterns_file):
        print("✅ Padrões carregados e processados com sucesso!")
        
        # Salvar base de conhecimento
        rag_kb.save_knowledge_base("/home/ubuntu/juridoc_rag_knowledge_base.json")
        
        # Mostrar estatísticas
        stats = rag_kb.get_statistics()
        print("\n📊 Estatísticas da Base de Conhecimento:")
        for doc_type, type_stats in stats.items():
            print(f"  📄 {doc_type.upper()}:")
            for metric, value in type_stats.items():
                print(f"    {metric}: {value}")
        
        # Teste de consulta estrutural
        print("\n🧪 Teste de orientação estrutural para petição:")
        guidance = rag_kb.get_structural_guidance('peticao', 'danos morais')
        
        if guidance:
            print("  📋 Seções mais frequentes:")
            for secao, freq in guidance['templates_secoes']['mais_frequentes'][:5]:
                print(f"    {secao}: {freq} ocorrências")
            
            print("  📝 Guias estruturais disponíveis:")
            for guia in guidance['guias_estruturais']:
                print(f"    {guia['titulo']}: {guia['descricao']}")
        
        # Teste de template de seção
        print("\n🧪 Teste de template de seção:")
        template = rag_kb.get_section_template('peticao', 'cabecalho_autoridade')
        if template:
            print(f"  Formato: {template['formato']}")
            print(f"  Elementos: {template['elementos']}")
        
        print("\n✅ Base de Conhecimento RAG criada com sucesso!")
    else:
        print("❌ Falha ao carregar padrões estruturais.")

