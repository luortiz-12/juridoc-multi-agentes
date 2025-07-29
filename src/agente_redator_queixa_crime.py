# agente_redator_queixa_crime.py - Agente Especializado em Queixa-Crime

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any
import re
from datetime import datetime

class AgenteRedatorQueixaCrime:
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de QUEIXA-CRIME inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        print(f"📝 Gerando seção criminal: {secao_nome}")
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
            "fatos": f"{instrucao_formato}\n\nRedija a seção 'DOS FATOS' de uma queixa-crime. Descreva o crime, as circunstâncias, o local e a data. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>DOS FATOS</h2>.",
            "direito": f"{instrucao_formato}\n\nRedija a seção 'DO DIREITO' de uma queixa-crime. Foque em tipificar o crime (ex: Calúnia, Art. 138 do Código Penal) e na legitimidade da ação penal privada. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('legislacao_formatada', 'N/A')}. Comece com <h2>DO DIREITO</h2>.",
            "pedidos": f"{instrucao_formato}\n\nRedija a seção 'DOS PEDIDOS' de uma queixa-crime. Peça o recebimento da queixa, a citação do querelado e a condenação nas penas do artigo correspondente. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>DOS PEDIDOS</h2>."
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        secao_fatos, secao_direito, secao_pedidos = await asyncio.gather(*tasks)
        
        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>Queixa-Crime</title><style>body{{font-family:'Times New Roman',serif;line-height:1.8;text-align:justify;margin:3cm}}h1{{text-align:center;font-size:16pt}}h2{{text-align:left;font-size:14pt;margin-top:30px;font-weight:bold}}p{{text-indent:2em;margin-bottom:15px}}.qualificacao p{{text-indent:0}}</style></head>
<body>
    <h1>EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CRIMINAL DA COMARCA DE {dados_formulario.get('reu', {}).get('cidade', 'CIDADE')} - {dados_formulario.get('reu', {}).get('estado', 'UF')}</h1>
    <div class="qualificacao" style="margin-top:50px;">
        <p><strong>{dados_formulario.get('autor',{}).get('nome','').upper()}</strong> (Querelante), {dados_formulario.get('autor',{}).get('qualificacao','')}, vem, por seu advogado, oferecer</p>
        <h1 style="margin-top:20px;">QUEIXA-CRIME</h1>
        <p>em face de <strong>{dados_formulario.get('reu',{}).get('nome','').upper()}</strong> (Querelado), {dados_formulario.get('reu',{}).get('qualificacao','')}, pelos fatos e fundamentos a seguir.</p>
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
