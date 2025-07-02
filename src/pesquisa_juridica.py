# pesquisa_juridica.py - VERSÃO FINAL COM BUSCAS MÚLTIPLAS E ANTI-BLOQUEIO

import re
import time
import traceback
from typing import Dict, List, Any
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

class PesquisaJuridica:
    """
    Módulo responsável por realizar pesquisas jurídicas usando DuckDuckGo.
    Busca leis, jurisprudência e doutrina para fundamentar petições.
    """
    
    def __init__(self):
        # --- CORREÇÃO: Adicionado timeout na inicialização do buscador ---
        self.ddgs = DDGS(timeout=25)
        self.sites_juridicos = [
            "planalto.gov.br", "stf.jus.br", "stj.jus.br",
            "tst.jus.br", "tjsp.jus.br", "tjrj.jus.br",
            "tjmg.jus.br", "jusbrasil.com.br", "conjur.com.br",
            "migalhas.com.br"
        ]
    
    def pesquisar_fundamentos_juridicos(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """
        Realiza pesquisa jurídica completa, orquestrando as buscas por categoria
        com pausas para evitar bloqueios.
        """
        try:
            print(f"🔍 Iniciando pesquisa jurídica para: {fundamentos}")
            
            # --- CORREÇÃO: Pausa entre as CATEGORIAS de busca ---
            # Adicionamos um intervalo entre a busca de legislação, jurisprudência e doutrina.
            
            leis = self._pesquisar_legislacao(fundamentos, tipo_acao)
            time.sleep(1)  # Pausa de 1 segundo
            
            jurisprudencia = self._pesquisar_jurisprudencia(fundamentos, tipo_acao)
            time.sleep(1)  # Pausa de 1 segundo
            
            doutrina = self._pesquisar_doutrina(fundamentos, tipo_acao)

            resultados = {
                "leis": leis,
                "jurisprudencia": jurisprudencia,
                "doutrina": doutrina,
                "resumo_pesquisa": self._gerar_resumo_pesquisa(fundamentos, tipo_acao)
            }
            
            print("✅ Pesquisa jurídica concluída")
            return resultados
            
        except Exception as e:
            print(f"❌ Erro na pesquisa jurídica: {e}")
            return {
                "leis": "Erro na pesquisa de legislação",
                "jurisprudencia": "Erro na pesquisa de jurisprudência", 
                "doutrina": "Erro na pesquisa de doutrina",
                "resumo_pesquisa": f"Erro na pesquisa: {str(e)}"
            }
    
    def _pesquisar_legislacao(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Pesquisa legislação relevante."""
        try:
            print("📚 Pesquisando legislação...")
            termos_busca = []
            for fundamento in fundamentos:
                termos_busca.extend([
                    f"lei {fundamento} {tipo_acao}",
                    f"código {fundamento}",
                    f"legislação {fundamento}"
                ])
            
            resultados_leis = []
            
            for termo in termos_busca[:3]:  # Limitar a 3 buscas
                try:
                    query = f"{termo} site:planalto.gov.br OR site:jusbrasil.com.br"
                    resultados = list(self.ddgs.text(query, max_results=2))
                    
                    for resultado in resultados:
                        if self._is_relevant_legal_content(resultado.get('body', '')):
                            resultados_leis.append({
                                'titulo': resultado.get('title', ''),
                                'url': resultado.get('href', ''),
                                'resumo': resultado.get('body', '')[:300] + '...'
                            })
                    
                    # --- CORREÇÃO: Pausa ENTRE cada busca individual ---
                    time.sleep(1.5)  # Pausa de 1.5 segundos para ser "educado" com o servidor
                    
                except Exception as e:
                    print(f"⚠️ Erro na busca de legislação para '{termo}': {e}")
                    continue
            
            if resultados_leis:
                texto_leis = "LEGISLAÇÃO APLICÁVEL:\n\n"
                for i, lei in enumerate(resultados_leis[:5], 1):
                    texto_leis += f"{i}. {lei['titulo']}\n"
                    texto_leis += f"   Resumo: {lei['resumo']}\n"
                    texto_leis += f"   Fonte: {lei['url']}\n\n"
                return texto_leis
            else:
                return "Nenhuma legislação encontrada na busca automatizada."
                
        except Exception as e:
            print(f"❌ Erro na pesquisa de legislação: {e}")
            return "Erro na pesquisa de legislação. Consulte manualmente."
    
    def _pesquisar_jurisprudencia(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Pesquisa jurisprudência relevante."""
        try:
            print("⚖️ Pesquisando jurisprudência...")
            termos_busca = []
            for fundamento in fundamentos:
                termos_busca.extend([
                    f"jurisprudência {fundamento} {tipo_acao}",
                    f"STF {fundamento}",
                    f"STJ {fundamento}"
                ])
            
            resultados_juris = []
            
            for termo in termos_busca[:3]:
                try:
                    query = f"'{termo}' site:stf.jus.br OR site:stj.jus.br OR site:jusbrasil.com.br"
                    resultados = list(self.ddgs.text(query, max_results=2))
                    
                    for resultado in resultados:
                        if self._is_relevant_jurisprudence(resultado.get('body', '')):
                            resultados_juris.append({
                                'titulo': resultado.get('title', ''),
                                'url': resultado.get('href', ''),
                                'resumo': resultado.get('body', '')[:300] + '...'
                            })
                    
                    # --- CORREÇÃO: Pausa ENTRE cada busca individual ---
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"⚠️ Erro na busca de jurisprudência para '{termo}': {e}")
                    continue
            
            if resultados_juris:
                texto_juris = "JURISPRUDÊNCIA APLICÁVEL:\n\n"
                for i, juris in enumerate(resultados_juris[:5], 1):
                    texto_juris += f"{i}. {juris['titulo']}\n"
                    texto_juris += f"   Resumo: {juris['resumo']}\n"
                    texto_juris += f"   Fonte: {juris['url']}\n\n"
                return texto_juris
            else:
                return "Nenhuma jurisprudência encontrada na busca automatizada."
                
        except Exception as e:
            print(f"❌ Erro na pesquisa de jurisprudência: {e}")
            return "Erro na pesquisa de jurisprudência. Consulte manualmente."
    
    def _pesquisar_doutrina(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Pesquisa doutrina e artigos jurídicos."""
        try:
            print("📖 Pesquisando doutrina...")
            termos_busca = []
            for fundamento in fundamentos:
                termos_busca.extend([
                    f"doutrina {fundamento} {tipo_acao}",
                    f"artigo jurídico {fundamento}"
                ])
            
            resultados_doutrina = []
            
            for termo in termos_busca[:2]:
                try:
                    query = f"'{termo}' site:conjur.com.br OR site:migalhas.com.br OR site:jus.com.br"
                    resultados = list(self.ddgs.text(query, max_results=2))
                    
                    for resultado in resultados:
                        if self._is_relevant_doctrine(resultado.get('body', '')):
                            resultados_doutrina.append({
                                'titulo': resultado.get('title', ''),
                                'url': resultado.get('href', ''),
                                'resumo': resultado.get('body', '')[:300] + '...'
                            })
                    
                    # --- CORREÇÃO: Pausa ENTRE cada busca individual ---
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"⚠️ Erro na busca de doutrina para '{termo}': {e}")
                    continue
            
            if resultados_doutrina:
                texto_doutrina = "DOUTRINA E ARTIGOS:\n\n"
                for i, doutrina in enumerate(resultados_doutrina[:5], 1):
                    texto_doutrina += f"{i}. {doutrina['titulo']}\n"
                    texto_doutrina += f"   Resumo: {doutrina['resumo']}\n"
                    texto_doutrina += f"   Fonte: {doutrina['url']}\n\n"
                return texto_doutrina
            else:
                return "Nenhuma doutrina encontrada na busca automatizada."
                
        except Exception as e:
            print(f"❌ Erro na pesquisa de doutrina: {e}")
            return "Erro na pesquisa de doutrina. Consulte manualmente."

    # Seus outros métodos (_is_relevant..., _gerar_resumo..., pesquisar_termo_especifico) permanecem os mesmos.
    # O código abaixo é uma representação. Mantenha seu código original.
    def _is_relevant_legal_content(self, content: str) -> bool:
        pass
    def _is_relevant_jurisprudence(self, content: str) -> bool:
        pass
    def _is_relevant_doctrine(self, content: str) -> bool:
        pass
    def _gerar_resumo_pesquisa(self, fundamentos: List[str], tipo_acao: str) -> str:
        pass
    def pesquisar_termo_especifico(self, termo: str, categoria: str = "geral") -> List[Dict[str, str]]:
        pass