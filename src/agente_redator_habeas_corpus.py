# agente_redator_habeas_corpus.py - Agente Especializado em Habeas Corpus

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any
import re
from datetime import datetime

class AgenteRedatorHabeasCorpus:
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de HABEAS CORPUS inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        print(f"📝 Gerando seção de Habeas Corpus: {secao_nome}")
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat", messages=[{"role": "user", "content": prompt}],
                max_tokens=4096, temperature=0.3
            )
            return re.sub(r'^```html|```$', '', response.choices[0].message.content.strip())
        except Exception as e:
            return f"<h2>Erro ao Gerar Seção: {secao_nome}</h2><p>{e}</p>"

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        instrucao_formato = "Sua resposta DEVE ser um bloco de texto formatado usando APENAS as seguintes tags HTML: <h2>, <h3>, <p>, <strong>. NÃO use Markdown."
        
        prompts = {
            "fatos": f"{instrucao_formato}\n\nRedija a seção 'DOS FATOS' de um Habeas Corpus. Descreva a prisão, o constrangimento ilegal, a autoridade coatora e o motivo pelo qual a prisão é ilegal. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>DOS FATOS E DO CONSTRANGIMENTO ILEGAL</h2>.",
            "direito": f"{instrucao_formato}\n\nRedija a seção 'DO DIREITO' de um Habeas Corpus. Foque no direito à liberdade (Art. 5º, LXVIII, CF) e nos artigos do Código de Processo Penal sobre as hipóteses de soltura. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('legislacao_formatada', 'N/A')}. Comece com <h2>DO DIREITO E DO PEDIDO LIMINAR</h2>.",
            "pedidos": f"{instrucao_formato}\n\nRedija a seção 'DOS PEDIDOS' de um Habeas Corpus. Peça a concessão liminar da ordem para expedir o alvará de soltura e, no mérito, a confirmação da ordem. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>DOS PEDIDOS</h2>."
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        secao_fatos, secao_direito, secao_pedidos = await asyncio.gather(*tasks)
        
        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>Habeas Corpus</title><style>body{{font-family:'Times New Roman',serif;line-height:1.8;text-align:justify;margin:3cm}}h1{{text-align:center;font-size:16pt}}h2{{text-align:left;font-size:14pt;margin-top:30px;font-weight:bold}}p{{text-indent:2em;margin-bottom:15px}}.qualificacao p{{text-indent:0}}</style></head>
<body>
    <h1>EXCELENTÍSSIMO SENHOR DOUTOR DESEMBARGADOR PRESIDENTE DO EGRÉGIO TRIBUNAL DE JUSTIÇA DO ESTADO DE {dados_formulario.get('reu', {}).get('estado', 'UF')}</h1>
    <div class="qualificacao" style="margin-top:50px;">
        <p><strong>{dados_formulario.get('advogado_nome', '[NOME DO ADVOGADO]')}</strong>, (qualificação do advogado), impetrante, vem, respeitosamente, impetrar a presente</p>
        <h1 style="margin-top:20px;">ORDEM DE HABEAS CORPUS COM PEDIDO LIMINAR</h1>
        <p>em favor de <strong>{dados_formulario.get('paciente', {}).get('nome', '').upper()}</strong> (Paciente), {dados_formulario.get('paciente', {}).get('qualificacao', '')}, atualmente recolhido em {dados_formulario.get('local_prisao', '[LOCAL DA PRISÃO]')}, apontando como autoridade coatora o <strong>{dados_formulario.get('autoridade_coatora', '[AUTORIDADE COATORA]')}</strong>, pelos fatos e fundamentos a seguir.</p>
    </div>
    {secao_fatos}
    {secao_direito}
    {secao_pedidos}
    <p style="margin-top:50px;">Nestes termos,<br>Pede deferimento.</p>
    <p style="text-align:center;margin-top:50px;">[Local], {datetime.now().strftime('%d de %B de %Y')}.</p>
    <p style="text-align:center;margin-top:80px;">_________________________________________<br>ADVOGADO<br>OAB/SP Nº XXX.XXX</p>
</body></html>
        """

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict) -> Dict:
        try:
            return {"documento_html": asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica))}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}
