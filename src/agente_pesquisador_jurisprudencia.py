# agente_pesquisador_jurisprudencia.py - v5.0 (funcional)
import asyncio
import aiohttp
import re
import openai
import os
import random
from datetime import datetime
from typing import Dict, Any, List
from googlesearch import search
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class AgentePesquisadorJurisprudencia:
    """
    Agente Especializado em Pesquisa de Jurisprudência.
    v5.0: Busca URLs de acórdãos reais, extrai texto completo e valida com IA.
    """
    def __init__(self, api_key: str = None):
        print("⚖️  Inicializando Agente de Pesquisa de JURISPRUDÊNCIA (v5.0)...")
        
        if not api_key:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        
        if not api_key:
            raise ValueError("A chave da API da DeepSeek é necessária e não foi encontrada.")
        
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        ]
        
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        self.config = {
            'tamanho_minimo_conteudo': 200,  # Conteúdo mínimo para considerar relevante
            'min_sucessos_por_termo': 5,
            'google_search_results': 50,      # Lista inicial de URLs
            'timeout_geral_pesquisa': 120,
        }
        
        self.sites_prioritarios = [
            'stj.jus.br', 
            'stf.jus.br', 
            'tst.jus.br', 
            'jusbrasil.com.br',
            'conjur.com.br', 
            'migalhas.com.br', 
            'ambito-juridico.com.br'
        ]
        
        print("✅ Sistema de pesquisa de JURISPRUDÊNCIA inicializado.")

    async def _validar_relevancia_com_ia_async(self, texto: str, termo_pesquisa: str) -> bool:
        """Usa IA para validar se o conteúdo extraído é relevante."""
        try:
            prompt = f"""
            Analise o seguinte texto e determine se ele é uma JURISPRUDÊNCIA (decisão judicial, acórdão, ementa) relevante para o termo de pesquisa "{termo_pesquisa}".
            Responda APENAS com "SIM" se for relevante, ou "NÃO" caso contrário.

            TEXTO:
            ---
            {texto[:2000]}
            ---
            """
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.0
            )
            resposta = response.choices[0].message.content.strip().upper()
            return "SIM" in resposta
        except Exception as e:
            print(f"⚠️ Erro na validação com IA: {e}")
            return False

    async def _extrair_texto_async(self, session, url: str, termo_pesquisa: str) -> Dict[str, Any]:
        """Extrai o conteúdo completo de uma URL e valida com IA."""
        print(f"→ Extraindo: {url}")
        try:
            headers = self.headers.copy()
            headers['User-Agent'] = random.choice(self.user_agents)

            async with session.get(url, headers=headers, timeout=30, ssl=False) as response:
                if response.status != 200:
                    print(f"❌ Falha (Status {response.status}): {url}")
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove elementos irrelevantes
                for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    tag.decompose()
                
                texto = soup.get_text(separator=' ', strip=True)
                texto = re.sub(r'\s+', ' ', texto).strip()
                
                if len(texto) < self.config['tamanho_minimo_conteudo']:
                    print(f"⚠️ Descartado (curto): {url}")
                    return None

                # Valida relevância com IA
                if await self._validar_relevancia_com_ia_async(texto, termo_pesquisa):
                    print(f"✔ SUCESSO: {url} ({len(texto)} caracteres)")
                    return {"url": url, "titulo": soup.title.string.strip() if soup.title else "N/A", "texto": texto}
                else:
                    print(f"⚠️ Descartado (IA reprovou): {url}")
                    return None

        except Exception as e:
            print(f"❌ Erro ao extrair {url}: {type(e).__name__}")
            return None

    async def _pesquisar_termo_async(self, termo: str) -> List[Dict[str, Any]]:
        """Busca URLs reais de acórdãos e extrai conteúdo."""
        print(f"\n📚 Pesquisando jurisprudência para: '{termo}'")
        resultados = []
        urls_vistas = set()
        loop = asyncio.get_event_loop()

        # Monta query Google
        dominios_query = " OR ".join([f"site:{site}" for site in self.sites_prioritarios])
        query = f'"{termo}" acórdão jurisprudência ementa {dominios_query}'

        urls_encontradas = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config['google_search_results'], lang="pt")))
        urls_filtradas = [url for url in urls_encontradas if url not in urls_vistas and "/busca?" not in url]
        urls_vistas.update(urls_filtradas)

        async with aiohttp.ClientSession() as session:
            tasks = [self._extrair_texto_async(session, url, termo) for url in urls_filtradas]
            resultados_tasks = await asyncio.gather(*tasks)

        resultados = [res for res in resultados_tasks if res][:self.config['min_sucessos_por_termo']]
        print(f"🎯 Pesquisa concluída para '{termo}' com {len(resultados)} resultados válidos.\n")
        return resultados

    async def pesquisar_jurisprudencia_async(self, termos: List[str]) -> List[Dict[str, Any]]:
        tasks = [self._pesquisar_termo_async(termo) for termo in termos]
        resultados_por_termo = await asyncio.gather(*tasks)
        return [item for sublist in resultados_por_termo for item in sublist]

    def pesquisar(self, termos: List[str]) -> List[Dict[str, Any]]:
        inicio = datetime.now()
        try:
            resultados = asyncio.run(self.pesquisar_jurisprudencia_async(termos))
        except Exception as e:
            print(f"❌ Erro crítico na pesquisa: {e}")
            return []

        tempo_total = (datetime.now() - inicio).total_seconds()
        print(f"✅ Total de {len(resultados)} conteúdos encontrados.")
        print(f"✅ Pesquisa concluída em {tempo_total:.1f}s\n")
        return resultados

# ==========================
# Exemplo de uso
# ==========================
if __name__ == "__main__":
    agente = AgentePesquisadorJurisprudencia()
    resultados = agente.pesquisar(["dano moral"])
    for res in resultados:
        print(f"\nTítulo: {res['titulo']}")
        print(f"URL: {res['url']}")
        print(f"Texto (primeiros 500 chars): {res['texto'][:500]}...\n")
