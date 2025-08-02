# agente_coletor_trabalhista.py - Novo Agente Especializado em Coletar Dados para Petições Trabalhistas

import re
import traceback
from typing import Dict, Any, List

class AgenteColetorTrabalhista:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber os dados brutos de um formulário já identificado como "Ação Trabalhista".
    - Mapear os campos específicos de uma petição trabalhista.
    - Consolidar os fatos de forma coesa.
    - Extrair os fundamentos jurídicos relevantes para a pesquisa.
    - Montar a estrutura de dados limpa para os agentes de pesquisa e redação.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados TRABALHISTA...")
        self.mapeamento_flexivel = {
            'autor_nome': ['clientenome'],
            'autor_qualificacao': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte'],
            'reu_qualificacao': ['qualificacaoparte'],
            'fatos': ['fatos'],
            'pedido': ['pedido'],
            'valor_causa': ['valorcausa'],
            'documentos': ['documentos'],
            'info_extra_trabalhista': ['infoextratrabalhista', 'informacaoextratrabalhista'],
            'data_admissao': ['dataadmissaotrabalhista'],
            'data_demissao': ['datademisaotrabalhista'],
            'salario': ['salariotrabalhista'],
            'jornada': ['jornadadetrabalho'],
            'motivo_saida': ['motivosaidatrablhista'],
            'cargo': ['cargo']
        }
        print("✅ Agente Coletor TRABALHISTA pronto.")

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
            return {"status": "erro", "erro": f"Falha no processamento dos dados trabalhistas: {e}"}

    def _consolidar_fatos(self, dados: Dict[str, Any]) -> str:
        """Junta informações de múltiplos campos para criar uma narrativa de fatos unificada."""
        narrativa = []
        if self._obter_valor(dados, 'fatos'):
            narrativa.append(str(self._obter_valor(dados, 'fatos')))
        if self._obter_valor(dados, 'jornada'):
            narrativa.append(f"A jornada de trabalho era a seguinte: {self._obter_valor(dados, 'jornada')}.")
        if self._obter_valor(dados, 'motivo_saida'):
            narrativa.append(f"O motivo da saída foi: {self._obter_valor(dados, 'motivo_saida')}.")
        if self._obter_valor(dados, 'info_extra_trabalhista'):
            narrativa.append(f"Informações adicionais relevantes: {self._obter_valor(dados, 'info_extra_trabalhista')}.")
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, dados: Dict[str, Any]) -> List[str]:
        """Extrai os termos jurídicos chave dos fatos consolidados para guiar a pesquisa."""
        fundamentos = set()
        texto_analise = (fatos + " " + str(self._obter_valor(dados, 'pedido', ''))).lower()

        # COMENTÁRIO: Lógica de extração de fundamentos específica para o contexto trabalhista.
        fundamentos.update(["direito do trabalho", "CLT"])
        if "horas extras" in texto_analise:
            fundamentos.update(["horas extras", "controle de jornada"])
        if "teletrabalho" in texto_analise or "remoto" in texto_analise:
            fundamentos.add("horas extras teletrabalho")
        if "comissões" in texto_analise or "comissão" in texto_analise:
            fundamentos.update(["integração de comissões", "cálculo verbas rescisórias"])
        if "assédio moral" in texto_analise:
            fundamentos.add("assédio moral trabalho")
        if "pejotização" in texto_analise or "vínculo empregatício" in texto_analise:
            fundamentos.update(["reconhecimento vínculo empregatício", "pejotização fraude"])
        if "dano existencial" in texto_analise:
            fundamentos.add("dano existencial trabalhista")
        
        if len(fundamentos) > 2:
            fundamentos.discard("direito do trabalho")
            fundamentos.discard("CLT")
        
        return list(fundamentos)[:5]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str]) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados para os próximos agentes."""
        
        estrutura_final = {
            "tipo_documento": "Ação Trabalhista",
            "tipo_acao": "Ação Trabalhista",
            "fundamentos_necessarios": fundamentos,
            "fatos": fatos_consolidados,
            "autor": {
                "nome": self._obter_valor(dados, 'autor_nome', "[NOME DO RECLAMANTE]"),
                "qualificacao": self._obter_valor(dados, 'autor_qualificacao', "[QUALIFICAÇÃO DO RECLAMANTE]")
            },
            "reu": {
                "nome": self._obter_valor(dados, 'reu_nome', "[NOME DA RECLAMADA]"),
                "qualificacao": self._obter_valor(dados, 'reu_qualificacao', "[QUALIFICAÇÃO DA RECLAMADA]")
            },
            "pedidos": self._obter_valor(dados, 'pedido', "[PEDIDOS A SEREM ESPECIFICADOS]"),
            "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}",
            "documentos": self._obter_valor(dados, 'documentos', ""),
            "competencia": "Justiça do Trabalho",
            # Adiciona dados específicos do contrato de trabalho
            "data_admissao": self._obter_valor(dados, 'data_admissao'),
            "data_demissao": self._obter_valor(dados, 'data_demissao'),
            "salario": self._obter_valor(dados, 'salario'),
            "cargo": self._obter_valor(dados, 'cargo', "[CARGO NÃO INFORMADO]"),
        }
        return estrutura_final