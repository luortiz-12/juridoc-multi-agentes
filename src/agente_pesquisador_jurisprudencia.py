# agente_pesquisador_jurisprudencia.py - v3.5 (Com Pesquisa via Google Search)

import asyncio
import aiohttp
import re
import openai
import os
from datetime import datetime
from typing import Dict, Any, List
# COMENTÁRIO: A biblioteca foi trocada para 'googlesearch', conforme solicitado.
from googlesearch import search
from bs4 import BeautifulSoup

class AgentePesquisadorJurisprudencia:
    """
    Agente Especializado em Pesquisa de Jurisprudência.
    v3.5: Utiliza o Google Search para a busca, alinhado com os outros agentes de pesquisa.
    """
    def __init__(self, api_key: str = None):
        print("⚖️  Inicializando Agente de Pesquisa de JURISPRUDÊNCIA (v3.5 com Google Search)...")
        
        if not api_key:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        
        if not api_key:
            raise ValueError("A chave da API da DeepSeek é necessária para o filtro de relevância e não foi encontrada.")
        
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        self.config = {
            'tamanho_minimo_conteudo': 500,
            'min_sucessos_por_termo': 10,
            'search_results_per_request': 25,
        }
        self.sites_prioritarios = ['conjur.com.br', 'migalhas.com.br', 'stj.jus.br', 'stf.jus.br', 'tst.jus.br', 'ambito-juridico.com.br']
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
        print(f"\n📚 Buscando jurisprudência para o termo: '{termo}'...")
        site_query = " OR ".join([f"site:{site}" for site in self.sites_prioritarios])
        query = f'jurisprudência ementa acórdão sobre "{termo}" {site_query}'
        
        resultados_sucesso = []
        try:
            # COMENTÁRIO: A busca agora é feita com a biblioteca 'googlesearch'.
            loop = asyncio.get_event_loop()
            urls_encontradas = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config['search_results_per_request'], lang="pt")))
            
            async with aiohttp.ClientSession() as session:
                for url in urls_encontradas:
                    if len(resultados_sucesso) >= self.config['min_sucessos_por_termo']:
                        break
                    resultado = await self._extrair_e_validar_async(session, url, termo)
                    if resultado:
                        resultados_sucesso.append(resultado)
            
            print(f"🎯 Pesquisa para '{termo}' concluída com {len(resultados_sucesso)} extrações bem-sucedidas.")
            return resultados_sucesso
        except Exception as e:
            print(f"⚠️ Falha crítica na busca para '{termo}': {e}")
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
