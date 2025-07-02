# pesquisa_juridica.py - Módulo de Pesquisa Jurídica com DuckDuckGo

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
        self.ddgs = DDGS()
        self.sites_juridicos = [
            "planalto.gov.br",
            "stf.jus.br", 
            "stj.jus.br",
            "tst.jus.br",
            "tjsp.jus.br",
            "tjrj.jus.br",
            "tjmg.jus.br",
            "jusbrasil.com.br",
            "conjur.com.br",
            "migalhas.com.br"
        ]
    
    def pesquisar_fundamentos_juridicos(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """
        Realiza pesquisa jurídica completa baseada nos fundamentos necessários.
        
        Args:
            fundamentos: Lista de temas jurídicos para pesquisar
            tipo_acao: Tipo da ação para contextualizar a pesquisa
            
        Returns:
            Dict com resultados organizados por categoria
        """
        try:
            print(f"🔍 Iniciando pesquisa jurídica para: {fundamentos}")
            
            resultados = {
                "leis": self._pesquisar_legislacao(fundamentos, tipo_acao),
                "jurisprudencia": self._pesquisar_jurisprudencia(fundamentos, tipo_acao),
                "doutrina": self._pesquisar_doutrina(fundamentos, tipo_acao),
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
            
            # Termos de busca para legislação
            termos_busca = []
            for fundamento in fundamentos:
                termos_busca.extend([
                    f"lei {fundamento} {tipo_acao}",
                    f"código {fundamento}",
                    f"legislação {fundamento}"
                ])
            
            resultados_leis = []
            
            for termo in termos_busca[:3]:  # Limitar a 3 buscas para não sobrecarregar
                try:
                    query = f"{termo} site:planalto.gov.br OR site:jusbrasil.com.br"
                    resultados = list(self.ddgs.text(query, max_results=3))
                    
                    for resultado in resultados:
                        if self._is_relevant_legal_content(resultado.get('body', '')):
                            resultados_leis.append({
                                'titulo': resultado.get('title', ''),
                                'url': resultado.get('href', ''),
                                'resumo': resultado.get('body', '')[:300] + '...'
                            })
                    
                    time.sleep(1)  # Evitar rate limiting
                    
                except Exception as e:
                    print(f"⚠️ Erro na busca de legislação para '{termo}': {e}")
                    continue
            
            # Formatar resultados
            if resultados_leis:
                texto_leis = "LEGISLAÇÃO APLICÁVEL:\n\n"
                for i, lei in enumerate(resultados_leis[:5], 1):
                    texto_leis += f"{i}. {lei['titulo']}\n"
                    texto_leis += f"   Resumo: {lei['resumo']}\n"
                    texto_leis += f"   Fonte: {lei['url']}\n\n"
                return texto_leis
            else:
                return "Consulte a legislação específica aplicável ao caso."
                
        except Exception as e:
            print(f"❌ Erro na pesquisa de legislação: {e}")
            return "Erro na pesquisa de legislação. Consulte manualmente."
    
    def _pesquisar_jurisprudencia(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Pesquisa jurisprudência relevante."""
        try:
            print("⚖️ Pesquisando jurisprudência...")
            
            # Termos de busca para jurisprudência
            termos_busca = []
            for fundamento in fundamentos:
                termos_busca.extend([
                    f"jurisprudência {fundamento} {tipo_acao}",
                    f"STF {fundamento}",
                    f"STJ {fundamento}",
                    f"tribunal {fundamento} {tipo_acao}"
                ])
            
            resultados_juris = []
            
            for termo in termos_busca[:3]:  # Limitar a 3 buscas
                try:
                    query = f"{termo} site:stf.jus.br OR site:stj.jus.br OR site:jusbrasil.com.br"
                    resultados = list(self.ddgs.text(query, max_results=3))
                    
                    for resultado in resultados:
                        if self._is_relevant_jurisprudence(resultado.get('body', '')):
                            resultados_juris.append({
                                'titulo': resultado.get('title', ''),
                                'url': resultado.get('href', ''),
                                'resumo': resultado.get('body', '')[:300] + '...'
                            })
                    
                    time.sleep(1)  # Evitar rate limiting
                    
                except Exception as e:
                    print(f"⚠️ Erro na busca de jurisprudência para '{termo}': {e}")
                    continue
            
            # Formatar resultados
            if resultados_juris:
                texto_juris = "JURISPRUDÊNCIA APLICÁVEL:\n\n"
                for i, juris in enumerate(resultados_juris[:5], 1):
                    texto_juris += f"{i}. {juris['titulo']}\n"
                    texto_juris += f"   Resumo: {juris['resumo']}\n"
                    texto_juris += f"   Fonte: {juris['url']}\n\n"
                return texto_juris
            else:
                return "Consulte jurisprudência específica dos tribunais superiores."
                
        except Exception as e:
            print(f"❌ Erro na pesquisa de jurisprudência: {e}")
            return "Erro na pesquisa de jurisprudência. Consulte manualmente."
    
    def _pesquisar_doutrina(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Pesquisa doutrina e artigos jurídicos."""
        try:
            print("📖 Pesquisando doutrina...")
            
            # Termos de busca para doutrina
            termos_busca = []
            for fundamento in fundamentos:
                termos_busca.extend([
                    f"doutrina {fundamento} {tipo_acao}",
                    f"artigo jurídico {fundamento}",
                    f"comentários {fundamento}"
                ])
            
            resultados_doutrina = []
            
            for termo in termos_busca[:3]:  # Limitar a 3 buscas
                try:
                    query = f"{termo} site:conjur.com.br OR site:migalhas.com.br OR site:jusbrasil.com.br"
                    resultados = list(self.ddgs.text(query, max_results=3))
                    
                    for resultado in resultados:
                        if self._is_relevant_doctrine(resultado.get('body', '')):
                            resultados_doutrina.append({
                                'titulo': resultado.get('title', ''),
                                'url': resultado.get('href', ''),
                                'resumo': resultado.get('body', '')[:300] + '...'
                            })
                    
                    time.sleep(1)  # Evitar rate limiting
                    
                except Exception as e:
                    print(f"⚠️ Erro na busca de doutrina para '{termo}': {e}")
                    continue
            
            # Formatar resultados
            if resultados_doutrina:
                texto_doutrina = "DOUTRINA E ARTIGOS:\n\n"
                for i, doutrina in enumerate(resultados_doutrina[:5], 1):
                    texto_doutrina += f"{i}. {doutrina['titulo']}\n"
                    texto_doutrina += f"   Resumo: {doutrina['resumo']}\n"
                    texto_doutrina += f"   Fonte: {doutrina['url']}\n\n"
                return texto_doutrina
            else:
                return "Consulte doutrina especializada sobre o tema."
                
        except Exception as e:
            print(f"❌ Erro na pesquisa de doutrina: {e}")
            return "Erro na pesquisa de doutrina. Consulte manualmente."
    
    def _is_relevant_legal_content(self, content: str) -> bool:
        """Verifica se o conteúdo é relevante para legislação."""
        keywords = ['lei', 'código', 'artigo', 'parágrafo', 'inciso', 'decreto', 'medida provisória']
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in keywords)
    
    def _is_relevant_jurisprudence(self, content: str) -> bool:
        """Verifica se o conteúdo é relevante para jurisprudência."""
        keywords = ['acórdão', 'decisão', 'julgamento', 'tribunal', 'ministro', 'relator', 'ementa']
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in keywords)
    
    def _is_relevant_doctrine(self, content: str) -> bool:
        """Verifica se o conteúdo é relevante para doutrina."""
        keywords = ['doutrina', 'comentário', 'análise', 'interpretação', 'entendimento', 'autor']
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in keywords)
    
    def _gerar_resumo_pesquisa(self, fundamentos: List[str], tipo_acao: str) -> str:
        """Gera um resumo da pesquisa realizada."""
        return f"""
        RESUMO DA PESQUISA JURÍDICA:
        
        Tipo de Ação: {tipo_acao}
        Fundamentos Pesquisados: {', '.join(fundamentos)}
        
        A pesquisa foi realizada nos principais sites jurídicos brasileiros, incluindo:
        - Planalto (legislação federal)
        - STF e STJ (jurisprudência dos tribunais superiores)
        - Tribunais estaduais
        - Portais jurídicos especializados
        
        Os resultados foram filtrados por relevância e organizados por categoria
        (legislação, jurisprudência e doutrina) para fundamentar adequadamente a petição.
        """
    
    def pesquisar_termo_especifico(self, termo: str, categoria: str = "geral") -> List[Dict[str, str]]:
        """
        Pesquisa um termo específico e retorna resultados estruturados.
        
        Args:
            termo: Termo específico para pesquisar
            categoria: Categoria da pesquisa (legislacao, jurisprudencia, doutrina, geral)
            
        Returns:
            Lista de resultados estruturados
        """
        try:
            if categoria == "legislacao":
                query = f"{termo} site:planalto.gov.br OR site:jusbrasil.com.br lei código"
            elif categoria == "jurisprudencia":
                query = f"{termo} site:stf.jus.br OR site:stj.jus.br acórdão decisão"
            elif categoria == "doutrina":
                query = f"{termo} site:conjur.com.br OR site:migalhas.com.br artigo"
            else:
                query = f"{termo} direito jurídico"
            
            resultados = list(self.ddgs.text(query, max_results=5))
            
            resultados_estruturados = []
            for resultado in resultados:
                resultados_estruturados.append({
                    'titulo': resultado.get('title', ''),
                    'url': resultado.get('href', ''),
                    'resumo': resultado.get('body', '')[:200] + '...',
                    'categoria': categoria
                })
            
            return resultados_estruturados
            
        except Exception as e:
            print(f"❌ Erro na pesquisa específica: {e}")
            return []

