# agente_pesquisa_contratos.py - Agente de Pesquisa Especializado em Contratos com Logs Aprimorados

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
    v2.0: Logs detalhados para cada etapa da extração de conteúdo.
    """
    def __init__(self):
        print("🔍 Inicializando Agente de Pesquisa de CONTRATOS (Logs Aprimorados)...")
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        self.sites_prioritarios = ['jusbrasil.com.br', 'conjur.com.br', 'migalhas.com.br', 'planalto.gov.br']
        self.config = {'tamanho_minimo_conteudo': 500, 'tamanho_maximo_conteudo': 20000, 'max_sites_por_query': 3}
        print("✅ Sistema de pesquisa de CONTRATOS inicializado.")

    async def _extrair_conteudo_url_async(self, session, url: str) -> Dict[str, Any]:
        """Extrai conteúdo de uma URL de forma assíncrona com logs detalhados."""
        # COMENTÁRIO: Adicionado log para cada tentativa de acesso.
        print(f"🌐 Acessando URL: {url}")
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
                    
                    # COMENTÁRIO: Adicionado log específico para conteúdo descartado por ser muito curto.
                    if len(texto_limpo) < self.config['tamanho_minimo_conteudo']:
                        print(f"⚠️ Conteúdo descartado de {url}: muito curto ({len(texto_limpo)} caracteres)")
                        return None
                    
                    print(f"📄 Conteúdo de contrato extraído de: {url} ({len(texto_limpo)} caracteres)")
                    return {"url": url, "texto": texto_limpo[:self.config['tamanho_maximo_conteudo']]}
                else:
                    # COMENTÁRIO: Log de erro mais específico para falhas de acesso HTTP.
                    print(f"❌ Erro ao acessar {url}: Status {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Erro ao extrair conteúdo de contrato de {url}: {type(e).__name__} - {e}")
            return None

    async def _pesquisar_e_extrair_async(self, termo: str) -> List[Dict[str, Any]]:
        print(f"📚 Buscando modelos e cláusulas para: '{termo}'...")
        site_query = " OR ".join([f"site:{site}" for site in self.sites_prioritarios])
        query = f'"{termo}" {site_query}'
        try:
            loop = asyncio.get_event_loop()
            urls = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config['max_sites_por_query'], lang="pt")))
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
        
        # COMENTÁRIO: Log de resumo final mais detalhado.
        print("\n--- RESUMO DA PESQUISA DE CONTRATOS ---")
        print(f"Fundamentos pesquisados: {fundamentos}")
        conteudos_encontrados = resultado.get("conteudos_extraidos", [])
        if conteudos_encontrados:
            print(f"✅ {len(conteudos_encontrados)} modelos/conteúdos relevantes encontrados.")
            for i, item in enumerate(conteudos_encontrados, 1):
                print(f"  {i}. {item['url']} ({len(item['texto'])} chars)")
        else:
            print("⚠️ Nenhum modelo ou conteúdo relevante foi extraído com sucesso.")
        print(f"✅ PESQUISA DE CONTRATOS CONCLUÍDA em {tempo_total:.1f} segundos\n")
        
        return resultado