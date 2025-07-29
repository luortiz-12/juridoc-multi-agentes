# agente_coletor_dados.py - Versão 5.0 (Suporte a Contratos)

import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v5.0 - Suporte a múltiplos tipos de documentos.
    - Identifica Petições (Trabalhista, Cível, Criminal) e Contratos.
    - Extrai fundamentos de forma especializada para cada tipo de documento.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v5.0 (Multi-Documento)...")
        # COMENTÁRIO: Adicionados os novos campos do formulário de Contrato.
        self.mapeamento_flexivel = {
            'contratante_nome': ['nomedocontratante'], 'contratante_cpf': ['cpfdacontratante'], 'contratante_rg': ['rgdocontratante'],
            'contratante_cnpj': ['cnpjdacontratante'], 'contratante_endereco': ['endereçodocontratante'],
            'contratado_nome': ['nomedocontratado'], 'contratado_cpf': ['cpfdacontratado'], 'contratado_rg': ['rgdocontratado'],
            'contratado_cnpj': ['cnpjdacontratado'], 'contratado_endereco': ['endereçodocontratado'],
            'objeto_contrato': ['objetodocontrato'], 'valor_contrato': ['valordocontrato'], 'forma_pagamento': ['formadepagamento'],
            'prazos': ['prazos'], 'responsabilidades': ['responsabilidadesdaspartes'], 'penalidades': ['penalidadespordescumprimento'],
            'foro': ['forodeeleição'],
            # ... (mapeamentos de petições mantidos)
        }
        print("✅ Agente Coletor pronto para processar múltiplos tipos de documentos.")

    def _normalizar_chave(self, chave: str) -> str:
        return re.sub(r'[^a-z0-9]', '', str(chave).lower())

    def _obter_valor(self, dados: Dict[str, Any], nome_interno: str, padrao: Any = None) -> Any:
        chaves_possiveis = self.mapeamento_flexivel.get(nome_interno, [])
        for chave in chaves_possiveis:
            if chave in dados and dados[chave] is not None and str(dados[chave]).strip() != "":
                return dados[chave]
        return padrao

    def coletar_e_processar(self, dados_brutos_n8n: Dict[str, Any]) -> Dict[str, Any]:
        try:
            dados_normalizados = {self._normalizar_chave(k): v for k, v in dados_brutos_n8n.items()}
            contexto, dados_relevantes = self._identificar_contexto_e_dados(dados_normalizados)
            print(f"🔍 Contexto jurídico identificado: {contexto}")
            fatos_consolidados = self._consolidar_fatos(dados_relevantes, contexto)
            fundamentos = self._extrair_fundamentos_necessarios(fatos_consolidados, contexto, dados_relevantes)
            print(f"🔑 Fundamentos extraídos para pesquisa: {fundamentos}")
            dados_estruturados = self._montar_estrutura_final(dados_relevantes, fatos_consolidados, fundamentos, contexto)
            return {"status": "sucesso", "dados_estruturados": dados_estruturados}
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": f"Falha no processamento dos dados de entrada: {e}"}

    def _identificar_contexto_e_dados(self, dados_normalizados: Dict[str, Any]) -> (str, Dict[str, Any]):
        dados_relevantes = {k: v for k, v in dados_normalizados.items() if v is not None and str(v).strip() != ""}
        
        # COMENTÁRIO: Adicionada a lógica para identificar um Contrato.
        # A presença de campos como 'nomedocontratante' ou 'objetodocontrato' é um forte indicador.
        if any(k in dados_relevantes for k in ['nomedocontratante', 'objetodocontrato', 'valordocontrato']):
            return "Contrato", dados_relevantes
        # ... (lógicas de identificação de petições mantidas)
        return "Petição", dados_relevantes # Fallback genérico para petições

    def _consolidar_fatos(self, dados: Dict[str, Any], contexto: str) -> str:
        # Para contratos, o campo "fatos" não é usado, pois os dados são estruturados.
        if contexto == "Contrato":
            return self._obter_valor(dados, 'objeto_contrato', '[Objeto do contrato não especificado]')
        # ... (lógica de consolidação para petições mantida)
        return str(self._obter_valor(dados, 'fatos', ''))

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str, dados: Dict[str, Any]) -> List[str]:
        fundamentos = set()
        if contexto == "Contrato":
            # COMENTÁRIO: Para contratos, a pesquisa é focada no objeto do contrato.
            objeto = self._obter_valor(dados, 'objeto_contrato', '')
            fundamentos.add(f"modelo de contrato de {objeto}")
            fundamentos.add(f"cláusulas essenciais contrato de {objeto}")
            fundamentos.add(f"legislação aplicável a contrato de {objeto}")
        # ... (lógica de extração para petições mantida)
            
        return list(filter(None, fundamentos))

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        estrutura_final = {"tipo_documento": contexto, "fundamentos_necessarios": fundamentos}

        if contexto == "Contrato":
            # COMENTÁRIO: Estrutura de dados específica para contratos.
            estrutura_final['contratante'] = {
                "nome": self._obter_valor(dados, 'contratante_nome'), "cpf": self._obter_valor(dados, 'contratante_cpf'),
                "rg": self._obter_valor(dados, 'contratante_rg'), "cnpj": self._obter_valor(dados, 'contratante_cnpj'),
                "endereco": self._obter_valor(dados, 'contratante_endereco')
            }
            estrutura_final['contratado'] = {
                "nome": self._obter_valor(dados, 'contratado_nome'), "cpf": self._obter_valor(dados, 'contratado_cpf'),
                "rg": self._obter_valor(dados, 'contratado_rg'), "cnpj": self._obter_valor(dados, 'contratado_cnpj'),
                "endereco": self._obter_valor(dados, 'contratado_endereco')
            }
            estrutura_final.update({
                "objeto": fatos_consolidados, "valor": self._obter_valor(dados, 'valor_contrato'),
                "pagamento": self._obter_valor(dados, 'forma_pagamento'), "prazos": self._obter_valor(dados, 'prazos'),
                "responsabilidades": self._obter_valor(dados, 'responsabilidades'), "penalidades": self._obter_valor(dados, 'penalidades'),
                "foro": self._obter_valor(dados, 'foro')
            })
        else:
            # Estrutura para petições
            estrutura_final['tipo_acao'] = self._obter_valor(dados, 'tipoDocumento', 'Petição') # Adaptação
            # ... (estrutura de petições mantida)

        return estrutura_final