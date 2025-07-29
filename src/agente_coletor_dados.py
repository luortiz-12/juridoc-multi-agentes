# agente_coletor_dados.py - Versão 4.0 (Suporte a Petições Criminais)

import json
import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v4.0 - Suporte a múltiplos contextos jurídicos.
    - Identifica Ações Trabalhistas, Cíveis, Queixas-Crime e Habeas Corpus.
    - Consolida fatos e extrai fundamentos de forma especializada para cada área.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v4.0 (Multi-Contexto)...")
        # COMENTÁRIO: Adicionados os novos campos dos formulários criminais ao mapeamento.
        self.mapeamento_flexivel = {
            'autor_nome': ['clientenome'], 'autor_qualificacao': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte', 'nomecontrariopeticao'], 'reu_qualificacao': ['qualificacao', 'qualificacaoparte', 'qualificacaocontrariopeticao'],
            'fatos': ['fatos'], 'pedido': ['pedido'], 'valor_causa': ['valorcausa'], 'documentos': ['documentos'],
            'info_extra_civil': ['infoextrascivil', 'informacaoextrapeticaocivil'],
            'info_extra_trabalhista': ['infoextratrabalhista', 'informacaoextratrabalhista'],
            'info_extra_criminal': ['infoextracriminal'],
            'info_extra_habeascorpus': ['infoextrahabiescorpus'],
            'data_admissao': ['dataadmissaotrabalhista'], 'data_demissao': ['datademisaotrabalhista'],
            'salario': ['salariotrabalhista'], 'jornada': ['jornadadetrabalho'], 'motivo_saida': ['motivosaidatrablhista'],
            'descricao_crime': ['descricaodocrime'], 'data_fato_criminal': ['datafatocriminal'], 'local_fato_criminal': ['localfatocriminal'],
            'nome_vitima': ['nomevitimacriminal'], 'qualificacao_vitima': ['qualificacaovitimacriminal'],
            'autoridade_coatora': ['autoridadecoatorahabiescorpus'], 'local_prisao': ['localdapisaohabiescorpus'],
            'data_prisao': ['dtaprisãohabiescorpus'], 'motivo_prisao': ['motivopisaohabiescorpus'],
            'fundamento_liberdade': ['fundamentodeliberdadehabiescorpus']
        }
        print("✅ Agente Coletor pronto para processar múltiplos tipos de petição.")

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
            fundamentos = self._extrair_fundamentos_necessarios(fatos_consolidados, contexto)
            print(f"🔑 Fundamentos extraídos para pesquisa: {fundamentos}")
            dados_estruturados = self._montar_estrutura_final(dados_relevantes, fatos_consolidados, fundamentos, contexto)
            return {"status": "sucesso", "dados_estruturados": dados_estruturados}
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": f"Falha no processamento dos dados de entrada: {e}"}

    def _identificar_contexto_e_dados(self, dados_normalizados: Dict[str, Any]) -> (str, Dict[str, Any]):
        """Analisa os campos preenchidos para determinar a área do direito."""
        dados_relevantes = {k: v for k, v in dados_normalizados.items() if v is not None and str(v).strip() != ""}
        
        # COMENTÁRIO: A lógica de identificação foi expandida para os novos tipos.
        if any(k in dados_relevantes for k in ['autoridadecoatorahabiescorpus', 'localdapisaohabiescorpus']):
            return "Habeas Corpus", dados_relevantes
        if any(k in dados_relevantes for k in ['datafatocriminal', 'localfatocriminal', 'nomevitimacriminal']):
            return "Queixa-Crime", dados_relevantes
        if any(k in dados_relevantes for k in ['dataadmissaotrabalhista', 'salariotrabalhista']):
            return "Ação Trabalhista", dados_relevantes
        
        return "Ação Cível", dados_relevantes

    def _consolidar_fatos(self, dados: Dict[str, Any], contexto: str) -> str:
        """Junta informações de múltiplos campos para criar uma narrativa de fatos unificada."""
        narrativa = [str(self._obter_valor(dados, 'fatos', ''))]
        
        # COMENTÁRIO: Adicionada a consolidação para os novos tipos de petição.
        if contexto == "Queixa-Crime":
            if self._obter_valor(dados, 'descricao_crime'): narrativa.append(f"Descrição do crime: {self._obter_valor(dados, 'descricao_crime')}.")
            if self._obter_valor(dados, 'data_fato_criminal'): narrativa.append(f"O fato ocorreu em {self._obter_valor(dados, 'data_fato_criminal')}.")
            if self._obter_valor(dados, 'local_fato_criminal'): narrativa.append(f"Local do fato: {self._obter_valor(dados, 'local_fato_criminal')}.")
            if self._obter_valor(dados, 'info_extra_criminal'): narrativa.append(f"Informações adicionais: {self._obter_valor(dados, 'info_extra_criminal')}.")
        elif contexto == "Habeas Corpus":
            if self._obter_valor(dados, 'autoridade_coatora'): narrativa.append(f"A autoridade coatora é: {self._obter_valor(dados, 'autoridade_coatora')}.")
            if self._obter_valor(dados, 'data_prisao'): narrativa.append(f"A prisão ocorreu em: {self._obter_valor(dados, 'data_prisao')}.")
            if self._obter_valor(dados, 'motivo_prisao'): narrativa.append(f"O motivo alegado para a prisão foi: {self._obter_valor(dados, 'motivo_prisao')}.")
            if self._obter_valor(dados, 'fundamento_liberdade'): narrativa.append(f"O fundamento para o pedido de liberdade é: {self._obter_valor(dados, 'fundamento_liberdade')}.")
        
        # ... (lógicas para cível e trabalhista permanecem)
            
        return " ".join(filter(None, narrativa))

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str) -> List[str]:
        """Extrai os termos jurídicos chave dos fatos consolidados para guiar a pesquisa."""
        fundamentos = set()
        texto_analise = fatos.lower()

        # COMENTÁRIO: Adicionada a extração de fundamentos para os novos tipos.
        if contexto == "Queixa-Crime":
            fundamentos.update(["direito penal", "código penal", "queixa-crime", "código de processo penal"])
            if "honra" in texto_analise or "injúria" in texto_analise: fundamentos.add("crime de injúria")
            if "calúnia" in texto_analise: fundamentos.add("crime de calúnia")
            if "difamação" in texto_analise: fundamentos.add("crime de difamação")
        elif contexto == "Habeas Corpus":
            fundamentos.update(["habeas corpus", "direito constitucional", "direito de ir e vir", "artigo 5 CF", "código de processo penal"])
            if "constrangimento ilegal" in texto_analise: fundamentos.add("constrangimento ilegal")
            if "prisão preventiva" in texto_analise: fundamentos.add("requisitos da prisão preventiva")
        elif contexto == "Ação Trabalhista":
            fundamentos.update(["direito trabalhista", "CLT"])
            # ... (lógica trabalhista)
        elif "Consumidor" in contexto:
            fundamentos.update(["direito do consumidor", "Código de Defesa do Consumidor"])
            if "vício" in texto_analise or "defeito" in texto_analise: fundamentos.add("vício do produto CDC artigo 18")
            if "dano moral" in texto_analise: fundamentos.add("dano moral consumidor")
            
        return list(fundamentos) if fundamentos else ["direito civil", "código civil"]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        # A lógica de montagem é genérica e já funciona bem, mas podemos adicionar campos específicos se necessário.
        autor = {"nome": self._obter_valor(dados, 'autor_nome', "[NOME]"), "qualificacao": self._obter_valor(dados, 'autor_qualificacao', "[QUALIFICAÇÃO]")}
        reu = {"nome": self._obter_valor(dados, 'reu_nome', "[PARTE CONTRÁRIA]"), "qualificacao": self._obter_valor(dados, 'reu_qualificacao', "[QUALIFICAÇÃO]")}
        
        estrutura_final = {
            "autor": autor, "reu": reu, "tipo_acao": contexto, "fatos": fatos_consolidados,
            "pedidos": self._obter_valor(dados, 'pedido', "[PEDIDOS]"),
            "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}",
            "documentos": self._obter_valor(dados, 'documentos', ""),
            "fundamentos_necessarios": fundamentos,
            "competencia": "Justiça do Trabalho" if contexto == "Ação Trabalhista" else ("Justiça Criminal" if "Crime" in contexto else "Justiça Comum"),
        }
        
        # Adiciona dados específicos do contexto, se existirem
        if contexto == "Queixa-Crime":
            estrutura_final['vitima'] = {
                "nome": self._obter_valor(dados, 'nome_vitima'),
                "qualificacao": self._obter_valor(dados, 'qualificacao_vitima')
            }
        elif contexto == "Habeas Corpus":
             estrutura_final['paciente'] = autor # Em HC, o cliente é o "paciente"
             estrutura_final['autoridade_coatora'] = self._obter_valor(dados, 'autoridade_coatora')

        return estrutura_final
