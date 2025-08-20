# agente_pesquisador_jurisprudencia.py - v4.0 (Com Estratégia Anti-Bloqueio via Google Cache)

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
    v4.0: Utiliza o cache do Google para acessar o conteúdo das páginas,
    reduzindo drasticamente a probabilidade de ser bloqueado (erro 403).
    """
    def __init__(self, api_key: str = None):
        print("⚖️  Inicializando Agente de Pesquisa de JURISPRUDÊNCIA (v4.0)...")
        
        if not api_key:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        
        if not api_key:
            raise ValueError("A chave da API da DeepSeek é necessária para o filtro de relevância e não foi encontrada.")
        
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        ]
        
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.config = {
            'tamanho_minimo_conteudo': 500,
            'min_sucessos_por_termo': 4,
            'google_search_results': 20,
        }
        self.sites_prioritarios = ['stj.jus.br',
    'stf.jus.br',
    'tst.jus.br',
    'jusbrasil.com.br',   # ADICIONADO
    'conjur.com.br',
    'migalhas.com.br',
    'ambito-juridico.com.br',
    'ibdfam.org.br'
]
        print("✅ Sistema de pesquisa de JURISPRUDÊNCIA inicializado.")

    async def _validar_relevancia_com_ia_async(self, texto: str, termo_pesquisa: str) -> bool:
        """Usa a IA da DeepSeek para validar se o conteúdo extraído é relevante."""
        try:
            prompt = f"""
            Analise o seguinte texto e determine se ele é uma JURISPRUDÊNCIA (decisão judicial, acórdão, ementa) relevante para o termo de pesquisa "{termo_pesquisa}".
            Responda APENAS com "SIM" se for uma jurisprudência relevante, ou "NÃO" caso contrário.

            TEXTO PARA ANÁLISE:
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

    async def _extrair_e_validar_async(self, session, url: str, termo_pesquisa: str) -> Dict[str, Any]:
        """Extrai o conteúdo de uma URL e depois valida sua relevância com a IA."""
        
        # COMENTÁRIO: Esta é a nova estratégia anti-bloqueio.
        # Em vez de acessar a URL diretamente, acessamos a versão em cache do Google.
        cached_url = f"http://webcache.googleusercontent.com/search?q=cache:{url}"
        
        print(f"→ Tentando extrair de (via cache): {url}")
        try:
            request_headers = self.headers.copy()
            request_headers['User-Agent'] = random.choice(self.user_agents)

            async with session.get(cached_url, headers=request_headers, timeout=20, ssl=False) as response:
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

                    print(f"  -> Validando relevância do conteúdo com IA...")
                    if await self._validar_relevancia_com_ia_async(texto_limpo, termo_pesquisa):
                        print(f"✔ SUCESSO (IA APROVOU): Conteúdo extraído de {url} ({len(texto_limpo)} caracteres)")
                        return { "url": url, "texto": texto_limpo, "titulo": soup.title.string.strip() if soup.title else "N/A" }
                    else:
                        print(f"⚠️ Descartado (IA Reprovou como irrelevante): {url}")
                        return None
                else:
                    print(f"❌ Falha (Status {response.status}): {url}")
                    return None
        except Exception as e:
            print(f"❌ Falha (Erro: {type(e).__name__}): {url}")
            return None

    async def _pesquisar_termo_async(self, termo: str) -> List[Dict[str, Any]]:
        """Busca um único termo e extrai o conteúdo até atingir a meta."""
        print(f"\n📚 Buscando jurisprudência para o termo: '{termo}' em todos os domínios (query única)...")
        
        dominios_query = " OR ".join([f"site:{site}" for site in self.sites_prioritarios])
        query = f'"{termo}" jurisprudência ementa acórdão {dominios_query}'
        
        resultados_sucesso = []
        try:
            loop = asyncio.get_event_loop()
            num_results_to_fetch = self.config['min_sucessos_por_termo'] * 2
            urls_encontradas = await loop.run_in_executor(None, lambda: list(search(query, num_results=num_results_to_fetch, lang="pt")))
            
            async with aiohttp.ClientSession() as session:
                tasks = [self._extrair_e_validar_async(session, url, termo) for url in urls_encontradas]
                resultados_tasks = await asyncio.gather(*tasks)

            resultados_sucesso = [res for res in resultados_tasks if res][:self.config['min_sucessos_por_termo']]
            
            print(f"🎯 Pesquisa para '{termo}' concluiu com {len(resultados_sucesso)} extrações bem-sucedidas.")
            return resultados_sucesso

        except Exception as e:
            print(f"⚠️ Falha crítica na busca do Google: {e}")
            return []

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
