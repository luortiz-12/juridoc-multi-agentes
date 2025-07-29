# agente_coletor_dados.py - Versão 5.3 (Lógica de Fundamentos Aprimorada)

import json
import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v5.3 - Suporte a múltiplos tipos de documentos.
    - Lógica de extração de fundamentos aprimorada para ser mais sensível ao conteúdo.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v5.3 (Multi-Documento)...")
        self.mapeamento_flexivel = {
            'tipo_contrato': ['tipodecontrato'],
            'contratante_nome': ['nomedocontratante', 'contratante'], 'contratante_cpf': ['cpfdacontratante', 'cpfcontratante'],
            'contratante_rg': ['rgdocontratante', 'rgcontratante'], 'contratante_cnpj': ['cnpjdacontratante', 'cnpjcontratante'],
            'contratante_endereco': ['endereçodocontratante', 'endereçocontratante'],
            'contratado_nome': ['nomedocontratado', 'contratado'], 'contratado_cpf': ['cpfdacontratado', 'cpfcontratado'],
            'contratado_rg': ['rgdocontratado', 'rgcontratado'], 'contratado_cnpj': ['cnpjdacontratado', 'cnpjcontratado'],
            'contratado_endereco': ['endereçodocontratado', 'endereçocontratado'],
            'objeto_contrato': ['objetodocontrato', 'objeto'], 'valor_contrato': ['valordocontrato', 'valor'],
            'forma_pagamento': ['formadepagamento'], 'prazos': ['prazos', 'prazosdepagamento'],
            'responsabilidades': ['responsabilidadesdaspartes'], 'penalidades': ['penalidadespordescumprimento'],
            'foro': ['forodeeleição', 'foro'],
            'autor_nome': ['clientenome'], 'qualificacao_cliente': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte'], 'qualificacao_reu': ['qualificacaoparte'],
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
        
        texto_analise = (
            str(self._obter_valor(dados_relevantes, 'fatos', '')) + " " +
            str(self._obter_valor(dados_relevantes, 'pedido', '')) + " " +
            str(self._obter_valor(dados_relevantes, 'info_extra_civil', '')) + " " +
            str(self._obter_valor(dados_relevantes, 'info_extra_trabalhista', ''))
        ).lower()

        if any(k in dados_relevantes for k in ['contratante', 'objetodocontrato', 'objeto', 'valordocontrato', 'valor', 'tipodecontrato']):
            return "Contrato", dados_relevantes
        if any(k in dados_relevantes for k in ['solicitante', 'consulta']):
            return "Parecer Jurídico", dados_relevantes
        
        palavras_trabalhistas = ['clt', 'reclamante', 'vínculo empregatício', 'verbas rescisórias', 'demissão', 'admissão', 'teletrabalho']
        if any(k in dados_relevantes for k in ['dataadmissaotrabalhista', 'salariotrabalhista']) or any(p in texto_analise for p in palavras_trabalhistas):
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

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str, dados: Dict[str, Any]) -> List[str]:
        fundamentos = set()
        texto_analise = fatos.lower()

        if contexto == "Ação Trabalhista":
            # COMENTÁRIO: Lógica de extração aprimorada para ser mais sensível ao conteúdo.
            fundamentos.update(["direito trabalhista", "CLT"])
            if "pejotização" in texto_analise or "vínculo empregatício" in texto_analise:
                fundamentos.update(["reconhecimento de vínculo empregatício", "pejotização", "artigo 3º da CLT"])
            if "horas extras" in texto_analise:
                fundamentos.update(["horas extras teletrabalho", "controle de jornada", "CLT art. 62"])
            if "comissões" in texto_analise or "comissão" in texto_analise:
                fundamentos.update(["integração de comissões ao salário", "cálculo verbas rescisórias comissões", "Súmula 340 TST"])
            if "dano existencial" in texto_analise:
                fundamentos.add("dano existencial jornada excessiva")
            if "assédio moral" in texto_analise:
                fundamentos.update(["assédio moral", "danos morais"])
            if "doença ocupacional" in texto_analise:
                fundamentos.update(["doença ocupacional", "estabilidade acidentária"])
        
        elif "Consumidor" in contexto:
            fundamentos.update(["direito do consumidor", "Código de Defesa do Consumidor"])
            if "vício" in texto_analise or "defeito" in texto_analise:
                fundamentos.add("vício do produto CDC artigo 18")
            if "dano moral" in texto_analise:
                fundamentos.add("dano moral consumidor")
        
        palavras_irrelevantes = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'art', 'artigo'}
        fundamentos_filtrados = {f.strip() for f in fundamentos if f and f.lower() not in palavras_irrelevantes and len(f.strip()) > 2}
            
        return list(fundamentos_filtrados) if fundamentos_filtrados else ["direito civil", "código civil"]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        # ... (O resto da função permanece o mesmo)
        estrutura_final = {
            "tipo_documento": contexto,
            "fundamentos_necessarios": fundamentos
        }

        if "Parecer" in contexto:
            estrutura_final.update({
                "solicitante": self._obter_valor(dados, 'solicitante'),
                "assunto": self._obter_valor(dados, 'assunto'),
            })
        else:
            estrutura_final.update({
                "autor": {"nome": self._obter_valor(dados, 'autor_nome'), "qualificacao": self._obter_valor(dados, 'qualificacao_cliente')},
                "reu": {"nome": self._obter_valor(dados, 'reu_nome'), "qualificacao": self._obter_valor(dados, 'qualificacao_reu')},
                "pedidos": self._obter_valor(dados, 'pedido'),
                "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}"
            })
            if contexto == "Ação Trabalhista":
                estrutura_final.update({
                    "data_admissao": self._obter_valor(dados, 'data_admissao'), "data_demissao": self._obter_valor(dados, 'data_demissao'),
                    "salario": self._obter_valor(dados, 'salario'), "cargo": self._obter_valor(dados, 'cargo', "[CARGO]"),
                    "jornada": self._obter_valor(dados, 'jornada'), "motivo_saida": self._obter_valor(dados, 'motivo_saida')
                })

        return estrutura_final
