# rag_real_online_search.py (Versão com Busca Real)

import os
import json
import requests
from typing import Dict, List, Any
from urllib.parse import quote
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class RealJuridicalSearcher:
    """
    Buscador jurídico que se conecta a fontes online REAIS,
    usando busca no Google com web scraping para extrair dados.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.google_base_url = "https://www.google.com/search"
        self.timeout = 15
        self.max_results_per_source = 3 # Reduzido para evitar bloqueios e sobrecarga
    
    def _scrape_google_for_site(self, query: str, site_filter: str) -> List[Dict[str, Any]]:
        """
        Função central de web scraping. Faz uma busca no Google filtrando por um site específico.
        """
        print(f"--- Buscando no Google: '{query}' (site: {site_filter}) ---")
        results = []
        try:
            search_query = f"{query} site:{site_filter}"
            params = {'q': search_query, 'num': self.max_results_per_source + 2} # Pede um pouco mais para garantir
            response = self.session.get(self.google_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            for g in soup.find_all('div', class_='g'):
                title_elem = g.find('h3')
                link_elem = g.find('a')
                snippet_elem = g.find('div', style="display:block") or g.find('div', class_='VwiC3b')
                
                if title_elem and link_elem:
                    title = title_elem.get_text()
                    url = link_elem.get('href')
                    description = snippet_elem.get_text() if snippet_elem else ""

                    if url and not url.startswith('/search'):
                        results.append({
                            'title': title,
                            'description': description,
                            'url': url,
                            'source': site_filter
                        })
                if len(results) >= self.max_results_per_source:
                    break
            
            print(f"  ✅ {site_filter}: Encontrou {len(results)} resultados.")
            return results
            
        except Exception as e:
            print(f"  ❌ Erro ao buscar em {site_filter}: {e}")
            return []

    def comprehensive_real_search(self, query: str) -> Dict[str, Any]:
        """
        Busca abrangente em fontes reais de forma paralela.
        """
        print(f"🔍 Busca real abrangente para: '{query}'")
        
        results_data = {
            'query': query,
            'timestamp': time.time(),
            'sources': {},
            'summary': {}
        }
        
        # Fontes para buscar
        sites_to_search = {
            'jusbrasil': 'jusbrasil.com.br',
            'stj': 'stj.jus.br',
            'stf': 'stf.jus.br'
        }

        with ThreadPoolExecutor(max_workers=len(sites_to_search)) as executor:
            future_to_site = {
                executor.submit(self._scrape_google_for_site, query, site_url): site_name
                for site_name, site_url in sites_to_search.items()
            }
            
            total_results_count = 0
            for future in as_completed(future_to_site):
                site_name = future_to_site[future]
                try:
                    site_results = future.result()
                    results_data['sources'][site_name] = {
                        'results': site_results,
                        'count': len(site_results),
                        'success': True
                    }
                    total_results_count += len(site_results)
                except Exception as e:
                    print(f"Erro ao processar resultado para {site_name}: {e}")
                    results_data['sources'][site_name] = {'results': [], 'count': 0, 'success': False, 'error': str(e)}

        results_data['summary'] = {
            'total_results': total_results_count,
            'successful_sources': sum(1 for s in results_data['sources'].values() if s['success'] and s['count'] > 0),
            'total_sources': len(sites_to_search)
        }
        
        print(f"📊 Busca concluída: {results_data['summary']['total_results']} resultados de {results_data['summary']['successful_sources']} fontes.")
        return results_data