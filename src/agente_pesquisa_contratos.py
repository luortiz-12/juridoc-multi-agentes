# agente_pesquisa_contratos.py - Versão 3.0 (Pesquisa Ampla e Aprofundada)

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
    v3.0: Realiza uma pesquisa ampla no Google, sem se restringir a sites pré-definidos,
    garantindo uma maior diversidade de fontes e resiliência a bloqueios.
    """
    def __init__(self):
        print("🔍 Inicializando Agente de Pesquisa de CONTRATOS (Pesquisa Ampla v3.0)...")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.config = {
            'tamanho_minimo_conteudo': 500,
            'tamanho_maximo_conteudo': 20000,
            'min_sucessos_por_termo': 4,
            'google_search_results': 10,
        }
        print("✅ Sistema de pesquisa de CONTRATOS inicializado.")

    async def _extrair_conteudo_url_async(self, session, url: str) -> Dict[str, Any]:
        """Extrai conteúdo de uma URL de forma assíncrona com logs detalhados."""
        print(f"→ Tentando extrair de: {url}")
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
                    
                    if len(texto_limpo) < self.config['tamanho_minimo_conteudo']:
                        print(f"⚠️ Descartado (curto): {url}")
                        return None

                    print(f"✔ SUCESSO: Conteúdo extraído de {url} ({len(texto_limpo)} caracteres)")
                    return {"url": url, "texto": texto_limpo[:self.config['tamanho_maximo_conteudo']]}
                else:
                    print(f"❌ Falha (Status {response.status}): {url}")
                    return None
        except Exception as e:
            print(f"❌ Falha (Erro: {type(e).__name__}): {url}")
            return None

    async def _pesquisar_e_extrair_async(self, termo: str) -> List[Dict[str, Any]]:
        """
        COMENTÁRIO: Lógica principal aprimorada. Agora ele busca mais links e tenta extrair
        até atingir a meta de sucessos, ignorando as falhas.
        """
        print(f"\n📚 Buscando modelos e cláusulas para: '{termo}'...")
        
        # COMENTÁRIO: A restrição "site:" foi removida para permitir uma pesquisa ampla no Google.
        # A query foi aprimorada para buscar por termos mais eficazes.
        query = f'"{termo}" completo para preencher'
        
        resultados_sucesso = []
        urls_tentadas = set()
        
        try:
            loop = asyncio.get_event_loop()
            urls_google = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config['google_search_results'], lang="pt")))
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for url in urls_google:
                    if url not in urls_tentadas:
                        urls_tentadas.add(url)
                        tasks.append(self._extrair_conteudo_url_async(session, url))
                
                resultados_tasks = await asyncio.gather(*tasks)
                
                resultados_sucesso = [res for res in resultados_tasks if res]

                # Limita ao número mínimo de sucessos desejado
                resultados_sucesso = resultados_sucesso[:self.config['min_sucessos_por_termo']]

            print(f"🎯 Pesquisa para '{termo}' concluída com {len(resultados_sucesso)} extrações bem-sucedidas.")
            return resultados_sucesso

        except Exception as e:
            print(f"⚠️ Falha crítica na busca do Google para '{termo}': {e}")
            return resultados_sucesso

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