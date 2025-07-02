# agente_tecnico_peticao.py - VERSÃO FINAL (O ESTRATEGISTA)

import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
# Importa a classe de pesquisa do seu outro arquivo
from pesquisa_juridica import PesquisaJuridica
# --- CORREÇÃO AQUI ---
# Importamos 'List' e 'Dict' para usar nas anotações de tipo das funções.
from typing import List, Dict

class AgenteTecnicoPeticao:
    """
    Agente especialista que analisa fatos, realiza pesquisa jurídica online
    e estrutura a tese e os fundamentos para uma petição.
    """
    def __init__(self, llm_api_key: str):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=llm_api_key, temperature=0.1)
        self.pesquisa = PesquisaJuridica()
        self.prompt_template = PromptTemplate(
            input_variables=["dados_processados", "pesquisa_juridica"],
            template="""
            Você é um advogado pesquisador sênior. Sua missão é analisar os fatos de um caso, junto com os resultados de uma pesquisa jurídica online, e construir a tese jurídica mais forte para uma petição.

            DADOS DO CASO:
            {dados_processados}

            PESQUISA ONLINE REALIZADA:
            {pesquisa_juridica}

            SUA TAREFA:
            Com base em TUDO, estruture uma análise jurídica detalhada em formato JSON. Seja preciso e técnico. Identifique o ramo do direito (Cível, Trabalhista, etc.), os artigos de lei e a jurisprudência mais relevante encontrada.

            FORMATO DE RESPOSTA (JSON VÁLIDO):
            {{
                "tipo_acao": "Ex: Reclamação Trabalhista com Pedido de Indenização por Danos Morais",
                "fundamentos_legais": [{{"lei": "CLT", "artigos": "Art. 483, 'd'", "descricao": "Rescisão indireta por descumprimento de obrigações contratuais."}}],
                "principios_juridicos": ["Princípio da Proteção ao Trabalhador"],
                "jurisprudencia_relevante": "Cite as decisões mais importantes encontradas na pesquisa sobre horas extras e assédio moral.",
                "analise_juridica_detalhada": "Parágrafo explicando como os fatos (horas extras não pagas, assédio) se conectam com a CLT e a jurisprudência para justificar a rescisão indireta e o dano moral."
            }}
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def analisar_dados(self, dados_processados: dict) -> dict:
        """
        Executa o processo completo de análise e pesquisa.
        """
        try:
            print("🧠 Etapa Técnica: Analisando e pesquisando...")
            
            temas_para_pesquisa = self._extrair_temas(dados_processados)
            
            pesquisa_juridica = self.pesquisa.pesquisar_fundamentos_juridicos(
                fundamentos=temas_para_pesquisa,
                tipo_acao=dados_processados.get("tipo_acao", "petição")
            )
            
            dados_formatados = json.dumps(dados_processados, indent=2, ensure_ascii=False)
            pesquisa_formatada = json.dumps(pesquisa_juridica, indent=2, ensure_ascii=False)
            
            resposta_llm = self.chain.invoke({
                "dados_processados": dados_formatados,
                "pesquisa_juridica": pesquisa_formatada
            })
            
            texto_gerado = resposta_llm['text']
            texto_limpo = texto_gerado.strip()
            if '```json' in texto_limpo: texto_limpo = texto_limpo.split('```json', 1)[-1]
            if '```' in texto_limpo: texto_limpo = texto_limpo.split('```', 1)[0]
            
            analise_final = json.loads(texto_limpo.strip())
            return analise_final

        except Exception as e:
            print(f"❌ Erro no Agente Técnico de Petição: {e}")
            return {"erro": "Falha na análise técnica da petição", "detalhes": str(e)}

    def _extrair_temas(self, dados_processados: dict) -> List[str]:
        fatos = dados_processados.get("fatos_peticao", "")
        pedido = dados_processados.get("pedido_peticao", "")
        texto_completo = (fatos + " " + pedido).lower()
        
        temas = set()
        if "hora extra" in texto_completo: temas.add("horas extras")
        if "assédio moral" in texto_completo: temas.add("assédio moral no trabalho")
        if "rescisão indireta" in texto_completo: temas.add("rescisão indireta do contrato de trabalho")
        
        return list(temas) if temas else ["direito geral"]