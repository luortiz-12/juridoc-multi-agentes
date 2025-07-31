# agente_coletor_queixa_crime.py - Novo Agente Especializado em Coletar Dados para Queixa-Crime

import re
import traceback
from typing import Dict, Any, List

class AgenteColetorQueixaCrime:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber os dados brutos de um formulário já identificado como "Queixa-Crime".
    - Mapear os campos específicos de uma queixa-crime.
    - Consolidar os fatos de forma coesa.
    - Extrair os fundamentos jurídicos relevantes para a pesquisa.
    - Montar a estrutura de dados limpa para os próximos agentes.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados de QUEIXA-CRIME...")
        # COMENTÁRIO: Este mapeamento contém apenas os campos relevantes para uma queixa-crime.
        self.mapeamento_flexivel = {
            'autor_nome': ['clientenome'],
            'autor_qualificacao': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte'],
            'reu_qualificacao': ['qualificacaoparte'],
            'fatos': ['fatos'],
            'pedido': ['pedido'],
            'valor_causa': ['valorcausa'],
            'documentos': ['documentos'],
            'descricao_crime': ['descricaodocrime'],
            'data_fato': ['datafatocriminal'],
            'hora_fato': ['horafatocriminal'],
            'local_fato': ['localfatocriminal'],
            'nome_vitima': ['nomevitimacrime'],
            'qualificacao_vitima': ['qualificacaovitimacrime'],
            'testemunhas': ['testemunhocrime'],
            'info_extra_criminal': ['infoextracrime'],
        }
        print("✅ Agente Coletor de QUEIXA-CRIME pronto.")

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
            return {"status": "erro", "erro": f"Falha no processamento dos dados da queixa-crime: {e}"}

    def _consolidar_fatos(self, dados: Dict[str, Any]) -> str:
        """Junta informações de múltiplos campos para criar uma narrativa de fatos unificada."""
        narrativa = []
        if self._obter_valor(dados, 'fatos'):
            narrativa.append(str(self._obter_valor(dados, 'fatos')))
        if self._obter_valor(dados, 'descricao_crime'):
            narrativa.append(f"O crime pode ser descrito como: {self._obter_valor(dados, 'descricao_crime')}.")
        if self._obter_valor(dados, 'data_fato'):
            narrativa.append(f"O fato ocorreu na data de {self._obter_valor(dados, 'data_fato')}, aproximadamente às {self._obter_valor(dados, 'hora_fato', 'hora não informada')}.")
        if self._obter_valor(dados, 'local_fato'):
            narrativa.append(f"O local do ocorrido foi: {self._obter_valor(dados, 'local_fato')}.")
        if self._obter_valor(dados, 'info_extra_criminal'):
            narrativa.append(f"Informações adicionais relevantes: {self._obter_valor(dados, 'info_extra_criminal')}.")
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, dados: Dict[str, Any]) -> List[str]:
        """Extrai os termos jurídicos chave dos fatos consolidados para guiar a pesquisa."""
        fundamentos = set()
        texto_analise = (fatos + " " + str(self._obter_valor(dados, 'pedido', ''))).lower()

        fundamentos.update(["direito penal", "queixa-crime", "código de processo penal"])
        if any(k in texto_analise for k in ["honra", "injúria", "injuriado"]):
            fundamentos.add("crime de injúria")
        if any(k in texto_analise for k in ["difamação", "difamado"]):
            fundamentos.add("crime de difamação")
        if any(k in texto_analise for k in ["calúnia", "caluniado"]):
            fundamentos.add("crime de calúnia")
        if "dano moral" in texto_analise:
            fundamentos.add("reparação dano moral criminal")
        
        if len(fundamentos) > 3:
            fundamentos.discard("direito penal")
        
        return list(fundamentos)[:5]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str]) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados para os próximos agentes."""
        
        estrutura_final = {
            "tipo_documento": "Queixa-Crime",
            "tipo_acao": "Queixa-Crime",
            "fundamentos_necessarios": fundamentos,
            "fatos": fatos_consolidados,
            "autor": {
                "nome": self._obter_valor(dados, 'autor_nome', "[NOME DO QUERELANTE]"),
                "qualificacao": self._obter_valor(dados, 'autor_qualificacao', "[QUALIFICAÇÃO DO QUERELANTE]")
            },
            "reu": {
                "nome": self._obter_valor(dados, 'reu_nome', "[NOME DO QUERELADO]"),
                "qualificacao": self._obter_valor(dados, 'reu_qualificacao', "[QUALIFICAÇÃO DO QUERELADO]")
            },
            "vitima": {
                "nome": self._obter_valor(dados, 'nome_vitima', self._obter_valor(dados, 'autor_nome')),
                "qualificacao": self._obter_valor(dados, 'qualificacao_vitima', self._obter_valor(dados, 'autor_qualificacao'))
            },
            "pedidos": self._obter_valor(dados, 'pedido', "[PEDIDOS A SEREM ESPECIFICADOS]"),
            "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}",
            "documentos": self._obter_valor(dados, 'documentos', ""),
            "competencia": "Justiça Criminal",
        }
        return estrutura_final
