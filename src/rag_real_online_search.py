# rag_real_online_search.py
"""
Implementação real do sistema de busca online jurídica.
Conecta com APIs reais do LexML e outras fontes jurídicas brasileiras.
"""

import os
import json
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from urllib.parse import quote, urljoin
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class RealJuridicalSearcher:
    """
    Buscador jurídico real que conecta com APIs e sites oficiais.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # URLs e configurações das fontes reais
        self.sources = {
            'lexml': {
                'api_url': 'https://www.lexml.gov.br/busca/SRU',
                'description': 'Portal LexML - Legislação Federal',
                'format': 'xml'
            },
            'planalto_search': {
                'search_url': 'https://www.google.com/search',
                'site_filter': 'site:planalto.gov.br',
                'description': 'Presidência da República via Google',
                'format': 'html'
            },
            'jusbrasil': {
                'search_url': 'https://www.jusbrasil.com.br/busca',
                'description': 'JusBrasil - Jurisprudência e Legislação',
                'format': 'html'
            }
        }
        
        self.timeout = 15
        self.max_results = 10
    
    def search_lexml_legislation(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca legislação na API real do LexML.
        """
        try:
            print(f"🔍 Buscando no LexML: '{query}'")
            
            # Preparar parâmetros da API LexML
            params = {
                'operation': 'searchRetrieve',
                'query': f'dc.title="{query}" OR dc.description="{query}"',
                'maximumRecords': self.max_results
            }
            
            # Fazer requisição à API
            response = self.session.get(
                self.sources['lexml']['api_url'],
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parsear XML de resposta
            results = self._parse_lexml_xml(response.text, query)
            
            print(f"  ✅ LexML: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            print(f"  ❌ Erro no LexML: {e}")
            return []
    
    def search_planalto_google(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca no site do Planalto via Google Search.
        """
        try:
            print(f"🔍 Buscando no Planalto via Google: '{query}'")
            
            # Construir query para Google com filtro do site
            google_query = f"{query} {self.sources['planalto_search']['site_filter']}"
            
            params = {
                'q': google_query,
                'num': self.max_results
            }
            
            response = self.session.get(
                self.sources['planalto_search']['search_url'],
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parsear resultados do Google
            results = self._parse_google_results(response.text, 'planalto')
            
            print(f"  ✅ Planalto: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            print(f"  ❌ Erro no Planalto: {e}")
            return []
    
    def search_jusbrasil(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca jurisprudência no JusBrasil.
        """
        try:
            print(f"⚖️ Buscando no JusBrasil: '{query}'")
            
            params = {
                'q': query,
                'p': 1
            }
            
            response = self.session.get(
                self.sources['jusbrasil']['search_url'],
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parsear resultados do JusBrasil
            results = self._parse_jusbrasil_results(response.text, query)
            
            print(f"  ✅ JusBrasil: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            print(f"  ❌ Erro no JusBrasil: {e}")
            return []
    
    def comprehensive_real_search(self, query: str) -> Dict[str, Any]:
        """
        Busca abrangente em fontes reais.
        """
        print(f"🔍 Busca real abrangente para: '{query}'")
        
        results = {
            'query': query,
            'timestamp': time.time(),
            'sources': {},
            'summary': {
                'total_results': 0,
                'successful_sources': 0,
                'failed_sources': 0
            }
        }
        
        # Buscar em paralelo
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.search_lexml_legislation, query): 'lexml',
                executor.submit(self.search_planalto_google, query): 'planalto',
                executor.submit(self.search_jusbrasil, query): 'jusbrasil'
            }
            
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    source_results = future.result(timeout=self.timeout)
                    results['sources'][source_name] = {
                        'results': source_results,
                        'count': len(source_results),
                        'success': True
                    }
                    
                    if source_results:
                        results['summary']['successful_sources'] += 1
                        results['summary']['total_results'] += len(source_results)
                    else:
                        results['summary']['failed_sources'] += 1
                        
                except Exception as e:
                    results['sources'][source_name] = {
                        'results': [],
                        'count': 0,
                        'success': False,
                        'error': str(e)
                    }
                    results['summary']['failed_sources'] += 1
        
        print(f"📊 Busca concluída: {results['summary']['total_results']} resultados de {results['summary']['successful_sources']} fontes")
        
        return results
    
    def _parse_lexml_xml(self, xml_content: str, query: str) -> List[Dict[str, Any]]:
        """
        Parseia resposta XML do LexML.
        """
        results = []
        
        try:
            # Remover namespaces para simplificar parsing
            xml_clean = re.sub(r'xmlns[^=]*="[^"]*"', '', xml_content)
            xml_clean = re.sub(r'[a-zA-Z]+:', '', xml_clean)
            
            root = ET.fromstring(xml_clean)
            
            # Encontrar todos os registros
            records = root.findall('.//record')
            
            for record in records:
                try:
                    # Extrair dados do registro
                    title_elem = record.find('.//title')
                    description_elem = record.find('.//description')
                    date_elem = record.find('.//date')
                    identifier_elem = record.find('.//identifier')
                    tipo_elem = record.find('.//tipoDocumento')
                    
                    title = title_elem.text if title_elem is not None else 'Sem título'
                    description = description_elem.text if description_elem is not None else 'Sem descrição'
                    date = date_elem.text if date_elem is not None else 'Sem data'
                    identifier = identifier_elem.text if identifier_elem is not None else ''
                    tipo = tipo_elem.text if tipo_elem is not None else 'Documento'
                    
                    # Construir URL (se possível)
                    url = f"https://www.lexml.gov.br/urn/{identifier}" if identifier else "https://www.lexml.gov.br"
                    
                    result = {
                        'title': title.strip(),
                        'description': description.strip()[:300],
                        'url': url,
                        'date': date,
                        'type': tipo,
                        'source': 'LexML',
                        'category': 'legislation',
                        'relevance': self._calculate_relevance(title + ' ' + description, query)
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    print(f"Erro ao processar registro LexML: {e}")
                    continue
            
        except Exception as e:
            print(f"Erro ao parsear XML do LexML: {e}")
        
        return results[:self.max_results]
    
    def _parse_google_results(self, html_content: str, source: str) -> List[Dict[str, Any]]:
        """
        Parseia resultados do Google Search.
        """
        results = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Encontrar divs de resultados do Google
            result_divs = soup.find_all('div', class_='g')
            
            for div in result_divs[:self.max_results]:
                try:
                    # Extrair título
                    title_elem = div.find('h3')
                    title = title_elem.get_text().strip() if title_elem else 'Sem título'
                    
                    # Extrair URL
                    link_elem = div.find('a')
                    url = link_elem.get('href') if link_elem else ''
                    
                    # Extrair snippet/descrição
                    snippet_elem = div.find('span', class_='aCOpRe') or div.find('div', class_='VwiC3b')
                    description = snippet_elem.get_text().strip() if snippet_elem else 'Sem descrição'
                    
                    # Filtrar apenas URLs do Planalto
                    if 'planalto.gov.br' in url:
                        result = {
                            'title': title,
                            'description': description[:300],
                            'url': url,
                            'source': 'Planalto',
                            'category': 'legislation',
                            'type': 'documento_oficial',
                            'relevance': 0.8
                        }
                        
                        results.append(result)
                        
                except Exception as e:
                    print(f"Erro ao processar resultado do Google: {e}")
                    continue
            
        except Exception as e:
            print(f"Erro ao parsear resultados do Google: {e}")
        
        return results
    
    def _parse_jusbrasil_results(self, html_content: str, query: str) -> List[Dict[str, Any]]:
        """
        Parseia resultados do JusBrasil.
        """
        results = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Encontrar elementos de resultado (estrutura pode variar)
            result_elements = soup.find_all('div', class_='SearchResult') or soup.find_all('article')
            
            for element in result_elements[:self.max_results]:
                try:
                    # Extrair título
                    title_elem = element.find('h2') or element.find('h3') or element.find('a')
                    title = title_elem.get_text().strip() if title_elem else 'Sem título'
                    
                    # Extrair URL
                    link_elem = element.find('a')
                    url = link_elem.get('href') if link_elem else ''
                    if url and not url.startswith('http'):
                        url = 'https://www.jusbrasil.com.br' + url
                    
                    # Extrair descrição
                    desc_elem = element.find('p') or element.find('div', class_='description')
                    description = desc_elem.get_text().strip() if desc_elem else 'Sem descrição'
                    
                    result = {
                        'title': title,
                        'description': description[:300],
                        'url': url,
                        'source': 'JusBrasil',
                        'category': 'jurisprudence',
                        'type': 'jurisprudencia',
                        'relevance': self._calculate_relevance(title + ' ' + description, query)
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    print(f"Erro ao processar resultado do JusBrasil: {e}")
                    continue
            
        except Exception as e:
            print(f"Erro ao parsear resultados do JusBrasil: {e}")
        
        return results
    
    def _calculate_relevance(self, text: str, query: str) -> float:
        """
        Calcula relevância simples baseada em palavras-chave.
        """
        text_lower = text.lower()
        query_words = query.lower().split()
        
        matches = sum(1 for word in query_words if word in text_lower)
        relevance = matches / len(query_words) if query_words else 0
        
        return min(relevance, 1.0)
    
    def get_best_results(self, search_results: Dict[str, Any], max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Seleciona os melhores resultados de todas as fontes.
        """
        all_results = []
        
        for source_name, source_data in search_results.get('sources', {}).items():
            if source_data.get('success', False):
                for result in source_data.get('results', []):
                    all_results.append(result)
        
        # Ordenar por relevância
        all_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        return all_results[:max_results]
    
    def save_results(self, results: Dict[str, Any], filepath: str):
        """
        Salva resultados em arquivo JSON.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ Resultados salvos em: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return False

if __name__ == "__main__":
    # Teste do buscador real
    print("🚀 Testando Buscador Jurídico Real...")
    
    searcher = RealJuridicalSearcher()
    
    # Teste com diferentes queries
    test_queries = [
        "danos morais",
        "contrato de trabalho",
        "responsabilidade civil"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Teste {i}: '{query}'")
        
        # Busca abrangente
        results = searcher.comprehensive_real_search(query)
        
        # Obter melhores resultados
        best_results = searcher.get_best_results(results, max_results=5)
        
        print(f"🏆 Top {len(best_results)} resultados:")
        for j, result in enumerate(best_results, 1):
            print(f"  {j}. {result['title'][:60]}... ({result['source']})")
            print(f"     Relevância: {result['relevance']:.2f}")
        
        # Salvar resultados
        filename = f"/home/ubuntu/real_search_results_{query.replace(' ', '_')}.json"
        searcher.save_results(results, filename)
    
    print("\n✅ Testes do buscador real concluídos!")

