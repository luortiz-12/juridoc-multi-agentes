# agente_redator_parecer.py - Versão 3.0 (Modular e Aprimorada)

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

class AgenteRedatorParecer:
    """
    Agente Redator Otimizado e Especializado em Pareceres Jurídicos.
    v3.0: Utiliza prompts modulares e assíncronos para cada seção, garantindo
    maior detalhe, qualidade e o cumprimento da meta de 30.000 caracteres.
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de PARECER JURÍDICO (Modular v3.0) inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção específica."""
        print(f"📝 Gerando/Melhorando seção de parecer: {secao_nome}")
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
        instrucao_fidelidade = "ATENÇÃO: Sua tarefa é redigir um texto jurídico. Você DEVE se basear ESTRITAMENTE nos dados fornecidos no JSON 'DADOS DO CASO' e na 'PESQUISA' jurídica. NÃO invente fatos."

        instrucao_melhoria = ""
        if recomendacoes:
            instrucao_melhoria = f"\n\nINSTRUÇÕES PARA MELHORIA: A versão anterior foi considerada insatisfatória. Reescreva e expanda significativamente o conteúdo para atender a seguinte recomendação: '{' '.join(recomendacoes)}'."

        # COMENTÁRIO: A redação agora é modular, com um prompt detalhado para cada seção e metas de caracteres individuais.
        prompts = {
            "ementa": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a 'EMENTA' de um parecer jurídico. Crie um resumo conciso em 3 a 5 tópicos. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h3>EMENTA</h3>.",
            "relatorio": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a seção 'I - RELATÓRIO' de um parecer jurídico. Seja extremamente detalhado, com no mínimo 8.000 caracteres. Descreva a consulta feita pelo solicitante. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>I - RELATÓRIO</h2>.",
            "fundamentacao": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a seção 'II - FUNDAMENTAÇÃO' de um parecer jurídico. Seja detalhado, com no mínimo 15.000 caracteres. Analise a questão com base na legislação e jurisprudência pesquisadas. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('pesquisa_formatada', 'N/A')}. Comece com <h2>II - FUNDAMENTAÇÃO</h2>.",
            "conclusao": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a seção 'III - CONCLUSÃO' de um parecer jurídico. Seja detalhado, com no mínimo 7.000 caracteres. Responda objetivamente à consulta com base na fundamentação. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>III - CONCLUSÃO</h2>."
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        secao_ementa, secao_relatorio, secao_fundamentacao, secao_conclusao = await asyncio.gather(*tasks)
        
        documento_html = f"{secao_ementa}{secao_relatorio}{secao_fundamentacao}{secao_conclusao}"
        
        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>Parecer Jurídico</title><style>body{{font-family:'Times New Roman',serif;line-height:1.6;text-align:justify;margin:3cm}}h1,h2,h3{{text-align:center;font-weight:bold}}h1{{font-size:16pt}}h2{{font-size:14pt;margin-top:30px;text-align:left;}}h3{{font-size:12pt;margin-top:20px;text-align:left;font-style:italic;}}p{{text-indent:2em;margin-bottom:15px}}</style></head>
<body>
    <h1>PARECER JURÍDICO</h1>
    <p><strong>De:</strong> [Seu Nome/Escritório]</p>
    <p><strong>Para:</strong> {dados_formulario.get('solicitante')}</p>
    <p><strong>Assunto:</strong> {dados_formulario.get('assunto')}</p>
    <p><strong>Data:</strong> {datetime.now().strftime('%d de August de %Y')}.</p>
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
