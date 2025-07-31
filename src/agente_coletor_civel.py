# agente_coletor_civel.py - Novo Agente Especializado em Coletar Dados para Petições Cíveis

import re
import traceback
from typing import Dict, Any, List

class AgenteColetorCivel:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber os dados brutos de um formulário já identificado como "Ação Cível".
    - Mapear os campos específicos de uma petição cível.
    - Consolidar os fatos de forma coesa.
    - Extrair os fundamentos jurídicos relevantes para a pesquisa.
    - Montar a estrutura de dados limpa para os agentes de pesquisa e redação.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados CÍVEL...")
        # COMENTÁRIO: Este mapeamento contém apenas os campos relevantes para uma petição cível.
        self.mapeamento_flexivel = {
            'autor_nome': ['clientenome'],
            'autor_qualificacao': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte'],
            'reu_qualificacao': ['qualificacaoparte'],
            'fatos': ['fatos'],
            'pedido': ['pedido'],
            'valor_causa': ['valorcausa'],
            'documentos': ['documentos'],
            'info_extra_civil': ['infoextrascivil', 'informacaoextrapeticaocivil'],
        }
        print("✅ Agente Coletor CÍVEL pronto.")

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
            fundamentos = self._extrair_fundamentos_necessarios(fatos_consolidados, dados_normalizados)
            
            dados_estruturados = self._montar_estrutura_final(dados_normalizados, fatos_consolidados, fundamentos)
            
            return {"status": "sucesso", "dados_estruturados": dados_estruturados}
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": f"Falha no processamento dos dados cíveis: {e}"}

    def _consolidar_fatos(self, dados: Dict[str, Any]) -> str:
        """Junta informações de múltiplos campos para criar uma narrativa de fatos unificada."""
        narrativa = []
        if self._obter_valor(dados, 'fatos'):
            narrativa.append(str(self._obter_valor(dados, 'fatos')))
        if self._obter_valor(dados, 'info_extra_civil'):
            narrativa.append(f"Informações adicionais relevantes: {self._obter_valor(dados, 'info_extra_civil')}.")
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, dados: Dict[str, Any]) -> List[str]:
        """Extrai os termos jurídicos chave dos fatos consolidados para guiar a pesquisa."""
        fundamentos = set()
        texto_analise = (fatos + " " + str(self._obter_valor(dados, 'pedido', ''))).lower()

        # Lógica inteligente para extrair termos de pesquisa contextuais
        palavras_irrelevantes = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'que', 'foi', 'mas', 'sem', 'ser', 'uma', 'por', 'são', 'qual', 'quais', 'os', 'as', 'dos', 'das', 'é', 'se', 'seu', 'sua', 'pelo', 'pela'}
        
        palavras = re.findall(r'\b\w+\b', texto_analise)
        palavras_filtradas = [p for p in palavras if p not in palavras_irrelevantes and len(p) > 3]

        # Cria frases de 2 e 3 palavras (bigramas e trigramas)
        if len(palavras_filtradas) >= 2:
            for i in range(len(palavras_filtradas) - 1):
                fundamentos.add(" ".join(palavras_filtradas[i:i+2]))
        if len(palavras_filtradas) >= 3:
            for i in range(len(palavras_filtradas) - 2):
                fundamentos.add(" ".join(palavras_filtradas[i:i+3]))
        
        if not fundamentos:
            fundamentos.update(["direito civil", "código civil", "danos materiais", "danos morais"])
        
        # Limita a no máximo 5 termos de pesquisa para eficiência
        return list(fundamentos)[:5]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str]) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados para os próximos agentes."""
        
        # COMENTÁRIO: A estrutura de dados é específica para uma petição cível.
        # O 'tipo_documento' e 'tipo_acao' são definidos como 'Ação Cível' por este agente.
        estrutura_final = {
            "tipo_documento": "Ação Cível",
            "tipo_acao": "Ação Cível",
            "fundamentos_necessarios": fundamentos,
            "fatos": fatos_consolidados,
            "autor": {
                "nome": self._obter_valor(dados, 'autor_nome', "[NOME DO AUTOR]"),
                "qualificacao": self._obter_valor(dados, 'autor_qualificacao', "[QUALIFICAÇÃO DO AUTOR]")
            },
            "reu": {
                "nome": self._obter_valor(dados, 'reu_nome', "[NOME DO RÉU]"),
                "qualificacao": self._obter_valor(dados, 'reu_qualificacao', "[QUALIFICAÇÃO DO RÉU]")
            },
            "pedidos": self._obter_valor(dados, 'pedido', "[PEDIDOS A SEREM ESPECIFICADOS]"),
            "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}",
            "documentos": self._obter_valor(dados, 'documentos', ""),
            "competencia": "Justiça Comum"
        }
        return estrutura_final
