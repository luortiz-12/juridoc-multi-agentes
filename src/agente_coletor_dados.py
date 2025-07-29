# agente_coletor_dados.py - Versão 5.2 (Suporte a Contratos Específicos)

import json
import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v5.2 - Suporte a múltiplos tipos de documentos.
    - Identifica Petições (Trabalhista, Cível, Criminal) e Contratos.
    - Extrai fundamentos de forma especializada, usando o tipo de contrato quando especificado.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v5.2 (Multi-Documento)...")
        # COMENTÁRIO: Adicionado o mapeamento para o novo campo 'Tipo-de-contrato'.
        self.mapeamento_flexivel = {
            'tipo_contrato': ['tipodecontrato'],
            'contratante_nome': ['nomedocontratante', 'contratante'],
            'contratante_cpf': ['cpfdacontratante', 'cpfcontratante'],
            'contratante_rg': ['rgdocontratante', 'rgcontratante'],
            'contratante_cnpj': ['cnpjdacontratante', 'cnpjcontratante'],
            'contratante_endereco': ['endereçodocontratante', 'endereçocontratante'],
            'contratado_nome': ['nomedocontratado', 'contratado'],
            'contratado_cpf': ['cpfdacontratado', 'cpfcontratado'],
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
            'autor_nome': ['clientenome'], 'qualificacao_cliente': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte'], 'qualificacao_reu': ['qualificacaoparte'],
            'fatos': ['fatos'], 'pedido': ['pedido'], 'valor_causa': ['valorcausa'],
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
        
        if any(k in dados_relevantes for k in ['contratante', 'objetodocontrato', 'objeto', 'valordocontrato', 'valor', 'tipodecontrato']):
            return "Contrato", dados_relevantes
        
        if any(k in dados_relevantes for k in ['solicitante', 'consulta']):
            return "Parecer Jurídico", dados_relevantes
        if any(k in dados_relevantes for k in ['dataadmissaotrabalhista', 'salariotrabalhista']):
            return "Ação Trabalhista", dados_relevantes
        
        return "Petição", dados_relevantes

    def _consolidar_fatos(self, dados: Dict[str, Any], contexto: str) -> str:
        if contexto == "Contrato":
            return self._obter_valor(dados, 'objeto_contrato', '[Objeto do contrato não especificado]')
        return str(self._obter_valor(dados, 'fatos', ''))

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str, dados: Dict[str, Any]) -> List[str]:
        fundamentos = set()
        if contexto == "Contrato":
            # COMENTÁRIO: Lógica aprimorada. Ele primeiro tenta usar o tipo específico de contrato.
            # Se não houver, ele usa o objeto do contrato para a pesquisa.
            tipo_especifico = self._obter_valor(dados, 'tipo_contrato', '')
            objeto = self._obter_valor(dados, 'objeto_contrato', '')
            
            termo_principal = tipo_especifico if tipo_especifico else f"de {objeto}"
            
            fundamentos.add(f"modelo de {termo_principal}")
            fundamentos.add(f"cláusulas essenciais {termo_principal}")
            fundamentos.add(f"legislação aplicável a {termo_principal}")
        # ... (outras lógicas de extração)
            
        return list(filter(None, fundamentos))

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        estrutura_final = {"tipo_documento": contexto, "fundamentos_necessarios": fundamentos}

        if contexto == "Contrato":
            estrutura_final['tipo_contrato_especifico'] = self._obter_valor(dados, 'tipo_contrato') # Adiciona o tipo para o redator
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
        else: # Estrutura para Petições e Pareceres
            estrutura_final['tipo_acao'] = contexto
            estrutura_final['fatos'] = fatos_consolidados
            if "Parecer" in contexto:
                 estrutura_final.update({
                    "solicitante": self._obter_valor(dados, 'solicitante'),
                    "assunto": self._obter_valor(dados, 'assunto'),
                })
            else: # Petições
                estrutura_final.update({
                    "autor": {"nome": self._obter_valor(dados, 'autor_nome'), "qualificacao": self._obter_valor(dados, 'qualificacao_cliente')},
                    "reu": {"nome": self._obter_valor(dados, 'reu_nome'), "qualificacao": self._obter_valor(dados, 'qualificacao_reu')},
                    "pedidos": self._obter_valor(dados, 'pedido'),
                    "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}"
                })

        return estrutura_final