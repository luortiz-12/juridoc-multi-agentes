# agente_redator_trabalhista.py - Versão 4.1 (Com Prompts Rígidos Anti-Alucinação)

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

class AgenteRedatorTrabalhista:
    """
    Agente Redator Especializado em Direito do Trabalho.
    v4.1: Utiliza prompts rígidos para garantir a fidelidade aos dados do formulário
    e evitar a invenção de fatos ("alucinação").
    """
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator TRABALHISTA (v4.1 com Prompts Rígidos) inicializado com sucesso.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção específica."""
        print(f"📝 Gerando/Melhorando seção trabalhista: {secao_nome}")
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
                temperature=0.4
            )
            resultado = response.choices[0].message.content.strip()
            return re.sub(r'^```html|```$', '', resultado).strip()
        except Exception as e:
            print(f"❌ ERRO na API para a seção {secao_nome}: {e}")
            return f"<h2>Erro ao Gerar Seção: {secao_nome}</h2><p>{e}</p>"

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> str:
        """Cria ou melhora as seções do documento em paralelo."""
        
        instrucao_formato = "Sua resposta DEVE ser um bloco de código HTML bem formatado. NÃO use Markdown (como `**` ou `*`). Para ênfase, use apenas tags HTML como `<strong>` para negrito."

        # COMENTÁRIO: Esta é a nova instrução crucial para evitar que a IA invente dados.
        instrucao_fidelidade = "ATENÇÃO: Sua tarefa é redigir um texto jurídico. Você DEVE se basear ESTRITAMENTE nos dados fornecidos no JSON 'DADOS DO CASO' e na 'PESQUISA' jurídica. Use seu conhecimento e criatividade para expandir e detalhar a história, conectando os fatos com os fundamentos legais encontrados na pesquisa. NÃO invente nomes, valores, datas ou qualquer fato que contradiga os dados fornecidos."

        instrucao_melhoria = ""
        if recomendacoes:
            instrucao_melhoria = f"\n\nINSTRUÇÕES PARA MELHORIA: A versão anterior foi considerada insatisfatória. Reescreva e expanda significativamente o conteúdo para atender a seguinte recomendação: '{' '.join(recomendacoes)}'. Use o rascunho anterior como referência do que NÃO fazer.\nRASCUNHO ANTERIOR:\n{documento_anterior}"

        prompts = {
            "fatos": f"{instrucao_formato}\n\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a seção 'DOS FATOS' de uma petição inicial trabalhista. Seja extremamente detalhado, com no mínimo 10.000 caracteres. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece sua resposta com <h2>DOS FATOS</h2>.",
            "legislacao": f"{instrucao_formato}\n\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a subseção 'DA FUNDAMENTAÇÃO LEGAL' para uma petição trabalhista. Seja detalhado, com no mínimo 7.000 caracteres. Use os dados da pesquisa para fundamentar. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('legislacao_formatada', 'N/A')}. Comece sua resposta com <h3>Da Fundamentação Legal</h3>.",
            "jurisprudencia": f"{instrucao_formato}\n\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a subseção sobre a 'JURISPRUDÊNCIA APLICÁVEL' para uma petição trabalhista. Seja detalhado, com no mínimo 7.000 caracteres. Use os dados da pesquisa para citar precedentes. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('jurisprudencia_formatada', 'N/A')}. Comece sua resposta com <h3>Da Jurisprudência Aplicável</h3>.",
            "doutrina": f"{instrucao_formato}\n\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a subseção sobre a 'ANÁLISE DOUTRINÁRIA' para uma petição trabalhista. Seja detalhado, com no mínimo 7.000 caracteres. Use os dados da pesquisa. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('doutrina_formatada', 'N/A')}. Comece sua resposta com <h3>Da Análise Doutrinária</h3>.",
            "pedidos": f"{instrucao_formato}\n\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a seção 'DOS PEDIDOS' de uma petição inicial trabalhista. Seja detalhado, com no mínimo 5.000 caracteres. Baseie-se estritamente no campo 'pedidos' dos dados. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece sua resposta com <h2>DOS PEDIDOS</h2>."
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        secao_fatos, sub_leg, sub_jur, sub_dout, secao_pedidos = await asyncio.gather(*tasks)
        
        secao_direito = f"<h2>DO DIREITO</h2>{sub_leg}{sub_jur}{sub_dout}"
        
        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>Petição Inicial Trabalhista</title><style>body{{font-family:'Times New Roman',serif;line-height:1.5;text-align:justify;margin:3cm}}h1{{text-align:center;font-size:16pt}}h2{{text-align:left;font-size:14pt;margin-top:30px;font-weight:bold}}h3{{text-align:left;font-size:12pt;margin-top:20px;font-weight:bold}}p{{text-indent:2em;margin-bottom:15px}}.qualificacao p{{text-indent:0}}</style></head>
<body>
    <h1>EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DA ___ VARA DO TRABALHO DE {dados_formulario.get('reu', {}).get('cidade', 'CIDADE')} - {dados_formulario.get('reu', {}).get('estado', 'UF')}</h1>
    <div class="qualificacao" style="margin-top:50px;"><p><strong>{dados_formulario.get('autor',{}).get('nome','').upper()}</strong>, {dados_formulario.get('autor',{}).get('qualificacao','')}, residente e domiciliada em [ENDEREÇO A SER PREENCHIDO], vem, com o devido respeito, por intermédio de seu advogado que esta subscreve (procuração anexa), propor a presente</p><h1 style="margin-top:20px;">AÇÃO TRABALHISTA</h1><p>em face de <strong>{dados_formulario.get('reu',{}).get('nome','').upper()}</strong>, {dados_formulario.get('reu',{}).get('qualificacao','')}, pelos fatos e fundamentos a seguir expostos.</p></div>
    {secao_fatos}
    {secao_direito}
    {secao_pedidos}
    <h2 style="font-size:12pt;text-align:left;">DO VALOR DA CAUSA</h2><p>Dá-se à causa o valor de {dados_formulario.get('valor_causa', 'R$ 0,00')}.</p><p style="margin-top:50px;">Nestes termos,<br>Pede deferimento.</p><p style="text-align:center;margin-top:50px;">[Local], {datetime.now().strftime('%d de %B de %Y')}.</p><p style="text-align:center;margin-top:80px;">_________________________________________<br>ADVOGADO<br>OAB/SP Nº XXX.XXX</p>
</body></html>
        """

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> Dict:
        """Ponto de entrada síncrono que executa a lógica assíncrona, passando o feedback se existir."""
        try:
            documento_html = asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica, documento_anterior, recomendacoes))
            return {"documento_html": documento_html}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}
