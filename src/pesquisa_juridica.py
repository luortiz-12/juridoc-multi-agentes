# pesquisa_juridica.py - Pesquisa com logs detalhados dos sites acessados

import os
import json
import re
import time
import random
from typing import Dict, Any, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Imports para pesquisa
try:
    from googlesearch import search
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class PesquisaJuridica:
    """
    Pesquisa Jurídica com logs detalhados dos sites acessados.
    """
    
    def __init__(self):
        print("🔍 Inicializando Pesquisa Jurídica FORMATADA...")
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        self.cache_pesquisa = {}
        self.cache_lock = threading.Lock()
        
        # Configurações otimizadas para velocidade
        self.delay_entre_buscas = (0.5, 1.0)
        self.delay_entre_sites = (0.2, 0.5)
        self.timeout_site = 8
        self.max_sites_por_query = 3
        
        # Log de sites acessados
        self.sites_acessados = []
        self.conteudos_extraidos = []
        
        print("✅ Sistema de pesquisa jurídica FORMATADA inicializado")
    
    def pesquisar_fundamentacao_completa(self, fundamentos: List[str], tipo_acao: str = "") -> Dict[str, Any]:
        """
        Realiza pesquisa jurídica completa com logs detalhados.
        """
        try:
            print(f"🔍 Iniciando pesquisa jurídica FORMATADA para: {fundamentos}")
            print(f"📋 Tipo de ação: {tipo_acao}")
            
            # Limpar logs anteriores
            self.sites_acessados = []
            self.conteudos_extraidos = []
            
            inicio = time.time()
            
            # Identificar área do direito
            area_direito = self._identificar_area_direito(fundamentos, tipo_acao)
            print(f"📚 Área identificada: {area_direito}")
            
            # Realizar pesquisas em paralelo
            resultados = self._executar_pesquisas_com_logs(fundamentos, area_direito)
            
            # Formatar resultados profissionalmente
            resultado_formatado = self._formatar_resultados_com_logs(resultados, area_direito)
            
            tempo_total = time.time() - inicio
            print(f"✅ PESQUISA FORMATADA CONCLUÍDA em {tempo_total:.1f} segundos")
            print(f"🌐 Total de sites acessados: {len(self.sites_acessados)}")
            print(f"📄 Total de conteúdos extraídos: {len(self.conteudos_extraidos)}")
            
            return resultado_formatado
            
        except Exception as e:
            print(f"❌ Erro na pesquisa formatada: {e}")
            return self._gerar_fallback_formatado(fundamentos, tipo_acao)
    
    def _identificar_area_direito(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Identifica área do direito baseada nos fundamentos."""
        
        texto_analise = " ".join(fundamentos + [tipo_acao]).lower()
        
        if any(palavra in texto_analise for palavra in 
               ['trabalhista', 'clt', 'rescisão', 'horas extras', 'assédio moral', 'empregado']):
            return 'trabalhista'
        elif any(palavra in texto_analise for palavra in 
                ['consumidor', 'cdc', 'fornecedor', 'defeito', 'vício']):
            return 'consumidor'
        elif any(palavra in texto_analise for palavra in 
                ['penal', 'crime', 'delito', 'código penal']):
            return 'penal'
        else:
            return 'civil'
    
    def _executar_pesquisas_com_logs(self, fundamentos: List[str], area_direito: str) -> Dict[str, Any]:
        """Executa pesquisas com logs detalhados."""
        
        print("📚 Buscando LEGISLAÇÃO (modo rápido)...")
        legislacao = self._buscar_legislacao_com_logs(fundamentos, area_direito)
        
        print("⚖️ Buscando JURISPRUDÊNCIA (modo rápido)...")
        jurisprudencia = self._buscar_jurisprudencia_com_logs(fundamentos, area_direito)
        
        print("📖 Buscando DOUTRINA (modo rápido)...")
        doutrina = self._buscar_doutrina_com_logs(fundamentos, area_direito)
        
        return {
            'legislacao': legislacao,
            'jurisprudencia': jurisprudencia,
            'doutrina': doutrina,
            'area_direito': area_direito
        }
    
    def _buscar_legislacao_com_logs(self, fundamentos: List[str], area_direito: str) -> List[Dict[str, str]]:
        """Busca legislação com logs detalhados."""
        
        legislacao_encontrada = []
        
        # Queries específicas por área
        if area_direito == 'trabalhista':
            queries = [
                f"CLT artigo {fundamentos[0]} site:planalto.gov.br",
                f"lei trabalhista {fundamentos[0]} site:lexml.gov.br"
            ]
        else:
            queries = [
                f"lei {fundamentos[0]} site:planalto.gov.br",
                f"código civil {fundamentos[0]} site:lexml.gov.br"
            ]
        
        for query in queries[:2]:  # Limitar para velocidade
            print(f"🔍 Pesquisando Google: {query}")
            
            try:
                if GOOGLE_SEARCH_AVAILABLE:
                    urls = list(search(query, num_results=self.max_sites_por_query, sleep_interval=0.5))
                    
                    for url in urls:
                        print(f"🌐 Acessando site: {url}")
                        self.sites_acessados.append(url)
                        
                        conteudo = self._extrair_conteudo_site(url)
                        if conteudo:
                            print(f"📄 Conteúdo extraído: {len(conteudo)} caracteres")
                            self.conteudos_extraidos.append({
                                'url': url,
                                'tipo': 'legislacao',
                                'tamanho': len(conteudo),
                                'conteudo_preview': conteudo[:200] + '...'
                            })
                            
                            legislacao_encontrada.append({
                                'titulo': self._extrair_titulo_legislacao(conteudo),
                                'artigo': self._extrair_artigo_legislacao(conteudo),
                                'fonte': url,
                                'conteudo': conteudo[:1000]  # Primeiros 1000 chars
                            })
                
                # Delay entre queries
                time.sleep(random.uniform(*self.delay_entre_buscas))
                
            except Exception as e:
                print(f"❌ Erro na busca de legislação '{query}': {e}")
        
        print(f"📚 Legislação encontrada: {len(legislacao_encontrada)} itens")
        return legislacao_encontrada
    
    def _buscar_jurisprudencia_com_logs(self, fundamentos: List[str], area_direito: str) -> List[Dict[str, str]]:
        """Busca jurisprudência com logs detalhados."""
        
        jurisprudencia_encontrada = []
        
        # Queries específicas por área
        if area_direito == 'trabalhista':
            queries = [
                f"TST {fundamentos[0]} site:tst.jus.br",
                f"jurisprudência trabalhista {fundamentos[0]} site:stf.jus.br"
            ]
        else:
            queries = [
                f"STJ {fundamentos[0]} site:stj.jus.br",
                f"jurisprudência {fundamentos[0]} site:stf.jus.br"
            ]
        
        for query in queries[:2]:  # Limitar para velocidade
            print(f"🔍 Pesquisando Google: {query}")
            
            try:
                if GOOGLE_SEARCH_AVAILABLE:
                    urls = list(search(query, num_results=self.max_sites_por_query, sleep_interval=0.5))
                    
                    for url in urls:
                        print(f"🌐 Acessando site: {url}")
                        self.sites_acessados.append(url)
                        
                        conteudo = self._extrair_conteudo_site(url)
                        if conteudo:
                            print(f"📄 Conteúdo extraído: {len(conteudo)} caracteres")
                            self.conteudos_extraidos.append({
                                'url': url,
                                'tipo': 'jurisprudencia',
                                'tamanho': len(conteudo),
                                'conteudo_preview': conteudo[:200] + '...'
                            })
                            
                            jurisprudencia_encontrada.append({
                                'ementa': self._extrair_ementa_jurisprudencia(conteudo),
                                'tribunal': self._extrair_tribunal(url),
                                'fonte': url,
                                'conteudo': conteudo[:1000]  # Primeiros 1000 chars
                            })
                
                # Delay entre queries
                time.sleep(random.uniform(*self.delay_entre_buscas))
                
            except Exception as e:
                print(f"❌ Erro na busca de jurisprudência '{query}': {e}")
        
        print(f"⚖️ Jurisprudência encontrada: {len(jurisprudencia_encontrada)} itens")
        return jurisprudencia_encontrada
    
    def _buscar_doutrina_com_logs(self, fundamentos: List[str], area_direito: str) -> List[Dict[str, str]]:
        """Busca doutrina com logs detalhados."""
        
        doutrina_encontrada = []
        
        # Queries para doutrina
        queries = [
            f"doutrina {fundamentos[0]} site:conjur.com.br",
            f"artigo jurídico {fundamentos[0]} site:migalhas.com.br"
        ]
        
        for query in queries[:2]:  # Limitar para velocidade
            print(f"🔍 Pesquisando Google: {query}")
            
            try:
                if GOOGLE_SEARCH_AVAILABLE:
                    urls = list(search(query, num_results=self.max_sites_por_query, sleep_interval=0.5))
                    
                    for url in urls:
                        print(f"🌐 Acessando site: {url}")
                        self.sites_acessados.append(url)
                        
                        conteudo = self._extrair_conteudo_site(url)
                        if conteudo:
                            print(f"📄 Conteúdo extraído: {len(conteudo)} caracteres")
                            self.conteudos_extraidos.append({
                                'url': url,
                                'tipo': 'doutrina',
                                'tamanho': len(conteudo),
                                'conteudo_preview': conteudo[:200] + '...'
                            })
                            
                            doutrina_encontrada.append({
                                'titulo': self._extrair_titulo_artigo(conteudo),
                                'autor': self._extrair_autor_artigo(conteudo),
                                'fonte': url,
                                'conteudo': conteudo[:1000]  # Primeiros 1000 chars
                            })
                
                # Delay entre queries
                time.sleep(random.uniform(*self.delay_entre_buscas))
                
            except Exception as e:
                print(f"❌ Erro na busca de doutrina '{query}': {e}")
        
        print(f"📖 Doutrina encontrada: {len(doutrina_encontrada)} itens")
        return doutrina_encontrada
    
    def _extrair_conteudo_site(self, url: str) -> str:
        """Extrai conteúdo de um site específico."""
        
        try:
            if not REQUESTS_AVAILABLE:
                return ""
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout_site)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remover scripts e styles
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extrair texto
                texto = soup.get_text()
                
                # Limpar texto
                linhas = (linha.strip() for linha in texto.splitlines())
                chunks = (frase.strip() for linha in linhas for frase in linha.split("  "))
                texto_limpo = ' '.join(chunk for chunk in chunks if chunk)
                
                return texto_limpo[:2000]  # Limitar tamanho
            
            return ""
            
        except Exception as e:
            print(f"❌ Erro ao extrair conteúdo de {url}: {e}")
            return ""
    
    def _extrair_titulo_legislacao(self, conteudo: str) -> str:
        """Extrai título de legislação."""
        # Buscar padrões de lei
        match = re.search(r'(Lei nº? [\d\.\/]+|Decreto nº? [\d\.\/]+|CLT.*?Art\.?\s*\d+)', conteudo, re.IGNORECASE)
        return match.group(1) if match else "Legislação encontrada"
    
    def _extrair_artigo_legislacao(self, conteudo: str) -> str:
        """Extrai artigo específico da legislação."""
        # Buscar artigos
        match = re.search(r'Art\.?\s*\d+.*?(?=Art\.?\s*\d+|$)', conteudo, re.IGNORECASE | re.DOTALL)
        return match.group(0)[:500] if match else conteudo[:500]
    
    def _extrair_ementa_jurisprudencia(self, conteudo: str) -> str:
        """Extrai ementa de jurisprudência."""
        # Buscar ementa
        match = re.search(r'EMENTA:?\s*(.*?)(?=ACÓRDÃO|RELATÓRIO|$)', conteudo, re.IGNORECASE | re.DOTALL)
        return match.group(1)[:500] if match else conteudo[:500]
    
    def _extrair_tribunal(self, url: str) -> str:
        """Extrai nome do tribunal da URL."""
        if 'stf.jus.br' in url:
            return 'STF'
        elif 'stj.jus.br' in url:
            return 'STJ'
        elif 'tst.jus.br' in url:
            return 'TST'
        else:
            return 'Tribunal'
    
    def _extrair_titulo_artigo(self, conteudo: str) -> str:
        """Extrai título de artigo doutrinário."""
        # Buscar título no início
        linhas = conteudo.split('\n')[:10]
        for linha in linhas:
            if len(linha.strip()) > 20 and len(linha.strip()) < 200:
                return linha.strip()
        return "Artigo doutrinário"
    
    def _extrair_autor_artigo(self, conteudo: str) -> str:
        """Extrai autor do artigo."""
        # Buscar padrões de autor
        match = re.search(r'Por:?\s*([A-Z][a-z]+ [A-Z][a-z]+)', conteudo)
        return match.group(1) if match else "Autor não identificado"
    
    def _formatar_resultados_com_logs(self, resultados: Dict[str, Any], area_direito: str) -> Dict[str, Any]:
        """Formata resultados incluindo logs detalhados."""
        
        return {
            'status': 'sucesso',
            'area_direito': area_direito,
            'legislacao_formatada': self._formatar_legislacao(resultados['legislacao']),
            'jurisprudencia_formatada': self._formatar_jurisprudencia(resultados['jurisprudencia']),
            'doutrina_formatada': self._formatar_doutrina(resultados['doutrina']),
            'total_fontes': len(resultados['legislacao']) + len(resultados['jurisprudencia']) + len(resultados['doutrina']),
            'sites_acessados': self.sites_acessados,
            'conteudos_extraidos': self.conteudos_extraidos,
            'timestamp': datetime.now().isoformat()
        }
    
    def _formatar_legislacao(self, legislacao: List[Dict[str, str]]) -> str:
        """Formata legislação encontrada."""
        if not legislacao:
            return "Legislação específica não encontrada nas pesquisas realizadas."
        
        texto_formatado = "LEGISLAÇÃO APLICÁVEL:\n\n"
        for item in legislacao:
            texto_formatado += f"• {item['titulo']}\n"
            texto_formatado += f"  {item['artigo']}\n"
            texto_formatado += f"  Fonte: {item['fonte']}\n\n"
        
        return texto_formatado
    
    def _formatar_jurisprudencia(self, jurisprudencia: List[Dict[str, str]]) -> str:
        """Formata jurisprudência encontrada."""
        if not jurisprudencia:
            return "Jurisprudência específica não encontrada nas pesquisas realizadas."
        
        texto_formatado = "JURISPRUDÊNCIA APLICÁVEL:\n\n"
        for item in jurisprudencia:
            texto_formatado += f"• {item['tribunal']}\n"
            texto_formatado += f"  EMENTA: {item['ementa']}\n"
            texto_formatado += f"  Fonte: {item['fonte']}\n\n"
        
        return texto_formatado
    
    def _formatar_doutrina(self, doutrina: List[Dict[str, str]]) -> str:
        """Formata doutrina encontrada."""
        if not doutrina:
            return "Doutrina específica não encontrada nas pesquisas realizadas."
        
        texto_formatado = "DOUTRINA APLICÁVEL:\n\n"
        for item in doutrina:
            texto_formatado += f"• {item['titulo']}\n"
            texto_formatado += f"  Autor: {item['autor']}\n"
            texto_formatado += f"  Fonte: {item['fonte']}\n\n"
        
        return texto_formatado
    
    def _gerar_fallback_formatado(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """Gera fallback quando pesquisa falha."""
        
        area_direito = self._identificar_area_direito(fundamentos, tipo_acao)
        
        return {
            'status': 'fallback',
            'area_direito': area_direito,
            'legislacao_formatada': f"Legislação aplicável à área de {area_direito} deve ser consultada.",
            'jurisprudencia_formatada': f"Jurisprudência dos tribunais superiores sobre {area_direito}.",
            'doutrina_formatada': f"Doutrina especializada em {area_direito}.",
            'total_fontes': 0,
            'sites_acessados': [],
            'conteudos_extraidos': [],
            'motivo_fallback': 'Erro na pesquisa online',
            'timestamp': datetime.now().isoformat()
        }
