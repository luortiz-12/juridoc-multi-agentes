# pesquisa_juridica.py - Versão 4.0 (Pesquisa Persistente e Aprofundada)

import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Dict, Any, List
from googlesearch import search
from bs4 import BeautifulSoup

class PesquisaJuridica:
    """
    Agente de Pesquisa Jurídica Otimizado v4.0.
    - Realiza uma pesquisa persistente, garantindo um número mínimo de extrações bem-sucedidas.
    - É mais resiliente a bloqueios e erros de extração.
    """
    def __init__(self):
        print("🔍 Inicializando Pesquisa Jurídica OTIMIZADA v4.0 (Persistente)...")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        # COMENTÁRIO: Novas configurações para a pesquisa persistente.
        self.config = {
            'tamanho_minimo_conteudo': 1000,
            'tamanho_maximo_conteudo': 30000,
            'min_sucessos_por_termo': 4, # META: Garantir pelo menos 4 conteúdos por termo.
            'google_search_results': 10, # Busca mais links para ter mais opções.
        }
        self.sites_prioritarios = {
            'legislacao': ['planalto.gov.br', 'lexml.gov.br'],
            'jurisprudencia': ['tst.jus.br', 'stj.jus.br', 'stf.jus.br', 'conjur.com.br'],
            'doutrina': ['conjur.com.br', 'migalhas.com.br', 'ambito-juridico.com.br']
        }
        print("✅ Sistema de pesquisa jurídica OTIMIZADA inicializado.")

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
                    return { "url": url, "texto": texto_limpo[:self.config['tamanho_maximo_conteudo']], "titulo": soup.title.string.strip() if soup.title else "N/A" }
                else:
                    print(f"❌ Falha (Status {response.status}): {url}")
                    return None
        except Exception as e:
            print(f"❌ Falha (Erro: {type(e).__name__}): {url}")
            return None

    async def _pesquisar_e_extrair_async(self, termo: str, tipo_pesquisa: str) -> List[Dict[str, Any]]:
        """
        COMENTÁRIO: Lógica principal aprimorada. Agora ele busca mais links e tenta extrair
        até atingir a meta de sucessos, ignorando as falhas.
        """
        print(f"\n📚 Buscando {tipo_pesquisa.upper()} para o termo: '{termo}'...")
        site_query = " OR ".join([f"site:{site}" for site in self.sites_prioritarios.get(tipo_pesquisa, [])])
        query = f'"{termo}" {tipo_pesquisa} {site_query}'
        
        resultados_sucesso = []
        urls_tentadas = set()
        
        try:
            loop = asyncio.get_event_loop()
            urls_google = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config['google_search_results'], lang="pt")))
            
            async with aiohttp.ClientSession() as session:
                for url in urls_google:
                    if url not in urls_tentadas:
                        urls_tentadas.add(url)
                        resultado = await self._extrair_conteudo_url_async(session, url)
                        if resultado:
                            resultados_sucesso.append(resultado)
                        
                        # Verifica se a meta foi atingida
                        if len(resultados_sucesso) >= self.config['min_sucessos_por_termo']:
                            print(f"🎯 Meta de {self.config['min_sucessos_por_termo']} sucessos atingida para '{termo}'.")
                            break
            
            return resultados_sucesso

        except Exception as e:
            print(f"⚠️ Falha crítica na busca do Google para '{termo}': {e}")
            return resultados_sucesso # Retorna o que conseguiu até o momento

    async def _pesquisar_fundamentacao_completa_async(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """Cria e executa todas as tarefas de pesquisa em paralelo."""
        tasks = []
        for fundamento in fundamentos[:3]: # Limita a 3 fundamentos para não sobrecarregar
            tasks.append(self._pesquisar_e_extrair_async(fundamento, "legislacao"))
            tasks.append(self._pesquisar_e_extrair_async(fundamento, "jurisprudencia"))
            tasks.append(self._pesquisar_e_extrair_async(fundamento, "doutrina"))

        resultados_brutos = await asyncio.gather(*tasks)
        
        resultados_finais = {"legislacao": [], "jurisprudencia": [], "doutrina": []}
        idx = 0
        for _ in fundamentos[:3]:
            resultados_finais["legislacao"].extend(resultados_brutos[idx])
            resultados_finais["jurisprudencia"].extend(resultados_brutos[idx+1])
            resultados_finais["doutrina"].extend(resultados_brutos[idx+2])
            idx += 3

        for tipo in ["legislacao", "jurisprudencia", "doutrina"]:
            resultados_finais[f'{tipo}_formatada'] = "\n\n".join([f"Fonte: {item['url']}\nConteúdo: {item['texto'][:1500]}..." for item in resultados_finais[tipo]])
        
        todos_conteudos = resultados_finais["legislacao"] + resultados_finais["jurisprudencia"] + resultados_finais["doutrina"]
        resultados_finais["conteudos_extraidos"] = todos_conteudos
        
        return resultados_finais

    def pesquisar_fundamentacao_completa(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """Ponto de entrada síncrono que executa a lógica assíncrona."""
        inicio_pesquisa = datetime.now()
        print(f"🔍 Iniciando pesquisa jurídica OTIMIZADA para: {fundamentos}")
        try:
            resultado = asyncio.run(self._pesquisar_fundamentacao_completa_async(fundamentos, tipo_acao))
        except Exception as e:
            print(f"❌ Erro crítico durante a pesquisa assíncrona: {e}")
            return self._gerar_resultado_fallback()
        tempo_total = (datetime.now() - inicio_pesquisa).total_seconds()
        print(f"✅ PESQUISA OTIMIZADA CONCLUÍDA em {tempo_total:.1f} segundos")
        return resultado

    def _gerar_resultado_fallback(self) -> Dict[str, Any]:
        """Gera um resultado vazio em caso de falha total da pesquisa."""
        return {
            "status": "fallback",
            "legislacao_formatada": "A pesquisa de legislação falhou.",
            "jurisprudencia_formatada": "A pesquisa de jurisprudência falhou.",
            "doutrina_formatada": "A pesquisa de doutrina falhou.",
        }
