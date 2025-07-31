# agente_coletor_parecer.py - Novo Agente Especializado em Coletar Dados para Pareceres Jurídicos

import re
import traceback
from typing import Dict, Any, List

class AgenteColetorParecer:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber os dados brutos de um formulário já identificado como "Parecer Jurídico".
    - Mapear os campos específicos de um parecer.
    - Consolidar a consulta para o redator.
    - Extrair os fundamentos jurídicos relevantes para a pesquisa.
    - Montar a estrutura de dados limpa para os próximos agentes.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados de PARECER JURÍDICO...")
        # COMENTÁRIO: Este mapeamento contém apenas os campos relevantes para um parecer.
        self.mapeamento_flexivel = {
            'solicitante': ['solicitante'],
            'assunto': ['assunto'],
            'consulta': ['consulta'],
            'legislacao_aplicavel': ['legislacaoaplicavel', 'legislacao'],
            'analise': ['analise'],
            'conclusao_previa': ['conclusao'],
        }
        print("✅ Agente Coletor de PARECER JURÍDICO pronto.")

    def _normalizar_chave(self, chave: str) -> str:
        """Normaliza uma chave de dicionário para um formato padronizado."""
        return re.sub(r'[^a-z0-9]', '', str(chave).lower())

    def _obter_valor(self, dados: Dict[str, Any], nome_interno: str, padrao: Any = None) -> Any:
        """Busca um valor no dicionário de dados usando a lista de chaves possíveis."""
        chaves_possiveis = self.mapeamento_flexivel.get(nome_interno, [])
        for chave in chaves_possiveis:
            if chave in dados and dados[chave] is not None and str(dados[chave]).strip() != "":
                return dados[chave]
        return padrao

    def coletar_e_processar(self, dados_brutos_n8n: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ponto de entrada principal do agente. Recebe o JSON do N8N e retorna a estrutura de dados processada.
        """
        try:
            dados_normalizados = {self._normalizar_chave(k): v for k, v in dados_brutos_n8n.items()}
            
            fatos_consolidados = self._consolidar_fatos(dados_normalizados)
            fundamentos = self._extrair_fundamentos_necessarios(dados_normalizados)
            
            dados_estruturados = self._montar_estrutura_final(dados_normalizados, fatos_consolidados, fundamentos)
            
            return {"status": "sucesso", "dados_estruturados": dados_estruturados}
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": f"Falha no processamento dos dados do parecer: {e}"}

    def _consolidar_fatos(self, dados: Dict[str, Any]) -> str:
        """Junta a consulta e a análise preliminar em uma única narrativa."""
        narrativa = []
        if self._obter_valor(dados, 'consulta'):
            narrativa.append(f"Consulta: {self._obter_valor(dados, 'consulta')}")
        if self._obter_valor(dados, 'analise'):
            narrativa.append(f"Análise Preliminar Fornecida: {self._obter_valor(dados, 'analise')}")
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, dados: Dict[str, Any]) -> List[str]:
        """Extrai os termos jurídicos chave para guiar a pesquisa."""
        fundamentos = set()
        
        assunto = self._obter_valor(dados, 'assunto', '')
        legislacao = self._obter_valor(dados, 'legislacao_aplicavel', '')
        consulta = self._obter_valor(dados, 'consulta', '')
        
        texto_completo_parecer = f"{assunto} {legislacao} {consulta}"
        
        termos_chave = re.findall(r'\"[a-zA-Z\s]+\"|\b[A-Z]{3,}\b|\b[\w\.]+\b', texto_completo_parecer)
        fundamentos.update(termos_chave)
        
        palavras_irrelevantes = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'ser', 'uma', 'por', 'são', 'qual', 'quais'}
        fundamentos_filtrados = {f.strip(" .,'\"?") for f in fundamentos if f and f.lower() not in palavras_irrelevantes and len(f.strip()) > 2}
            
        return list(fundamentos_filtrados)[:5] # Limita a no máximo 5 termos

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str]) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados para os próximos agentes."""
        
        estrutura_final = {
            "tipo_documento": "Parecer Jurídico",
            "tipo_acao": "Parecer Jurídico",
            "fundamentos_necessarios": fundamentos,
            "fatos": fatos_consolidados, # 'fatos' aqui contém a consulta consolidada
            "solicitante": self._obter_valor(dados, 'solicitante'),
            "assunto": self._obter_valor(dados, 'assunto'),
            "conclusao_previa": self._obter_valor(dados, 'conclusao_previa')
        }
        return estrutura_final