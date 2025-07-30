# agente_redator_estudo_de_caso.py - Agente Especializado em Estudos de Caso Jurídicos

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

class AgenteRedatorEstudoDeCaso:
    """
    Agente Redator Otimizado e Especializado na redação de Estudos de Caso Jurídicos.
    - Utiliza prompts modulares e assíncronos para cada seção.
    - Aceita feedback do Agente Validador para melhorar rascunhos.
    - Tem uma meta de geração de conteúdo de 30.000 caracteres.
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de ESTUDO DE CASO inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção específica."""
        print(f"📝 Gerando/Melhorando seção de Estudo de Caso: {secao_nome}")
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

        # Prompts modulares com requisitos de tamanho para atingir a meta de 30k.
        prompts = {
            "ementa": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a 'EMENTA' de um estudo de caso jurídico. Crie um resumo conciso em 3 a 5 tópicos. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h3>EMENTA</h3>.",
            "relatorio": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a seção 'I - RELATÓRIO' de um estudo de caso. Seja extremamente detalhado, com no mínimo 10.000 caracteres. Descreva a consulta e os fatos do caso. DADOS: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>I - RELATÓRIO</h2>.",
            "analise": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a seção 'II - ANÁLISE DO CASO' de um estudo de caso. Seja detalhado, com no mínimo 15.000 caracteres. Analise a questão com base na legislação e jurisprudência pesquisadas. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('pesquisa_formatada', 'N/A')}. Comece com <h2>II - ANÁLISE DO CASO</h2>.",
            "conclusao": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a seção 'III - CONCLUSÃO' de um estudo de caso. Seja detalhado, com no mínimo 5.000 caracteres. Responda objetivamente à consulta com base na análise. CONTEXTO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>III - CONCLUSÃO</h2>."
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        secao_ementa, secao_relatorio, secao_analise, secao_conclusao = await asyncio.gather(*tasks)
        
        documento_html = f"{secao_ementa}{secao_relatorio}{secao_analise}{secao_conclusao}"
        
        # Template HTML final para o Estudo de Caso
        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>Estudo de Caso Jurídico</title><style>body{{font-family:'Times New Roman',serif;line-height:1.6;text-align:justify;margin:3cm}}h1,h2,h3{{text-align:center;font-weight:bold}}h1{{font-size:16pt}}h2{{font-size:14pt;margin-top:30px;text-align:left;}}h3{{font-size:12pt;margin-top:20px;text-align:left;font-style:italic;}}p{{text-indent:2em;margin-bottom:15px}}</style></head>
<body>
    <h1>ESTUDO DE CASO</h1>
    <p><strong>Para:</strong> {dados_formulario.get('solicitante', '[Solicitante não informado]')}</p>
    <p><strong>Assunto:</strong> {dados_formulario.get('assunto', '[Assunto não informado]')}</p>
    <p><strong>Data:</strong> {datetime.now().strftime('%d de %B de %Y')}</p>
    <hr>
    {documento_html}
</body></html>
        """

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> Dict:
        """Ponto de entrada síncrono que executa a lógica assíncrona, passando o feedback se existir."""
        try:
            documento_html = asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica, documento_anterior, recomendacoes))
            return {"documento_html": documento_html}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}