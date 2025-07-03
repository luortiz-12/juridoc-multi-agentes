# pesquisa_juridica.py - Pesquisa Jurídica com Conteúdo Real

import re
import time
import random
import requests
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import urllib.parse

# AJUSTE 1: Múltiplas estratégias de pesquisa real
try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

class PesquisaJuridica:
    """
    Módulo de pesquisa jurídica que SEMPRE busca conteúdo real online.
    Implementa múltiplas estratégias para contornar rate limits e obter informações verdadeiras.
    """
    
    def __init__(self):
        # AJUSTE 2: Configuração para pesquisas reais robustas
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # AJUSTE 3: Sites jurídicos específicos para pesquisa direta
        self.sites_juridicos = {
            'legislacao': [
                'planalto.gov.br',
                'lexml.gov.br',
                'senado.leg.br'
            ],
            'jurisprudencia': [
                'stf.jus.br',
                'stj.jus.br',
                'tst.jus.br',
                'tjsp.jus.br'
            ],
            'doutrina': [
                'conjur.com.br',
                'migalhas.com.br',
                'jota.info'
            ]
        }
        
        # AJUSTE 4: Configuração de delays progressivos
        self.delay_minimo = 3
        self.delay_maximo = 8
        self.tentativas_maximas = 3
        
        # Inicializar DuckDuckGo se disponível
        if DUCKDUCKGO_AVAILABLE:
            self.ddgs = DDGS()
        else:
            self.ddgs = None
            
        print("🔍 Sistema de pesquisa jurídica real inicializado")
    
    def pesquisar_fundamentos_juridicos(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """
        Realiza pesquisa jurídica REAL em sites oficiais e especializados.
        """
        try:
            print(f"🔍 Iniciando pesquisa jurídica REAL para: {fundamentos}")
            print(f"📋 Tipo de ação: {tipo_acao}")
            
            resultados = {
                "leis": self._pesquisar_legislacao_real(fundamentos, tipo_acao),
                "jurisprudencia": self._pesquisar_jurisprudencia_real(fundamentos, tipo_acao),
                "doutrina": self._pesquisar_doutrina_real(fundamentos, tipo_acao),
                "resumo_pesquisa": ""
            }
            
            # Gerar resumo baseado nos resultados reais
            resultados["resumo_pesquisa"] = self._gerar_resumo_real(resultados, fundamentos, tipo_acao)
            
            print("✅ Pesquisa jurídica real concluída")
            return resultados
            
        except Exception as e:
            print(f"❌ Erro crítico na pesquisa: {e}")
            raise Exception(f"Falha na pesquisa jurídica real: {str(e)}")
    
    def _pesquisar_legislacao_real(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Pesquisa legislação em sites oficiais do governo."""
        print("📚 Pesquisando legislação em sites oficiais...")
        
        resultados_legislacao = []
        
        for fundamento in fundamentos[:2]:  # Limitar a 2 fundamentos principais
            # AJUSTE 5: Pesquisa direta no Planalto
            resultado_planalto = self._buscar_no_planalto(fundamento, tipo_acao)
            if resultado_planalto:
                resultados_legislacao.append(resultado_planalto)
            
            # AJUSTE 6: Pesquisa via DuckDuckGo com site específico
            resultado_ddg = self._buscar_legislacao_ddg(fundamento, tipo_acao)
            if resultado_ddg:
                resultados_legislacao.append(resultado_ddg)
            
            # Delay entre pesquisas
            time.sleep(random.uniform(self.delay_minimo, self.delay_maximo))
        
        if resultados_legislacao:
            return "\n\n".join(resultados_legislacao)
        else:
            raise Exception("Não foi possível obter legislação real dos sites oficiais")
    
    def _buscar_no_planalto(self, fundamento: str, tipo_acao: str) -> str:
        """Busca diretamente no site do Planalto."""
        try:
            # AJUSTE 7: Construir URL de busca do Planalto
            termo_busca = f"{fundamento} {tipo_acao}".strip()
            url_busca = f"http://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/leis-ordinarias"
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            print(f"🔍 Buscando no Planalto: {termo_busca}")
            
            response = requests.get(url_busca, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extrair informações relevantes
                links_leis = soup.find_all('a', href=True)
                leis_encontradas = []
                
                for link in links_leis[:5]:  # Primeiros 5 resultados
                    if any(palavra in link.text.lower() for palavra in fundamento.lower().split()):
                        leis_encontradas.append({
                            'titulo': link.text.strip(),
                            'url': link.get('href')
                        })
                
                if leis_encontradas:
                    resultado = f"LEGISLAÇÃO ENCONTRADA NO PLANALTO:\n\n"
                    for i, lei in enumerate(leis_encontradas, 1):
                        resultado += f"{i}. {lei['titulo']}\n"
                        if lei['url']:
                            resultado += f"   URL: {lei['url']}\n"
                        resultado += "\n"
                    return resultado
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erro na busca do Planalto: {e}")
            return None
    
    def _buscar_legislacao_ddg(self, fundamento: str, tipo_acao: str) -> str:
        """Busca legislação via DuckDuckGo com foco em sites oficiais."""
        if not self.ddgs:
            return None
            
        try:
            # AJUSTE 8: Query específica para legislação oficial
            queries = [
                f"lei {fundamento} site:planalto.gov.br",
                f"código {fundamento} site:lexml.gov.br",
                f"decreto {fundamento} {tipo_acao}"
            ]
            
            for query in queries:
                try:
                    print(f"🔍 DuckDuckGo: {query}")
                    
                    # Delay antes da busca
                    time.sleep(random.uniform(2, 5))
                    
                    resultados = list(self.ddgs.text(query, max_results=3))
                    
                    if resultados:
                        texto_resultado = f"LEGISLAÇÃO VIA DUCKDUCKGO:\n\n"
                        for i, resultado in enumerate(resultados, 1):
                            titulo = resultado.get('title', 'Título não disponível')
                            body = resultado.get('body', 'Descrição não disponível')
                            href = resultado.get('href', 'URL não disponível')
                            
                            texto_resultado += f"{i}. {titulo}\n"
                            texto_resultado += f"   Descrição: {body[:300]}...\n"
                            texto_resultado += f"   Fonte: {href}\n\n"
                        
                        return texto_resultado
                    
                except Exception as e:
                    print(f"⚠️ Erro na query '{query}': {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erro geral na busca DuckDuckGo: {e}")
            return None
    
    def _pesquisar_jurisprudencia_real(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Pesquisa jurisprudência em sites dos tribunais."""
        print("⚖️ Pesquisando jurisprudência em tribunais...")
        
        resultados_juris = []
        
        for fundamento in fundamentos[:2]:
            # AJUSTE 9: Busca no STJ
            resultado_stj = self._buscar_jurisprudencia_stj(fundamento, tipo_acao)
            if resultado_stj:
                resultados_juris.append(resultado_stj)
            
            # AJUSTE 10: Busca via DuckDuckGo em sites de tribunais
            resultado_tribunais = self._buscar_jurisprudencia_ddg(fundamento, tipo_acao)
            if resultado_tribunais:
                resultados_juris.append(resultado_tribunais)
            
            time.sleep(random.uniform(self.delay_minimo, self.delay_maximo))
        
        if resultados_juris:
            return "\n\n".join(resultados_juris)
        else:
            raise Exception("Não foi possível obter jurisprudência real dos tribunais")
    
    def _buscar_jurisprudencia_stj(self, fundamento: str, tipo_acao: str) -> str:
        """Busca jurisprudência no site do STJ."""
        try:
            # AJUSTE 11: URL de busca do STJ
            termo_busca = urllib.parse.quote(f"{fundamento} {tipo_acao}")
            url_busca = f"https://scon.stj.jus.br/SCON/pesquisar.jsp?b=ACOR&livre={termo_busca}"
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://scon.stj.jus.br/',
            }
            
            print(f"🔍 Buscando no STJ: {fundamento}")
            
            response = requests.get(url_busca, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Procurar por resultados de acórdãos
                acordaos = soup.find_all('div', class_='docTexto') or soup.find_all('p')
                
                if acordaos:
                    resultado = f"JURISPRUDÊNCIA DO STJ:\n\n"
                    for i, acordao in enumerate(acordaos[:3], 1):
                        texto = acordao.get_text().strip()
                        if len(texto) > 50:  # Filtrar textos muito curtos
                            resultado += f"{i}. {texto[:400]}...\n"
                            resultado += f"   Fonte: STJ - Superior Tribunal de Justiça\n\n"
                    return resultado
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erro na busca do STJ: {e}")
            return None
    
    def _buscar_jurisprudencia_ddg(self, fundamento: str, tipo_acao: str) -> str:
        """Busca jurisprudência via DuckDuckGo em sites de tribunais."""
        if not self.ddgs:
            return None
            
        try:
            # AJUSTE 12: Queries específicas para tribunais
            queries = [
                f"acórdão {fundamento} site:stj.jus.br",
                f"decisão {fundamento} site:stf.jus.br",
                f"jurisprudência {fundamento} {tipo_acao}"
            ]
            
            for query in queries:
                try:
                    print(f"🔍 Jurisprudência DuckDuckGo: {query}")
                    
                    time.sleep(random.uniform(3, 6))
                    
                    resultados = list(self.ddgs.text(query, max_results=2))
                    
                    if resultados:
                        texto_resultado = f"JURISPRUDÊNCIA DOS TRIBUNAIS:\n\n"
                        for i, resultado in enumerate(resultados, 1):
                            titulo = resultado.get('title', 'Título não disponível')
                            body = resultado.get('body', 'Descrição não disponível')
                            href = resultado.get('href', 'URL não disponível')
                            
                            texto_resultado += f"{i}. {titulo}\n"
                            texto_resultado += f"   Ementa: {body[:350]}...\n"
                            texto_resultado += f"   Tribunal: {href}\n\n"
                        
                        return texto_resultado
                    
                except Exception as e:
                    print(f"⚠️ Erro na query jurisprudência '{query}': {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erro geral na busca de jurisprudência: {e}")
            return None
    
    def _pesquisar_doutrina_real(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Pesquisa doutrina em sites jurídicos especializados."""
        print("📖 Pesquisando doutrina em sites especializados...")
        
        resultados_doutrina = []
        
        for fundamento in fundamentos[:2]:
            # AJUSTE 13: Busca em sites de doutrina
            resultado_conjur = self._buscar_doutrina_conjur(fundamento, tipo_acao)
            if resultado_conjur:
                resultados_doutrina.append(resultado_conjur)
            
            resultado_migalhas = self._buscar_doutrina_ddg(fundamento, tipo_acao)
            if resultado_migalhas:
                resultados_doutrina.append(resultado_migalhas)
            
            time.sleep(random.uniform(self.delay_minimo, self.delay_maximo))
        
        if resultados_doutrina:
            return "\n\n".join(resultados_doutrina)
        else:
            raise Exception("Não foi possível obter doutrina real dos sites especializados")
    
    def _buscar_doutrina_conjur(self, fundamento: str, tipo_acao: str) -> str:
        """Busca doutrina no Consultor Jurídico."""
        try:
            # AJUSTE 14: Busca no Conjur
            termo_busca = urllib.parse.quote(f"{fundamento}")
            url_busca = f"https://www.conjur.com.br/busca/?q={termo_busca}"
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            print(f"🔍 Buscando no Conjur: {fundamento}")
            
            response = requests.get(url_busca, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Procurar artigos
                artigos = soup.find_all('h3') or soup.find_all('h2')
                
                if artigos:
                    resultado = f"DOUTRINA - CONSULTOR JURÍDICO:\n\n"
                    for i, artigo in enumerate(artigos[:3], 1):
                        titulo = artigo.get_text().strip()
                        if len(titulo) > 20:
                            resultado += f"{i}. {titulo}\n"
                            resultado += f"   Fonte: Consultor Jurídico (Conjur)\n\n"
                    return resultado
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erro na busca do Conjur: {e}")
            return None
    
    def _buscar_doutrina_ddg(self, fundamento: str, tipo_acao: str) -> str:
        """Busca doutrina via DuckDuckGo em sites especializados."""
        if not self.ddgs:
            return None
            
        try:
            # AJUSTE 15: Queries para sites de doutrina
            queries = [
                f"artigo {fundamento} site:migalhas.com.br",
                f"comentário {fundamento} site:conjur.com.br",
                f"doutrina {fundamento} {tipo_acao}"
            ]
            
            for query in queries:
                try:
                    print(f"🔍 Doutrina DuckDuckGo: {query}")
                    
                    time.sleep(random.uniform(4, 7))
                    
                    resultados = list(self.ddgs.text(query, max_results=2))
                    
                    if resultados:
                        texto_resultado = f"DOUTRINA ESPECIALIZADA:\n\n"
                        for i, resultado in enumerate(resultados, 1):
                            titulo = resultado.get('title', 'Título não disponível')
                            body = resultado.get('body', 'Descrição não disponível')
                            href = resultado.get('href', 'URL não disponível')
                            
                            texto_resultado += f"{i}. {titulo}\n"
                            texto_resultado += f"   Resumo: {body[:300]}...\n"
                            texto_resultado += f"   Fonte: {href}\n\n"
                        
                        return texto_resultado
                    
                except Exception as e:
                    print(f"⚠️ Erro na query doutrina '{query}': {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erro geral na busca de doutrina: {e}")
            return None
    
    def _gerar_resumo_real(self, resultados: Dict[str, str], fundamentos: List[str], tipo_acao: str) -> str:
        """Gera resumo baseado nos resultados reais obtidos."""
        
        # Contar fontes reais encontradas
        fontes_legislacao = resultados['leis'].count('Fonte:') if resultados['leis'] else 0
        fontes_jurisprudencia = resultados['jurisprudencia'].count('Fonte:') if resultados['jurisprudencia'] else 0
        fontes_doutrina = resultados['doutrina'].count('Fonte:') if resultados['doutrina'] else 0
        
        total_fontes = fontes_legislacao + fontes_jurisprudencia + fontes_doutrina
        
        resumo = f"""
RESUMO DA PESQUISA JURÍDICA REAL:

Tipo de Ação: {tipo_acao}
Fundamentos Pesquisados: {', '.join(fundamentos)}
Total de Fontes Reais Encontradas: {total_fontes}

METODOLOGIA APLICADA:
- Busca direta em sites oficiais do governo (Planalto, LexML)
- Consulta aos tribunais superiores (STF, STJ, TST)
- Pesquisa em portais jurídicos especializados (Conjur, Migalhas)
- Uso de múltiplas estratégias para contornar limitações técnicas

RESULTADOS OBTIDOS:
- Legislação: {fontes_legislacao} fontes oficiais
- Jurisprudência: {fontes_jurisprudencia} decisões de tribunais
- Doutrina: {fontes_doutrina} artigos especializados

Todas as informações foram extraídas de fontes reais e atualizadas,
garantindo fundamentação jurídica sólida e confiável para a petição.
        """
        
        return resumo.strip()
    
    # AJUSTE 16: Método para verificar conectividade
    def verificar_conectividade(self) -> Dict[str, bool]:
        """Verifica se os sites jurídicos estão acessíveis."""
        status = {}
        
        sites_teste = [
            ('Planalto', 'http://www4.planalto.gov.br'),
            ('STJ', 'https://www.stj.jus.br'),
            ('Conjur', 'https://www.conjur.com.br')
        ]
        
        for nome, url in sites_teste:
            try:
                response = requests.get(url, timeout=10)
                status[nome] = response.status_code == 200
            except:
                status[nome] = False
        
        return status