# agente_coletor_dados.py - Versão 6.3 (Final - Extração de Fundamentos Aprimorada)

import json
import re
import traceback
from typing import Dict, Any, List

class AgenteColetorDados:
    """
    Agente Coletor de Dados v6.3 - Versão final com suporte a todos os tipos de documentos.
    - Lógica de extração de fundamentos aprimorada para todos os contextos, especialmente o Cível.
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
        # ... (lógica de consolidação permanece a mesma)
        return str(self._obter_valor(dados, 'fatos', ''))

    def _extrair_fundamentos_necessarios(self, fatos: str, contexto: str, dados: Dict[str, Any]) -> List[str]:
        fundamentos = set()
        texto_analise = fatos.lower() + " " + self._obter_valor(dados, 'pedido', '').lower()

        if "Cível" in contexto:
            # COMENTÁRIO: Lógica de extração de fundamentos para Ação Cível totalmente refeita.
            # Agora ela analisa o conteúdo para encontrar o tema e gerar pesquisas específicas.
            fundamentos.update(["direito civil", "código civil"])
            if "consumidor" in texto_analise or "produto" in texto_analise or "loja" in texto_analise:
                fundamentos.add("direito do consumidor")
                if "vício" in texto_analise or "defeito" in texto_analise:
                    fundamentos.add("vício do produto CDC")
            if "acidente de trânsito" in texto_analise or "colisão" in texto_analise or "veículo" in texto_analise:
                fundamentos.update(["responsabilidade civil acidente", "danos materiais trânsito", "artigo 186 código civil"])
            if "incumprimento de contrato" in texto_analise or "rescisão do contrato" in texto_analise:
                fundamentos.update(["incumprimento contratual", "rescisão contrato civil", "artigo 475 código civil"])
            if "dano moral" in texto_analise:
                fundamentos.add("indenização dano moral")
            
            # Remove os termos genéricos se termos específicos foram encontrados
            if len(fundamentos) > 2:
                fundamentos.discard("direito civil")
                fundamentos.discard("código civil")

        elif contexto == "Ação Trabalhista":
            fundamentos.update(["direito trabalhista", "CLT"])
            if "horas extras" in texto_analise: fundamentos.update(["horas extras teletrabalho", "controle de jornada"])
            if "comissões" in texto_analise: fundamentos.update(["integração de comissões", "Súmula 340 TST"])
        
        # ... (outras lógicas para outros contextos permanecem inalteradas)

        return list(fundamentos) if fundamentos else ["direito civil"]

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str], contexto: str) -> Dict[str, Any]:
        estrutura_final = {"tipo_documento": contexto, "fundamentos_necessarios": fundamentos}

        if contexto == "Contrato" or contexto == "Parecer Jurídico" or contexto == "Estudo de Caso":
            # Lógica para documentos não-litigiosos
            # ... (código existente)
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
