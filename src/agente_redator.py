# agente_redator.py - Versão adaptada para usar a API da DeepSeek via injeção de dependência

import json
import logging
# COMENTÁRIO: A importação foi corrigida para usar o nome correto da classe: 'DeepSeekAPI'.
from deepseek import DeepSeekAPI
import os
from typing import Dict, List, Any
import re
from datetime import datetime
import traceback

class AgenteRedator:
    """
    Agente Redator adaptado para usar os modelos da DeepSeek.
    Recebe a chave da API durante a inicialização.
    """
    
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        
        if not api_key:
            print("❌ ERRO: Nenhuma chave de API foi fornecida ao AgenteRedator.")
            raise ValueError("DEEPSEEK_API_KEY não configurada")
        
        self.api_key = api_key
        print(f"✅ Agente Redator recebeu a chave da API: {self.api_key[:5]}...{self.api_key[-4:]}")
        
        # COMENTÁRIO: A inicialização do cliente foi corrigida para usar a classe 'DeepSeekAPI' diretamente.
        self.client = DeepSeekAPI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1"
        )
        print("✅ Cliente DeepSeek inicializado com sucesso.")

    def redigir_peticao_completa(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print("✍️ Iniciando redação modular com a API DeepSeek...")
            documento_html = self.gerar_documento_html_puro(dados_estruturados, pesquisa_juridica)
            print(f"✅ Petição finalizada com DeepSeek: {len(documento_html)} caracteres")
            return {"documento_html": documento_html}
        
        except Exception as e:
            print(f"❌ ERRO GERAL na redação da petição: {e}")
            self.logger.error(f"Erro na redação da petição: {traceback.format_exc()}")
            return {"status": "erro", "erro": str(e), "dados_estruturados": dados_estruturados}

    def _chamar_api_com_log(self, prompt: str, model: str, max_tokens: int, temperature: float, timeout_especifico: int) -> str:
        try:
            print(f"🤖 Chamando API DeepSeek - Modelo: {model}, Tokens: {max_tokens}, Timeout: {timeout_especifico}s")
            print(f"📝 Prompt (início): {prompt[:250].strip().replace(chr(10), ' ')}...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=float(timeout_especifico)
            )
            
            resultado = response.choices[0].message.content.strip()

            refusal_phrases = ["i'm sorry", "i cannot", "i am unable", "não posso atender"]
            if any(phrase in resultado.lower() for phrase in refusal_phrases):
                print(f"❌ ERRO: A API se recusou a processar o prompt.")
                raise Exception("API Refusal: O modelo se recusou a gerar o conteúdo para esta seção.")

            resultado = re.sub(r'^```html|```$', '', resultado).strip()
            print(f"✅ DeepSeek respondeu com sucesso ({len(resultado)} chars)")
            return resultado
        
        except Exception as e:
            print(f"❌ ERRO na chamada à API da DeepSeek: {e}")
            self.logger.error(f"Erro na chamada DeepSeek: {traceback.format_exc()}")
            raise e

    def _gerar_secao_html(self, prompt: str, secao_nome: str) -> str:
        print(f"📝 Gerando seção: {secao_nome}")
        return self._chamar_api_com_log(prompt, "deepseek-chat", 4000, 0.4, 240)

    def gerar_documento_html_puro(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        print("📝 Iniciando redação das seções individuais...")

        prompt_fatos = f"""
        Redija a seção **DOS FATOS** de uma petição inicial.
        REQUISITOS:
        - Use um tom formal e jurídico.
        - Expanda a narrativa fornecida, adicionando detalhes para criar uma história coesa e persuasiva.
        - Mínimo de 8.000 caracteres.
        - DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        - Retorne APENAS o bloco de HTML para esta seção, começando com `<h2>DOS FATOS</h2>`.
        """
        secao_fatos_html = self._gerar_secao_html(prompt_fatos, "DOS FATOS")

        prompt_direito_legislacao = f"""
        Redija a subseção sobre a **FUNDAMENTAÇÃO LEGAL** para a seção "DO DIREITO".
        CONTEXTO E FATOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        FUNDAMENTOS JURÍDICOS IDENTIFICADOS PARA PESQUISA: {', '.join(dados_formulario.get('fundamentos_necessarios', []))}
        CONTEÚDO DA PESQUISA DE LEGISLAÇÃO (USE SE FOR RELEVANTE):
        {pesquisas.get('legislacao_formatada', 'Nenhuma legislação específica foi encontrada na pesquisa.')}
        INSTRUÇÕES:
        1. Baseie sua argumentação nos **fatos do caso** e nos **fundamentos identificados**.
        2. Se o conteúdo da pesquisa de legislação for útil e relevante, utilize-o para explicar os artigos de lei mais importantes e como se aplicam ao caso.
        3. **Se o conteúdo da pesquisa for irrelevante, genérico ou vazio, ignore-o.** Redija a fundamentação legal com base apenas nos fatos e em seu conhecimento geral sobre a legislação aplicável ao caso.
        4. Mínimo de 5.000 caracteres.
        5. Retorne APENAS o bloco de HTML, começando com `<h3>Da Fundamentação Legal</h3>`.
        """
        sub_direito_leg_html = self._gerar_secao_html(prompt_direito_legislacao, "DO DIREITO (LEGISLAÇÃO)")

        prompt_direito_jurisprudencia = f"""
        Redija a subseção sobre a **JURISPRUDÊNCIA APLICÁVEL**.
        CONTEXTO E FATOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        CONTEÚDO DA PESQUISA DE JURISPRUDÊNCIA (USE SE FOR RELEVANTE):
        {pesquisas.get('jurisprudencia_formatada', 'Nenhuma jurisprudência específica foi encontrada na pesquisa.')}
        INSTRUÇÕES:
        1. Se o conteúdo da pesquisa de jurisprudência contiver julgados relevantes, transcreva os trechos mais importantes dentro de `<blockquote>` e, após cada citação, adicione um parágrafo de análise conectando o precedente ao caso concreto.
        2. **Se o conteúdo da pesquisa for irrelevante ou vazio, ignore-o.** Em vez disso, redija um texto genérico explicando a importância da jurisprudência para o tema e mencione, com base no seu conhecimento geral, quais são os entendimentos consolidados dos tribunais sobre os fundamentos do caso.
        3. Mínimo de 5.000 caracteres.
        4. Retorne APENAS o bloco de HTML, começando com `<h3>Da Jurisprudência Aplicável</h3>`.
        """
        sub_direito_jur_html = self._gerar_secao_html(prompt_direito_jurisprudencia, "DO DIREITO (JURISPRUDÊNCIA)")

        prompt_direito_doutrina = f"""
        Redija a subseção sobre a **DOUTRINA** e o **DANO MORAL**.
        CONTEXTO E FATOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
        CONTEÚDO DA PESQUISA DE DOUTRINA (USE SE FOR RELEVANTE):
        {pesquisas.get('doutrina_formatada', 'Nenhuma doutrina específica foi encontrada na pesquisa.')}
        INSTRUÇÕES:
        1. Se o conteúdo da pesquisa de doutrina for relevante, resuma os principais argumentos dos autores para construir a tese do caso (ex: dano moral, vínculo empregatício, etc.).
        2. **Se o conteúdo da pesquisa for irrelevante ou vazio, ignore-o.** Redija a análise doutrinária com base apenas nos fatos e em seu conhecimento jurídico geral sobre os temas.
        3. Mínimo de 5.000 caracteres.
        4. Retorne APENAS o bloco de HTML, começando com `<h3>Da Análise Doutrinária</h3>`.
        """
        sub_direito_dout_html = self._gerar_secao_html(prompt_direito_doutrina, "DO DIREITO (DOUTRINA)")
        
        secao_direito_html = f"<h2>DO DIREITO</h2>{sub_direito_leg_html}{sub_direito_jur_html}{sub_direito_dout_html}"

        prompt_pedidos = f"""
        Redija a seção **DOS PEDIDOS** de uma petição inicial.
        REQUISITOS:
        - Crie uma lista (`<ul>` e `<li>`) detalhada.
        - Para cada item da lista, adicione um parágrafo (`<p>`) explicativo, detalhando o fundamento do pedido.
        - Mínimo de 5.000 caracteres.
        - DADOS DO CASO (use o campo 'pedidos' como base): {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}
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
    <h1>EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DA ___ VARA DO TRABALHO DE {dados_formulario.get('reu', {}).get('cidade', 'CIDADE COMPETENTE')} - {dados_formulario.get('reu', {}).get('estado', 'UF')}</h1>
    <div class="qualificacao" style="margin-top: 50px;">
        <p>
            <strong>{dados_formulario.get('autor', {}).get('nome', '').upper()}</strong>, {dados_formulario.get('autor', {}).get('qualificacao', '')}, residente e domiciliada em [ENDEREÇO A SER PREENCHIDO], vem, com o devido respeito, por intermédio de seu advogado que esta subscreve (procuração anexa), propor a presente
        </p>
        <h1 style="margin-top: 20px;">AÇÃO TRABALHISTA</h1>
        <p>
            em face de <strong>{dados_formulario.get('reu', {}).get('nome', '').upper()}</strong>, {dados_formulario.get('reu', {}).get('qualificacao', '')}, pelos fatos e fundamentos a seguir expostos.
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
