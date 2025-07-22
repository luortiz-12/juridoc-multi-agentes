# agente_redator.py - Agente Redator com Pré-Processamento Inteligente

import json
import logging
import openai
import os
from typing import Dict, List, Any
import re
from datetime import datetime
import traceback

class AgenteRedator:
    """
    Agente Redator Inteligente que implementa uma estratégia de duas etapas:
    1. PRÉ-PROCESSAMENTO: Usa a IA para ler a pesquisa completa e extrair apenas os trechos mais relevantes.
    2. REDAÇÃO FINAL: Usa a IA para redigir a petição, integrando os trechos já filtrados.
    Isso garante alta qualidade, evita perda de contexto e previne timeouts.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ ERRO: OPENAI_API_KEY não encontrada nas variáveis de ambiente")
            raise ValueError("OPENAI_API_KEY não configurada")
        
        print(f"✅ OPENAI_API_KEY encontrada: {api_key[:10]}...{api_key[-4:]}")
        
        self.client = openai.OpenAI(
            api_key=api_key,
            timeout=300.0
        )
        print("✅ Cliente OpenAI inicializado com sucesso.")

    def redigir_peticao_completa(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal que orquestra a geração da petição.
        """
        try:
            print("✍️ Iniciando redação inteligente da petição com IA...")
            
            documento_html = self.gerar_documento_html_puro(dados_estruturados, pesquisa_juridica)
            
            tamanho_documento = len(documento_html)
            score_qualidade = self._calcular_score_qualidade(documento_html, dados_estruturados)
            
            print(f"✅ Petição finalizada com IA: {tamanho_documento} caracteres")
            print(f"📊 Score de qualidade: {score_qualidade}")
            
            return {
                "status": "sucesso",
                "documento_html": documento_html,
                "dados_estruturados": dados_estruturados,
                "metadados": {
                    "timestamp": datetime.now().isoformat(),
                    "tamanho_caracteres": tamanho_documento,
                    "score_qualidade": score_qualidade,
                    "estrategia_aplicada": "ia_pre_processamento_e_redacao",
                    "ia_funcionou": True
                }
            }
        
        except Exception as e:
            print(f"❌ ERRO GERAL na redação da petição: {e}")
            self.logger.error(f"Erro na redação da petição: {traceback.format_exc()}")
            return {"status": "erro", "erro": str(e)}

    def _calcular_score_qualidade(self, documento_html: str, dados_estruturados: Dict) -> int:
        """
        Calcula um score de qualidade básico para o documento gerado.
        """
        score = 50
        if len(documento_html) > 30000: score += 20
        elif len(documento_html) > 20000: score += 10
        
        # Verifica se os nomes das partes foram inseridos
        if dados_estruturados.get('autor', {}).get('nome', '') in documento_html: score += 10
        if dados_estruturados.get('reu', {}).get('nome', '') in documento_html: score += 10
        
        # Verifica se a fundamentação foi minimamente preenchida
        if len(re.findall(r'fundamentacao-item', documento_html)) > 1: score += 10
            
        return min(score, 100)

    def _chamar_openai_com_log(self, prompt: str, model: str, max_tokens: int, temperature: float, timeout_especifico: int) -> str:
        """
        Método centralizado para chamar a API da OpenAI com logs e timeout.
        """
        try:
            print(f"🤖 Chamando OpenAI - Modelo: {model}, Tokens: {max_tokens}, Timeout: {timeout_especifico}s")
            print(f"📝 Prompt (início): {prompt[:150].strip().replace(chr(10), ' ')}...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=float(timeout_especifico)
            )
            
            resultado = response.choices[0].message.content.strip()
            print(f"✅ OpenAI respondeu com sucesso ({len(resultado)} chars)")
            return resultado
        
        except Exception as e:
            print(f"❌ ERRO na chamada à API da OpenAI: {e}")
            self.logger.error(f"Erro na chamada OpenAI: {traceback.format_exc()}")
            raise e

    def _extrair_conteudo_relevante(self, texto_completo: str, contexto_caso: str, tipo: str) -> str:
        """
        PRIMEIRA ETAPA DA IA: Filtra o conteúdo mais relevante de um documento de pesquisa.
        """
        print(f"🔍 Extraindo conteúdo relevante de '{tipo}'...")
        prompt = f"""
        Você é um assistente jurídico de elite. Sua tarefa é analisar o texto completo de um documento ({tipo}) e extrair APENAS os trechos mais relevantes para o caso em questão.

        CASO: "{contexto_caso[:1500]}"

        DOCUMENTO COMPLETO:
        ---
        {texto_completo}
        ---

        INSTRUÇÕES:
        - Se for legislação, extraia os artigos que se aplicam diretamente aos fatos.
        - Se for jurisprudência, extraia a ementa e os 2-3 parágrafos do voto que são cruciais para o caso.
        - Se for doutrina, extraia os 2-3 parágrafos que definem os conceitos-chave do caso.
        - Retorne APENAS os trechos extraídos, sem nenhuma explicação ou formatação adicional.
        """
        # Usamos um modelo mais rápido e um timeout menor para esta tarefa de extração
        return self._chamar_openai_com_log(prompt, "gpt-4-turbo", 1500, 0.1, 120)

    def processar_fundamentacao(self, pesquisas: List[Dict], tipo: str, contexto_caso: str) -> str:
        """
        SEGUNDA ETAPA DA IA: Pega os trechos relevantes e os transforma em um bloco de HTML fundamentado.
        """
        try:
            print(f"📄 Processando fundamentação de '{tipo}' com IA...")
            if not pesquisas: return ""

            conteudo_relevante_agregado = ""
            # Limita a análise aos 2 primeiros documentos para agilidade e custo
            for item in pesquisas[:2]:
                texto_completo = item.get('texto', '')
                if texto_completo:
                    trechos_relevantes = self._extrair_conteudo_relevante(texto_completo, contexto_caso, tipo)
                    conteudo_relevante_agregado += f"\n\n--- Fonte: {item.get('url', 'N/A')} ---\n{trechos_relevantes}"

            if not conteudo_relevante_agregado:
                return f"<div class='fundamentacao-item erro'><p>Nenhum conteúdo relevante de {tipo} foi encontrado para este caso.</p></div>"

            prompt_formatacao = f"""
            Você é um advogado sênior. Com base nos trechos relevantes abaixo, crie um bloco de fundamentação jurídica em HTML.

            CASO: "{contexto_caso[:1000]}"
            
            TRECHOS RELEVANTES DE {tipo.upper()}:
            {conteudo_relevante_agregado}

            INSTRUÇÕES:
            1. Crie um texto coeso e autoral, usando os trechos como base.
            2. Se for jurisprudência, use `<blockquote>` para citações diretas.
            3. Explique como cada ponto se aplica aos fatos do caso.
            4. Retorne um único bloco de HTML formatado com a classe 'fundamentacao-item'.
            """
            return self._chamar_openai_com_log(prompt_formatacao, "gpt-4", 2000, 0.3, 180)

        except Exception as e:
            print(f"❌ ERRO no processamento de {tipo}: {e}")
            return f"<div class='fundamentacao-item erro'><p>Ocorreu um erro ao processar a {tipo}. A argumentação se baseará nos princípios gerais do direito.</p></div>"

    def gerar_documento_html_puro(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        """
        Orquestra a análise, o pré-processamento e a geração final do documento HTML.
        """
        contexto_caso = f"Fatos: {dados_formulario.get('fatos', '')}. Pedidos: {dados_formulario.get('pedidos', '')}"
        
        print("🔄 Iniciando pré-processamento das fundamentações...")
        
        legislacao_html = self.processar_fundamentacao(pesquisas.get('legislacao', []), "legislação", contexto_caso)
        print("\n--- HTML GERADO (LEGISLAÇÃO) ---\n", legislacao_html, "\n---------------------------------\n")

        jurisprudencia_html = self.processar_fundamentacao(pesquisas.get('jurisprudencia', []), "jurisprudência", contexto_caso)
        print("\n--- HTML GERADO (JURISPRUDÊNCIA) ---\n", jurisprudencia_html, "\n---------------------------------\n")

        doutrina_html = self.processar_fundamentacao(pesquisas.get('doutrina', []), "doutrina", contexto_caso)
        print("\n--- HTML GERADO (DOUTRINA) ---\n", doutrina_html, "\n---------------------------------\n")

        return self._gerar_documento_final_com_ia(dados_formulario, legislacao_html, jurisprudencia_html, doutrina_html)

    def _gerar_documento_final_com_ia(self, dados: Dict, legislacao: str, jurisprudencia: str, doutrina: str) -> str:
        """
        ETAPA FINAL: Monta a petição completa, integrando os blocos de HTML já prontos.
        """
        print("🎯 Montando o documento final com IA...")
        
        prompt_documento = f"""
        Você é um advogado sênior, especialista em redação de petições. Sua tarefa é redigir uma petição inicial trabalhista completa, coesa, persuasiva e com pelo menos 30.000 caracteres.

        DADOS DO CASO:
        {json.dumps(dados, ensure_ascii=False, indent=2)}

        BLOCOS DE FUNDAMENTAÇÃO JURÍDICA (JÁ PROCESSADOS E FORMATADOS EM HTML):
        
        BLOCO DE LEGISLAÇÃO:
        {legislacao if legislacao else "<p>Nenhuma legislação específica foi processada.</p>"}

        BLOCO DE JURISPRUDÊNCIA:
        {jurisprudencia if jurisprudencia else "<p>Nenhuma jurisprudência específica foi processada.</p>"}

        BLOCO DE DOUTRINA:
        {doutrina if doutrina else "<p>Nenhuma doutrina específica foi processada.</p>"}

        INSTRUÇÕES FINAIS DE REDAÇÃO:
        1. Crie uma petição inicial completa com **pelo menos 30.000 caracteres**. Para isso, detalhe extensivamente cada seção.
        2. Use os dados do caso para preencher as seções de Qualificação e Fatos de forma muito detalhada.
        3. Na seção "DO DIREITO", integre os três blocos de fundamentação (Legislação, Jurisprudência, Doutrina) de forma natural e coesa. Expanda a análise, conectando os pontos e construindo uma narrativa jurídica robusta.
        4. Formule a seção "DOS PEDIDOS" de forma clara e objetiva.
        5. Retorne APENAS o código HTML completo do documento.
        6. Utilize um CSS inline profissional e elegante (font-family: 'Times New Roman', serif; line-height: 1.6;).
        """
        
        return self._chamar_openai_com_log(prompt_documento, "gpt-4-turbo", 4000, 0.4, 240)

    def _extrair_autor_doutrina(self, url: str) -> str:
        """Extrai o nome do autor/fonte a partir da URL."""
        if 'conjur.com.br' in url: return 'Consultor Jurídico'
        if 'migalhas.com.br' in url: return 'Migalhas'
        return 'Doutrina especializada'
