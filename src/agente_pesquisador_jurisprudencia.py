# agente_pesquisador_jurisprudencia.py - v2.1 (Com Pesquisa Aprofundada)

import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Dict, Any, List
from googlesearch import search
from bs4 import BeautifulSoup

class AgentePesquisadorJurisprudencia:
    """
    Agente Especializado em Pesquisa de Jurisprudência.
    v2.1: Realiza uma pesquisa mais aprofundada, buscando garantir no mínimo 10 resultados positivos.
    """
    def __init__(self):
        print("⚖️  Inicializando Agente de Pesquisa de JURISPRUDÊNCIA (v2.1)...")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        # COMENTÁRIO: As configurações foram ajustadas para uma pesquisa mais aprofundada.
        # A meta de sucessos foi aumentada para 10 e, para suportar isso,
        # o número de resultados do Google também foi aumentado.
        self.config = {
            'tamanho_minimo_conteudo': 500,
            'min_sucessos_por_termo': 10,
            'google_search_results': 20,
        }
        self.sites_prioritarios = ['stj.jus.br', 'stf.jus.br', 'tst.jus.br', 'conjur.com.br', 'migalhas.com.br']
        print("✅ Sistema de pesquisa de JURISPRUDÊNCIA inicializado.")

    async def _extrair_conteudo_url_async(self, session, url: str) -> Dict[str, Any]:
        """Extrai conteúdo de uma URL de forma assíncrona."""
        print(f"→ Tentando extrair de: {url}")
        try:
            async with session.get(url, headers=self.headers, timeout=15, ssl=False) as response:
                if response.status == 200:
                    raw_html = await response.read()
                    html = raw_html.decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                        tag.decompose()
                    
                    texto = soup.body.get_text(separator=' ', strip=True) if soup.body else ""
                    texto_limpo = re.sub(r'\s+', ' ', texto).strip()
                    
                    if len(texto_limpo) < self.config['tamanho_minimo_conteudo']:
                        print(f"⚠️ Descartado (curto): {url}")
                        return None

                    print(f"✔ SUCESSO: Conteúdo extraído de {url} ({len(texto_limpo)} caracteres)")
                    return { "url": url, "texto": texto_limpo, "titulo": soup.title.string.strip() if soup.title else "N/A" }
                else:
                    print(f"❌ Falha (Status {response.status}): {url}")
                    return None
        except Exception as e:
            print(f"❌ Falha (Erro: {type(e).__name__}): {url}")
            return None

    async def _pesquisar_termo_async(self, termo: str) -> List[Dict[str, Any]]:
        """Busca um único termo e extrai o conteúdo até atingir a meta."""
        print(f"\n📚 Buscando jurisprudência para o termo: '{termo}'...")
        site_query = " OR ".join([f"site:{site}" for site in self.sites_prioritarios])
        query = f'jurisprudência ementa acórdão sobre "{termo}" {site_query}'
        
        resultados_sucesso = []
        try:
            loop = asyncio.get_event_loop()
            urls_google = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config['google_search_results'], lang="pt")))
            
            async with aiohttp.ClientSession() as session:
                for url in urls_google:
                    if len(resultados_sucesso) >= self.config['min_sucessos_por_termo']:
                        break
                    resultado = await self._extrair_conteudo_url_async(session, url)
                    if resultado:
                        resultados_sucesso.append(resultado)
            
            print(f"🎯 Pesquisa para '{termo}' concluída com {len(resultados_sucesso)} extrações bem-sucedidas.")
            return resultados_sucesso
        except Exception as e:
            print(f"⚠️ Falha crítica na busca do Google para '{termo}': {e}")
            return resultados_sucesso

    async def pesquisar_jurisprudencia_async(self, termos: List[str]) -> List[Dict[str, Any]]:
        """Cria e executa todas as tarefas de pesquisa em paralelo."""
        tasks = [self._pesquisar_termo_async(termo) for termo in termos]
        resultados_por_termo = await asyncio.gather(*tasks)
        
        todos_os_resultados = [item for sublist in resultados_por_termo for item in sublist]
        return todos_os_resultados

    def pesquisar(self, termos: List[str]) -> List[Dict[str, Any]]:
        """Ponto de entrada síncrono que executa a lógica assíncrona."""
        inicio_pesquisa = datetime.now()
        try:
            resultado = asyncio.run(self.pesquisar_jurisprudencia_async(termos))
        except Exception as e:
            print(f"❌ Erro crítico durante a pesquisa de jurisprudência: {e}")
            return []
        
        tempo_total = (datetime.now() - inicio_pesquisa).total_seconds()
        print(f"\n--- RESUMO DA PESQUISA DE JURISPRUDÊNCIA ---")
        print(f"✅ Total de {len(resultado)} conteúdos relevantes encontrados.")
        print(f"✅ PESQUISA CONCLUÍDA em {tempo_total:.1f} segundos\n")
        return resultado
