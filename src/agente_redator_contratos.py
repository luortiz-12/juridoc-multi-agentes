# agente_redator_contratos.py - Versão 3.0 (Dinâmica e Aprimorada)

import json
import logging
import asyncio
import openai
import os
from typing import Dict, Any
import re
from datetime import datetime

class AgenteRedatorContratos:
    """
    Agente Redator Otimizado e Especializado na redação de Contratos.
    v3.0: Utiliza prompts dinâmicos que se adaptam ao tipo de contrato especificado,
    garantindo cláusulas mais relevantes e um documento de maior qualidade.
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de CONTRATOS (Dinâmico v3.0) inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção específica do contrato."""
        print(f"📝 Gerando cláusula: {secao_nome}")
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.2
            )
            return re.sub(r'^```html|```$', '', response.choices[0].message.content.strip())
        except Exception as e:
            print(f"❌ ERRO na API para a cláusula {secao_nome}: {e}")
            return f"<h3>ERRO AO GERAR CLÁUSULA - {secao_nome.upper()}</h3><p>Detalhes: {e}</p>"

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        """Cria e executa todas as tarefas de redação de cláusulas em paralelo."""
        
        instrucao_formato = "Sua resposta DEVE ser um bloco de código HTML. Use <h3> para o título da cláusula (ex: '<h3>CLÁUSULA PRIMEIRA - DO OBJETO</h3>'), <p> para o texto, e <strong> para negrito. NÃO use Markdown (`**`). Seja extremamente detalhado e formal."

        # COMENTÁRIO: O tipo de contrato é extraído para tornar os prompts dinâmicos.
        tipo_contrato = dados_formulario.get('tipo_contrato_especifico', 'DE PRESTAÇÃO DE SERVIÇOS')

        # COMENTÁRIO: Os prompts agora incluem o 'tipo_contrato' para guiar a IA a gerar conteúdo específico.
        prompts = {
            "objeto": f"{instrucao_formato}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA PRIMEIRA - DO OBJETO'. Detalhe o seguinte: {dados_formulario.get('objeto', '')}",
            "valor": f"{instrucao_formato}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA SEGUNDA - DO VALOR E DA FORMA DE PAGAMENTO'. Detalhe o valor de {dados_formulario.get('valor', '')} e a forma de pagamento: {dados_formulario.get('pagamento', '')}",
            "prazos": f"{instrucao_formato}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA TERCEIRA - DOS PRAZOS'. Detalhe os seguintes prazos: {dados_formulario.get('prazos', '')}",
            "obrigacoes": f"{instrucao_formato}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA QUARTA - DAS OBRIGAÇÕES DAS PARTES'. Crie subtítulos com '<strong>Obrigações do CONTRATANTE:</strong>' e '<strong>Obrigações do CONTRATADO:</strong>'. Detalhe as seguintes responsabilidades: {dados_formulario.get('responsabilidades', '')}",
            "penalidades": f"{instrucao_formato}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA QUINTA - DAS PENALIDADES'. Detalhe as seguintes penalidades por descumprimento: {dados_formulario.get('penalidades', '')}",
            "propriedade": f"{instrucao_formato}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA SEXTA - DA PROPRIEDADE INTELECTUAL'. Crie uma cláusula padrão definindo a quem pertence a propriedade intelectual do trabalho desenvolvido (códigos, designs, etc.) após a quitação final.",
            "confidencialidade": f"{instrucao_formato}\n\nRedija a 'CLÁUSULA SÉTIMA - DA CONFIDENCIALIDADE'. Crie uma cláusula padrão obrigando ambas as partes a manter sigilo sobre as informações trocadas.",
            "rescisao": f"{instrucao_formato}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA OITAVA - DA RESCISÃO'. Detalhe as condições e consequências da rescisão do contrato.",
            "foro": f"{instrucao_formato}\n\nRedija a 'CLÁUSULA NONA - DO FORO'. Especifique o foro de eleição como: {dados_formulario.get('foro', '')}",
        }
        
        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        resultados = await asyncio.gather(*tasks)
        
        clausulas_html = "\n".join(resultados)

        contratante = dados_formulario.get('contratante', {})
        contratado = dados_formulario.get('contratado', {})
        
        # COMENTÁRIO: O template final é limpo e usa o 'tipo_contrato' no título principal.
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

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict) -> Dict:
        try:
            return {"documento_html": asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica))}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}
