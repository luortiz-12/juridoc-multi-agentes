# pesquisa_juridica_completa.py - Pesquisa com Extração Completa e Navegação Profunda

import os
import time
import random
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from typing import Dict, Any, List
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse

class PesquisaJuridica:
    """
    Pesquisa Jurídica com Extração COMPLETA e Navegação PROFUNDA:
    - Extrai conteúdo integral dos sites (não apenas resumos)
    - Navega profundamente nos sites para encontrar conteúdo completo
    - Segue links internos quando necessário
    - Extrai textos longos e substanciais
    """
    
    def __init__(self):
        print("🔍 Inicializando Pesquisa Jurídica COMPLETA...")
        
        # Configurações para extração completa
        self.config = {
            'tamanho_minimo_conteudo': 1000,      # Mínimo 1000 caracteres por conteúdo
            'tamanho_maximo_conteudo': 30000,     # Máximo 30000 caracteres por conteúdo
            'max_sites_por_query': 5,             # Máximo 5 sites por query
            'max_paginas_por_site': 7,            # Máximo 7 páginas por site
            'timeout_por_pagina': 15,             # 15 segundos por página
            'delay_entre_paginas': (1, 3),        # 1-3 segundos entre páginas
            'profundidade_navegacao': 2,          # Até 2 níveis de profundidade
        }
        
        # User agents rotativos
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Sites prioritários por tipo
        self.sites_prioritarios = {
            'legislacao': [
                'planalto.gov.br',
                'lexml.gov.br',
                'senado.leg.br',
                'camara.leg.br'
            ],
            'jurisprudencia': [
                'stf.jus.br',
                'stj.jus.br',
                'tst.jus.br',
                'trf1.jus.br',
                'trf2.jus.br',
                'trf3.jus.br',
                'trf4.jus.br',
                'trf5.jus.br'
            ],
            'doutrina': [
                'conjur.com.br',
                'migalhas.com.br',
                'jota.info',
                'jusbrasil.com.br'
            ]
        }
        
        print("✅ Sistema de pesquisa jurídica COMPLETA inicializado")
    
    def pesquisar_fundamentacao_completa(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """
        Realiza pesquisa completa com extração integral de conteúdo.
        """
        try:
            print(f"🔍 Iniciando pesquisa jurídica COMPLETA para: {fundamentos}")
            print(f"📋 Tipo de ação: {tipo_acao}")
            
            inicio_pesquisa = datetime.now()
            
            # Identificar área do direito
            area_direito = self._identificar_area_direito(fundamentos, tipo_acao)
            print(f"📚 Área identificada: {area_direito}")
            
            # Realizar pesquisas por tipo
            resultados = {
                'legislacao': self._pesquisar_legislacao_completa(fundamentos, area_direito),
                'jurisprudencia': self._pesquisar_jurisprudencia_completa(fundamentos, area_direito),
                'doutrina': self._pesquisar_doutrina_completa(fundamentos, area_direito)
            }
            
            # Compilar resultados
            resultado_final = self._compilar_resultados_completos(resultados, area_direito)
            
            tempo_total = (datetime.now() - inicio_pesquisa).total_seconds()
            print(f"✅ PESQUISA COMPLETA CONCLUÍDA em {tempo_total:.1f} segundos")
            
            return resultado_final
            
        except Exception as e:
            print(f"❌ Erro na pesquisa completa: {e}")
            return self._gerar_resultado_fallback(fundamentos, tipo_acao)
    
    def _pesquisar_legislacao_completa(self, fundamentos: List[str], area_direito: str) -> List[Dict[str, Any]]:
        """
        Pesquisa legislação com extração completa de artigos e dispositivos.
        """
        print("📚 Buscando LEGISLAÇÃO (extração completa)...")
        
        resultados = []
        sites_prioritarios = self.sites_prioritarios['legislacao']
        
        # Queries específicas para legislação
        queries_legislacao = []
        for fundamento in fundamentos[:3]:  # Máximo 3 fundamentos
            for site in sites_prioritarios[:2]:  # Máximo 2 sites prioritários
                queries_legislacao.append(f"{fundamento} artigo lei site:{site}")
        
        for query in queries_legislacao:
            print(f"🔍 Pesquisando Google: {query}")
            
            try:
                # Buscar URLs no Google
                urls_encontradas = list(search(query, num_results=self.config['max_sites_por_query'], sleep_interval=1))
                
                for url in urls_encontradas:
                    # Extrair conteúdo completo do site
                    conteudo_completo = self._extrair_conteudo_completo_site(url, 'legislacao')
                    
                    if conteudo_completo and len(conteudo_completo['texto']) >= self.config['tamanho_minimo_conteudo']:
                        resultados.append(conteudo_completo)
                        
                        # Parar se já temos conteúdo suficiente
                        if len(resultados) >= 5:
                            break
                
                # Delay entre queries
                time.sleep(random.uniform(*self.config['delay_entre_paginas']))
                
            except Exception as e:
                print(f"⚠️ Erro na query '{query}': {e}")
                continue
        
        print(f"📚 Legislação encontrada: {len(resultados)} itens completos")
        return resultados
    
    def _pesquisar_jurisprudencia_completa(self, fundamentos: List[str], area_direito: str) -> List[Dict[str, Any]]:
        """
        Pesquisa jurisprudência com extração completa de ementas e decisões.
        """
        print("⚖️ Buscando JURISPRUDÊNCIA (extração completa)...")
        
        resultados = []
        sites_prioritarios = self.sites_prioritarios['jurisprudencia']
        
        # Queries específicas para jurisprudência
        queries_jurisprudencia = []
        for fundamento in fundamentos[:3]:
            for site in sites_prioritarios[:3]:  # Máximo 3 tribunais
                queries_jurisprudencia.append(f"jurisprudência {fundamento} site:{site}")
        
        for query in queries_jurisprudencia:
            print(f"🔍 Pesquisando Google: {query}")
            
            try:
                urls_encontradas = list(search(query, num_results=self.config['max_sites_por_query'], sleep_interval=1))
                
                for url in urls_encontradas:
                    conteudo_completo = self._extrair_conteudo_completo_site(url, 'jurisprudencia')
                    
                    if conteudo_completo and len(conteudo_completo['texto']) >= self.config['tamanho_minimo_conteudo']:
                        resultados.append(conteudo_completo)
                        
                        if len(resultados) >= 5:
                            break
                
                time.sleep(random.uniform(*self.config['delay_entre_paginas']))
                
            except Exception as e:
                print(f"⚠️ Erro na query '{query}': {e}")
                continue
        
        print(f"⚖️ Jurisprudência encontrada: {len(resultados)} itens completos")
        return resultados
    
    def _pesquisar_doutrina_completa(self, fundamentos: List[str], area_direito: str) -> List[Dict[str, Any]]:
        """
        Pesquisa doutrina com extração completa de artigos e análises.
        """
        print("📖 Buscando DOUTRINA (extração completa)...")
        
        resultados = []
        sites_prioritarios = self.sites_prioritarios['doutrina']
        
        # Queries específicas para doutrina
        queries_doutrina = []
        for fundamento in fundamentos[:3]:
            for site in sites_prioritarios[:2]:
                queries_doutrina.append(f"artigo {fundamento} {area_direito} site:{site}")
        
        for query in queries_doutrina:
            print(f"🔍 Pesquisando Google: {query}")
            
            try:
                urls_encontradas = list(search(query, num_results=self.config['max_sites_por_query'], sleep_interval=1))
                
                for url in urls_encontradas:
                    conteudo_completo = self._extrair_conteudo_completo_site(url, 'doutrina')
                    
                    if conteudo_completo and len(conteudo_completo['texto']) >= self.config['tamanho_minimo_conteudo']:
                        resultados.append(conteudo_completo)
                        
                        if len(resultados) >= 5:
                            break
                
                time.sleep(random.uniform(*self.config['delay_entre_paginas']))
                
            except Exception as e:
                print(f"⚠️ Erro na query '{query}': {e}")
                continue
        
        print(f"📖 Doutrina encontrada: {len(resultados)} itens completos")
        return resultados
    
    def _extrair_conteudo_completo_site(self, url: str, tipo_conteudo: str) -> Dict[str, Any]:
        """
        Extrai conteúdo COMPLETO de um site, navegando profundamente se necessário.
        """
        print(f"🌐 Extraindo conteúdo COMPLETO de: {url}")
        
        try:
            # Configurar sessão
            session = requests.Session()
            session.headers.update({
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Acessar página principal
            response = session.get(url, timeout=self.config['timeout_por_pagina'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair conteúdo da página principal
            conteudo_principal = self._extrair_texto_pagina(soup, tipo_conteudo)
            
            # Se conteúdo é insuficiente, navegar profundamente
            if len(conteudo_principal) < self.config['tamanho_minimo_conteudo']:
                print(f"📄 Conteúdo insuficiente ({len(conteudo_principal)} chars), navegando profundamente...")
                conteudo_adicional = self._navegar_profundamente(session, url, soup, tipo_conteudo)
                conteudo_principal += "\n\n" + conteudo_adicional
            
            # Limpar e formatar texto
            texto_final = self._limpar_texto_completo(conteudo_principal)
            
            # Limitar tamanho máximo
            if len(texto_final) > self.config['tamanho_maximo_conteudo']:
                texto_final = texto_final[:self.config['tamanho_maximo_conteudo']] + "..."
            
            print(f"📄 Conteúdo COMPLETO extraído: {len(texto_final)} caracteres")
            
            return {
                'url': url,
                'tipo': tipo_conteudo,
                'texto': texto_final,
                'tamanho': len(texto_final),
                'titulo': self._extrair_titulo(soup),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro ao extrair conteúdo completo de {url}: {e}")
            return None
    
    def _navegar_profundamente(self, session: requests.Session, url_base: str, soup: BeautifulSoup, tipo_conteudo: str) -> str:
        """
        Navega profundamente no site para encontrar conteúdo mais completo.
        """
        print("🔍 Navegando profundamente no site...")
        
        conteudo_adicional = ""
        links_relevantes = self._encontrar_links_relevantes(soup, url_base, tipo_conteudo)
        
        for link in links_relevantes[:self.config['max_paginas_por_site']]:
            try:
                print(f"🌐 Acessando página adicional: {link}")
                
                response = session.get(link, timeout=self.config['timeout_por_pagina'])
                response.raise_for_status()
                
                soup_adicional = BeautifulSoup(response.content, 'html.parser')
                texto_adicional = self._extrair_texto_pagina(soup_adicional, tipo_conteudo)
                
                if len(texto_adicional) >= 500:  # Mínimo 500 caracteres por página adicional
                    conteudo_adicional += "\n\n" + texto_adicional
                    print(f"📄 Conteúdo adicional extraído: {len(texto_adicional)} caracteres")
                
                # Delay entre páginas
                time.sleep(random.uniform(*self.config['delay_entre_paginas']))
                
                # Parar se já temos conteúdo suficiente
                if len(conteudo_adicional) >= self.config['tamanho_minimo_conteudo']:
                    break
                    
            except Exception as e:
                print(f"⚠️ Erro ao acessar {link}: {e}")
                continue
        
        return conteudo_adicional
    
    def _encontrar_links_relevantes(self, soup: BeautifulSoup, url_base: str, tipo_conteudo: str) -> List[str]:
        """
        Encontra links relevantes na página para navegação profunda.
        """
        links_relevantes = []
        base_domain = urlparse(url_base).netloc
        
        # Palavras-chave por tipo de conteúdo
        palavras_chave = {
            'legislacao': ['artigo', 'lei', 'decreto', 'código', 'dispositivo', 'parágrafo'],
            'jurisprudencia': ['acórdão', 'ementa', 'decisão', 'súmula', 'jurisprudência', 'tribunal'],
            'doutrina': ['artigo', 'análise', 'comentário', 'doutrina', 'estudo', 'parecer']
        }
        
        palavras_tipo = palavras_chave.get(tipo_conteudo, [])
        
        # Buscar links com texto relevante
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            texto_link = link.get_text().lower()
            
            # Verificar se é link interno
            if href.startswith('/'):
                url_completa = urljoin(url_base, href)
            elif base_domain in href:
                url_completa = href
            else:
                continue
            
            # Verificar se o texto do link é relevante
            if any(palavra in texto_link for palavra in palavras_tipo):
                if url_completa not in links_relevantes and url_completa != url_base:
                    links_relevantes.append(url_completa)
        
        return links_relevantes[:10]  # Máximo 10 links relevantes
    
    def _extrair_texto_pagina(self, soup: BeautifulSoup, tipo_conteudo: str) -> str:
        """
        Extrai texto completo de uma página baseado no tipo de conteúdo.
        """
        texto_extraido = ""
        
        # Estratégias específicas por tipo
        if tipo_conteudo == 'legislacao':
            texto_extraido = self._extrair_texto_legislacao(soup)
        elif tipo_conteudo == 'jurisprudencia':
            texto_extraido = self._extrair_texto_jurisprudencia(soup)
        elif tipo_conteudo == 'doutrina':
            texto_extraido = self._extrair_texto_doutrina(soup)
        
        # Fallback: extração geral
        if len(texto_extraido) < 200:
            texto_extraido = self._extrair_texto_geral(soup)
        
        return texto_extraido
    
    def _extrair_texto_legislacao(self, soup: BeautifulSoup) -> str:
        """
        Extrai texto específico de páginas de legislação.
        """
        texto = ""
        
        # Buscar por seletores específicos de legislação
        seletores_legislacao = [
            '.artigo', '.paragrafo', '.inciso', '.alinea',
            '[class*="artigo"]', '[class*="dispositivo"]',
            '.texto-lei', '.conteudo-lei', '.texto-norma'
        ]
        
        for seletor in seletores_legislacao:
            elementos = soup.select(seletor)
            for elemento in elementos:
                texto += elemento.get_text() + "\n\n"
        
        # Se não encontrou, buscar por padrões de artigos
        if len(texto) < 200:
            # Buscar por padrões "Art. X" ou "Artigo X"
            for p in soup.find_all(['p', 'div', 'span']):
                texto_p = p.get_text()
                if re.search(r'Art\.?\s*\d+|Artigo\s*\d+', texto_p):
                    texto += texto_p + "\n\n"
        
        return texto
    
    def _extrair_texto_jurisprudencia(self, soup: BeautifulSoup) -> str:
        """
        Extrai texto específico de páginas de jurisprudência.
        """
        texto = ""
        
        # Buscar por seletores específicos de jurisprudência
        seletores_jurisprudencia = [
            '.ementa', '.acordao', '.decisao', '.voto',
            '[class*="ementa"]', '[class*="acordao"]',
            '.texto-decisao', '.conteudo-acordao'
        ]
        
        for seletor in seletores_jurisprudencia:
            elementos = soup.select(seletor)
            for elemento in elementos:
                texto += elemento.get_text() + "\n\n"
        
        # Buscar por padrões de jurisprudência
        if len(texto) < 200:
            for p in soup.find_all(['p', 'div']):
                texto_p = p.get_text()
                if any(palavra in texto_p.lower() for palavra in ['ementa', 'acórdão', 'decisão', 'relatório']):
                    texto += texto_p + "\n\n"
        
        return texto
    
    def _extrair_texto_doutrina(self, soup: BeautifulSoup) -> str:
        """
        Extrai texto específico de páginas de doutrina.
        """
        texto = ""
        
        # Buscar por seletores específicos de artigos doutrinários
        seletores_doutrina = [
            '.artigo-conteudo', '.texto-artigo', '.conteudo-principal',
            '[class*="content"]', '[class*="article"]',
            '.post-content', '.entry-content'
        ]
        
        for seletor in seletores_doutrina:
            elementos = soup.select(seletor)
            for elemento in elementos:
                # Remover elementos indesejados
                for tag_indesejada in elemento.find_all(['script', 'style', 'nav', 'footer', 'header']):
                    tag_indesejada.decompose()
                
                texto += elemento.get_text() + "\n\n"
        
        return texto
    
    def _extrair_texto_geral(self, soup: BeautifulSoup) -> str:
        """
        Extração geral de texto quando métodos específicos falham.
        """
        # Remover elementos indesejados
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        # Buscar por conteúdo principal
        conteudo_principal = soup.find('main') or soup.find('article') or soup.find('body')
        
        if conteudo_principal:
            return conteudo_principal.get_text()
        else:
            return soup.get_text()
    
    def _extrair_titulo(self, soup: BeautifulSoup) -> str:
        """
        Extrai título da página.
        """
        titulo = soup.find('title')
        if titulo:
            return titulo.get_text().strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Título não encontrado"
    
    def _limpar_texto_completo(self, texto: str) -> str:
        """
        Limpa e formata texto extraído mantendo conteúdo completo.
        """
        if not texto:
            return ""
        
        # Remover caracteres especiais problemáticos
        texto = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\-\+\=\%\$\@\#\n]', ' ', texto)
        
        # Normalizar espaços
        texto = re.sub(r'\s+', ' ', texto)
        
        # Normalizar quebras de linha
        texto = re.sub(r'\n+', '\n', texto)
        
        # Remover linhas muito curtas (menos de 10 caracteres)
        linhas = texto.split('\n')
        linhas_filtradas = [linha.strip() for linha in linhas if len(linha.strip()) >= 10]
        
        return '\n'.join(linhas_filtradas).strip()
    
    def _identificar_area_direito(self, fundamentos: List[str], tipo_acao: str) -> str:
        """
        Identifica área do direito baseada nos fundamentos.
        """
        fundamentos_texto = ' '.join(fundamentos).lower()
        tipo_acao_lower = tipo_acao.lower()
        
        if any(palavra in fundamentos_texto or palavra in tipo_acao_lower 
               for palavra in ['trabalho', 'trabalhista', 'clt', 'emprego']):
            return 'trabalhista'
        elif any(palavra in fundamentos_texto or palavra in tipo_acao_lower 
                 for palavra in ['consumidor', 'cdc', 'fornecedor']):
            return 'consumidor'
        elif any(palavra in fundamentos_texto or palavra in tipo_acao_lower 
                 for palavra in ['civil', 'contrato', 'responsabilidade']):
            return 'civil'
        else:
            return 'geral'
    
    def _compilar_resultados_completos(self, resultados: Dict[str, List], area_direito: str) -> Dict[str, Any]:
        """
        Compila resultados completos da pesquisa.
        """
        # Contar totais
        total_legislacao = len(resultados['legislacao'])
        total_jurisprudencia = len(resultados['jurisprudencia'])
        total_doutrina = len(resultados['doutrina'])
        total_sites = total_legislacao + total_jurisprudencia + total_doutrina
        
        # Compilar todos os conteúdos
        todos_conteudos = []
        todos_conteudos.extend(resultados['legislacao'])
        todos_conteudos.extend(resultados['jurisprudencia'])
        todos_conteudos.extend(resultados['doutrina'])
        
        # Gerar textos formatados completos
        legislacao_formatada = self._formatar_legislacao_completa(resultados['legislacao'])
        jurisprudencia_formatada = self._formatar_jurisprudencia_completa(resultados['jurisprudencia'])
        doutrina_formatada = self._formatar_doutrina_completa(resultados['doutrina'])
        
        print(f"🌐 Total de sites acessados: {total_sites}")
        print(f"📄 Total de conteúdos extraídos: {len(todos_conteudos)}")
        
        return {
            "status": "sucesso",
            "area_direito": area_direito,
            "legislacao_formatada": legislacao_formatada,
            "jurisprudencia_formatada": jurisprudencia_formatada,
            "doutrina_formatada": doutrina_formatada,
            "conteudos_extraidos": todos_conteudos,
            "sites_acessados": [conteudo['url'] for conteudo in todos_conteudos],
            "estatisticas": {
                "total_sites_acessados": total_sites,
                "total_conteudos_extraidos": len(todos_conteudos),
                "legislacao_encontrada": total_legislacao,
                "jurisprudencia_encontrada": total_jurisprudencia,
                "doutrina_encontrada": total_doutrina,
                "caracteres_totais_extraidos": sum(conteudo['tamanho'] for conteudo in todos_conteudos)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _formatar_legislacao_completa(self, legislacao: List[Dict[str, Any]]) -> str:
        """
        Formata legislação com conteúdo completo.
        """
        if not legislacao:
            return "Legislação específica não encontrada nas pesquisas realizadas."
        
        texto_formatado = "LEGISLAÇÃO APLICÁVEL (CONTEÚDO COMPLETO):\n\n"
        
        for i, item in enumerate(legislacao, 1):
            texto_formatado += f"DISPOSITIVO LEGAL {i}:\n"
            texto_formatado += f"Fonte: {item['titulo']}\n"
            texto_formatado += f"Conteúdo Integral:\n{item['texto']}\n"
            texto_formatado += "-" * 80 + "\n\n"
        
        return texto_formatado
    
    def _formatar_jurisprudencia_completa(self, jurisprudencia: List[Dict[str, Any]]) -> str:
        """
        Formata jurisprudência com conteúdo completo.
        """
        if not jurisprudencia:
            return "Jurisprudência específica não encontrada nas pesquisas realizadas."
        
        texto_formatado = "JURISPRUDÊNCIA DOS TRIBUNAIS SUPERIORES (CONTEÚDO COMPLETO):\n\n"
        
        for i, item in enumerate(jurisprudencia, 1):
            texto_formatado += f"PRECEDENTE JUDICIAL {i}:\n"
            texto_formatado += f"Tribunal: {item['titulo']}\n"
            texto_formatado += f"Decisão Completa:\n{item['texto']}\n"
            texto_formatado += "-" * 80 + "\n\n"
        
        return texto_formatado
    
    def _formatar_doutrina_completa(self, doutrina: List[Dict[str, Any]]) -> str:
        """
        Formata doutrina com conteúdo completo.
        """
        if not doutrina:
            return "Doutrina específica não encontrada nas pesquisas realizadas."
        
        texto_formatado = "DOUTRINA ESPECIALIZADA (CONTEÚDO COMPLETO):\n\n"
        
        for i, item in enumerate(doutrina, 1):
            texto_formatado += f"ANÁLISE DOUTRINÁRIA {i}:\n"
            texto_formatado += f"Fonte: {item['titulo']}\n"
            texto_formatado += f"Conteúdo Integral:\n{item['texto']}\n"
            texto_formatado += "-" * 80 + "\n\n"
        
        return texto_formatado
    
    def _gerar_resultado_fallback(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """
        Gera resultado fallback quando pesquisa falha.
        """
        return {
            "status": "fallback",
            "area_direito": "geral",
            "legislacao_formatada": "Legislação aplicável não pôde ser pesquisada no momento.",
            "jurisprudencia_formatada": "Jurisprudência aplicável não pôde ser pesquisada no momento.",
            "doutrina_formatada": "Doutrina aplicável não pôde ser pesquisada no momento.",
            "conteudos_extraidos": [],
            "sites_acessados": [],
            "estatisticas": {
                "total_sites_acessados": 0,
                "total_conteudos_extraidos": 0,
                "legislacao_encontrada": 0,
                "jurisprudencia_encontrada": 0,
                "doutrina_encontrada": 0,
                "caracteres_totais_extraidos": 0
            },
            "timestamp": datetime.now().isoformat()
        }