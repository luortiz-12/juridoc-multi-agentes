# agente_redator.py - Agente Redator com Pré-Processamento Inteligente e Citação Integral de Jurisprudência

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
    1. PRÉ-PROCESSAMENTO: Usa a IA para ler a pesquisa e criar blocos de fundamentação em HTML.
       - Para jurisprudência, a IA é instruída a citar os trechos mais importantes na íntegra.
       - Para legislação e doutrina, a IA cria textos autorais explicativos.
    2. REDAÇÃO FINAL: Usa a IA para redigir a petição, integrando e expandindo massivamente os blocos já prontos para atingir o tamanho alvo.
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
                    "estrategia_aplicada": "ia_pre_processamento_com_citacao_e_redacao_final",
                    "ia_funcionou": True
                }
            }
        
        except Exception as e:
            print(f"❌ ERRO GERAL na redação da petição: {e}")
            self.logger.error(f"Erro na redação da petição: {traceback.format_exc()}")
            return {"status": "erro", "erro": str(e), "dados_estruturados": dados_estruturados}

    def _calcular_score_qualidade(self, documento_html: str, dados_estruturados: Dict) -> int:
        """
        Calcula um score de qualidade básico para o documento gerado.
        """
        score = 50
        if len(documento_html) > 30000: score += 20
        elif len(documento_html) > 15000: score += 10
        
        if dados_estruturados.get('autor', {}).get('nome', '') in documento_html: score += 10
        if dados_estruturados.get('reu', {}).get('nome', '') in documento_html: score += 10
        
        if "DO DIREITO" in documento_html and len(documento_html.split("DO DIREITO")[1]) > 500: score += 10
            
        return min(score, 100)

    def _chamar_openai_com_log(self, prompt: str, model: str, max_tokens: int, temperature: float, timeout_especifico: int) -> str:
        """
        Método centralizado para chamar a API da OpenAI com logs e timeout.
        """
        try:
            print(f"🤖 Chamando OpenAI - Modelo: {model}, Tokens: {max_tokens}, Timeout: {timeout_especifico}s")
            print(f"📝 Prompt (início): {prompt[:200].strip().replace(chr(10), ' ')}...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=float(timeout_especifico)
            )
            
            resultado = response.choices[0].message.content.strip()
            resultado = re.sub(r'^```html|```$', '', resultado).strip()
            print(f"✅ OpenAI respondeu com sucesso ({len(resultado)} chars)")
            return resultado
        
        except Exception as e:
            print(f"❌ ERRO na chamada à API da OpenAI: {e}")
            self.logger.error(f"Erro na chamada OpenAI: {traceback.format_exc()}")
            raise e

    def processar_fundamentacao(self, pesquisas: List[Dict], tipo: str, contexto_caso: str) -> str:
        """
        ETAPA DE PRÉ-PROCESSAMENTO: Pega os trechos relevantes e os transforma em um bloco de HTML fundamentado,
        com citação integral para jurisprudência.
        """
        try:
            print(f"📄 Processando fundamentação de '{tipo}' com IA...")
            if not pesquisas: return ""

            conteudo_para_analise = ""
            for item in pesquisas[:2]:
                texto_completo = item.get('texto', '')
                if texto_completo:
                    conteudo_para_analise += f"\n\n--- Fonte: {item.get('url', 'N/A')} ---\n{texto_completo[:8000]}"

            if not conteudo_para_analise:
                return f"<div class='fundamentacao-item erro'><p>Nenhum conteúdo de {tipo} foi encontrado para análise.</p></div>"

            # --- AJUSTE CRÍTICO NO PROMPT ---
            # Instruções específicas para cada tipo de pesquisa.
            prompt_formatacao = f"""
            Você é um advogado sênior. Com base nos trechos de pesquisa abaixo, crie um bloco de fundamentação jurídica em HTML para uma petição.

            CONTEXTO DO CASO: "{contexto_caso[:1000]}"
            
            TRECHOS DE PESQUISA DE {tipo.upper()}:
            {conteudo_para_analise}

            INSTRUÇÕES DETALHADAS:
            - Se o tipo for 'legislação', explique os artigos de lei mais importantes e como se aplicam ao caso. NÃO transcreva os artigos literalmente.
            - Se o tipo for 'jurisprudência', sua tarefa principal é identificar a ementa e os trechos mais importantes do voto. **TRANSCREVA ESSES TRECHOS NA ÍNTEGRA** dentro de `<blockquote>`. Após a citação, adicione um parágrafo de análise conectando o precedente ao caso concreto.
            - Se o tipo for 'doutrina', resuma os principais argumentos dos autores e explique sua relevância para o caso.
            - Crie um texto jurídico coeso e autoral, em português do Brasil.
            - Retorne um único bloco de HTML formatado profissionalmente, usando a classe 'fundamentacao-item' para cada tópico.
            """
            return self._chamar_openai_com_log(prompt_formatacao, "gpt-4o", 2000, 0.3, 180)

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
        jurisprudencia_html = self.processar_fundamentacao(pesquisas.get('jurisprudencia', []), "jurisprudência", contexto_caso)
        doutrina_html = self.processar_fundamentacao(pesquisas.get('doutrina', []), "doutrina", contexto_caso)

        return self._gerar_documento_final_com_ia(dados_formulario, legislacao_html, jurisprudencia_html, doutrina_html)

    def _gerar_documento_final_com_ia(self, dados: Dict, legislacao: str, jurisprudencia: str, doutrina: str) -> str:
        """
        ETAPA FINAL: Monta a petição completa, integrando e expandindo massivamente os blocos de HTML.
        """
        print("🎯 Montando o documento final com IA...")
        
        prompt_documento = f"""
        Você é um advogado sênior, especialista em redação de petições. Sua tarefa é redigir uma petição inicial trabalhista EXTREMAMENTE DETALHADA, coesa, persuasiva e com pelo menos 30.000 caracteres.

        DADOS DO CASO:
        {json.dumps(dados, ensure_ascii=False, indent=2)}

        BLOCOS DE FUNDAMENTAÇÃO JURÍDICA (JÁ PROCESSADOS PELA IA):
        
        BLOCO DE LEGISLAÇÃO:
        {legislacao if legislacao else "<p>Nenhuma legislação específica foi processada.</p>"}

        BLOCO DE JURISPRUDÊNCIA:
        {jurisprudencia if jurisprudencia else "<p>Nenhuma jurisprudência específica foi processada.</p>"}

        BLOCO DE DOUTRINA:
        {doutrina if doutrina else "<p>Nenhuma doutrina específica foi processada.</p>"}

        INSTRUÇÕES FINAIS DE REDAÇÃO (MUITO IMPORTANTE):
        1. **META DE TAMANHO OBRIGATÓRIA:** O documento final deve ter **pelo menos 30.000 caracteres**. Para atingir esta meta, você deve ser prolixo, detalhista e exaustivo em CADA seção. Um documento curto será considerado uma falha.
        2. **EXPANSÃO DOS FATOS:** Na seção "DOS FATOS", não se limite a repetir os dados. Detalhe o cotidiano da Reclamante, descreva o ambiente de trabalho, narre exemplos específicos de humilhação e explique o impacto do não pagamento das horas extras na sua vida. Crie uma narrativa rica e detalhada.
        3. **EXPANSÃO DO DIREITO:** Na seção "DO DIREITO", integre os três blocos de fundamentação fornecidos. **NÃO os insira como placeholders**. Use o conteúdo deles (incluindo as citações em `<blockquote>` que você receberá) para construir uma argumentação jurídica robusta, detalhada e fluida, conectando cada ponto aos fatos do caso. Expanda a análise com seus conhecimentos. Crie subtópicos como "Da Rescisão Indireta", "Das Horas Extras Não Remuneradas", "Do Assédio Moral e o Dano Existencial".
        4. **DETALHAMENTO DOS PEDIDOS:** Na seção "DOS PEDIDOS", não apenas liste os pedidos. Crie um parágrafo para cada pedido, explicando o seu fundamento legal e o porquê de sua aplicação ao caso concreto.
        5. **FORMATAÇÃO ESTRITA:** **Retorne APENAS o código HTML completo do documento, começando com `<!DOCTYPE html>` e terminando com `</html>`. NÃO inclua explicações, comentários ou formatação de markdown como \`\`\`html.**
        6. **ESTILO:** Utilize um CSS inline profissional e elegante (font-family: 'Times New Roman', serif; line-height: 1.8; text-align: justify;).
        """
        
        return self._chamar_openai_com_log(prompt_documento, "gpt-4o", 4000, 0.4, 240)

    def _extrair_autor_doutrina(self, url: str) -> str:
        """Extrai o nome do autor/fonte a partir da URL."""
        if 'conjur.com.br' in url: return 'Consultor Jurídico'
        if 'migalhas.com.br' in url: return 'Migalhas'
        return 'Doutrina especializada'
