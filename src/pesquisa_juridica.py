# pesquisa_juridica.py - Versão Otimizada com Busca Assíncrona

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List
from datetime import datetime
from googlesearch import search
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

class PesquisaJuridica:
    """
    Agente de Pesquisa Jurídica Otimizado.
    - Utiliza programação assíncrona para realizar buscas e extrações de conteúdo em paralelo,
      reduzindo drasticamente o tempo de espera.
    """
    def __init__(self):
        print("🔍 Inicializando Pesquisa Jurídica OTIMIZADA...")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # COMENTÁRIO: As configurações foram mantidas, mas o timeout e delay serão tratados pela lógica assíncrona.
        self.config = {
            'tamanho_minimo_conteudo': 1000,
            'tamanho_maximo_conteudo': 30000,
            'max_sites_por_query': 2,
        }
        self.sites_prioritarios = {
            'legislacao': ['planalto.gov.br', 'lexml.gov.br'],
            'jurisprudencia': ['tst.jus.br', 'stj.jus.br', 'stf.jus.br'],
            'doutrina': ['conjur.com.br', 'migalhas.com.br']
        }
        print("✅ Sistema de pesquisa jurídica OTIMIZADA inicializado")

    # COMENTÁRIO: Esta é a nova função assíncrona para extrair conteúdo de uma única URL.
    # Ela usa 'aiohttp' para fazer requisições web sem bloquear o programa.
    async def _extrair_conteudo_url_async(self, session, url: str) -> Dict[str, Any]:
        """Extrai conteúdo de uma URL de forma assíncrona."""
        try:
            async with session.get(url, headers=self.headers, timeout=20, ssl=False) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove tags indesejadas antes de extrair o texto
                    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                        tag.decompose()
                    
                    texto = soup.body.get_text(separator=' ', strip=True) if soup.body else ""
                    texto_limpo = re.sub(r'\s+', ' ', texto).strip()
                    
                    if len(texto_limpo) < self.config['tamanho_minimo_conteudo']:
                        return None # Descarta conteúdo irrelevante

                    print(f"📄 Conteúdo extraído de: {url} ({len(texto_limpo)} caracteres)")
                    return {
                        "url": url,
                        "texto": texto_limpo[:self.config['tamanho_maximo_conteudo']],
                        "tamanho": len(texto_limpo),
                        "titulo": soup.title.string.strip() if soup.title else "Título não encontrado",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    print(f"❌ Erro ao acessar {url}: Status {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Erro ao extrair conteúdo de {url}: {e}")
            return None

    # COMENTÁRIO: Esta função agora coordena a pesquisa e extração de forma assíncrona.
    async def _pesquisar_e_extrair_async(self, termo: str, tipo_pesquisa: str) -> List[Dict[str, Any]]:
        """Realiza a busca no Google e dispara a extração paralela do conteúdo."""
        print(f"📚 Buscando {tipo_pesquisa.upper()} para o termo: '{termo}'...")
        sites = self.sites_prioritarios.get(tipo_pesquisa, [])
        site_query = " OR ".join([f"site:{site}" for site in sites])
        query = f"{tipo_pesquisa} {termo} {site_query}"
        
        try:
            # A busca do Google ainda é síncrona, mas é rápida.
            loop = asyncio.get_event_loop()
            urls = await loop.run_in_executor(None, lambda: list(search(query, num_results=self.config['max_sites_por_query'], lang="pt")))
        except Exception as e:
            print(f"⚠️ Falha na busca do Google para '{termo}': {e}")
            return []

        # COMENTÁRIO: 'asyncio.gather' executa todas as extrações de conteúdo ao mesmo tempo.
        # Isto é o que torna o processo muito mais rápido.
        async with aiohttp.ClientSession() as session:
            tasks = [self._extrair_conteudo_url_async(session, url) for url in urls]
            resultados = await asyncio.gather(*tasks)
            return [res for res in resultados if res] # Filtra resultados que falharam (None)

    # COMENTÁRIO: A lógica principal da pesquisa agora está dentro de uma função assíncrona.
    async def _pesquisar_fundamentacao_completa_async(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """Cria e executa todas as tarefas de pesquisa em paralelo."""
        area_direito = "trabalhista" if "trabalhista" in tipo_acao.lower() else "civil"
        
        # Cria uma lista de todas as tarefas de pesquisa a serem executadas
        tasks = []
        for fundamento in fundamentos[:3]: # Limita a 3 fundamentos para não sobrecarregar
            tasks.append(self._pesquisar_e_extrair_async(fundamento, "legislacao"))
            tasks.append(self._pesquisar_e_extrair_async(fundamento, "jurisprudencia"))
            tasks.append(self._pesquisar_e_extrair_async(fundamento, "doutrina"))

        resultados_brutos = await asyncio.gather(*tasks)
        
        # Organiza os resultados
        resultados_finais = {"legislacao": [], "jurisprudencia": [], "doutrina": []}
        idx = 0
        for _ in fundamentos[:3]:
            resultados_finais["legislacao"].extend(resultados_brutos[idx])
            resultados_finais["jurisprudencia"].extend(resultados_brutos[idx+1])
            resultados_finais["doutrina"].extend(resultados_brutos[idx+2])
            idx += 3

        # Formata os resultados para o Agente Redator
        resultados_finais['legislacao_formatada'] = "\n\n".join([f"Fonte: {item['url']}\nConteúdo: {item['texto'][:1500]}..." for item in resultados_finais['legislacao']])
        resultados_finais['jurisprudencia_formatada'] = "\n\n".join([f"Fonte: {item['url']}\nConteúdo: {item['texto'][:1500]}..." for item in resultados_finais['jurisprudencia']])
        resultados_finais['doutrina_formatada'] = "\n\n".join([f"Fonte: {item['url']}\nConteúdo: {item['texto'][:1500]}..." for item in resultados_finais['doutrina']])
        
        # Adiciona metadados para o orquestrador
        todos_conteudos = resultados_finais["legislacao"] + resultados_finais["jurisprudencia"] + resultados_finais["doutrina"]
        resultados_finais["conteudos_extraidos"] = todos_conteudos
        resultados_finais["sites_acessados"] = [c['url'] for c in todos_conteudos]
        
        return resultados_finais

    def pesquisar_fundamentacao_completa(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """
        Ponto de entrada síncrono que executa a lógica assíncrona.
        Isso evita a necessidade de alterar o orquestrador.
        """
        inicio_pesquisa = datetime.now()
        print(f"🔍 Iniciando pesquisa jurídica OTIMIZADA para: {fundamentos}")
        
        try:
            # COMENTÁRIO: 'asyncio.run' inicia o loop de eventos assíncronos e executa nossa função principal.
            resultado = asyncio.run(self._pesquisar_fundamentacao_completa_async(fundamentos, tipo_acao))
        except Exception as e:
            print(f"❌ Erro crítico durante a pesquisa assíncrona: {e}")
            return self._gerar_resultado_fallback(fundamentos, tipo_acao)

        tempo_total = (datetime.now() - inicio_pesquisa).total_seconds()
        print(f"✅ PESQUISA OTIMIZADA CONCLUÍDA em {tempo_total:.1f} segundos")
        
        return resultado

    def _gerar_resultado_fallback(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """Gera um resultado vazio em caso de falha total da pesquisa."""
        return {
            "status": "fallback",
            "legislacao_formatada": "A pesquisa de legislação falhou.",
            "jurisprudencia_formatada": "A pesquisa de jurisprudência falhou.",
            "doutrina_formatada": "A pesquisa de doutrina falhou.",
            "conteudos_extraidos": [],
            "sites_acessados": []
        }