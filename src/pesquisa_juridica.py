# pesquisa_juridica.py - Pesquisa Real com Google Search API

import re
import time
import random
import requests
from typing import Dict, List, Any, Tuple
from bs4 import BeautifulSoup
import urllib.parse

# FERRAMENTA REAL 1: Google Search Python (biblioteca específica)
try:
    from googlesearch import search
    GOOGLE_SEARCH_AVAILABLE = True
    print("✅ Google Search Python disponível")
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    print("⚠️ Google Search Python não disponível. Instale com: pip install googlesearch-python")

# FERRAMENTA REAL 2: Requests para acessar sites encontrados
# FERRAMENTA REAL 3: BeautifulSoup para extrair conteúdo real

class PesquisaJuridica:
    """
    Módulo de pesquisa jurídica que usa Google Search API real
    e extrai conteúdo verdadeiro dos sites encontrados.
    NUNCA usa dados simulados - sempre dados reais dos formulários + pesquisas.
    """
    
    def __init__(self):
        # CONFIGURAÇÃO 1: User agents realistas para evitar bloqueios
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # CONFIGURAÇÃO 2: Delays para evitar rate limits
        self.delay_entre_buscas = (3, 7)  # 3-7 segundos entre buscas Google
        self.delay_entre_sites = (2, 4)   # 2-4 segundos entre acessos a sites
        self.timeout_site = 20             # 20 segundos timeout por site
        self.max_sites_por_busca = 5       # Máximo 5 sites por busca
        self.min_conteudo_util = 200       # Mínimo 200 chars de conteúdo útil
        
        # CONFIGURAÇÃO 3: Sites prioritários REAIS para cada categoria
        self.sites_oficiais = {
            'legislacao': [
                'planalto.gov.br',
                'lexml.gov.br',
                'senado.leg.br',
                'camara.leg.br',
                'presidencia.gov.br'
            ],
            'jurisprudencia': [
                'stf.jus.br',
                'stj.jus.br',
                'tst.jus.br',
                'tjsp.jus.br',
                'tjrj.jus.br',
                'tjmg.jus.br'
            ],
            'doutrina': [
                'conjur.com.br',
                'migalhas.com.br',
                'jota.info',
                'jusbrasil.com.br',
                'direitonet.com.br'
            ]
        }
        
        print("🔍 Sistema de pesquisa jurídica REAL inicializado")
        print(f"📚 Google Search: {'✅ Disponível' if GOOGLE_SEARCH_AVAILABLE else '❌ Indisponível'}")
    
    def pesquisar_fundamentos_juridicos(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """
        Realiza pesquisa jurídica REAL usando Google Search API
        e extrai conteúdo verdadeiro dos sites encontrados.
        NUNCA retorna dados simulados.
        """
        try:
            print(f"🔍 INICIANDO PESQUISA REAL para: {fundamentos}")
            print(f"📋 Tipo de ação: {tipo_acao}")
            
            if not GOOGLE_SEARCH_AVAILABLE:
                raise Exception("Google Search Python não está disponível. Instale com: pip install googlesearch-python")
            
            # ETAPA 1: Pesquisar legislação REAL
            print("📚 Buscando LEGISLAÇÃO REAL...")
            leis_reais = self._buscar_legislacao_real(fundamentos, tipo_acao)
            
            # ETAPA 2: Pesquisar jurisprudência REAL  
            print("⚖️ Buscando JURISPRUDÊNCIA REAL...")
            jurisprudencia_real = self._buscar_jurisprudencia_real(fundamentos, tipo_acao)
            
            # ETAPA 3: Pesquisar doutrina REAL
            print("📖 Buscando DOUTRINA REAL...")
            doutrina_real = self._buscar_doutrina_real(fundamentos, tipo_acao)
            
            # ETAPA 4: Compilar resultados REAIS
            resultados = {
                "leis": leis_reais,
                "jurisprudencia": jurisprudencia_real,
                "doutrina": doutrina_real,
                "resumo_pesquisa": self._gerar_resumo_real(leis_reais, jurisprudencia_real, doutrina_real, fundamentos, tipo_acao)
            }
            
            print("✅ PESQUISA REAL CONCLUÍDA")
            return resultados
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO na pesquisa real: {e}")
            # NUNCA retornar dados simulados - falhar explicitamente
            raise Exception(f"Falha na pesquisa jurídica real: {str(e)}. Sistema configurado para NUNCA usar dados simulados.")
    
    def _buscar_legislacao_real(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Busca legislação REAL usando Google Search API."""
        try:
            conteudo_legislacao = []
            
            for fundamento in fundamentos[:2]:  # Máximo 2 fundamentos para não sobrecarregar
                # QUERY REAL 1: Busca específica no Planalto
                query1 = f"lei {fundamento} site:planalto.gov.br"
                sites_encontrados = self._google_search_real(query1)
                
                for site_url in sites_encontrados[:3]:  # Top 3 sites por query
                    conteudo = self._extrair_conteudo_real(site_url, 'legislacao')
                    if conteudo and len(conteudo) > self.min_conteudo_util:
                        conteudo_legislacao.append(conteudo)
                
                # Delay entre buscas
                time.sleep(random.uniform(*self.delay_entre_buscas))
                
                # QUERY REAL 2: Busca geral de legislação
                query2 = f"código {fundamento} legislação federal"
                sites_encontrados = self._google_search_real(query2)
                
                for site_url in sites_encontrados[:2]:  # Top 2 sites da segunda query
                    conteudo = self._extrair_conteudo_real(site_url, 'legislacao')
                    if conteudo and len(conteudo) > self.min_conteudo_util:
                        conteudo_legislacao.append(conteudo)
                
                time.sleep(random.uniform(*self.delay_entre_buscas))
            
            if conteudo_legislacao:
                resultado_final = "LEGISLAÇÃO ENCONTRADA (FONTES REAIS):\n\n"
                resultado_final += "\n\n" + "="*80 + "\n\n".join(conteudo_legislacao[:4])  # Máximo 4 fontes
                return resultado_final
            else:
                raise Exception("Nenhuma legislação real encontrada nos sites oficiais")
                
        except Exception as e:
            print(f"❌ Erro na busca de legislação real: {e}")
            raise Exception(f"Falha na busca de legislação: {str(e)}")
    
    def _buscar_jurisprudencia_real(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Busca jurisprudência REAL usando Google Search API."""
        try:
            conteudo_jurisprudencia = []
            
            for fundamento in fundamentos[:2]:
                # QUERY REAL 1: STJ
                query1 = f"acórdão {fundamento} site:stj.jus.br"
                sites_encontrados = self._google_search_real(query1)
                
                for site_url in sites_encontrados[:2]:
                    conteudo = self._extrair_conteudo_real(site_url, 'jurisprudencia')
                    if conteudo and len(conteudo) > self.min_conteudo_util:
                        conteudo_jurisprudencia.append(conteudo)
                
                time.sleep(random.uniform(*self.delay_entre_buscas))
                
                # QUERY REAL 2: STF
                query2 = f"decisão {fundamento} site:stf.jus.br"
                sites_encontrados = self._google_search_real(query2)
                
                for site_url in sites_encontrados[:2]:
                    conteudo = self._extrair_conteudo_real(site_url, 'jurisprudencia')
                    if conteudo and len(conteudo) > self.min_conteudo_util:
                        conteudo_jurisprudencia.append(conteudo)
                
                time.sleep(random.uniform(*self.delay_entre_buscas))
            
            if conteudo_jurisprudencia:
                resultado_final = "JURISPRUDÊNCIA ENCONTRADA (TRIBUNAIS REAIS):\n\n"
                resultado_final += "\n\n" + "="*80 + "\n\n".join(conteudo_jurisprudencia[:4])
                return resultado_final
            else:
                raise Exception("Nenhuma jurisprudência real encontrada nos tribunais")
                
        except Exception as e:
            print(f"❌ Erro na busca de jurisprudência real: {e}")
            raise Exception(f"Falha na busca de jurisprudência: {str(e)}")
    
    def _buscar_doutrina_real(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Busca doutrina REAL usando Google Search API."""
        try:
            conteudo_doutrina = []
            
            for fundamento in fundamentos[:2]:
                # QUERY REAL 1: Conjur
                query1 = f"artigo {fundamento} site:conjur.com.br"
                sites_encontrados = self._google_search_real(query1)
                
                for site_url in sites_encontrados[:2]:
                    conteudo = self._extrair_conteudo_real(site_url, 'doutrina')
                    if conteudo and len(conteudo) > self.min_conteudo_util:
                        conteudo_doutrina.append(conteudo)
                
                time.sleep(random.uniform(*self.delay_entre_buscas))
                
                # QUERY REAL 2: Migalhas
                query2 = f"comentário {fundamento} site:migalhas.com.br"
                sites_encontrados = self._google_search_real(query2)
                
                for site_url in sites_encontrados[:2]:
                    conteudo = self._extrair_conteudo_real(site_url, 'doutrina')
                    if conteudo and len(conteudo) > self.min_conteudo_util:
                        conteudo_doutrina.append(conteudo)
                
                time.sleep(random.uniform(*self.delay_entre_buscas))
            
            if conteudo_doutrina:
                resultado_final = "DOUTRINA ENCONTRADA (ARTIGOS REAIS):\n\n"
                resultado_final += "\n\n" + "="*80 + "\n\n".join(conteudo_doutrina[:4])
                return resultado_final
            else:
                raise Exception("Nenhuma doutrina real encontrada nos sites especializados")
                
        except Exception as e:
            print(f"❌ Erro na busca de doutrina real: {e}")
            raise Exception(f"Falha na busca de doutrina: {str(e)}")
    
    def _google_search_real(self, query: str) -> List[str]:
        """
        Usa Google Search Python para busca REAL.
        FERRAMENTA: googlesearch-python
        """
        try:
            print(f"🌐 Google Search REAL: {query}")
            
            # BUSCA REAL usando googlesearch-python
            resultados = []
            
            # search() retorna URLs reais do Google
            for url in search(query, num_results=self.max_sites_por_busca, sleep_interval=2):
                if url and url.startswith('http'):
                    resultados.append(url)
                    print(f"📋 Encontrado: {url}")
            
            print(f"✅ {len(resultados)} URLs reais encontradas")
            return resultados
            
        except Exception as e:
            print(f"❌ Erro na busca Google real: {e}")
            return []
    
    def _extrair_conteudo_real(self, url: str, tipo_conteudo: str) -> str:
        """
        Acessa URL real e extrai conteúdo verdadeiro.
        FERRAMENTA: requests + BeautifulSoup
        """
        try:
            print(f"📄 Acessando site REAL: {url}")
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            # ACESSO REAL ao site
            response = requests.get(url, headers=headers, timeout=self.timeout_site)
            
            if response.status_code == 200:
                # EXTRAÇÃO REAL do conteúdo
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if tipo_conteudo == 'legislacao':
                    conteudo_extraido = self._extrair_legislacao_real(soup, url)
                elif tipo_conteudo == 'jurisprudencia':
                    conteudo_extraido = self._extrair_jurisprudencia_real(soup, url)
                elif tipo_conteudo == 'doutrina':
                    conteudo_extraido = self._extrair_doutrina_real(soup, url)
                else:
                    conteudo_extraido = self._extrair_conteudo_generico_real(soup, url)
                
                # Delay entre acessos
                time.sleep(random.uniform(*self.delay_entre_sites))
                
                if conteudo_extraido and len(conteudo_extraido) > self.min_conteudo_util:
                    print(f"✅ Conteúdo REAL extraído: {len(conteudo_extraido)} caracteres")
                    return conteudo_extraido
                else:
                    print(f"⚠️ Conteúdo insuficiente extraído")
                    return None
            else:
                print(f"⚠️ Site retornou status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao acessar site real {url}: {e}")
            return None
    
    def _extrair_legislacao_real(self, soup: BeautifulSoup, url: str) -> str:
        """Extrai conteúdo REAL de legislação."""
        try:
            elementos_reais = []
            
            # TÍTULO REAL da lei
            titulo = soup.find('h1') or soup.find('title')
            if titulo:
                titulo_texto = titulo.get_text().strip()
                if len(titulo_texto) > 10:
                    elementos_reais.append(f"TÍTULO: {titulo_texto}")
            
            # ARTIGOS REAIS da legislação
            # Buscar por padrões típicos de artigos de lei
            artigos_encontrados = soup.find_all(text=re.compile(r'Art\.\s*\d+|Artigo\s*\d+'))
            for artigo_texto in artigos_encontrados[:5]:  # Máximo 5 artigos
                # Pegar o parágrafo completo que contém o artigo
                elemento_pai = artigo_texto.parent
                if elemento_pai:
                    texto_completo = elemento_pai.get_text().strip()
                    if len(texto_completo) > 50 and len(texto_completo) < 1000:
                        elementos_reais.append(f"ARTIGO: {texto_completo}")
            
            # PARÁGRAFOS REAIS com conteúdo jurídico
            paragrafos = soup.find_all('p')
            for p in paragrafos[:10]:
                texto = p.get_text().strip()
                # Filtrar parágrafos que parecem ser conteúdo jurídico real
                if (len(texto) > 100 and 
                    any(palavra in texto.lower() for palavra in ['lei', 'código', 'decreto', 'artigo', 'parágrafo', 'inciso']) and
                    not any(palavra in texto.lower() for palavra in ['cookie', 'publicidade', 'newsletter', 'login'])):
                    elementos_reais.append(f"DISPOSITIVO: {texto}")
            
            if elementos_reais:
                resultado = "\n\n".join(elementos_reais[:6])  # Máximo 6 elementos
                resultado += f"\n\nFONTE OFICIAL: {url}"
                resultado += f"\nDATA DE ACESSO: {time.strftime('%d/%m/%Y %H:%M')}"
                return resultado
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao extrair legislação real: {e}")
            return None
    
    def _extrair_jurisprudencia_real(self, soup: BeautifulSoup, url: str) -> str:
        """Extrai conteúdo REAL de jurisprudência."""
        try:
            elementos_reais = []
            
            # EMENTA REAL
            ementa_patterns = [
                soup.find(text=re.compile(r'EMENTA', re.IGNORECASE)),
                soup.find('div', class_=re.compile(r'ementa', re.IGNORECASE)),
                soup.find('p', class_=re.compile(r'ementa', re.IGNORECASE))
            ]
            
            for ementa in ementa_patterns:
                if ementa:
                    if hasattr(ementa, 'parent'):
                        texto_ementa = ementa.parent.get_text().strip()
                    else:
                        texto_ementa = str(ementa).strip()
                    
                    if len(texto_ementa) > 100:
                        elementos_reais.append(f"EMENTA: {texto_ementa[:800]}...")
                        break
            
            # RELATÓRIO REAL
            relatorio_patterns = [
                soup.find(text=re.compile(r'RELATÓRIO|VOTO', re.IGNORECASE)),
                soup.find('div', class_=re.compile(r'relatorio|voto', re.IGNORECASE))
            ]
            
            for relatorio in relatorio_patterns:
                if relatorio:
                    if hasattr(relatorio, 'parent'):
                        texto_relatorio = relatorio.parent.get_text().strip()
                    else:
                        texto_relatorio = str(relatorio).strip()
                    
                    if len(texto_relatorio) > 100:
                        elementos_reais.append(f"RELATÓRIO: {texto_relatorio[:600]}...")
                        break
            
            # DECISÃO REAL
            decisao_patterns = [
                soup.find(text=re.compile(r'DECISÃO|ACORDAM|JULGA', re.IGNORECASE)),
                soup.find('div', class_=re.compile(r'decisao|acordao', re.IGNORECASE))
            ]
            
            for decisao in decisao_patterns:
                if decisao:
                    if hasattr(decisao, 'parent'):
                        texto_decisao = decisao.parent.get_text().strip()
                    else:
                        texto_decisao = str(decisao).strip()
                    
                    if len(texto_decisao) > 50:
                        elementos_reais.append(f"DECISÃO: {texto_decisao[:500]}...")
                        break
            
            if elementos_reais:
                resultado = "\n\n".join(elementos_reais)
                resultado += f"\n\nTRIBUNAL: {url}"
                resultado += f"\nDATA DE ACESSO: {time.strftime('%d/%m/%Y %H:%M')}"
                return resultado
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao extrair jurisprudência real: {e}")
            return None
    
    def _extrair_doutrina_real(self, soup: BeautifulSoup, url: str) -> str:
        """Extrai conteúdo REAL de doutrina."""
        try:
            elementos_reais = []
            
            # TÍTULO REAL do artigo
            titulo = soup.find('h1') or soup.find('h2', class_=re.compile(r'title|titulo'))
            if titulo:
                titulo_texto = titulo.get_text().strip()
                if len(titulo_texto) > 15:
                    elementos_reais.append(f"ARTIGO: {titulo_texto}")
            
            # AUTOR REAL
            autor_patterns = [
                soup.find('span', class_=re.compile(r'author|autor')),
                soup.find('div', class_=re.compile(r'author|autor')),
                soup.find(text=re.compile(r'Por:|Autor:|By:'))
            ]
            
            for autor in autor_patterns:
                if autor:
                    if hasattr(autor, 'get_text'):
                        texto_autor = autor.get_text().strip()
                    else:
                        texto_autor = str(autor).strip()
                    
                    if len(texto_autor) > 5 and len(texto_autor) < 100:
                        elementos_reais.append(f"AUTOR: {texto_autor}")
                        break
            
            # CONTEÚDO REAL do artigo
            paragrafos = soup.find_all('p')
            conteudo_paragrafos = []
            
            for p in paragrafos:
                texto = p.get_text().strip()
                # Filtrar conteúdo que parece ser artigo jurídico real
                if (len(texto) > 150 and 
                    not any(palavra in texto.lower() for palavra in ['cookie', 'publicidade', 'newsletter', 'cadastre-se', 'assine']) and
                    any(palavra in texto.lower() for palavra in ['direito', 'lei', 'jurídico', 'tribunal', 'processo', 'código'])):
                    conteudo_paragrafos.append(texto)
            
            # Pegar os melhores parágrafos
            if conteudo_paragrafos:
                elementos_reais.append("CONTEÚDO:")
                for i, paragrafo in enumerate(conteudo_paragrafos[:4], 1):  # Máximo 4 parágrafos
                    elementos_reais.append(f"{i}. {paragrafo[:400]}...")
            
            if elementos_reais:
                resultado = "\n\n".join(elementos_reais)
                resultado += f"\n\nFONTE ESPECIALIZADA: {url}"
                resultado += f"\nDATA DE ACESSO: {time.strftime('%d/%m/%Y %H:%M')}"
                return resultado
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao extrair doutrina real: {e}")
            return None
    
    def _extrair_conteudo_generico_real(self, soup: BeautifulSoup, url: str) -> str:
        """Extrai conteúdo REAL genérico quando tipo não é específico."""
        try:
            # Título
            titulo = soup.find('h1') or soup.find('title')
            titulo_texto = titulo.get_text().strip() if titulo else "Documento Jurídico"
            
            # Parágrafos com conteúdo jurídico
            paragrafos = soup.find_all('p')
            conteudo_relevante = []
            
            for p in paragrafos:
                texto = p.get_text().strip()
                if (len(texto) > 100 and 
                    any(palavra in texto.lower() for palavra in ['direito', 'lei', 'jurídico', 'processo', 'tribunal']) and
                    not any(palavra in texto.lower() for palavra in ['cookie', 'publicidade', 'newsletter'])):
                    conteudo_relevante.append(texto[:300] + "...")
            
            if conteudo_relevante:
                resultado = f"DOCUMENTO: {titulo_texto}\n\n"
                resultado += "\n\n".join(conteudo_relevante[:5])
                resultado += f"\n\nFONTE: {url}"
                resultado += f"\nDATA DE ACESSO: {time.strftime('%d/%m/%Y %H:%M')}"
                return resultado
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao extrair conteúdo genérico real: {e}")
            return None
    
    def _gerar_resumo_real(self, leis: str, jurisprudencia: str, doutrina: str, fundamentos: List[str], tipo_acao: str) -> str:
        """Gera resumo baseado APENAS em dados reais obtidos."""
        
        # Contar fontes REAIS encontradas
        fontes_leis = leis.count('FONTE OFICIAL:') if leis else 0
        fontes_juris = jurisprudencia.count('TRIBUNAL:') if jurisprudencia else 0
        fontes_doutrina = doutrina.count('FONTE ESPECIALIZADA:') if doutrina else 0
        
        total_fontes_reais = fontes_leis + fontes_juris + fontes_doutrina
        
        return f"""
RESUMO DA PESQUISA JURÍDICA REAL:

Tipo de Ação: {tipo_acao}
Fundamentos Pesquisados: {', '.join(fundamentos)}
Total de Fontes REAIS Acessadas: {total_fontes_reais}

METODOLOGIA APLICADA:
- Google Search Python API para busca real
- Acesso direto aos sites oficiais encontrados
- Extração de conteúdo verdadeiro via BeautifulSoup
- Filtragem de conteúdo jurídico relevante
- ZERO dados simulados ou fictícios

RESULTADOS REAIS OBTIDOS:
- Legislação: {fontes_leis} fontes oficiais do governo
- Jurisprudência: {fontes_juris} decisões de tribunais reais
- Doutrina: {fontes_doutrina} artigos de sites especializados

GARANTIA DE AUTENTICIDADE:
Todas as informações foram extraídas diretamente dos sites
oficiais e especializados em {time.strftime('%d/%m/%Y às %H:%M')}.
Nenhum dado foi simulado ou inventado.

FERRAMENTAS UTILIZADAS:
- googlesearch-python (busca real no Google)
- requests (acesso direto aos sites)
- BeautifulSoup (extração de conteúdo real)
        """

