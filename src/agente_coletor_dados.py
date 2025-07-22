# agente_coletor_dados.py - Versão 3.2 (Integração N8N Robusta e Flexível)

import json
import re
import traceback
from typing import Dict, Any, List, Optional

class AgenteColetorDados:
    """
    Agente Coletor de Dados v3.2 - Robusto para Integração N8N.
    - Normaliza as chaves do JSON de entrada para lidar com inconsistências de nomenclatura (maiúsculas/minúsculas, hifens).
    - Utiliza um mapeamento flexível para encontrar dados em chaves com nomes variados.
    - Identifica o contexto jurídico (Trabalhista, Civil, Criminal) com base nos campos preenchidos e no conteúdo.
    - Consolida inteligentemente os fatos de múltiplos campos em uma única narrativa.
    - Extrai os fundamentos jurídicos corretos a partir do contexto real dos fatos.
    - Estrutura os dados de forma limpa para os agentes subsequentes.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v3.2 (N8N)...")
        
        # COMENTÁRIO: Este é o novo "dicionário de sinônimos" para os campos.
        # Ele mapeia um nome de campo interno e estável (ex: 'autor_nome') para uma lista
        # de possíveis chaves normalizadas que podem vir do formulário/n8n.
        self.mapeamento_flexivel = {
            'autor_nome': ['clientenome'],
            'autor_qualificacao': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte', 'nomecontrariopeticao'],
            'reu_qualificacao': ['qualificacao', 'qualificacaoparte', 'qualificacaocontrariopeticao'],
            'fatos': ['fatos'],
            'pedido': ['pedido', 'verbaspleiteadastrabalhista'],
            'valor_causa': ['valorcausa'],
            'documentos': ['documentos'],
            'info_extra_trabalhista': ['infoextratrabalhista', 'informacaoextratrabalhista'],
            'data_admissao': ['dataadmissaotrabalhista'],
            'data_demissao': ['datademisaotrabalhista', 'datademissaopeticao'],
            'salario': ['salariotrabalhista'],
            'jornada': ['jornadadetrabalho', 'jornadatrabalhista'],
            'motivo_saida': ['motivosaidatrablhista', 'motivosaidatrabalhista'],
            'cargo': ['cargo']
        }
        print("✅ Agente Coletor pronto para processar dados do N8N.")

    def _normalizar_chave(self, chave: str) -> str:
        """Normaliza uma chave de dicionário para um formato padronizado e consistente."""
        return re.sub(r'[^a-z0-9]', '', str(chave).lower())

    def _obter_valor(self, dados: Dict[str, Any], nome_interno: str, padrao: Any = None) -> Any:
        """
        Busca um valor no dicionário de dados usando a lista de chaves possíveis do mapeamento flexível.
        """
        # COMENTÁRIO: Esta é a nova função de busca inteligente. Em vez de procurar por uma
        # chave fixa, ela testa todas as variações conhecidas para um determinado dado.
        chaves_possiveis = self.mapeamento_flexivel.get(nome_interno, [])
        for chave in chaves_possiveis:
            if chave in dados:
                valor = dados[chave]
                # Retorna apenas se o valor não for nulo ou uma string vazia
                if valor is not None and str(valor).strip() != "":
                    return valor
        return padrao

    def coletar_e_processar(self, dados_brutos_n8n: Dict[str, Any]) -> Dict[str, Any]:
        """Ponto de entrada principal do agente."""
        try:
            print("📊 Iniciando coleta e processamento de dados do N8N...")
            
            dados_normalizados = {self._normalizar_chave(k): v for k, v in dados_brutos_n8n.items()}
            
            contexto, dados_relevantes = self._identificar_contexto_e_dados(dados_normalizados)
            print(f"🔍 Contexto jurídico identificado: {contexto}")

            fatos_consolidados = self._consolidar_fatos(dados_relevantes)
            
            fundamentos = self._extrair_fundamentos_necessarios(fatos_consolidados, contexto)
            print(f"🔑 Fundamentos extraídos para pesquisa: {fundamentos}")

            dados_estruturados = self._montar_estrutura_final(dados_relevantes, fatos_consolidados, fundamentos, contexto)
            
            print("✅ Dados coletados e estruturados com sucesso.")
            return {"status": "sucesso", "dados_estruturados": dados_estruturados}

        except Exception as e:
            print(f"❌ Erro crítico no Agente Coletor de Dados: {e}")
            traceback.print_exc()
            return {"status": "erro", "erro": f"Falha no processamento dos dados de entrada: {e}"}

    def _identificar_contexto_e_dados(self, dados_normalizados: Dict[str, Any]) -> (str, Dict[str, Any]):
        """Analisa os campos preenchidos e o conteúdo para determinar a área do direito."""
        dados_relevantes = {k: v for k, v in dados_normalizados.items() if v is not None and str(v).strip() != ""}

        # COMENTÁRIO: Lógica de identificação aprimorada. Além de checar as chaves,
        # analisa o conteúdo dos campos de texto para uma decisão mais assertiva.
        texto_geral = (
            str(dados_relevantes.get('fatos', '')) + 
            str(dados_relevantes.get('pedido', '')) + 
            str(dados_relevantes.get('infoextratrabalhista', ''))
        ).lower()

        campos_trabalhistas = ['dataadmissaotrabalhista', 'salariotrabalhista', 'motivosaidatrabalhista']
        palavras_trabalhistas = ['clt', 'reclamante', 'vínculo empregatício', 'verbas rescisórias', 'fgts']

        if any(campo in dados_relevantes for campo in campos_trabalhistas) or any(palavra in texto_geral for palavra in palavras_trabalhistas):
            return "Ação Trabalhista", dados_relevantes

        campos_criminais = ['datafatocriminal', 'localfatocriminal', 'nomevitimacrime']
        if any(campo in dados_relevantes for campo in campos_criminais):
            return "Queixa-Crime", dados_relevantes

        return "Ação Cível", dados_relevantes

    def _consolidar_fatos(self, dados: Dict[str, Any]) -> str:
        """Junta informações de múltiplos campos para criar uma narrativa de fatos unificada."""
        narrativa = []
        
        fatos_base = self._obter_valor(dados, 'fatos')
        if fatos_base:
            narrativa.append(str(fatos_base))
        
        # Consolidação específica para dados trabalhistas
        cargo = self._obter_valor(dados, 'cargo')
        if cargo:
             narrativa.append(f"O cargo exercido era de {cargo}.")
        
        salario = self._obter_valor(dados, 'salario')
        if salario:
            narrativa.append(f"Recebia um salário mensal de R$ {salario}.")

        jornada = self._obter_valor(dados, 'jornada')
        if jornada:
            narrativa.append(f"A jornada de trabalho era a seguinte: {jornada}.")

        motivo_saida = self._obter_valor(dados, 'motivo_saida')
        if motivo_saida:
            narrativa.append(f"O motivo da saída foi: {motivo_saida}.")

        info_extra = self._obter_valor(dados, 'info_extra_trabalhista')
        if info_extra:
            narrativa.append(f"Informações adicionais relevantes: {info_extra}.")
            
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str) -> List[str]:
        """Extrai os termos jurídicos chave dos fatos consolidados para guiar a pesquisa."""
        fundamentos = set()
        texto_analise = fatos.lower()

        if contexto == "Ação Trabalhista":
            fundamentos.add("direito trabalhista")
            fundamentos.add("CLT")
            if "pejotização" in texto_analise or "pessoa jurídica" in texto_analise or "abrir uma empresa" in texto_analise:
                fundamentos.update(["reconhecimento de vínculo empregatício", "pejotização fraude trabalhista", "artigo 3º da CLT requisitos", "princípio da primazia da realidade", "subordinação jurídica"])
            if "horas extras" in texto_analise:
                fundamentos.update(["horas extras", "CLT art. 59"])
            if "assédio moral" in texto_analise or "humilhante" in texto_analise:
                fundamentos.update(["assédio moral", "danos morais"])
            if "estabilidade" in texto_analise or "doença ocupacional" in texto_analise:
                fundamentos.update(["doença ocupacional", "estabilidade acidentária", "Lei 8.213/91 art. 118", "danos morais acidentários"])
            if not fundamentos - {"direito trabalhista", "CLT"}:
                fundamentos.add("verbas rescisórias")
        
        return list(fundamentos) if fundamentos else ["direito civil", "código civil"]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados."""
        autor = {
            "nome": self._obter_valor(dados, 'autor_nome', "[NOME DO AUTOR]"),
            "qualificacao": self._obter_valor(dados, 'autor_qualificacao', "[QUALIFICAÇÃO DO AUTOR]")
        }
        reu = {
            "nome": self._obter_valor(dados, 'reu_nome', "[NOME DO RÉU]"),
            "qualificacao": self._obter_valor(dados, 'reu_qualificacao', "[QUALIFICAÇÃO DO RÉU]")
        }
        
        estrutura_final = {
            "autor": autor,
            "reu": reu,
            "tipo_acao": contexto,
            "fatos": fatos_consolidados,
            "pedidos": self._obter_valor(dados, 'pedido', "[PEDIDOS A SEREM ESPECIFICADOS]"),
            "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}",
            "documentos": self._obter_valor(dados, 'documentos', ""),
            "fundamentos_necessarios": fundamentos,
            "competencia": "Justiça do Trabalho" if contexto == "Ação Trabalhista" else "Justiça Comum",
            "observacoes": f"Documentos anexos: {self._obter_valor(dados, 'documentos', 'N/A')}",
            "urgencia": False
        }
        
        if contexto == "Ação Trabalhista":
            estrutura_final.update({
                "data_admissao": self._obter_valor(dados, 'data_admissao'),
                "data_demissao": self._obter_valor(dados, 'data_demissao'),
                "salario": self._obter_valor(dados, 'salario'),
                "cargo": self._obter_valor(dados, 'cargo', "[CARGO A SER INFORMADO]"),
                "jornada": self._obter_valor(dados, 'jornada'),
                "motivo_saida": self._obter_valor(dados, 'motivo_saida')
            })

        return estrutura_final
