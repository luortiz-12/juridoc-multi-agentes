# agente_coletor_habeas_corpus.py - Novo Agente Especializado em Coletar Dados para Habeas Corpus

import re
import traceback
from typing import Dict, Any, List

class AgenteColetorHabeasCorpus:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber os dados brutos de um formulário já identificado como "Habeas Corpus".
    - Mapear os campos específicos de um Habeas Corpus.
    - Consolidar os fatos de forma coesa.
    - Extrair os fundamentos jurídicos relevantes para a pesquisa.
    - Montar a estrutura de dados limpa para os próximos agentes.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados de HABEAS CORPUS...")
        # COMENTÁRIO: Este mapeamento contém apenas os campos relevantes para um Habeas Corpus.
        self.mapeamento_flexivel = {
            'paciente_nome': ['clientenome'],
            'paciente_qualificacao': ['qualificacaocliente'],
            'advogado_nome': ['advogadoimpetrante'], # Supondo um campo para o nome do advogado
            'fatos': ['fatos'],
            'pedido': ['pedido'],
            'documentos': ['documentos'],
            'autoridade_coatora': ['autoridadecoatorahabiescorpus'],
            'local_prisao': ['localdaprisaohabiescorpus'],
            'data_prisao': ['diadaprisaohabiescorpus', 'datadaprisao'],
            'motivo_prisao': ['motivodaprisaohabiescorpus'],
            'fundamento_liberdade': ['fundamentodeliberdadehabiescorpus'],
            'info_extra_hc': ['informacaoextrahabiescorpus'],
        }
        print("✅ Agente Coletor de HABEAS CORPUS pronto.")

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
            return {"status": "erro", "erro": f"Falha no processamento dos dados do Habeas Corpus: {e}"}

    def _consolidar_fatos(self, dados: Dict[str, Any]) -> str:
        """Junta informações de múltiplos campos para criar uma narrativa de fatos unificada."""
        narrativa = []
        if self._obter_valor(dados, 'fatos'):
            narrativa.append(str(self._obter_valor(dados, 'fatos')))
        if self._obter_valor(dados, 'motivo_prisao'):
            narrativa.append(f"O motivo alegado para a prisão foi: {self._obter_valor(dados, 'motivo_prisao')}.")
        if self._obter_valor(dados, 'fundamento_liberdade'):
            narrativa.append(f"O fundamento para o pedido de liberdade é: {self._obter_valor(dados, 'fundamento_liberdade')}.")
        if self._obter_valor(dados, 'info_extra_hc'):
            narrativa.append(f"Informações adicionais relevantes: {self._obter_valor(dados, 'info_extra_hc')}.")
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, dados: Dict[str, Any]) -> List[str]:
        """Extrai os termos jurídicos chave dos fatos consolidados para guiar a pesquisa."""
        fundamentos = set()
        texto_analise = (fatos + " " + str(self._obter_valor(dados, 'pedido', ''))).lower()

        fundamentos.update(["habeas corpus", "direito constitucional", "código de processo penal"])
        if "constrangimento ilegal" in texto_analise:
            fundamentos.add("constrangimento ilegal CPP")
        if "prisão preventiva" in texto_analise:
            fundamentos.update(["requisitos prisão preventiva", "artigo 312 CPP"])
        if "prisão em flagrante" in texto_analise:
            fundamentos.add("relaxamento prisão flagrante")
        if "liminar" in texto_analise:
            fundamentos.add("liminar em habeas corpus")
        
        if len(fundamentos) > 3:
            fundamentos.discard("direito constitucional")
        
        return list(fundamentos)[:5]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str]) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados para os próximos agentes."""
        
        # Em HC, o "autor" da ação (impetrante) é geralmente o advogado, e o "cliente" é o paciente.
        paciente_nome = self._obter_valor(dados, 'paciente_nome', "[NOME DO PACIENTE]")
        paciente_qualificacao = self._obter_valor(dados, 'paciente_qualificacao', "[QUALIFICAÇÃO DO PACIENTE]")

        estrutura_final = {
            "tipo_documento": "Habeas Corpus",
            "tipo_acao": "Habeas Corpus",
            "fundamentos_necessarios": fundamentos,
            "fatos": fatos_consolidados,
            "paciente": {
                "nome": paciente_nome,
                "qualificacao": paciente_qualificacao
            },
            # O orquestrador pode preencher os dados do advogado (impetrante) se necessário
            "advogado_nome": self._obter_valor(dados, 'advogado_nome', "[NOME DO ADVOGADO]"),
            "autoridade_coatora": self._obter_valor(dados, 'autoridade_coatora', "[AUTORIDADE COATORA]"),
            "local_prisao": self._obter_valor(dados, 'local_prisao', "[LOCAL DA PRISÃO]"),
            "pedidos": self._obter_valor(dados, 'pedido', "[PEDIDOS A SEREM ESPECIFICADOS]"),
            "documentos": self._obter_valor(dados, 'documentos', ""),
            "competencia": "Justiça Criminal",
        }
        return estrutura_final
