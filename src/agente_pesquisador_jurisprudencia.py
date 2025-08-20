# agente_pesquisador_jurisprudencia.py - v3.8 (Com Pesquisa Obrigatória por Domínio)

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
    v3.8: Garante que a pesquisa seja tentada em todos os domínios prioritários
    e extrai o conteúdo completo dos artigos encontrados.
    """
    def __init__(self, api_key: str = None):
        print("⚖️  Inicializando Agente de Pesquisa de JURISPRUDÊNCIA (v3.8)...")
        
        if not api_key:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        
        if not api_key:
            raise ValueError("A chave da API da DeepSeek é necessária para o filtro de relevância e não foi encontrada.")
        
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.config = {
            'tamanho_minimo_conteudo': 500,
            # COMENTÁRIO: A pesquisa agora busca 3 resultados por domínio, tornando a busca mais distribuída.
            'search_results_per_domain': 3,
        }
        self.sites_prioritarios = ['stj.jus.br', 'stf.jus.br', 'tst.jus.br', 'conjur.com.br', 'migalhas.com.br', 'ambito-juridico.com.br']
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
        print(f"→ Tentando extrair de: {url}")
        try:
            request_headers = self.headers.copy()
            request_headers['User-Agent'] = random.choice(self.user_agents)
            request_headers['Referer'] = 'https://www.google.com/'

            async with session.get(url, headers=request_headers, timeout=15, ssl=False) as response:
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
                        # COMENTÁRIO: Retorna o 'texto_limpo' completo, sem limitar o tamanho.
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

    async def _pesquisar_dominio_async(self, session, termo: str, dominio: str) -> List[Dict[str, Any]]:
        """Pesquisa um termo específico dentro de um único domínio."""
        query = f'jurisprudência ementa acórdão sobre "{termo}" site:{dominio}'
        resultados_sucesso = []
        try:
            loop = asyncio.get_event_loop()
            urls_encontradas = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config['search_results_per_domain'], lang="pt")))
            
            tasks = [self._extrair_e_validar_async(session, url, termo) for url in urls_encontradas]
            resultados_tasks = await asyncio.gather(*tasks)
            
            resultados_sucesso = [res for res in resultados_tasks if res]
            return resultados_sucesso
        except Exception as e:
            print(f"⚠️ Falha crítica na busca do Google para o domínio {dominio}: {e}")
            return []

    async def _pesquisar_termo_async(self, termo: str) -> List[Dict[str, Any]]:
        """
        COMENTÁRIO: A lógica foi reescrita. Agora, ele cria uma tarefa de pesquisa para cada
        domínio prioritário e as executa em paralelo, garantindo que todos sejam tentados.
        """
        print(f"\n📚 Buscando jurisprudência para o termo: '{termo}' em todos os domínios prioritários...")
        
        async with aiohttp.ClientSession() as session:
            tasks = [self._pesquisar_dominio_async(session, termo, site) for site in self.sites_prioritarios]
            resultados_por_dominio = await asyncio.gather(*tasks)
        
        # Junta os resultados de todos os domínios em uma única lista
        todos_os_resultados = [item for sublist in resultados_por_dominio for item in sublist]
        
        print(f"🎯 Pesquisa para '{termo}' concluída com {len(todos_os_resultados)} extrações bem-sucedidas no total.")
        return todos_os_resultados

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
