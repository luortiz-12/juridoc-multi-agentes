# agente_coletor_dados.py - Versão 3.3 (Lógica de Contexto e Fundamentos Aprimorada)

import json
import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v3.3 - Lógica de Contexto e Fundamentos Aprimorada.
    - Prioriza a análise de conteúdo dos campos 'fatos' e 'pedido' para identificar a área do direito.
    - Extrai fundamentos de pesquisa específicos para o contexto identificado.
    - É resiliente a "poluição de dados" de formulários.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v3.3 (N8N)...")
        self.mapeamento_flexivel = {
            'autor_nome': ['clientenome'], 'autor_qualificacao': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte', 'nomecontrariopeticao'], 'reu_qualificacao': ['qualificacao', 'qualificacaoparte', 'qualificacaocontrariopeticao'],
            'fatos': ['fatos'], 'pedido': ['pedido'], 'valor_causa': ['valorcausa'], 'documentos': ['documentos'],
            'info_extra_civil': ['infoextrascivil', 'informacaoextrapeticaocivil'],
            'info_extra_trabalhista': ['infoextratrabalhista', 'informacaoextratrabalhista'],
            'data_admissao': ['dataadmissaotrabalhista'], 'data_demissao': ['datademisaotrabalhista', 'datademissaopeticao'],
            'salario': ['salariotrabalhista'], 'jornada': ['jornadadetrabalho', 'jornadatrabalhista'],
            'motivo_saida': ['motivosaidatrablhista', 'motivosaidatrabalhista'],
            'verbas_pleiteadas': ['verbaspleiteadastrabalhista'], 'cargo': ['cargo']
        }
        print("✅ Agente Coletor pronto para processar dados do N8N.")

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
            print("📊 Iniciando coleta e processamento de dados do N8N...")
            dados_normalizados = {self._normalizar_chave(k): v for k, v in dados_brutos_n8n.items()}
            
            contexto, dados_relevantes = self._identificar_contexto_e_dados(dados_normalizados)
            print(f"🔍 Contexto jurídico identificado: {contexto}")

            fatos_consolidados = self._consolidar_fatos(dados_relevantes, contexto)
            
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
        dados_relevantes = {k: v for k, v in dados_normalizados.items() if v is not None and str(v).strip() != ""}
        
        texto_analise = (
            str(self._obter_valor(dados_relevantes, 'fatos', '')) + " " +
            str(self._obter_valor(dados_relevantes, 'pedido', '')) + " " +
            str(self._obter_valor(dados_relevantes, 'info_extra_civil', '')) + " " +
            str(self._obter_valor(dados_relevantes, 'info_extra_trabalhista', ''))
        ).lower()

        palavras_consumidor = ['consumidor', 'produto', 'defeito', 'vício', 'loja', 'comprou', 'restituição', 'troca', 'cdc']
        if any(palavra in texto_analise for palavra in palavras_consumidor):
            return "Ação Cível (Consumidor)", dados_relevantes

        palavras_trabalhistas = ['clt', 'reclamante', 'vínculo empregatício', 'verbas rescisórias', 'demissão', 'admissão']
        if any(palavra in texto_analise for palavra in palavras_trabalhistas):
            return "Ação Trabalhista", dados_relevantes

        return "Ação Cível", dados_relevantes

    def _consolidar_fatos(self, dados: Dict[str, Any], contexto: str) -> str:
        narrativa = []
        if self._obter_valor(dados, 'fatos'): narrativa.append(str(self._obter_valor(dados, 'fatos')))
        
        if contexto == "Ação Trabalhista":
            if self._obter_valor(dados, 'jornada'): narrativa.append(f"A jornada de trabalho era: {self._obter_valor(dados, 'jornada')}.")
            if self._obter_valor(dados, 'motivo_saida'): narrativa.append(f"O motivo da saída foi: {self._obter_valor(dados, 'motivo_saida')}.")
            if self._obter_valor(dados, 'info_extra_trabalhista'): narrativa.append(f"Informações adicionais: {self._obter_valor(dados, 'info_extra_trabalhista')}.")
        elif "Cível" in contexto:
            if self._obter_valor(dados, 'info_extra_civil'): narrativa.append(f"Informações adicionais: {self._obter_valor(dados, 'info_extra_civil')}.")
            
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str) -> List[str]:
        # COMENTÁRIO: Lógica de extração de fundamentos totalmente refeita para ser sensível ao contexto.
        fundamentos = set()
        texto_analise = fatos.lower()

        if contexto == "Ação Trabalhista":
            fundamentos.update(["direito trabalhista", "CLT"])
            if "pejotização" in texto_analise or "vínculo empregatício" in texto_analise:
                fundamentos.update(["reconhecimento de vínculo empregatício", "pejotização", "artigo 3º da CLT"])
            if "horas extras" in texto_analise:
                fundamentos.update(["horas extras", "CLT art. 59"])
            if "assédio moral" in texto_analise:
                fundamentos.update(["assédio moral", "danos morais"])
            if "doença ocupacional" in texto_analise:
                fundamentos.update(["doença ocupacional", "estabilidade acidentária", "Lei 8.213/91"])
        
        elif "Consumidor" in contexto:
            fundamentos.update(["direito do consumidor", "Código de Defesa do Consumidor"])
            if "vício" in texto_analise or "defeito" in texto_analise:
                fundamentos.add("vício do produto CDC artigo 18")
            if "dano moral" in texto_analise or "descaso" in texto_analise:
                fundamentos.add("dano moral consumidor")
        
        # Fallback genérico se nenhuma palavra-chave específica for encontrada
        if not fundamentos:
            if contexto == "Ação Trabalhista":
                return ["direito trabalhista", "verbas rescisórias"]
            else:
                return ["direito civil", "código civil"]
            
        return list(fundamentos)

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        autor = {"nome": self._obter_valor(dados, 'autor_nome', "[AUTOR]"), "qualificacao": self._obter_valor(dados, 'autor_qualificacao', "[QUALIFICAÇÃO]")}
        reu = {"nome": self._obter_valor(dados, 'reu_nome', "[RÉU]"), "qualificacao": self._obter_valor(dados, 'reu_qualificacao', "[QUALIFICAÇÃO]")}
        
        estrutura_final = {
            "autor": autor, "reu": reu, "tipo_acao": contexto, "fatos": fatos_consolidados,
            "pedidos": self._obter_valor(dados, 'pedido', "[PEDIDOS]"),
            "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}",
            "documentos": self._obter_valor(dados, 'documentos', ""),
            "fundamentos_necessarios": fundamentos,
            "competencia": "Justiça do Trabalho" if contexto == "Ação Trabalhista" else "Justiça Comum",
            "observacoes": f"Documentos anexos: {self._obter_valor(dados, 'documentos', 'N/A')}",
            "urgencia": False
        }
        
        if contexto == "Ação Trabalhista":
            estrutura_final.update({
                "data_admissao": self._obter_valor(dados, 'data_admissao'), "data_demissao": self._obter_valor(dados, 'data_demissao'),
                "salario": self._obter_valor(dados, 'salario'), "cargo": self._obter_valor(dados, 'cargo', "[CARGO]"),
                "jornada": self._obter_valor(dados, 'jornada'), "motivo_saida": self._obter_valor(dados, 'motivo_saida')
            })

        return estrutura_final
