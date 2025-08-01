# agente_coletor_estudo_de_caso.py - v2.0 (Extração de Fundamentos Aprimorada)

import re
import traceback
from typing import Dict, Any, List

class AgenteColetorEstudoDeCaso:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber os dados brutos de um formulário já identificado como "Estudo de Caso".
    - Extrair os fundamentos jurídicos relevantes, criando frases de pesquisa curtas e contextuais.
    - Montar a estrutura de dados limpa para os próximos agentes.
    """

    def __init__(self):
        print("📊 Inicializando Agente Coletor de Dados de ESTUDO DE CASO (v2.0)...")
        self.mapeamento_flexivel = {
            'titulo_caso': ['titulodecaso', 'titulodocaso'],
            'descricao_caso': ['descricaodocaso'],
            'contexto_juridico': ['contextojuridico'],
            'pontos_relevantes': ['pontosrelevantes'],
            'analise_caso': ['analisedocaso'],
            'conclusao_caso': ['conclusaodocaso', 'conclusao'],
        }
        print("✅ Agente Coletor de ESTUDO DE CASO pronto.")

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
            fundamentos = self._extrair_fundamentos_necessarios(dados_normalizados)
            
            dados_estruturados = self._montar_estrutura_final(dados_normalizados, fatos_consolidados, fundamentos)
            
            return {"status": "sucesso", "dados_estruturados": dados_estruturados}
        except Exception as e:
            traceback.print_exc()
            return {"status": "erro", "erro": f"Falha no processamento dos dados do Estudo de Caso: {e}"}

    def _consolidar_fatos(self, dados: Dict[str, Any]) -> str:
        """Junta informações de múltiplos campos para criar uma narrativa de fatos unificada."""
        narrativa = []
        if self._obter_valor(dados, 'descricao_caso'):
            narrativa.append(f"Descrição do Caso: {self._obter_valor(dados, 'descricao_caso')}")
        if self._obter_valor(dados, 'pontos_relevantes'):
            narrativa.append(f"Pontos Relevantes para Análise: {self._obter_valor(dados, 'pontos_relevantes')}")
        return " ".join(narrativa)

    def _extrair_fundamentos_necessarios(self, dados: Dict[str, Any]) -> List[str]:
        """
        COMENTÁRIO: Lógica de extração de fundamentos totalmente refeita.
        Agora, ela cria frases curtas e contextuais em vez de palavras soltas ou frases longas.
        """
        fundamentos = set()
        
        titulo_caso = self._obter_valor(dados, 'titulo_caso', '')
        contexto_juridico = self._obter_valor(dados, 'contexto_juridico', '')
        pontos_relevantes = self._obter_valor(dados, 'pontos_relevantes', '')
        
        texto_completo = f"{titulo_caso} {contexto_juridico} {pontos_relevantes}"
        
        # Remove pontuação e texto dentro de parênteses para limpar o texto
        texto_limpo = re.sub(r'\(.*?\)', '', texto_completo).replace(',', '').replace('.', '').replace('?', '')
        
        palavras_irrelevantes = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'ser', 'uma', 'por', 'são', 'qual', 'quais', 'os', 'as', 'dos', 'das', 'é', 'que', 'se', 'análise', 'sobre', 'para', 'sua', 'suas', 'seu', 'seus'}
        palavras = [p for p in texto_limpo.split() if p.lower() not in palavras_irrelevantes and len(p) > 3]

        # Adiciona siglas importantes (ex: LGPD, CLT)
        siglas = re.findall(r'\b[A-Z]{3,}\b', f"{contexto_juridico}")
        fundamentos.update(siglas)

        # Cria frases de 2 e 3 palavras (bigramas e trigramas) a partir das palavras-chave
        if len(palavras) >= 2:
            for i in range(len(palavras) - 1):
                fundamentos.add(" ".join(palavras[i:i+2]))
        if len(palavras) >= 3:
            for i in range(len(palavras) - 2):
                fundamentos.add(" ".join(palavras[i:i+3]))
        
        # Se nenhuma frase foi criada, adiciona palavras-chave do assunto
        if not fundamentos and titulo_caso:
            fundamentos.update([p for p in titulo_caso.split() if p.lower() not in palavras_irrelevantes])

        # Seleciona os fundamentos mais relevantes (os mais longos costumam ser mais específicos)
        fundamentos_ordenados = sorted(list(fundamentos), key=len, reverse=True)
        
        return fundamentos_ordenados[:5] # Limita a no máximo 5 termos

    def _montar_estrutura_final(self, dados: Dict[str, Any], fatos_consolidados: str, fundamentos: List[str]) -> Dict[str, Any]:
        """Monta o dicionário final com os dados limpos e estruturados para os próximos agentes."""
        
        estrutura_final = {
            "tipo_documento": "Estudo de Caso",
            "tipo_acao": "Estudo de Caso",
            "fundamentos_necessarios": fundamentos,
            "fatos": fatos_consolidados,
            "titulo_caso": self._obter_valor(dados, 'titulo_caso'),
            "descricao_caso": self._obter_valor(dados, 'descricao_caso'),
            "contexto_juridico": self._obter_valor(dados, 'contexto_juridico'),
            "pontos_relevantes": self._obter_valor(dados, 'pontos_relevantes'),
            "analise_caso": self._obter_valor(dados, 'analise_caso'),
            "conclusao_caso": self._obter_valor(dados, 'conclusao_caso'),
        }
        return estrutura_final
