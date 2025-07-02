# pesquisa_juridica.py - VERSÃO FINAL COM BUSCA SEQUENCIAL E OTIMIZADA

import re
import time
import traceback
from typing import Dict, List, Any
from duckduckgo_search import DDGS

class PesquisaJuridica:
    """
    Módulo que realiza pesquisas jurídicas de forma SEQUENCIAL e inteligente
    para garantir a qualidade e evitar bloqueios.
    """
    
    def __init__(self):
        self.ddgs = DDGS(timeout=30) # Aumenta o timeout para buscas mais completas

    def pesquisar_fundamentos_juridicos(self, fundamentos: List[str], tipo_acao: str) -> Dict[str, Any]:
        """
        Orquestra as buscas sequencialmente: primeiro legislação, depois jurisprudência, etc.
        """
        print(f"🔍 Iniciando pesquisa jurídica SEQUENCIAL para: {fundamentos}")
        
        try:
            # --- EXECUÇÃO SEQUENCIAL ---
            # Cada busca só começa quando a anterior termina.

            print("\n--- Etapa 1/3: Pesquisando Legislação ---")
            leis = self._pesquisar_legislacao(fundamentos, tipo_acao)
            
            print("\n--- Etapa 2/3: Pesquisando Jurisprudência ---")
            jurisprudencia = self._pesquisar_jurisprudencia(fundamentos, tipo_acao)
            
            print("\n--- Etapa 3/3: Pesquisando Doutrina ---")
            doutrina = self._pesquisar_doutrina(fundamentos, tipo_acao)

            resultados = {
                "leis": leis,
                "jurisprudencia": jurisprudencia,
                "doutrina": doutrina,
                "resumo_pesquisa": f"Pesquisa sequencial concluída para os temas: {', '.join(fundamentos)}."
            }
            
            print("\n✅ Pesquisa jurídica completa e finalizada.")
            return resultados
            
        except Exception as e:
            print(f"❌ Erro crítico durante o processo de pesquisa: {e}")
            return self._fallback_response(str(e))
    
    def _executar_busca_unica(self, query: str) -> List[Dict]:
        """Função central que executa uma única busca e trata o rate limit."""
        try:
            print(f"  -> Buscando por: '{query}'")
            # A biblioteca DDGS já faz uma busca de cada vez.
            # O próprio ato de chamar a função e esperar o retorno já é sequencial.
            return list(self.ddgs.text(query, max_results=5))
        except Exception as e:
            # O erro '202 Ratelimit' que vimos antes aconteceria aqui.
            print(f"  -> ⚠️  Aviso na busca: {e}. A busca para este termo falhou.")
            return [] # Retorna uma lista vazia em caso de erro, para não quebrar o fluxo.

    def _pesquisar_legislacao(self, fundamentos: List[str], tipo_acao: str) -> str:
        termo_principal = " ".join(fundamentos)
        query = f'lei código "{termo_principal}" {tipo_acao} site:planalto.gov.br OR site:jusbrasil.com.br'
        
        resultados = self._executar_busca_unica(query)
        
        # Formata a saída
        if resultados:
            texto_formatado = "LEGISLAÇÃO APLICÁVEL ENCONTRADA:\n"
            for res in resultados:
                texto_formatado += f"- {res.get('title', '')}\n  Fonte: {res.get('href', '')}\n"
            return texto_formatado
        return "Nenhuma legislação proeminente encontrada na busca automatizada."

    def _pesquisar_jurisprudencia(self, fundamentos: List[str], tipo_acao: str) -> str:
        termo_principal = " ".join(fundamentos)
        query = f'jurisprudência acórdão "{termo_principal}" {tipo_acao} site:stj.jus.br OR site:stf.jus.br OR site:tst.jus.br'

        resultados = self._executar_busca_unica(query)

        if resultados:
            texto_formatado = "JURISPRUDÊNCIA RELEVANTE ENCONTRADA:\n"
            for res in resultados:
                 texto_formatado += f"- {res.get('title', '')}\n  Fonte: {res.get('href', '')}\n  Resumo: {res.get('body', '')[:200]}...\n"
            return texto_formatado
        return "Nenhuma jurisprudência proeminente encontrada na busca automatizada."

    def _pesquisar_doutrina(self, fundamentos: List[str], tipo_acao: str) -> str:
        termo_principal = " ".join(fundamentos)
        query = f'doutrina artigo jurídico "{termo_principal}" {tipo_acao} site:conjur.com.br OR site:migalhas.com.br'
        
        resultados = self._executar_busca_unica(query)

        if resultados:
            texto_formatado = "DOUTRINA E ARTIGOS RELACIONADOS:\n"
            for res in resultados:
                texto_formatado += f"- {res.get('title', '')}\n  Fonte: {res.get('href', '')}\n"
            return texto_formatado
        return "Nenhuma doutrina proeminente encontrada na busca automatizada."

    def _fallback_response(self, erro: str) -> Dict[str, Any]:
        """Resposta padrão em caso de falha crítica na pesquisa."""
        return {
            "leis": "Erro na pesquisa de legislação.",
            "jurisprudencia": "Erro na pesquisa de jurisprudência.",
            "doutrina": "Erro na pesquisa de doutrina.",
            "resumo_pesquisa": f"Erro crítico durante a pesquisa: {erro}"
        }