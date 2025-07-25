# agente_redator_civel.py - Agente Especializado em Petições Cíveis

import json
import logging
import asyncio
import openai # Usa o SDK da OpenAI para compatibilidade
import os
from typing import Dict, Any
import re
from datetime import datetime

class AgenteRedatorCivel:
    """
    Agente Redator Otimizado e Especializado em Direito Cível e do Consumidor.
    """
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada para o AgenteRedatorCivel")
        
        # Configura o cliente OpenAI para usar a API da DeepSeek
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator CÍVEL inicializado com sucesso.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção."""
        print(f"📝 Gerando seção cível: {secao_nome}")
        try
            # A biblioteca da OpenAI v1+ não é nativamente assíncrona,
            # então executamos a chamada síncrona em uma thread separada para não bloquear.
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.4
            )
            resultado = response.choices[0].message.content.strip()
            return re.sub(r'^```html|```$', '', resultado).strip()
        except Exception as e:
            print(f"❌ ERRO na API para a seção {secao_nome}: {e}")
            return f"<h2>Erro ao Gerar Seção: {secao_nome}</h2><p>Ocorreu um erro ao tentar gerar o conteúdo para esta parte do documento. Detalhes: {e}</p>"

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        """Cria e executa todas as tarefas de redação em paralelo."""
        
        # Prompts altamente especializados para o contexto Cível/Consumidor.
        prompts = {
            "fatos": f"Redija a seção **DOS FATOS** de uma petição inicial cível. REQUISITOS: Use um tom formal e jurídico. Descreva a relação de consumo, o vício do produto e as tentativas de resolução. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}",
            "legislacao": f"Redija a subseção **DO DIREITO** para uma petição cível. Foque no Código de Defesa do Consumidor (Art. 18) e no Código Civil. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA DE LEGISLAÇÃO: {pesquisas.get('legislacao_formatada', 'N/A')}",
            "jurisprudencia": f"Redija a subseção sobre a **JURISPRUDÊNCIA** para uma petição cível. Cite precedentes sobre vício do produto e dano moral ao consumidor. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA DE JURISPRUDÊNCIA: {pesquisas.get('jurisprudencia_formatada', 'N/A')}",
            "doutrina": f"Redija a subseção sobre a **DOUTRINA** para uma petição cível. Discorra sobre a responsabilidade do fornecedor e a teoria do risco do empreendimento. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA DE DOUTRINA: {pesquisas.get('doutrina_formatada', 'N/A')}",
            "pedidos": f"Redija a seção **DOS PEDIDOS** de uma petição inicial cível. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}"
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        secao_fatos, sub_leg, sub_jur, sub_dout, secao_pedidos = await asyncio.gather(*tasks)
        
        secao_direito = f"<h2>DO DIREITO</h2>{sub_leg}{sub_jur}{sub_dout}"
        
        # Template HTML específico para a Justiça Comum Cível
        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>Petição Inicial Cível</title><style>body{{font-family:'Times New Roman',serif;line-height:1.8;text-align:justify;margin:3cm}}h1{{text-align:center;font-size:16pt}}h2{{text-align:left;font-size:14pt;margin-top:30px;font-weight:bold}}h3{{text-align:left;font-size:12pt;margin-top:20px;font-weight:bold}}p{{text-indent:2em;margin-bottom:15px}}blockquote{{margin-left:4cm;font-style:italic;border-left:2px solid #ccc;padding-left:10px}}.qualificacao p{{text-indent:0}}</style></head>
<body>
    <h1>EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA ___ VARA CÍVEL DA COMARCA DE {dados_formulario.get('reu', {}).get('cidade', 'CIDADE')} - {dados_formulario.get('reu', {}).get('estado', 'UF')}</h1>
    <div class="qualificacao" style="margin-top:50px;">
        <p><strong>{dados_formulario.get('autor',{}).get('nome','').upper()}</strong>, {dados_formulario.get('autor',{}).get('qualificacao','')}, residente e domiciliada em [ENDEREÇO A SER PREENCHIDO], vem, com o devido respeito, por intermédio de seu advogado que esta subscreve (procuração anexa), propor a presente</p>
        <h1 style="margin-top:20px;">AÇÃO CÍVEL</h1>
        <p>em face de <strong>{dados_formulario.get('reu',{}).get('nome','').upper()}</strong>, {dados_formulario.get('reu',{}).get('qualificacao','')}, pelos fatos e fundamentos a seguir expostos.</p>
    </div>
    {secao_fatos}
    {secao_direito}
    {secao_pedidos}
    <h2 style="font-size:12pt;text-align:left;">DO VALOR DA CAUSA</h2>
    <p>Dá-se à causa o valor de {dados_formulario.get('valor_causa', 'R$ 0,00')}.</p>
    <p style="margin-top:50px;">Nestes termos,<br>Pede deferimento.</p>
    <p style="text-align:center;margin-top:50px;">[Local], {datetime.now().strftime('%d de %B de %Y')}.</p>
    <p style="text-align:center;margin-top:80px;">_________________________________________<br>ADVOGADO<br>OAB/SP Nº XXX.XXX</p>
</body></html>
        """

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict) -> Dict:
        """Ponto de entrada síncrono que executa a lógica assíncrona."""
        try:
            documento_html = asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica))
            return {"documento_html": documento_html}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}
