# agente_redator.py - Agente Redator com Geração Modular e Granular

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
    Agente Redator com arquitetura modular de alta performance:
    1. PRÉ-PROCESSAMENTO: Analisa a pesquisa e cria blocos de fundamentação em HTML,
       citando jurisprudência na íntegra quando necessário.
    2. REDAÇÃO MODULAR: Gera cada seção da petição (Fatos, Direito, Pedidos) com chamadas
       de IA dedicadas. A seção "DO DIREITO" é subdividida em três chamadas granulares
       para garantir profundidade e evitar sobrecarga da IA.
    3. MONTAGEM FINAL: Concatena as seções geradas em um único documento HTML coeso.
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
        try:
            print("✍️ Iniciando redação modular e granular da petição com IA...")
            
            documento_html = self.gerar_documento_html_puro(dados_estruturados, pesquisa_juridica)
            
            tamanho_documento = len(documento_html)
            score_qualidade = self._calcular_score_qualidade(documento_html, dados_estruturados)
            
            print(f"✅ Petição finalizada com IA: {tamanho_documento} caracteres")
            print(f"📊 Score de qualidade: {score_qualidade}")
            
            # AJUSTE: Retornar apenas o documento HTML em um JSON simples, conforme solicitado.
            return {
                "documento_html": documento_html
            }
        
        except Exception as e:
            print(f"❌ ERRO GERAL na redação da petição: {e}")
            self.logger.error(f"Erro na redação da petição: {traceback.format_exc()}")
            return {"status": "erro", "erro": str(e), "dados_estruturados": dados_estruturados}

    def _calcular_score_qualidade(self, documento_html: str, dados_estruturados: Dict) -> int:
        score = 50
        if len(documento_html) > 30000: score += 20
        elif len(documento_html) > 15000: score += 10
        
        if dados_estruturados.get('autor', {}).get('nome', '') in documento_html: score += 10
        if dados_estruturados.get('reu', {}).get('nome', '') in documento_html: score += 10
        
        if "DO DIREITO" in documento_html and len(documento_html.split("DO DIREITO")[1]) > 1000: score += 10
            
        return min(score, 100)

    def _chamar_openai_com_log(self, prompt: str, model: str, max_tokens: int, temperature: float, timeout_especifico: int) -> str:
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
        try:
            print(f"📄 Processando fundamentação de '{tipo}' com IA...")
            if not pesquisas: return ""

            conteudo_para_analise = ""
            for item in pesquisas[:2]:
                texto_completo = item.get('texto', '')
                if texto_completo:
                    conteudo_para_analise += f"\n\n--- Fonte: {item.get('url', 'N/A')} ---\n{texto_completo[:8000]}"

            if not conteudo_para_analise:
                return f"<p>Nenhum conteúdo de {tipo} foi encontrado para análise.</p>"

            prompt_formatacao = f"""
            Você é um advogado sênior. Com base nos trechos de pesquisa abaixo, crie um bloco de fundamentação jurídica em HTML para uma petição.

            CONTEXTO DO CASO: "{contexto_caso[:1000]}"
            TRECHOS DE PESQUISA DE {tipo.upper()}:
            {conteudo_para_analise}

            INSTRUÇÕES DETALHADAS:
            - Se o tipo for 'legislação', explique os artigos de lei mais importantes e como se aplicam ao caso. NÃO transcreva os artigos literalmente.
            - Se o tipo for 'jurisprudência', sua tarefa principal é identificar a ementa e os trechos mais importantes do voto. **TRANSCREVA ESSES TRECHOS NA ÍNTEGRA** dentro de `<blockquote>`. Após a citação, adicione um parágrafo de análise conectando o precedente ao caso concreto.
            - Se o tipo for 'doutrina', resuma os principais argumentos dos autores e explique sua relevância para o caso.
            - Crie um texto jurídico coeso e autoral.
            - Retorne um único bloco de HTML formatado profissionalmente.
            """
            return self._chamar_openai_com_log(prompt_formatacao, "gpt-4o", 2000, 0.3, 180)

        except Exception as e:
            print(f"❌ ERRO no processamento de {tipo}: {e}")
            return f"<div class='fundamentacao-item erro'><p>Ocorreu um erro ao processar a {tipo}.</p></div>"

    def _gerar_secao_html(self, prompt: str, secao_nome: str) -> str:
        """Função genérica para gerar uma seção da petição."""
        print(f"📝 Gerando seção: {secao_nome}")
        return self._chamar_openai_com_log(prompt, "gpt-4o", 4000, 0.4, 240)

    def gerar_documento_html_puro(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        contexto_caso = f"Fatos: {dados_formulario.get('fatos', '')}. Pedidos: {dados_formulario.get('pedidos', '')}"
        
        print("🔄 Iniciando pré-processamento das fundamentações...")
        legislacao_html = self.processar_fundamentacao(pesquisas.get('legislacao', []), "legislação", contexto_caso)
        jurisprudencia_html = self.processar_fundamentacao(pesquisas.get('jurisprudencia', []), "jurisprudência", contexto_caso)
        doutrina_html = self.processar_fundamentacao(pesquisas.get('doutrina', []), "doutrina", contexto_caso)

        print("📝 Iniciando redação das seções individuais...")

        prompt_fatos = f"""
        Redija a seção **DOS FATOS** de uma petição inicial trabalhista.
        REQUISITOS:
        - Mínimo de **8.000 caracteres**. Seja prolixo e detalhista.
        - Narre o cotidiano da Reclamante, com exemplos vívidos de humilhação e o impacto financeiro da falta de pagamento das horas extras.
        - DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        - Retorne APENAS o bloco de HTML para esta seção, começando com `<h2>DOS FATOS</h2>`.
        """
        secao_fatos_html = self._gerar_secao_html(prompt_fatos, "DOS FATOS")

        # --- GERAÇÃO GRANULAR DA SEÇÃO "DO DIREITO" ---
        prompt_direito_legislacao = f"""
        Redija a subseção sobre a **FUNDAMENTAÇÃO LEGAL** para a seção "DO DIREITO".
        REQUISITOS:
        - Mínimo de **5.000 caracteres**.
        - Discorra detalhadamente sobre a rescisão indireta (art. 483 CLT) e horas extras (art. 59 CLT), conectando cada artigo aos fatos do caso.
        - DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        - BLOCO DE LEGISLAÇÃO PRÉ-PROCESSADO: {legislacao_html}
        - Retorne APENAS o bloco de HTML, começando com `<h3>Da Fundamentação Legal: Violações Contratuais Graves</h3>`.
        """
        sub_direito_leg_html = self._gerar_secao_html(prompt_direito_legislacao, "DO DIREITO (LEGISLAÇÃO)")

        prompt_direito_jurisprudencia = f"""
        Redija a subseção sobre a **JURISPRUDÊNCIA APLICÁVEL** para a seção "DO DIREITO".
        REQUISITOS:
        - Mínimo de **5.000 caracteres**.
        - Integre as citações da jurisprudência (`<blockquote>`) fornecidas, analise cada uma e explique como reforçam o pedido da Reclamante.
        - DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        - BLOCO DE JURISPRUDÊNCIA PRÉ-PROCESSADO: {jurisprudencia_html}
        - Retorne APENAS o bloco de HTML, começando com `<h3>Da Jurisprudência Aplicável ao Caso</h3>`.
        """
        sub_direito_jur_html = self._gerar_secao_html(prompt_direito_jurisprudencia, "DO DIREITO (JURISPRUDÊNCIA)")

        prompt_direito_doutrina = f"""
        Redija a subseção sobre a **DOUTRINA** e o **DANO MORAL** para a seção "DO DIREITO".
        REQUISITOS:
        - Mínimo de **5.000 caracteres**.
        - Use os conceitos doutrinários para construir a tese do assédio moral e do dano existencial.
        - DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        - BLOCO DE DOUTRINA PRÉ-PROCESSADO: {doutrina_html}
        - Retorne APENAS o bloco de HTML, começando com `<h3>Do Assédio Moral e do Dano Existencial: Análise Doutrinária</h3>`.
        """
        sub_direito_dout_html = self._gerar_secao_html(prompt_direito_doutrina, "DO DIREITO (DOUTRINA)")
        
        secao_direito_html = f"<h2>DO DIREITO</h2>{sub_direito_leg_html}{sub_direito_jur_html}{sub_direito_dout_html}"

        prompt_pedidos = f"""
        Redija a seção **DOS PEDIDOS** de uma petição inicial trabalhista.
        REQUISITOS:
        - Mínimo de **5.000 caracteres**.
        - Para cada pedido, crie um item de lista (`<li>`) e um parágrafo explicativo detalhando o fundamento legal.
        - DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        - Retorne APENAS o bloco de HTML, começando com `<h2>DOS PEDIDOS</h2>`.
        """
        secao_pedidos_html = self._gerar_secao_html(prompt_pedidos, "DOS PEDIDOS")

        print("🧩 Montando o documento final...")
        
        documento_final_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Petição Inicial Trabalhista</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; line-height: 1.8; text-align: justify; margin: 3cm; }}
        h1 {{ text-align: center; font-size: 16pt; }}
        h2 {{ text-align: left; font-size: 14pt; margin-top: 30px; font-weight: bold; }}
        h3 {{ text-align: left; font-size: 12pt; margin-top: 20px; font-weight: bold; }}
        p {{ text-indent: 2em; margin-bottom: 15px; }}
        blockquote {{ margin-left: 4cm; font-style: italic; border-left: 2px solid #ccc; padding-left: 10px; }}
        .qualificacao p {{ text-indent: 0; }}
    </style>
</head>
<body>
    <h1>EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DA ___ VARA DO TRABALHO DE SÃO PAULO - SP</h1>
    <div class="qualificacao" style="margin-top: 50px;">
        <p>
            <strong>{dados_formulario.get('autor', {}).get('nome', '').upper()}</strong>, {dados_formulario.get('autor', {}).get('qualificacao', '')}, residente e domiciliada em {dados_formulario.get('autor', {}).get('endereco', '[ENDEREÇO A SER PREENCHIDO]')}, vem, com o devido respeito, por intermédio de seu advogado que esta subscreve (procuração anexa), propor a presente
        </p>
        <h1 style="margin-top: 20px;">AÇÃO TRABALHISTA</h1>
        <p>
            em face de <strong>{dados_formulario.get('reu', {}).get('nome', '').upper()}</strong>, {dados_formulario.get('reu', {}).get('qualificacao', '')}, com sede {dados_formulario.get('reu', {}).get('endereco', '')}, pelos fatos e fundamentos a seguir expostos.
        </p>
    </div>
    {secao_fatos_html}
    {secao_direito_html}
    {secao_pedidos_html}
    <h2 style="font-size: 12pt; text-align:left;">DO VALOR DA CAUSA</h2>
    <p>Dá-se à causa o valor de {dados_formulario.get('valor_causa', 'R$ 0,00')}.</p>
    <p style="margin-top: 50px;">Nestes termos,<br>Pede deferimento.</p>
    <p style="text-align: center; margin-top: 50px;">[Local], {datetime.now().strftime('%d de %B de %Y')}.</p>
    <p style="text-align: center; margin-top: 80px;">_________________________________________<br>ADVOGADO<br>OAB/SP Nº XXX.XXX</p>
</body>
</html>
        """
        return documento_final_html.strip()
