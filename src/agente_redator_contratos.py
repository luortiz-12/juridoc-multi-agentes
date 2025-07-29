# agente_redator_contratos.py - Versão 4.0 (Com Ciclo de Feedback e Meta de 30k)

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

class AgenteRedatorContratos:
    """
    Agente Redator Otimizado e Especializado na redação de Contratos.
    v4.0: Utiliza prompts dinâmicos e modulares, aceita feedback para melhoria
    e tem uma meta de geração de conteúdo de 30.000 caracteres.
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de CONTRATOS (Dinâmico v4.0) inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção específica do contrato."""
        print(f"📝 Gerando/Melhorando cláusula: {secao_nome}")
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192, # Aumentado para permitir respostas mais longas
                temperature=0.2
            )
            return re.sub(r'^```html|```$', '', response.choices[0].message.content.strip())
        except Exception as e:
            print(f"❌ ERRO na API para a cláusula {secao_nome}: {e}")
            return f"<h3>ERRO AO GERAR CLÁUSULA - {secao_nome.upper()}</h3><p>Detalhes: {e}</p>"

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> str:
        """Cria ou melhora as cláusulas do documento em paralelo."""
        
        instrucao_formato = "Sua resposta DEVE ser um bloco de código HTML. Use <h3> para o título da cláusula (ex: '<h3>CLÁUSULA PRIMEIRA - DO OBJETO</h3>'), <p> para o texto, e <strong> para negrito. NÃO use Markdown (`**`). Seja extremamente detalhado e formal."

        instrucao_melhoria = ""
        if recomendacoes:
            instrucao_melhoria = f"\n\nINSTRUÇÕES PARA MELHORIA: A versão anterior foi considerada insatisfatória. Reescreva e expanda significativamente o conteúdo para atender a seguinte recomendação: '{' '.join(recomendacoes)}'. Use o rascunho anterior como referência do que NÃO fazer.\nRASCUNHO ANTERIOR:\n{documento_anterior}"

        tipo_contrato = dados_formulario.get('tipo_contrato_especifico', 'DE PRESTAÇÃO DE SERVIÇOS')

        # COMENTÁRIO: Prompts modulares com requisitos de tamanho para atingir a meta de 30k.
        prompts = {
            "objeto": f"{instrucao_formato}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA PRIMEIRA - DO OBJETO'. Seja extremamente detalhado, com no mínimo 4.000 caracteres. Detalhe o seguinte: {dados_formulario.get('objeto', '')}",
            "valor": f"{instrucao_formato}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA SEGUNDA - DO VALOR E DA FORMA DE PAGAMENTO'. Seja detalhado, com no mínimo 3.000 caracteres. Detalhe o valor de {dados_formulario.get('valor', '')} e a forma de pagamento: {dados_formulario.get('pagamento', '')}",
            "prazos": f"{instrucao_formato}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA TERCEIRA - DOS PRAZOS'. Seja detalhado, com no mínimo 3.000 caracteres. Detalhe os seguintes prazos: {dados_formulario.get('prazos', '')}",
            "obrigacoes": f"{instrucao_formato}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA QUARTA - DAS OBRIGAÇÕES DAS PARTES'. Seja detalhado, com no mínimo 5.000 caracteres. Crie subtítulos com '<strong>Obrigações do CONTRATANTE:</strong>' e '<strong>Obrigações do CONTRATADO:</strong>'. Detalhe as seguintes responsabilidades: {dados_formulario.get('responsabilidades', '')}",
            "penalidades": f"{instrucao_formato}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA QUINTA - DAS PENALIDADES'. Seja detalhado, com no mínimo 3.000 caracteres. Detalhe as seguintes penalidades por descumprimento: {dados_formulario.get('penalidades', '')}",
            "propriedade": f"{instrucao_formato}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA SEXTA - DA PROPRIEDADE INTELECTUAL'. Crie uma cláusula padrão detalhada, com no mínimo 3.000 caracteres, definindo a quem pertence a propriedade intelectual do trabalho desenvolvido.",
            "confidencialidade": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a 'CLÁUSULA SÉTIMA - DA CONFIDENCIALIDADE'. Crie uma cláusula padrão detalhada, com no mínimo 3.000 caracteres, obrigando ambas as partes a manter sigilo sobre as informações trocadas.",
            "rescisao": f"{instrucao_formato}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA OITAVA - DA RESCISÃO'. Seja detalhado, com no mínimo 3.000 caracteres. Detalhe as condições e consequências da rescisão do contrato.",
            "foro": f"{instrucao_formato}{instrucao_melhoria}\n\nRedija a 'CLÁUSULA NONA - DO FORO'. Especifique o foro de eleição como: {dados_formulario.get('foro', '')}",
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        resultados = await asyncio.gather(*tasks)
        
        clausulas_html = "\n".join(resultados)

        contratante = dados_formulario.get('contratante', {})
        contratado = dados_formulario.get('contratado', {})
        
        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>{tipo_contrato.title()}</title><style>body{{font-family:'Times New Roman',serif;line-height:1.6;text-align:justify;margin:3cm}}h1{{text-align:center;font-size:16pt;margin-bottom:2cm;}}h2{{font-size:14pt;margin-top:1.5cm;font-weight:bold;text-align:center;}}h3{{font-size:12pt;margin-top:1cm;font-weight:bold;}}p{{text-indent:2em;margin-bottom:15px}}</style></head>
<body>
    <h1>{tipo_contrato.upper()}</h1>
    <h2>DAS PARTES</h2>
    <p><strong>CONTRATANTE:</strong> {contratante.get('nome', '')}, pessoa jurídica de direito privado, inscrita no CNPJ sob o nº {contratante.get('cnpj', '')}, com sede em {contratante.get('endereco', '')}, neste ato representada na forma de seu contrato social.</p>
    <p><strong>CONTRATADO:</strong> {contratado.get('nome', '')}, pessoa jurídica de direito privado, inscrita no CNPJ sob o nº {contratado.get('cnpj', '')}, com sede em {contratado.get('endereco', '')}, neste ato representada na forma de seu contrato social.</p>
    <p>As partes acima identificadas têm, entre si, justo e acertado o presente Contrato, que se regerá pelas cláusulas seguintes e pelas condições descritas no presente.</p>
    {clausulas_html}
    <p>E, por estarem assim justos e contratados, firmam o presente instrumento, em duas vias de igual teor e forma, na presença de duas testemunhas.</p>
    <p style="text-align:center;margin-top:2cm;margin-bottom:0;">[Local], {datetime.now().strftime('%d de %B de %Y')}.</p>
    <p style="text-align:center;margin-top:2cm;margin-bottom:1cm;">_________________________________________<br><strong>{contratante.get('nome', '').upper()}</strong><br>Contratante</p>
    <p style="text-align:center;margin-bottom:2cm;">_________________________________________<br><strong>{contratado.get('nome', '').upper()}</strong><br>Contratado</p>
    <p style="text-align:center;margin-bottom:1cm;">_________________________________________<br>Testemunha 1</p>
    <p style="text-align:center;">_________________________________________<br>Testemunha 2</p>
</body></html>
        """

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> Dict:
        """Ponto de entrada síncrono que executa a lógica assíncrona, passando o feedback se existir."""
        try:
            documento_html = asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica, documento_anterior, recomendacoes))
            return {"documento_html": documento_html}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}
