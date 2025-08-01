# agente_redator_contratos.py - Versão 5.3 (Com Lógica de Qualificação e Cláusulas Corrigida)

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
    v5.3: Lógica de qualificação das partes e de inclusão de cláusulas aprimorada para evitar erros e alucinações.
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de CONTRATOS (Dinâmico v5.3) inicializado.")

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

        prompts = {
            "objeto": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA PRIMEIRA - DO OBJETO', detalhando o seguinte: {dados_formulario.get('objeto', '')}\n\nUse a seguinte pesquisa como referência:\n{pesquisa_formatada}",
            "valor": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA SEGUNDA - DO VALOR E DA FORMA DE PAGAMENTO', detalhando o valor de '{dados_formulario.get('valor', '')}' e a forma de pagamento: '{dados_formulario.get('pagamento', '')}'",
            "prazos": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA TERCEIRA - DOS PRAZOS', detalhando os seguintes prazos: '{dados_formulario.get('prazos', '')}'",
            "obrigacoes": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA QUARTA - DAS OBRIGAÇÕES DAS PARTES', detalhando as seguintes responsabilidades: '{dados_formulario.get('responsabilidades', '')}'. Crie subtítulos com '<strong>Obrigações do CONTRATANTE:</strong>' e '<strong>Obrigações do CONTRATADO:</strong>'.",
            "penalidades": f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA QUINTA - DAS PENALIDADES', detalhando as seguintes penalidades: '{dados_formulario.get('penalidades', '')}'",
        }

        # COMENTÁRIO: Lógica condicional aprimorada para incluir cláusulas apenas quando necessário.
        clausulas_a_gerar = ["objeto", "valor", "prazos", "obrigacoes", "penalidades"]
        
        contratos_com_pi_e_sigilo = ["prestação de serviços", "desenvolvimento de software", "franquia", "criação"]
        if any(termo in tipo_contrato.lower() for termo in contratos_com_pi_e_sigilo):
            print("  -> Tipo de contrato requer cláusulas de PI e Confidencialidade.")
            prompts["propriedade"] = f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA SEXTA - DA PROPRIEDADE INTELECTUAL', criando uma cláusula padrão que defina a quem pertence a propriedade intelectual do trabalho desenvolvido."
            prompts["confidencialidade"] = f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a 'CLÁUSULA SÉTIMA - DA CONFIDENCIALIDADE', criando uma cláusula padrão que obrigue as partes a manter sigilo."
            clausulas_a_gerar.extend(["propriedade", "confidencialidade"])
        else:
            print("  -> Tipo de contrato simples. Cláusulas de PI e Confidencialidade não serão geradas.")

        prompts["rescisao"] = f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nPara um '{tipo_contrato}', redija a 'CLÁUSULA DE RESCISÃO', detalhando as condições e consequências da rescisão."
        prompts["foro"] = f"{instrucao_formato}\n{instrucao_fidelidade}{instrucao_melhoria}\n\nRedija a 'CLÁUSULA DO FORO', especificando o foro de eleição como: '{dados_formulario.get('foro', '')}'"
        clausulas_a_gerar.extend(["rescisao", "foro"])

        tasks = [self._chamar_api_async(prompts[nome], nome) for nome in clausulas_a_gerar]
        resultados = await asyncio.gather(*tasks)
        
        clausulas_html = "\n".join(resultados)

        contratante = dados_formulario.get('contratante', {})
        contratado = dados_formulario.get('contratado', {})
        
        # COMENTÁRIO: A lógica de qualificação foi reescrita para ser mais robusta e evitar o erro 'TypeError'.
        # Ela agora lida corretamente com a presença ou ausência de CPF/CNPJ e outros campos.
        def montar_qualificacao(parte_dados, tipo_parte):
            nome = str(parte_dados.get('nome', ''))
            endereco = str(parte_dados.get('endereco', ''))
            
            qualificacao_texto = ""
            if parte_dados.get('cpf'):
                qualificacao_texto = f"pessoa física, portadora do CPF nº {parte_dados.get('cpf', '')}"
                if parte_dados.get('rg'):
                    qualificacao_texto += f" e do RG nº {parte_dados.get('rg')}"
            elif parte_dados.get('cnpj'):
                qualificacao_texto = f"pessoa jurídica de direito privado, inscrita no CNPJ sob o nº {parte_dados.get('cnpj', '')}"
            else:
                qualificacao_texto = "[QUALIFICAÇÃO NÃO INFORMADA]"

            return f"<p><strong>{tipo_parte.upper()}:</strong> {nome.upper()}, {qualificacao_texto}, com sede ou domicílio em {endereco}.</p>"

        qualificacao_contratante = montar_qualificacao(contratante, "Contratante")
        qualificacao_contratado = montar_qualificacao(contratado, "Contratado")

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
    <p style="text-align:center;margin-top:2cm;margin-bottom:1cm;">_________________________________________<br><strong>{str(contratante.get('nome', '')).upper()}</strong><br>Contratante</p>
    <p style="text-align:center;margin-bottom:2cm;">_________________________________________<br><strong>{str(contratado.get('nome', '')).upper()}</strong><br>Contratado</p>
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
