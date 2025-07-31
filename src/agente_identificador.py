# agente_identificador.py - Novo Agente Especializado em Identificar o Tipo de Documento

import re
from typing import Dict, Any, Tuple

class AgenteIdentificador:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber os dados brutos do formulário.
    - Analisar os campos preenchidos para determinar o tipo de documento.
    - Retornar apenas o tipo de documento identificado.
    """

    def __init__(self):
        print("🔎 Inicializando Agente Identificador...")
        # COMENTÁRIO: Este mapeamento contém apenas as chaves ÚNICAS que nos permitem
        # identificar o tipo de documento. Não precisamos de todos os campos aqui.
        self.mapeamento_identificacao = {
            "Estudo de Caso": ['titulodecaso', 'descricaodocaso', 'contextojuridico'],
            "Contrato": ['contratante', 'objetodocontrato', 'objeto', 'tipodecontrato'],
            "Parecer Jurídico": ['solicitante', 'consulta'],
            "Habeas Corpus": ['autoridadecoatorahabiescorpus', 'localdaprisaohabiescorpus'],
            "Queixa-Crime": ['datafatocriminal', 'descricaodocrime'],
            "Ação Trabalhista": ['dataadmissaotrabalhista', 'salariotrabalhista', 'motivosaidatrablhista'],
        }
        print("✅ Agente Identificador pronto.")

    def _normalizar_chave(self, chave: str) -> str:
        """Normaliza uma chave de dicionário para um formato padronizado."""
        return re.sub(r'[^a-z0-9]', '', str(chave).lower())

    def identificar_documento(self, dados_brutos_n8n: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ponto de entrada principal do agente. Recebe o JSON do N8N e retorna o tipo de documento.
        """
        try:
            print("--- INÍCIO DA IDENTIFICAÇÃO ---")
            dados_normalizados = {self._normalizar_chave(k): v for k, v in dados_brutos_n8n.items()}
            dados_relevantes = {k for k, v in dados_normalizados.items() if v is not None and str(v).strip() != ""}

            # COMENTÁRIO: O agente agora itera sobre as suas regras de identificação.
            # A ordem aqui define a prioridade.
            for tipo, chaves_identificadoras in self.mapeamento_identificacao.items():
                if any(chave in dados_relevantes for chave in chaves_identificadoras):
                    print(f"  -> Chaves encontradas que correspondem a: {tipo}")
                    print(f"✅ Tipo de Documento Identificado: {tipo}")
                    print("--- FIM DA IDENTIFICAÇÃO ---")
                    return {"status": "sucesso", "tipo_documento": tipo}

            # Se nenhuma regra corresponder, ele assume "Ação Cível" como padrão.
            tipo_documento = "Ação Cível"
            print(f"  -> Nenhuma chave específica encontrada. Assumindo o tipo padrão: {tipo_documento}")
            print(f"✅ Tipo de Documento Identificado: {tipo_documento}")
            print("--- FIM DA IDENTIFICAÇÃO ---")
            return {"status": "sucesso", "tipo_documento": tipo_documento}

        except Exception as e:
            print(f"❌ Erro crítico no Agente Identificador: {e}")
            return {"status": "erro", "erro": f"Falha ao identificar o tipo de documento: {e}"}

