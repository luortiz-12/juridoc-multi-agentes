# agente_coletor_dados.py - Versão 6.1 (Final - Suporte a todos os documentos)

import json
import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v6.1 - Versão final com suporte a todos os tipos de documentos.
    - Identifica Petições, Pareceres e Contratos.
    - Extrai fundamentos de forma especializada para cada tipo, incluindo o tipo específico de contrato.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v6.1 (Final)...")
        self.mapeamento_flexivel = {
            # Contrato
            'tipo_contrato': ['tipodecontrato'],
            'contratante_nome': ['nomedocontratante', 'contratante'], 'contratado_nome': ['nomedocontratado', 'contratado'],
            'objeto_contrato': ['objetodocontrato', 'objeto'], 'valor_contrato': ['valordocontrato', 'valor'],
            'forma_pagamento': ['formadepagamento'], 'prazos': ['prazos', 'prazosdepagamento'],
            'responsabilidades': ['responsabilidadesdaspartes'], 'penalidades': ['penalidadespordescumprimento'],
            'foro': ['forodeeleição', 'foro'],
            # Parecer
            'solicitante': ['solicitante'], 'assunto': ['assunto'], 'consulta': ['consulta'],
            'legislacao_aplicavel': ['legislacao', 'legislacaoaplicavel'], 'analise': ['analise'],
            # Petições
            'autor_nome': ['clientenome'], 'qualificacao_cliente': ['qualificacaocliente'],
            'reu_nome': ['nomedaparte'], 'qualificacao_reu': ['qualificacaoparte'],
            'fatos': ['fatos'], 'pedido': ['pedido'], 'valor_causa': ['valorcausa'],
            'data_admissao': ['dataadmissaotrabalhista'], 'salario': ['salariotrabalhista'],
            'data_fato_criminal': ['datafatocriminal'], 'local_fato_criminal': ['localfatocriminal'],
            'autoridade_coatora': ['autoridadecoatorahabiescorpus'], 'local_prisao': ['localdapisaohabiescorpus'],
        }
        print("✅ Agente Coletor pronto para processar todos os tipos de documentos.")

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
        
        if any(k in dados_relevantes for k in ['contratante', 'objetodocontrato', 'objeto', 'tipodecontrato']):
            return "Contrato", dados_relevantes
        if any(k in dados_relevantes for k in ['solicitante', 'consulta']):
            return "Parecer Jurídico", dados_relevantes
        if any(k in dados_relevantes for k in ['autoridadecoatorahabiescorpus']):
            return "Habeas Corpus", dados_relevantes
        if any(k in dados_relevantes for k in ['datafatocriminal']):
            return "Queixa-Crime", dados_relevantes
        if any(k in dados_relevantes for k in ['dataadmissaotrabalhista']):
            return "Ação Trabalhista", dados_relevantes
        
        return "Ação Cível", dados_relevantes

    def _consolidar_fatos(self, dados: Dict[str, Any], contexto: str) -> str:
        narrativa = []
        if contexto == "Contrato":
            return self._obter_valor(dados, 'objeto_contrato', '[Objeto do contrato não especificado]')
        elif contexto == "Parecer Jurídico":
            if self._obter_valor(dados, 'consulta'): narrativa.append(f"Consulta: {self._obter_valor(dados, 'consulta')}")
            if self._obter_valor(dados, 'analise'): narrativa.append(f"Análise Preliminar: {self._obter_valor(dados, 'analise')}")
        else: # Petições
            if self._obter_valor(dados, 'fatos'): narrativa.append(str(self._obter_valor(dados, 'fatos')))
            
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str, dados: Dict[str, Any]) -> List[str]:
        fundamentos = set()
        texto_analise = fatos.lower() + " " + self._obter_valor(dados, 'pedido', '').lower()

        if contexto == "Contrato":
            tipo_especifico = self._obter_valor(dados, 'tipo_contrato', '')
            objeto = self._obter_valor(dados, 'objeto_contrato', '')
            termo_principal = tipo_especifico if tipo_especifico else f"de {objeto}"
            fundamentos.add(f"modelo de {termo_principal}")
            fundamentos.add(f"cláusulas essenciais {termo_principal}")
        elif "Cível" in texto_analise:
            fundamentos.update(["direito civil", "código civil"])
            if "consumidor" in texto_analise or "produto" in texto_analise:
                fundamentos.add("direito do consumidor")
                if "vício" in texto_analise or "defeito" in texto_analise:
                    fundamentos.add("vício do produto CDC artigo 18")
            if "acidente de trânsito" in texto_analise:
                fundamentos.add("responsabilidade civil acidente de trânsito")
            if "dano moral" in texto_analise:
                fundamentos.add("dano moral")
        # ... (outras lógicas para outros contextos)

        palavras_irrelevantes = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'para', 'com', 'não'}
        fundamentos_filtrados = {f.strip() for f in fundamentos if f and f.lower() not in palavras_irrelevantes and len(f.strip()) > 2}
            
        return list(fundamentos_filtrados) if fundamentos_filtrados else ["direito civil"]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        """
        COMENTÁRIO: Esta função foi reestruturada com uma lógica if/elif/else clara.
        Cada tipo de documento tem seu próprio bloco de código para montar a estrutura de dados,
        garantindo que um não interfira com o outro.
        """
        estrutura_final = {"tipo_documento": contexto, "fundamentos_necessarios": fundamentos}

        if contexto == "Contrato":
            # COMENTÁRIO: Este bloco só é executado se o documento for um Contrato.
            estrutura_final['tipo_contrato_especifico'] = self._obter_valor(dados, 'tipo_contrato')
            estrutura_final['contratante'] = {"nome": self._obter_valor(dados, 'contratante_nome'), "cnpj": self._obter_valor(dados, 'contratante_cnpj'), "endereco": self._obter_valor(dados, 'contratante_endereco')}
            estrutura_final['contratado'] = {"nome": self._obter_valor(dados, 'contratado_nome'), "cnpj": self._obter_valor(dados, 'contratado_cnpj'), "endereco": self._obter_valor(dados, 'contratado_endereco')}
            estrutura_final.update({
                "objeto": fatos_consolidados, "valor": self._obter_valor(dados, 'valor_contrato'),
                "pagamento": self._obter_valor(dados, 'forma_pagamento'), "prazos": self._obter_valor(dados, 'prazos'),
                "responsabilidades": self._obter_valor(dados, 'responsabilidades'), "penalidades": self._obter_valor(dados, 'penalidades'),
                "foro": self._obter_valor(dados, 'foro')
            })
        elif contexto == "Parecer Jurídico":
            # COMENTÁRIO: Este bloco só é executado se o documento for um Parecer.
            estrutura_final.update({
                "solicitante": self._obter_valor(dados, 'solicitante'),
                "assunto": self._obter_valor(dados, 'assunto'),
            })
        else: 
            # COMENTÁRIO: Este bloco (else) trata de todos os outros tipos de documentos (Petições).
            estrutura_final['tipo_acao'] = contexto
            estrutura_final['fatos'] = fatos_consolidados
            estrutura_final.update({
                "autor": {"nome": self._obter_valor(dados, 'autor_nome'), "qualificacao": self._obter_valor(dados, 'qualificacao_cliente')},
                "reu": {"nome": self._obter_valor(dados, 'reu_nome'), "qualificacao": self._obter_valor(dados, 'qualificacao_reu')},
                "pedidos": self._obter_valor(dados, 'pedido'),
                "valor_causa": f"R$ {self._obter_valor(dados, 'valor_causa', '0.00')}"
            })
            if contexto == "Ação Trabalhista":
                 estrutura_final.update({
                    "data_admissao": self._obter_valor(dados, 'data_admissao'), "data_demissao": self._obter_valor(dados, 'data_demissao'),
                    "salario": self._obter_valor(dados, 'salario')
                })

        return estrutura_final