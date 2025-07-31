# agente_coletor_contratos.py - Novo Agente Especializado em Coletar Dados para Contratos

import re
import traceback
from typing import Dict, Any, List

class AgenteColetorContratos:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber os dados brutos de um formulário já identificado como "Contrato".
    - Mapear os campos específicos de um contrato.
    - Extrair os fundamentos jurídicos relevantes para a pesquisa (focando no tipo e objeto do contrato).
    - Montar a estrutura de dados limpa para os agentes de pesquisa e redação.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados de CONTRATOS...")
        # COMENTÁRIO: Este mapeamento contém apenas os campos relevantes para um contrato.
        self.mapeamento_flexivel = {
            'tipo_contrato': ['tipodecontrato'],
            'contratante_nome': ['nomedocontratante', 'contratante'],
            'contratante_cpf': ['cpfdocontratante', 'cpfcontratante'],
            'contratante_rg': ['rgdocontratante', 'rgcontratante'],
            'contratante_cnpj': ['cnpjdacontratante', 'cnpjcontratante'],
            'contratante_endereco': ['endereçodocontratante', 'endereçocontratante'],
            'contratado_nome': ['nomedocontratado', 'contratado'],
            'contratado_cpf': ['cpfdocontratado', 'cpfcontratado'],
            'contratado_rg': ['rgdocontratado', 'rgcontratado'],
            'contratado_cnpj': ['cnpjdacontratado', 'cnpjcontratado'],
            'contratado_endereco': ['endereçodocontratado', 'endereçocontratado'],
            'objeto_contrato': ['objetodocontrato', 'objeto'],
            'valor_contrato': ['valordocontrato', 'valor'],
            'forma_pagamento': ['formadepagamento'],
            'prazos': ['prazos', 'prazosdepagamento'],
            'responsabilidades': ['responsabilidadesdaspartes'],
            'penalidades': ['penalidadespordescumprimento'],
            'foro': ['forodeeleição', 'foro'],
        }
        print("✅ Agente Coletor de CONTRATOS pronto.")

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
            
            fundamentos = self._extrair_fundamentos_necessarios(dados_normalizados)
            
            dados_estruturados = self._montar_estrutura_final(dados_normalizados, fundamentos)
            
            return {"status": "sucesso", "dados_estruturados": dados_estruturados}
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": f"Falha no processamento dos dados do contrato: {e}"}

    def _extrair_fundamentos_necessarios(self, dados: Dict[str, Any]) -> List[str]:
        """Extrai os termos jurídicos chave para guiar a pesquisa de contratos."""
        fundamentos = set()
        
        tipo_especifico = self._obter_valor(dados, 'tipo_contrato', '')
        objeto = self._obter_valor(dados, 'objeto_contrato', '')
        
        termo_principal = tipo_especifico if tipo_especifico else f"de {objeto}"
        
        fundamentos.add(f"modelo de {termo_principal}")
        fundamentos.add(f"cláusulas essenciais {termo_principal}")
        fundamentos.add(f"legislação aplicável a {termo_principal}")
            
        return list(fundamentos)

    def _montar_estrutura_final(self, dados: Dict[str, Any], fundamentos: List[str]) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados para os próximos agentes."""
        
        estrutura_final = {
            "tipo_documento": "Contrato",
            "fundamentos_necessarios": fundamentos,
            "tipo_contrato_especifico": self._obter_valor(dados, 'tipo_contrato'),
            "contratante": {
                "nome": self._obter_valor(dados, 'contratante_nome'),
                "cpf": self._obter_valor(dados, 'contratante_cpf'),
                "rg": self._obter_valor(dados, 'contratante_rg'),
                "cnpj": self._obter_valor(dados, 'contratante_cnpj'),
                "endereco": self._obter_valor(dados, 'contratante_endereco')
            },
            "contratado": {
                "nome": self._obter_valor(dados, 'contratado_nome'),
                "cpf": self._obter_valor(dados, 'contratado_cpf'),
                "rg": self._obter_valor(dados, 'contratado_rg'),
                "cnpj": self._obter_valor(dados, 'contratado_cnpj'),
                "endereco": self._obter_valor(dados, 'contratado_endereco')
            },
            "objeto": self._obter_valor(dados, 'objeto_contrato'),
            "valor": self._obter_valor(dados, 'valor_contrato'),
            "pagamento": self._obter_valor(dados, 'forma_pagamento'),
            "prazos": self._obter_valor(dados, 'prazos'),
            "responsabilidades": self._obter_valor(dados, 'responsabilidades'),
            "penalidades": self._obter_valor(dados, 'penalidades'),
            "foro": self._obter_valor(dados, 'foro')
        }
        return estrutura_final
