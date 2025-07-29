# agente_coletor_dados.py - Versão 4.0 (Suporte a Múltiplos Tipos de Documentos)

import json
import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v4.0 - Suporte a múltiplos contextos jurídicos.
    - Identifica Ações Trabalhistas, Cíveis, Queixas-Crime, Habeas Corpus e Pareceres Jurídicos.
    - Consolida fatos e extrai fundamentos de forma especializada para cada área.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v4.0 (Multi-Contexto)...")
        # COMENTÁRIO: Adicionados os novos campos do formulário de Parecer Jurídico.
        self.mapeamento_flexivel = {
            'solicitante': ['solicitante'], 'assunto': ['assunto'], 'consulta': ['consulta'],
            'legislacao_aplicavel': ['legislacaoaplicavel'], 'analise': ['analise'], 'conclusao_previa': ['conclusao'],
            # ... (mapeamentos anteriores mantidos)
            'autor_nome': ['clientenome'], 'autor_qualificacao': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte', 'nomecontrariopeticao'], 'reu_qualificacao': ['qualificacao', 'qualificacaoparte', 'qualificacaocontrariopeticao'],
            'fatos': ['fatos'], 'pedido': ['pedido'], 'valor_causa': ['valorcausa'], 'documentos': ['documentos'],
            'info_extra_civil': ['infoextrascivil', 'informacaoextrapeticaocivil'],
            'info_extra_trabalhista': ['infoextratrabalhista', 'informacaoextratrabalhista'],
            'data_admissao': ['dataadmissaotrabalhista'], 'data_demissao': ['datademisaotrabalhista'],
            'salario': ['salariotrabalhista'], 'jornada': ['jornadadetrabalho'], 'motivo_saida': ['motivosaidatrablhista'],
        }
        print("✅ Agente Coletor pronto para processar múltiplos tipos de documentos.")

    def _normalizar_chave(self, chave: str) -> str:
        return re.sub(r'[^a-z0-9]', '', str(chave).lower())

    def _obter_valor(self, dados: Dict[str, Any], nome_interno: str, padrao: Any = None) -> Any:
        chaves_possiveis = self.mapeamento_flexivel.get(nome_interno, [])
        for chave in chaves_possiveis:
            if chave in dados:
                valor = dados[chave]
                if valor is not None and str(valor).strip() != "":
                    return valor
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
        """Analisa os campos preenchidos para determinar o tipo de documento."""
        dados_relevantes = {k: v for k, v in dados_normalizados.items() if v is not None and str(v).strip() != ""}
        
        # COMENTÁRIO: Adicionada a lógica para identificar um Parecer Jurídico.
        # A presença dos campos 'solicitante' ou 'consulta' é um forte indicador.
        if any(k in dados_relevantes for k in ['solicitante', 'consulta']):
            return "Parecer Jurídico", dados_relevantes
        if any(k in dados_relevantes for k in ['dataadmissaotrabalhista', 'salariotrabalhista']):
            return "Ação Trabalhista", dados_relevantes
        # ... (outras lógicas de identificação)
        
        return "Ação Cível", dados_relevantes

    def _consolidar_fatos(self, dados: Dict[str, Any], contexto: str) -> str:
        """Junta informações de múltiplos campos para criar a narrativa principal."""
        narrativa = []
        
        # COMENTÁRIO: Lógica de consolidação específica para o Parecer.
        if contexto == "Parecer Jurídico":
            if self._obter_valor(dados, 'consulta'): narrativa.append(f"Consulta: {self._obter_valor(dados, 'consulta')}")
            if self._obter_valor(dados, 'analise'): narrativa.append(f"Análise Preliminar Fornecida: {self._obter_valor(dados, 'analise')}")
        else:
            if self._obter_valor(dados, 'fatos'): narrativa.append(str(self._obter_valor(dados, 'fatos')))
            # ... (outras lógicas de consolidação)
            
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str, dados: Dict[str, Any]) -> List[str]:
        """Extrai os termos jurídicos chave para guiar a pesquisa."""
        fundamentos = set()
        texto_analise = fatos.lower()

        # COMENTÁRIO: Lógica de extração de fundamentos para o Parecer.
        # Usa os campos 'assunto' e 'legislacao_aplicavel' como fontes primárias.
        if contexto == "Parecer Jurídico":
            assunto = self._obter_valor(dados, 'assunto', '')
            legislacao = self._obter_valor(dados, 'legislacao_aplicavel', '')
            fundamentos.update(re.split(r'[,\s]+', assunto))
            fundamentos.update(re.split(r'[,\s]+', legislacao))
        elif contexto == "Ação Trabalhista":
            fundamentos.update(["direito trabalhista", "CLT"])
            # ... (lógica trabalhista)
        elif "Consumidor" in contexto:
            fundamentos.update(["direito do consumidor", "Código de Defesa do Consumidor"])
            if "vício" in texto_analise or "defeito" in texto_analise: fundamentos.add("vício do produto CDC artigo 18")
            if "dano moral" in texto_analise: fundamentos.add("dano moral consumidor")
            
        return list(filter(None, fundamentos)) # Remove strings vazias

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados."""
        
        estrutura_final = {
            "tipo_acao": contexto,
            "fatos": fatos_consolidados, # No parecer, 'fatos' conterá a consulta.
            "fundamentos_necessarios": fundamentos
        }

        if "Parecer" in contexto:
            estrutura_final.update({
                "solicitante": self._obter_valor(dados, 'solicitante'),
                "assunto": self._obter_valor(dados, 'assunto'),
                "conclusao_previa": self._obter_valor(dados, 'conclusao_previa')
            })
        else:
            # Estrutura para petições (autor vs réu)
            estrutura_final.update({
                "autor": {"nome": self._obter_valor(dados, 'autor_nome'), "qualificacao": self._obter_valor(dados, 'autor_qualificacao')},
                "reu": {"nome": self._obter_valor(dados, 'reu_nome'), "qualificacao": self._obter_valor(dados, 'reu_qualificacao')},
                "pedidos": self._obter_valor(dados, 'pedido'),
                "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}"
            })

        return estrutura_final