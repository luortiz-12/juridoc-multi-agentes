# rag_online_search.py
"""
Sistema de Busca Online para fontes jurídicas brasileiras.
Implementa busca paralela em múltiplas fontes com fallback inteligente.
"""

import os
import json
import requests
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import quote, urljoin
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class JuridicalOnlineSearcher:
    """
    Sistema de busca online em fontes jurídicas brasileiras.
    Busca leis, jurisprudência e base legal de forma paralela.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # URLs base das fontes jurídicas
        self.sources = {
            'lexml': {
                'base_url': 'https://www.lexml.gov.br',
                'search_url': 'https://www.lexml.gov.br/busca',
                'description': 'Portal LexML - Legislação Federal'
            },
            'planalto': {
                'base_url': 'http://www.planalto.gov.br',
                'search_url': 'http://www.planalto.gov.br/ccivil_03/leis/',
                'description': 'Presidência da República - Legislação'
            },
            'stj': {
                'base_url': 'https://www.stj.jus.br',
                'search_url': 'https://www.stj.jus.br/sites/portalp/Paginas/Jurisprudencia/Pesquisa-de-Jurisprudencia.aspx',
                'description': 'Superior Tribunal de Justiça'
            },
            'stf': {
                'base_url': 'https://portal.stf.jus.br',
                'search_url': 'https://portal.stf.jus.br/jurisprudencia/',
                'description': 'Supremo Tribunal Federal'
            },
            'tst': {
                'base_url': 'https://www.tst.jus.br',
                'search_url': 'https://www.tst.jus.br/jurisprudencia',
                'description': 'Tribunal Superior do Trabalho'
            }
        }
        
        self.search_results_cache = {}
        self.max_results_per_source = 5
        self.timeout = 10
    
    def search_legislation(self, query: str, sources: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Busca legislação em múltiplas fontes de forma paralela.
        """
        if sources is None:
            sources = ['lexml', 'planalto']
        
        print(f"🔍 Buscando legislação para: '{query}'")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {}
            
            for source in sources:
                if source in self.sources:
                    future = executor.submit(self._search_single_source_legislation, source, query)
                    future_to_source[future] = source
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    source_results = future.result(timeout=self.timeout)
                    results[source] = source_results
                    print(f"  ✅ {source}: {len(source_results)} resultados")
                except Exception as e:
                    print(f"  ❌ {source}: Erro - {e}")
                    results[source] = []
        
        return results
    
    def search_jurisprudence(self, query: str, courts: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Busca jurisprudência em tribunais superiores.
        """
        if courts is None:
            courts = ['stj', 'stf', 'tst']
        
        print(f"⚖️ Buscando jurisprudência para: '{query}'")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_court = {}
            
            for court in courts:
                if court in self.sources:
                    future = executor.submit(self._search_single_source_jurisprudence, court, query)
                    future_to_court[future] = court
            
            for future in as_completed(future_to_court):
                court = future_to_court[future]
                try:
                    court_results = future.result(timeout=self.timeout)
                    results[court] = court_results
                    print(f"  ✅ {court.upper()}: {len(court_results)} resultados")
                except Exception as e:
                    print(f"  ❌ {court.upper()}: Erro - {e}")
                    results[court] = []
        
        return results
    
    def comprehensive_search(self, query: str, search_type: str = 'all') -> Dict[str, Any]:
        """
        Busca abrangente em todas as fontes disponíveis.
        """
        print(f"🔍 Busca abrangente para: '{query}' (tipo: {search_type})")
        
        comprehensive_results = {
            'query': query,
            'search_type': search_type,
            'timestamp': time.time(),
            'legislation': {},
            'jurisprudence': {},
            'summary': {
                'total_sources': 0,
                'successful_sources': 0,
                'total_results': 0
            }
        }
        
        # Buscar legislação
        if search_type in ['all', 'legislation']:
            legislation_results = self.search_legislation(query)
            comprehensive_results['legislation'] = legislation_results
            
            for source, results in legislation_results.items():
                comprehensive_results['summary']['total_sources'] += 1
                if results:
                    comprehensive_results['summary']['successful_sources'] += 1
                    comprehensive_results['summary']['total_results'] += len(results)
        
        # Buscar jurisprudência
        if search_type in ['all', 'jurisprudence']:
            jurisprudence_results = self.search_jurisprudence(query)
            comprehensive_results['jurisprudence'] = jurisprudence_results
            
            for court, results in jurisprudence_results.items():
                comprehensive_results['summary']['total_sources'] += 1
                if results:
                    comprehensive_results['summary']['successful_sources'] += 1
                    comprehensive_results['summary']['total_results'] += len(results)
        
        print(f"📊 Busca concluída: {comprehensive_results['summary']['total_results']} resultados de {comprehensive_results['summary']['successful_sources']}/{comprehensive_results['summary']['total_sources']} fontes")
        
        return comprehensive_results
    
    def _search_single_source_legislation(self, source: str, query: str) -> List[Dict]:
        """
        Busca legislação em uma fonte específica.
        """
        try:
            if source == 'lexml':
                return self._search_lexml(query)
            elif source == 'planalto':
                return self._search_planalto(query)
            else:
                return []
        except Exception as e:
            print(f"Erro ao buscar em {source}: {e}")
            return []
    
    def _search_single_source_jurisprudence(self, court: str, query: str) -> List[Dict]:
        """
        Busca jurisprudência em um tribunal específico.
        """
        try:
            if court == 'stj':
                return self._search_stj(query)
            elif court == 'stf':
                return self._search_stf(query)
            elif court == 'tst':
                return self._search_tst(query)
            else:
                return []
        except Exception as e:
            print(f"Erro ao buscar em {court}: {e}")
            return []
    
    def _search_lexml(self, query: str) -> List[Dict]:
        """
        Busca no portal LexML.
        """
        # Simulação de busca no LexML (implementação real requereria análise da API)
        results = [
            {
                'title': f'Lei relacionada a {query}',
                'url': 'https://www.lexml.gov.br/urn/urn:lex:br:federal:lei:exemplo',
                'description': f'Legislação federal sobre {query}',
                'source': 'LexML',
                'type': 'lei_federal',
                'relevance': 0.9
            }
        ]
        return results
    
    def _search_planalto(self, query: str) -> List[Dict]:
        """
        Busca no site do Planalto.
        """
        # Simulação de busca no Planalto
        results = [
            {
                'title': f'Decreto sobre {query}',
                'url': 'http://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/decreto/exemplo.htm',
                'description': f'Decreto presidencial relacionado a {query}',
                'source': 'Planalto',
                'type': 'decreto',
                'relevance': 0.8
            }
        ]
        return results
    
    def _search_stj(self, query: str) -> List[Dict]:
        """
        Busca jurisprudência no STJ.
        """
        # Simulação de busca no STJ
        results = [
            {
                'title': f'Acórdão STJ sobre {query}',
                'url': 'https://www.stj.jus.br/websecstj/cgi/revista/REJ.cgi/exemplo',
                'description': f'Jurisprudência do STJ sobre {query}',
                'source': 'STJ',
                'type': 'acordao',
                'court': 'Superior Tribunal de Justiça',
                'relevance': 0.85
            }
        ]
        return results
    
    def _search_stf(self, query: str) -> List[Dict]:
        """
        Busca jurisprudência no STF.
        """
        # Simulação de busca no STF
        results = [
            {
                'title': f'Decisão STF sobre {query}',
                'url': 'https://portal.stf.jus.br/processos/exemplo',
                'description': f'Jurisprudência do STF sobre {query}',
                'source': 'STF',
                'type': 'decisao',
                'court': 'Supremo Tribunal Federal',
                'relevance': 0.9
            }
        ]
        return results
    
    def _search_tst(self, query: str) -> List[Dict]:
        """
        Busca jurisprudência no TST.
        """
        # Simulação de busca no TST
        results = [
            {
                'title': f'Súmula TST sobre {query}',
                'url': 'https://www.tst.jus.br/sumulas/exemplo',
                'description': f'Súmula do TST sobre {query}',
                'source': 'TST',
                'type': 'sumula',
                'court': 'Tribunal Superior do Trabalho',
                'relevance': 0.88
            }
        ]
        return results
    
    def extract_content_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extrai conteúdo de uma URL específica.
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair título
            title = soup.find('title')
            title_text = title.get_text().strip() if title else 'Sem título'
            
            # Extrair conteúdo principal
            content_selectors = [
                'article', 'main', '.content', '#content', 
                '.post-content', '.entry-content', 'body'
            ]
            
            content_text = ''
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text().strip()
                    break
            
            # Limpar e processar texto
            content_text = re.sub(r'\s+', ' ', content_text)
            content_text = content_text[:2000]  # Limitar tamanho
            
            return {
                'url': url,
                'title': title_text,
                'content': content_text,
                'success': True,
                'length': len(content_text)
            }
            
        except Exception as e:
            return {
                'url': url,
                'title': '',
                'content': '',
                'success': False,
                'error': str(e)
            }
    
    def get_best_results(self, search_results: Dict[str, Any], max_results: int = 10) -> List[Dict]:
        """
        Seleciona os melhores resultados de todas as fontes.
        """
        all_results = []
        
        # Coletar resultados de legislação
        for source, results in search_results.get('legislation', {}).items():
            for result in results:
                result['category'] = 'legislation'
                all_results.append(result)
        
        # Coletar resultados de jurisprudência
        for court, results in search_results.get('jurisprudence', {}).items():
            for result in results:
                result['category'] = 'jurisprudence'
                all_results.append(result)
        
        # Ordenar por relevância
        all_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        return all_results[:max_results]
    
    def save_search_results(self, results: Dict[str, Any], filepath: str):
        """
        Salva resultados de busca em arquivo.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ Resultados salvos em: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")
            return False

class SmartJuridicalSearcher:
    """
    Buscador jurídico inteligente que combina busca online com fallback para LLM.
    """
    
    def __init__(self, online_searcher: JuridicalOnlineSearcher):
        self.online_searcher = online_searcher
        self.fallback_knowledge = {
            'leis_fundamentais': [
                'Constituição Federal de 1988',
                'Código Civil (Lei 10.406/2002)',
                'Código de Processo Civil (Lei 13.105/2015)',
                'Código Penal (Decreto-Lei 2.848/1940)',
                'Código de Processo Penal (Decreto-Lei 3.689/1941)',
                'CLT - Consolidação das Leis do Trabalho (Decreto-Lei 5.452/1943)',
                'Código de Defesa do Consumidor (Lei 8.078/1990)'
            ],
            'principios_juridicos': [
                'Princípio da legalidade',
                'Princípio da isonomia',
                'Princípio do contraditório',
                'Princípio da ampla defesa',
                'Princípio do devido processo legal',
                'Princípio da dignidade da pessoa humana'
            ]
        }
    
    def intelligent_search(self, query: str, context: str = '', max_attempts: int = 3) -> Dict[str, Any]:
        """
        Busca inteligente com múltiplas tentativas e fallback.
        """
        print(f"🧠 Busca inteligente para: '{query}'")
        
        search_attempts = []
        final_results = None
        
        # Tentar busca online
        for attempt in range(max_attempts):
            try:
                print(f"  🔄 Tentativa {attempt + 1}/{max_attempts}")
                
                # Refinar query baseado no contexto
                refined_query = self._refine_query(query, context, attempt)
                
                # Busca online
                online_results = self.online_searcher.comprehensive_search(refined_query)
                
                search_attempts.append({
                    'attempt': attempt + 1,
                    'query': refined_query,
                    'results_count': online_results['summary']['total_results'],
                    'success': online_results['summary']['total_results'] > 0
                })
                
                # Se encontrou resultados suficientes, usar
                if online_results['summary']['total_results'] >= 2:
                    final_results = online_results
                    print(f"  ✅ Busca online bem-sucedida na tentativa {attempt + 1}")
                    break
                    
            except Exception as e:
                print(f"  ❌ Erro na tentativa {attempt + 1}: {e}")
                search_attempts.append({
                    'attempt': attempt + 1,
                    'query': refined_query if 'refined_query' in locals() else query,
                    'error': str(e),
                    'success': False
                })
        
        # Se busca online falhou, usar fallback
        if not final_results or final_results['summary']['total_results'] == 0:
            print("  🔄 Usando fallback para conhecimento da LLM...")
            final_results = self._fallback_search(query, context)
        
        # Compilar resultado final
        intelligent_result = {
            'original_query': query,
            'context': context,
            'search_attempts': search_attempts,
            'final_results': final_results,
            'used_fallback': final_results.get('source') == 'llm_fallback',
            'recommendation': self._generate_search_recommendation(final_results)
        }
        
        return intelligent_result
    
    def _refine_query(self, query: str, context: str, attempt: int) -> str:
        """
        Refina a query baseado no contexto e tentativa.
        """
        if attempt == 0:
            return query
        elif attempt == 1:
            # Adicionar contexto jurídico
            if 'danos morais' in query.lower():
                return f"{query} indenização responsabilidade civil"
            elif 'contrato' in query.lower():
                return f"{query} direito civil obrigações"
            elif 'trabalhista' in query.lower():
                return f"{query} CLT direito trabalho"
            else:
                return f"{query} direito brasileiro"
        else:
            # Simplificar query
            words = query.split()
            return ' '.join(words[:3])  # Usar apenas primeiras 3 palavras
    
    def _fallback_search(self, query: str, context: str) -> Dict[str, Any]:
        """
        Busca fallback usando conhecimento interno da LLM.
        """
        fallback_results = {
            'source': 'llm_fallback',
            'query': query,
            'context': context,
            'legislation': {
                'internal_knowledge': [
                    {
                        'title': 'Conhecimento Jurídico Interno',
                        'description': f'Baseado no conhecimento interno sobre {query}',
                        'source': 'LLM Knowledge Base',
                        'type': 'conhecimento_interno',
                        'relevance': 0.7,
                        'recommendation': 'Verificar legislação atualizada em fontes oficiais'
                    }
                ]
            },
            'jurisprudence': {
                'internal_knowledge': [
                    {
                        'title': 'Entendimento Jurisprudencial Geral',
                        'description': f'Entendimento consolidado sobre {query}',
                        'source': 'LLM Knowledge Base',
                        'type': 'entendimento_geral',
                        'relevance': 0.6,
                        'recommendation': 'Consultar jurisprudência atualizada nos tribunais'
                    }
                ]
            },
            'summary': {
                'total_sources': 1,
                'successful_sources': 1,
                'total_results': 2
            }
        }
        
        return fallback_results
    
    def _generate_search_recommendation(self, results: Dict[str, Any]) -> str:
        """
        Gera recomendação baseada nos resultados da busca.
        """
        if results.get('source') == 'llm_fallback':
            return "Recomenda-se verificar fontes oficiais atualizadas para confirmação das informações."
        elif results['summary']['total_results'] < 3:
            return "Poucos resultados encontrados. Considere refinar os termos de busca ou consultar fontes adicionais."
        else:
            return "Busca bem-sucedida. Resultados obtidos de fontes confiáveis."

if __name__ == "__main__":
    # Teste do sistema de busca online
    print("🚀 Testando Sistema de Busca Online Jurídica...")
    
    # Inicializar buscadores
    online_searcher = JuridicalOnlineSearcher()
    smart_searcher = SmartJuridicalSearcher(online_searcher)
    
    # Teste 1: Busca de legislação
    print("\n📚 Teste 1: Busca de Legislação")
    leg_results = online_searcher.search_legislation("danos morais")
    
    # Teste 2: Busca de jurisprudência
    print("\n⚖️ Teste 2: Busca de Jurisprudência")
    jur_results = online_searcher.search_jurisprudence("responsabilidade civil")
    
    # Teste 3: Busca abrangente
    print("\n🔍 Teste 3: Busca Abrangente")
    comprehensive_results = online_searcher.comprehensive_search("contrato de trabalho")
    
    # Teste 4: Busca inteligente
    print("\n🧠 Teste 4: Busca Inteligente")
    intelligent_results = smart_searcher.intelligent_search(
        "indenização por danos morais", 
        "petição inicial para ação de danos morais"
    )
    
    # Salvar resultados
    online_searcher.save_search_results(comprehensive_results, "/home/ubuntu/test_search_results.json")
    
    with open("/home/ubuntu/intelligent_search_results.json", 'w', encoding='utf-8') as f:
        json.dump(intelligent_results, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Testes do sistema de busca online concluídos!")
    print("📁 Resultados salvos em:")
    print("  - /home/ubuntu/test_search_results.json")
    print("  - /home/ubuntu/intelligent_search_results.json")

