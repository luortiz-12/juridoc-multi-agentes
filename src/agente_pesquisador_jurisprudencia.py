# agente_pesquisador_jurisprudencia_v6.py
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
    v6.0: Melhorias em robustez, tratamento de erros e otimização de scraping e IA.
    """
    def __init__(self, api_key: str = None):
        print("⚖️  Inicializando Agente de Pesquisa de JURISPRUDÊNCIA (v6.0)...")
        
        if not api_key:
            api_key = os.getenv('DEEPSEEK_API_KEY')
        
        if not api_key:
            raise ValueError("A chave da API da DeepSeek é necessária e não foi encontrada.")
        
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
        ]
        
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
        }
        
        self.config = {
            'tamanho_minimo_conteudo': 200,  # Conteúdo mínimo para considerar relevante
            'min_sucessos_por_termo': 5,
            'google_search_results': 50,      # Lista inicial de URLs
            'timeout_geral_pesquisa': 120,
            'timeout_requisicao_http': 30, # Timeout para requisições HTTP individuais
            'max_retries': 3, # Número máximo de tentativas para requisições falhas
            'retry_delay': 2, # Atraso entre as tentativas (em segundos)
        }
        
        self.sites_prioritarios = [
            'stj.jus.br', 
            'stf.jus.br', 
            'tst.jus.br', 
            'jusbrasil.com.br',
            'conjur.com.br', 
            'migalhas.com.br', 
            'ambito-juridico.com.br',
            'tjmg.jus.br', # Exemplo de TJ
            'trf1.jus.br' # Exemplo de TRF
        ]
        
        print("✅ Sistema de pesquisa de JURISPRUDÊNCIA inicializado.")

    async def _validar_relevancia_com_ia_async(self, texto: str, termo_pesquisa: str) -> bool:
        """Usa IA para validar se o conteúdo extraído é relevante, com prompt otimizado."""
        try:
            prompt = f"""
            Você é um especialista em direito brasileiro com foco em jurisprudência. Analise o texto a seguir e determine se ele é um documento de jurisprudência (decisão judicial, acórdão, ementa, súmula) relevante para o termo de pesquisa "{termo_pesquisa}".
            Considere a presença de elementos como: ementa, relator, número do processo, data de julgamento, órgão julgador, fundamentação jurídica e dispositivo.
            Responda APENAS com "SIM" se o texto for claramente uma jurisprudência relevante para o termo, ou "NÃO" caso contrário. Não adicione nenhuma outra palavra ou explicação.

            TEXTO:
            ---
            {texto[:4000]} # Aumentado para 4000 caracteres para mais contexto
            ---
            """
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.0 # Temperatura baixa para respostas determinísticas
            )
            resposta = response.choices[0].message.content.strip().upper()
            return "SIM" in resposta
        except openai.APIError as e:
            print(f"⚠️ Erro da API DeepSeek na validação com IA: {e}")
            return False
        except Exception as e:
            print(f"⚠️ Erro inesperado na validação com IA: {type(e).__name__} - {e}")
            return False

    async def _extrair_texto_async(self, session, url: str, termo_pesquisa: str) -> Dict[str, Any]:
        """Extrai o conteúdo completo de uma URL e valida com IA, com retries e melhor scraping."""
        print(f"→ Extraindo: {url}")
        for attempt in range(self.config['max_retries']):
            try:
                headers = self.headers.copy()
                headers['User-Agent'] = random.choice(self.user_agents)

                async with session.get(url, headers=headers, timeout=self.config['timeout_requisicao_http'], ssl=False) as response:
                    if response.status != 200:
                        print(f"❌ Falha (Status {response.status}, Tentativa {attempt + 1}/{self.config['max_retries']}): {url}")
                        if response.status in [403, 404, 500]: # Não tentar novamente para erros irrecuperáveis
                            break
                        await asyncio.sleep(self.config['retry_delay']) # Esperar antes de tentar novamente
                        continue

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Melhoria no scraping: focar em tags de conteúdo principal
                    # Priorizar tags semânticas e de texto
                    content_tags = ['article', 'main', 'div', 'p', 'h1', 'h2', 'h3', 'span', 'li']
                    text_parts = []
                    for tag_name in content_tags:
                        for tag in soup.find_all(tag_name):
                            # Evitar tags dentro de elementos de navegação, rodapé, etc.
                            if not any(ancestor.name in ['nav', 'footer', 'header', 'aside'] for ancestor in tag.parents):
                                text_parts.append(tag.get_text(separator=' ', strip=True))
                    
                    texto = ' '.join(text_parts)
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

            except aiohttp.ClientError as e:
                print(f"❌ Erro de conexão ao extrair {url} (Tentativa {attempt + 1}/{self.config['max_retries']}): {type(e).__name__} - {e}")
                await asyncio.sleep(self.config['retry_delay']) # Esperar antes de tentar novamente
            except asyncio.TimeoutError:
                print(f"❌ Timeout ao extrair {url} (Tentativa {attempt + 1}/{self.config['max_retries']})")
                await asyncio.sleep(self.config['retry_delay']) # Esperar antes de tentar novamente
            except Exception as e:
                print(f"❌ Erro inesperado ao extrair {url}: {type(e).__name__} - {e}")
                break # Não tentar novamente para erros inesperados
        return None

    async def _pesquisar_termo_async(self, termo: str) -> List[Dict[str, Any]]:
        """Busca URLs reais de acórdãos e extrai conteúdo."""
        print(f"\n📚 Pesquisando jurisprudência para: '{termo}'")
        resultados = []
        urls_vistas = set()
        loop = asyncio.get_event_loop()

        # Monta query Google
        dominios_query = " OR ".join([f"site:{site}" for site in self.sites_prioritarios])
        query = f'"{termo}" acórdão jurisprudência {dominios_query}'
        try:
            urls_encontradas = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config["google_search_results"], lang="pt")))
        except Exception as e:
            print(f"❌ Erro na busca do Google: {e}")
            return []
        urls_filtradas = [url for url in urls_encontradas if url not in urls_vistas and "/busca?" not in url and "google.com" not in url]
        urls_vistas.update(urls_filtradas)

        async with aiohttp.ClientSession() as session:
            tasks = [self._extrair_texto_async(session, url, termo) for url in urls_filtradas]
            # Usar gather com return_exceptions=True para que uma falha não cancele todas as outras
            resultados_tasks = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar resultados válidos e lidar com exceções
        resultados = [res for res in resultados_tasks if res and not isinstance(res, Exception)][:self.config['min_sucessos_por_termo']]
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
    async def main():
        # Certifique-se de que a variável de ambiente DEEPSEEK_API_KEY esteja configurada
        # ou passe a chave diretamente para o construtor.
        # Ex: agente = AgentePesquisadorJurisprudencia(api_key="SUA_CHAVE_AQUI")
        agente = AgentePesquisadorJurisprudencia()
        termos_pesquisa = ["dano moral", "recurso especial cabimento"]
        resultados = await agente.pesquisar_jurisprudencia_async(termos_pesquisa)
        
        if resultados:
            print("\n--- RESULTADOS FINAIS ---")
            for i, res in enumerate(resultados):
                print(f"\nResultado {i+1}:")
                print(f"  Título: {res['titulo']}")
                print(f"  URL: {res['url']}")
                print(f"  Texto (primeiros 500 chars): {res['texto'][:500]}...\n")
        else:
            print("Nenhum resultado relevante encontrado.")

    asyncio.run(main())