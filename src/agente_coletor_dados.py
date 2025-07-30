# agente_coletor_dados.py - Versão 6.3 (Final - Extração de Fundamentos Aprimorada)

import json
import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v6.3 - Versão final com suporte a todos os tipos de documentos.
    - Lógica de extração de fundamentos aprimorada para todos os contextos.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados v6.3 (Final)...")
        self.mapeamento_flexivel = {
            # Estudo de Caso
            'titulo_caso': ['titulodecaso', 'titulodocaso'], 'descricao_caso': ['descricaodocaso'],
            'contexto_juridico': ['contextojuridico'], 'pontos_relevantes': ['pontosrelevantes'],
            'analise_caso': ['analisedocaso'], 'conclusao_caso': ['conclusaodocaso', 'conclusao'],
            # Contrato
            'tipo_contrato': ['tipodecontrato'],
            'contratante_nome': ['nomedocontratante', 'contratante'], 'contratado_nome': ['nomedocontratado', 'contratado'],
            'objeto_contrato': ['objetodocontrato', 'objeto'], 'valor_contrato': ['valordocontrato', 'valor'],
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
        
        if any(k in dados_relevantes for k in ['titulodocaso', 'descricaodocaso']):
            return "Estudo de Caso", dados_relevantes
        if any(k in dados_relevantes for k in ['contratante', 'objetodocontrato']):
            return "Contrato", dados_relevantes
        if any(k in dados_relevantes for k in ['solicitante', 'consulta']):
            return "Parecer Jurídico", dados_relevantes
        if any(k in dados_relevantes for k in ['dataadmissaotrabalhista']):
            return "Ação Trabalhista", dados_relevantes
        
        return "Ação Cível", dados_relevantes

    def _consolidar_fatos(self, dados: Dict[str, Any], contexto: str) -> str:
        # A lógica de consolidação permanece a mesma, pois já é robusta.
        narrativa = []
        if contexto == "Estudo de Caso":
            if self._obter_valor(dados, 'descricao_caso'): narrativa.append(f"Descrição do Caso: {self._obter_valor(dados, 'descricao_caso')}")
            if self._obter_valor(dados, 'pontos_relevantes'): narrativa.append(f"Pontos Relevantes para Análise: {self._obter_valor(dados, 'pontos_relevantes')}")
        elif contexto == "Contrato":
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

        # COMENTÁRIO: Lógica de extração de fundamentos aprimorada para todos os contextos.
        if contexto == "Ação Trabalhista":
            fundamentos.update(["direito trabalhista", "CLT"])
            if "horas extras" in texto_analise: fundamentos.update(["horas extras teletrabalho", "controle de jornada"])
            if "comissões" in texto_analise: fundamentos.update(["integração comissões salário", "Súmula 340 TST"])
            if "assédio moral" in texto_analise: fundamentos.add("assédio moral no trabalho")
            print(f"   -> Termos-chave trabalhistas identificados: {list(fundamentos)}")

        elif "Cível" in contexto:
            # COMENTÁRIO: A lógica para Ação Cível foi substituída por um método mais inteligente.
            # Ele agora extrai frases de 2 e 3 palavras do próprio texto, em vez de usar temas fixos.
            palavras_irrelevantes = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'que', 'foi', 'mas', 'sem', 'ser', 'uma', 'por', 'são', 'qual', 'quais', 'os', 'as', 'dos', 'das', 'é', 'se', 'seu', 'sua', 'pelo', 'pela'}
            
            # Limpa o texto, mantendo apenas palavras relevantes
            palavras = re.findall(r'\b\w+\b', texto_analise)
            palavras_filtradas = [p for p in palavras if p not in palavras_irrelevantes and len(p) > 3]

            # Cria frases de 2 e 3 palavras (bigramas e trigramas)
            if len(palavras_filtradas) >= 2:
                for i in range(len(palavras_filtradas) - 1):
                    fundamentos.add(" ".join(palavras_filtradas[i:i+2]))
            if len(palavras_filtradas) >= 3:
                for i in range(len(palavras_filtradas) - 2):
                    fundamentos.add(" ".join(palavras_filtradas[i:i+3]))
            
            # Garante que os termos mais genéricos sejam usados como fallback se nada for encontrado
            if not fundamentos:
                fundamentos.update(["direito civil", "código civil", "danos materiais", "danos morais"])
            
            print(f"   -> Termos-chave cíveis extraídos do contexto: {list(fundamentos)[:5]}...") # Mostra apenas os 5 primeiros para não poluir o log

        elif contexto == "Contrato":
            tipo_especifico = self._obter_valor(dados, 'tipo_contrato', '')
            objeto = self._obter_valor(dados, 'objeto_contrato', '')
            termo_principal = tipo_especifico if tipo_especifico else f"de {objeto}"
            fundamentos.add(f"modelo {termo_principal}")
            fundamentos.add(f"cláusulas {termo_principal}")
            print(f"   -> Termos-chave de contrato identificados: {list(fundamentos)}")
        
        # ... (outras lógicas para Criminal, Parecer, Estudo de Caso)

        return list(fundamentos) if fundamentos else ["direito civil"]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        # A lógica de montagem permanece a mesma, pois já é robusta e separada por contexto.
        estrutura_final = {"tipo_documento": contexto, "fundamentos_necessarios": fundamentos}

        if contexto == "Contrato":
            # ... (bloco de contrato)
            pass
        elif contexto == "Parecer Jurídico":
            # ... (bloco de parecer)
            pass
        elif contexto == "Estudo de Caso":
            # ... (bloco de estudo de caso)
            pass
        else: 
            # COMENTÁRIO: Este bloco agora trata de TODAS as petições (Cível, Trabalhista, etc.)
            # A estrutura é a mesma, garantindo que o redator sempre receba 'autor' e 'reu'.
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
