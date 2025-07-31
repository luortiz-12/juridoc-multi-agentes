# agente_redator_parecer.py - Versão 2.1 (Com Prompts Rígidos Anti-Alucinação)

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
    Agente Redator Especializado em Pareceres Jurídicos.
    v2.1: Utiliza prompts rígidos para garantir a fidelidade aos dados do formulário
    e evitar a invenção de fatos ("alucinação").
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de PARECER JURÍDICO (v2.1) inicializado.")

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> str:
        """Gera o parecer completo com uma única chamada à API para garantir coesão."""
        print("📝 Gerando Parecer Jurídico completo...")
        
        # COMENTÁRIO: Instruções aprimoradas para forçar a fidelidade aos dados do formulário.
        instrucao_fidelidade = "ATENÇÃO: Sua tarefa é redigir um parecer jurídico. Você DEVE se basear ESTRITAMENTE nos dados fornecidos abaixo. NÃO invente nomes, valores, datas ou qualquer fato que não esteja presente nos dados. Sua tarefa é usar os dados fornecidos e a pesquisa para construir a análise, não criar uma nova."
        
        instrucao_melhoria = ""
        if recomendacoes:
            instrucao_melhoria = f"\n\nINSTRUÇÕES PARA MELHORIA: A versão anterior foi considerada insatisfatória. Reescreva e expanda o conteúdo para atender a seguinte recomendação: '{' '.join(recomendacoes)}'."

        prompt_completo = f"""
        {instrucao_fidelidade}{instrucao_melhoria}

        Você é um advogado especialista e parecerista. Sua tarefa é redigir um Parecer Jurídico técnico, objetivo e extremamente bem fundamentado com base nos dados fornecidos.

        ESTRUTURA OBRIGATÓRIA DO DOCUMENTO:
        1.  **EMENTA:** Um resumo conciso do parecer em 3 a 5 tópicos.
        2.  **I - RELATÓRIO:** Descreva detalhadamente a consulta feita pelo solicitante, usando os dados do campo 'Consulta Detalhada'.
        3.  **II - FUNDAMENTAÇÃO:** Analise a questão de forma aprofundada, com base na legislação e jurisprudência pesquisadas.
        4.  **III - CONCLUSÃO:** Responda objetivamente à consulta com base na fundamentação.

        DADOS PARA O PARECER:
        - **Solicitante:** {dados_formulario.get('solicitante')}
        - **Assunto Principal:** {dados_formulario.get('assunto')}
        - **Consulta Detalhada:** {dados_formulario.get('fatos')}
        - **Pesquisa Jurídica (Legislação):** {pesquisas.get('legislacao_formatada', 'Nenhuma pesquisa específica encontrada.')}
        - **Pesquisa Jurídica (Jurisprudência):** {pesquisas.get('jurisprudencia_formatada', 'Nenhuma pesquisa específica encontrada.')}

        REGRAS DE FORMATAÇÃO E CONTEÚDO:
        - A resposta DEVE ser um bloco de código HTML completo e bem formatado.
        - O texto final deve ter no mínimo 30.000 caracteres.
        - Use `<h2>` para os títulos principais (RELATÓRIO, FUNDAMENTAÇÃO, CONCLUSÃO).
        - Use `<h3>` para a EMENTA.
        - Use `<p>` para parágrafos e `<strong>` para negrito.
        - NÃO use Markdown (`**`).
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat", messages=[{"role": "user", "content": prompt_completo}],
                max_tokens=8192, temperature=0.3
            )
            documento_html = re.sub(r'^```html|```$', '', response.choices[0].message.content.strip())
        except Exception as e:
            print(f"❌ ERRO na API ao gerar o parecer: {e}")
            return f"<h1>Erro na Geração do Parecer</h1><p>{e}</p>"

        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>Parecer Jurídico</title><style>body{{font-family:'Times New Roman',serif;line-height:1.6;text-align:justify;margin:3cm}}h1,h2,h3{{text-align:center;font-weight:bold}}h1{{font-size:16pt}}h2{{font-size:14pt;margin-top:30px;text-align:left;}}h3{{font-size:12pt;margin-top:20px;text-align:left;font-style:italic;}}p{{text-indent:2em;margin-bottom:15px}}</style></head>
<body>
    <h1>PARECER JURÍDICO</h1>
    <p><strong>De:</strong> [Seu Nome/Escritório]</p>
    <p><strong>Para:</strong> {dados_formulario.get('solicitante')}</p>
    <p><strong>Assunto:</strong> {dados_formulario.get('assunto')}</p>
    <p><strong>Data:</strong> {datetime.now().strftime('%d de %B de %Y')}</p>
    <hr>
    {documento_html}
</body></html>
        """

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> Dict:
        try:
            return {"documento_html": asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica, documento_anterior, recomendacoes))}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}
