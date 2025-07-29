# agente_redator_queixa_crime.py - Versão 2.0 (Com Ciclo de Feedback e Meta de 30k)

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

class AgenteRedatorQueixaCrime:
    """
    Agente Redator Especializado em Queixa-Crime.
    v2.0: Aceita feedback do Agente Validador para melhorar rascunhos e
    tem uma meta de geração de conteúdo de 30.000 caracteres.
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de QUEIXA-CRIME (v2.0 com Feedback) inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção específica."""
        print(f"📝 Gerando/Melhorando seção criminal: {secao_nome}")
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
                temperature=0.3
            )
            return re.sub(r'^```html|```$', '', response.choices[0].message.content.strip())
        except Exception as e:
            print(f"❌ ERRO na API para a seção {secao_nome}: {e}")
            return f"<h2>Erro ao Gerar Seção: {secao_nome}</h2><p>{e}</p>"

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> str:
        """Cria ou melhora as seções do documento em paralelo."""
        
        instrucao_formato = "Sua resposta DEVE ser um bloco de código HTML bem formatado. NÃO use Markdown (como `**` ou `*`). Para ênfase, use apenas tags HTML como `<strong>` para negrito."

        instrucao_melhoria = ""
        if recomendacoes:
            instrucao_melhoria = f"\n\nINSTRUÇÕES PARA MELHORIA: A versão anterior foi considerada insatisfatória. Reescreva e expanda significativamente o conteúdo para atender a seguinte recomendação: '{' '.join(recomendacoes)}'. Use o rascunho anterior como referência do que NÃO fazer.\nRASCUNHO ANTERIOR:\n{documento_anterior}"

        # COMENTÁRIO: Prompts modulares com requisitos de tamanho para atingir a meta de 30k.
        prompts = {
            "fatos": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a seção 'DOS FATOS' de uma queixa-crime. Seja extremamente detalhado, com no mínimo 10.000 caracteres. Descreva o crime, as circunstâncias, o local e a data. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>DOS FATOS</h2>.",
            "direito_tipificacao": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a subseção 'DA TIPIFICAÇÃO PENAL' para uma queixa-crime. Seja detalhado, com no mínimo 7.000 caracteres. Foque em tipificar o crime (ex: Calúnia, Art. 138 do Código Penal). CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('legislacao_formatada', 'N/A')}. Comece com <h3>Da Tipificação Penal</h3>.",
            "direito_autoria": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a subseção 'DA AUTORIA E MATERIALIDADE' para uma queixa-crime. Seja detalhado, com no mínimo 7.000 caracteres. Demonstre quem cometeu o crime e como o crime se materializou. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h3>Da Autoria e Materialidade</h3>.",
            "direito_procedibilidade": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a subseção 'DA PROCEDIBILIDADE' para uma queixa-crime. Seja detalhado, com no mínimo 7.000 caracteres. Explique a legitimidade da ação penal privada. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h3>Da Procedibilidade da Ação</h3>.",
            "pedidos": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a seção 'DOS PEDIDOS' de uma queixa-crime. Seja detalhado, com no mínimo 5.000 caracteres. Peça o recebimento da queixa, a citação do querelado e a condenação. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>DOS PEDIDOS</h2>."
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        secao_fatos, sub_tip, sub_aut, sub_proc, secao_pedidos = await asyncio.gather(*tasks)
        
        secao_direito = f"<h2>DO DIREITO</h2>{sub_tip}{sub_aut}{sub_proc}"
        
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

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> Dict:
        """Ponto de entrada síncrono que executa a lógica assíncrona, passando o feedback se existir."""
        try:
            documento_html = asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica, documento_anterior, recomendacoes))
            return {"documento_html": documento_html}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}
