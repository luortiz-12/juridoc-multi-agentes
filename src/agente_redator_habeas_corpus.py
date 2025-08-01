# agente_redator_habeas_corpus.py - Versão 2.1 (Com Prompts Rígidos)

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

class AgenteRedatorHabeasCorpus:
    """
    Agente Redator Especializado em Habeas Corpus.
    v2.1: Utiliza prompts rígidos para garantir a fidelidade aos dados e evitar
    a repetição desnecessária da qualificação das partes.
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de HABEAS CORPUS (v2.1 com Prompts Rígidos) inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção específica."""
        print(f"📝 Gerando/Melhorando seção de Habeas Corpus: {secao_nome}")
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
        
        # COMENTÁRIO: Instruções aprimoradas para evitar alucinação e repetição.
        instrucao_fidelidade = "ATENÇÃO: Sua tarefa é redigir um texto jurídico. Você DEVE se basear ESTRITAMENTE nos dados fornecidos no JSON 'DADOS DO CASO' e na 'PESQUISA' jurídica. NÃO invente fatos que não estejam presentes nos dados."
        instrucao_referencia = "IMPORTANTE: Após a qualificação inicial das partes no início do documento, refira-se a elas apenas pelo nome e pela sua condição (ex: 'o Paciente', 'a Autoridade Coatora'). NÃO repita a qualificação completa no corpo do texto."

        instrucao_melhoria = ""
        if recomendacoes:
            instrucao_melhoria = f"\n\nINSTRUÇÕES PARA MELHORIA: A versão anterior foi considerada insatisfatória. Reescreva e expanda o conteúdo para atender a seguinte recomendação: '{' '.join(recomendacoes)}'."

        # COMENTÁRIO: As novas instruções foram adicionadas a todos os prompts.
        prompts = {
            "fatos": f"{instrucao_formato}\n{instrucao_fidelidade}\n{instrucao_referencia}{instrucao_melhoria}\n\nRedija a seção 'DOS FATOS E DO CONSTRANGIMENTO ILEGAL' de um Habeas Corpus. Seja extremamente detalhado, com no mínimo 10.000 caracteres. Descreva a prisão, o constrangimento ilegal, a autoridade coatora e o motivo pelo qual a prisão é ilegal. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>DOS FATOS E DO CONSTRANGIMENTO ILEGAL</h2>.",
            "direito": f"{instrucao_formato}\n{instrucao_fidelidade}\n{instrucao_referencia}{instrucao_melhoria}\n\nRedija a seção 'DO DIREITO E DO PEDIDO LIMINAR' de um Habeas Corpus. Seja detalhado, com no mínimo 15.000 caracteres. Foque no direito à liberdade (Art. 5º, LXVIII, CF) e nos artigos do Código de Processo Penal sobre as hipóteses de soltura. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. PESQUISA: {pesquisas.get('legislacao_formatada', 'N/A')}. Comece com <h2>DO DIREITO E DO PEDIDO LIMINAR</h2>.",
            "pedidos": f"{instrucao_formato}\n{instrucao_fidelidade}\n{instrucao_referencia}{instrucao_melhoria}\n\nRedija a seção 'DOS PEDIDOS' de um Habeas Corpus. Seja detalhado, com no mínimo 5.000 caracteres. Peça a concessão liminar da ordem para expedir o alvará de soltura e, no mérito, a confirmação da ordem. DADOS DO CASO: {json.dumps(dados_formulario, ensure_ascii=False)}. Comece com <h2>DOS PEDIDOS</h2>."
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
    <p style="text-align:center;margin-top:50px;">[Local], {datetime.now().strftime('%d de August de %Y')}.</p>
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
