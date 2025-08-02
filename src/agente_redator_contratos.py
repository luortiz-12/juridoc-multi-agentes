# agente_redator_contratos.py - Versão 5.0 (Com Lógica de Cláusulas Condicionais)

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
    v5.0: Utiliza lógica condicional para incluir cláusulas de Propriedade Intelectual
    e Confidencialidade apenas quando são relevantes para o tipo de contrato.
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de CONTRATOS (Dinâmico v5.0) inicializado.")

    async def _chamar_api_async(self, prompt: str, secao_nome: str) -> str:
        """Chama a API de forma assíncrona para gerar uma seção específica do contrato."""
        print(f"📝 Gerando/Melhorando cláusula: {secao_nome}")
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
                temperature=0.2
            )
            return re.sub(r'^```html|```$', '', response.choices[0].message.content.strip())
        except Exception as e:
            print(f"❌ ERRO na API para a cláusula {secao_nome}: {e}")
            return f"<h3>ERRO AO GERAR CLÁUSULA - {secao_nome.upper()}</h3><p>Detalhes: {e}</p>"

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict, documento_anterior: Optional[str] = None, recomendacoes: Optional[List[str]] = None) -> str:
        """Cria ou melhora as cláusulas do documento em paralelo."""
        
        print("--- DADOS RECEBIDOS PELO AGENTE REDATOR DE CONTRATOS ---")
        print(json.dumps(dados_formulario, indent=2, ensure_ascii=False))
        print("----------------------------------------------------")

        instrucao_formato = "Sua resposta DEVE ser um bloco de código HTML. Use <h3> para o título da cláusula (ex: '<h3>CLÁUSULA PRIMEIRA - DO OBJETO</h3>'), <p> para o texto, e <strong> para negrito. NÃO use Markdown (`**`). Seja extremamente detalhado e formal."
        instrucao_fidelidade = "ATENÇÃO: Sua tarefa é redigir uma cláusula de contrato. Você DEVE se basear ESTRITAMENTE nos dados fornecidos. NÃO invente informações. Sua tarefa é usar os dados fornecidos para redigir a cláusula de forma detalhada e juridicamente sólida."
        
        instrucao_melhoria = ""
        if recomendacoes:
            instrucao_melhoria = f"\n\nINSTRUÇÕES PARA MELHORIA: A versão anterior foi considerada insatisfatória. Reescreva e expanda o conteúdo para atender a seguinte recomendação: '{' '.join(recomendacoes)}'."

        tipo_contrato = dados_formulario.get('tipo_contrato_especifico', 'DE PRESTAÇÃO DE SERVIÇOS')
        pesquisa_formatada = pesquisas.get('pesquisa_formatada', 'Nenhuma pesquisa de referência foi encontrada.')

        # COMENTÁRIO: Os prompts são definidos em um dicionário base.
        prompts = {
            "objeto": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA PRIMEIRA - DO OBJETO', detalhando o seguinte: {dados_formulario.get('objeto', '')}\n\nUse a seguinte pesquisa como referência:\n{pesquisa_formatada}",
            "valor": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA SEGUNDA - DO VALOR E DA FORMA DE PAGAMENTO', detalhando o valor de '{dados_formulario.get('valor', '')}' e a forma de pagamento: '{dados_formulario.get('pagamento', '')}'",
            "prazos": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA TERCEIRA - DOS PRAZOS', detalhando os seguintes prazos: '{dados_formulario.get('prazos', '')}'",
            "obrigacoes": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA QUARTA - DAS OBRIGAÇÕES DAS PARTES', detalhando as seguintes responsabilidades: '{dados_formulario.get('responsabilidades', '')}'. Crie subtítulos com '<strong>Obrigações do CONTRATANTE:</strong>' e '<strong>Obrigações do CONTRATADO:</strong>'.",
            "penalidades": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA QUINTA - DAS PENALIDADES', detalhando as seguintes penalidades: '{dados_formulario.get('penalidades', '')}'",
            "rescisao": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA OITAVA - DA RESCISÃO', detalhando as condições e consequências da rescisão.",
            "foro": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a 'CLÁUSULA NONA - DO FORO', especificando o foro de eleição como: '{dados_formulario.get('foro', '')}'",
        }

        # COMENTÁRIO: Lógica condicional. As cláusulas de Propriedade Intelectual e Confidencialidade
        # só são adicionadas se o tipo de contrato for um dos que tipicamente as exigem.
        contratos_com_pi_e_sigilo = ["prestação de serviços", "desenvolvimento de software", "franquia", "criação"]
        if any(termo in tipo_contrato.lower() for termo in contratos_com_pi_e_sigilo):
            print("  -> Tipo de contrato requer cláusulas de PI e Confidencialidade.")
            prompts["propriedade"] = f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA SEXTA - DA PROPRIEDADE INTELECTUAL', criando uma cláusula padrão que defina a quem pertence a propriedade intelectual do trabalho desenvolvido."
            prompts["confidencialidade"] = f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a 'CLÁUSULA SÉTIMA - DA CONFIDENCIALIDADE', criando uma cláusula padrão que obrigue as partes a manter sigilo."
        else:
            print("  -> Tipo de contrato simples. Cláusulas de PI e Confidencialidade não serão geradas.")

        tasks = [self._chamar_api_async(p, n) for n, p in prompts.items()]
        resultados = await asyncio.gather(*tasks)
        
        clausulas_html = "\n".join(resultados)

        contratante = dados_formulario.get('contratante', {})
        contratado = dados_formulario.get('contratado', {})
        
        # COMENTÁRIO: O template de qualificação foi ajustado para lidar com pessoa física (CPF/RG) ou jurídica (CNPJ).
        qualificacao_contratante = f"<p><strong>CONTRATANTE:</strong> {contratante.get('nome', '')}, { 'pessoa física, portadora do CPF nº ' + contratante.get('cpf', '') + ' e do RG nº ' + contratante.get('rg', '') if contratante.get('cpf') else 'pessoa jurídica de direito privado, inscrita no CNPJ sob o nº ' + contratante.get('cnpj', '')}, com sede em {contratante.get('endereco', '')}.</p>"
        qualificacao_contratado = f"<p><strong>CONTRATADO:</strong> {contratado.get('nome', '')}, { 'pessoa física, portadora do CPF nº ' + contratado.get('cpf', '') + ' e do RG nº ' + contratado.get('rg', '') if contratado.get('cpf') else 'pessoa jurídica de direito privado, inscrita no CNPJ sob o nº ' + contratado.get('cnpj', '')}, com sede em {contratado.get('endereco', '')}.</p>"


        return f"""
<!DOCTYPE html><html lang="pt-BR"><head><title>{tipo_contrato.title()}</title><style>body{{font-family:'Times New Roman',serif;line-height:1.6;text-align:justify;margin:3cm}}h1{{text-align:center;font-size:16pt;margin-bottom:2cm;}}h2{{font-size:14pt;margin-top:1.5cm;font-weight:bold;text-align:center;}}h3{{font-size:12pt;margin-top:1cm;font-weight:bold;}}p{{text-indent:2em;margin-bottom:15px}}</style></head>
<body>
    <h1>{tipo_contrato.upper()}</h1>
    <h2>DAS PARTES</h2>
    {qualificacao_contratante}
    {qualificacao_contratado}
    <p>As partes acima identificadas têm, entre si, justo e acertado o presente Contrato, que se regerá pelas cláusulas seguintes e pelas condições descritas no presente.</p>
    {clausulas_html}
    <p>E, por estarem assim justos e contratados, firmam o presente instrumento, em duas vias de igual teor e forma, na presença de duas testemunhas.</p>
    <p style="text-align:center;margin-top:2cm;margin-bottom:0;">[Local], {datetime.now().strftime('%d de August de %Y')}.</p>
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
