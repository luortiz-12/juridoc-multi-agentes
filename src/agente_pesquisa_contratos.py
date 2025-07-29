# agente_pesquisa_contratos.py - Agente de Pesquisa Especializado em Contratos

import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Dict, Any, List
from googlesearch import search
from bs4 import BeautifulSoup

class AgentePesquisaContratos:
    """
    Agente de Pesquisa Otimizado e Especializado em encontrar modelos e cláusulas de contratos.
    """
    def __init__(self):
        print("🔍 Inicializando Agente de Pesquisa de CONTRATOS...")
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        # COMENTÁRIO: Sites prioritários focados em modelos de documentos e legislação.
        self.sites_prioritarios = ['jusbrasil.com.br', 'conjur.com.br', 'migalhas.com.br', 'planalto.gov.br']
        print("✅ Sistema de pesquisa de CONTRATOS inicializado.")

    async def _extrair_conteudo_url_async(self, session, url: str) -> Dict[str, Any]:
        try:
            async with session.get(url, headers=self.headers, timeout=15, ssl=False) as response:
                if response.status == 200:
                    raw_html = await response.read()
                    html = raw_html.decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                        tag.decompose()
                    texto = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
                    texto_limpo = re.sub(r'\n\s*\n', '\n', texto).strip()
                    if len(texto_limpo) > 500:
                        print(f"📄 Conteúdo de contrato extraído de: {url} ({len(texto_limpo)} caracteres)")
                        return {"url": url, "texto": texto_limpo[:20000]}
                return None
        except Exception as e:
            print(f"❌ Erro ao extrair conteúdo de contrato de {url}: {e}")
            return None

    async def _pesquisar_e_extrair_async(self, termo: str) -> List[Dict[str, Any]]:
        print(f"📚 Buscando modelos e cláusulas para: '{termo}'...")
        site_query = " OR ".join([f"site:{site}" for site in self.sites_prioritarios])
        query = f'"{termo}" {site_query}'
        try:
            loop = asyncio.get_event_loop()
            urls = await loop.run_in_executor(None, lambda: list(search(query, num_results=3, lang="pt")))
        except Exception as e:
            print(f"⚠️ Falha na busca do Google para '{termo}': {e}")
            return []

        async with aiohttp.ClientSession() as session:
            tasks = [self._extrair_conteudo_url_async(session, url) for url in urls]
            resultados = await asyncio.gather(*tasks)
            return [res for res in resultados if res]

    async def pesquisar_modelos_async(self, fundamentos: List[str]) -> Dict[str, Any]:
        tasks = [self._pesquisar_e_extrair_async(fundamento) for fundamento in fundamentos]
        resultados_brutos = await asyncio.gather(*tasks)
        
        todos_conteudos = [item for sublist in resultados_brutos for item in sublist]
        
        # Formata a pesquisa para o Agente Redator
        pesquisa_formatada = "## Modelos e Cláusulas de Referência Encontrados:\n\n"
        for item in todos_conteudos:
            pesquisa_formatada += f"### Fonte: {item['url']}\n\n"
            pesquisa_formatada += f"```text\n{item['texto'][:2000]}...\n```\n\n---\n\n"
            
        return {"pesquisa_formatada": pesquisa_formatada, "conteudos_extraidos": todos_conteudos}

    def pesquisar_fundamentacao_completa(self, fundamentos: List[str], **kwargs) -> Dict[str, Any]:
        """Ponto de entrada síncrono que executa a lógica assíncrona."""
        inicio_pesquisa = datetime.now()
        try:
            resultado = asyncio.run(self.pesquisar_modelos_async(fundamentos))
        except Exception as e:
            print(f"❌ Erro crítico durante a pesquisa de contratos: {e}")
            return {"pesquisa_formatada": "A pesquisa de modelos de contrato falhou.", "conteudos_extraidos": []}
        tempo_total = (datetime.now() - inicio_pesquisa).total_seconds()
        print(f"✅ PESQUISA DE CONTRATOS CONCLUÍDA em {tempo_total:.1f} segundos")
        return resultado
