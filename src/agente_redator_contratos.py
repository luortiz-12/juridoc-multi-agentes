# agente_redator_contratos.py - Agente Especializado em Contratos

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
    """
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("DEEPSEEK_API_KEY não configurada")
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("✅ Agente Redator de CONTRATOS inicializado.")

    async def gerar_documento_html_puro_async(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        print("📝 Gerando Contrato completo...")
        
        prompt_completo = f"""
        Você é um advogado especialista em direito contratual. Sua tarefa é redigir um contrato completo, formal e juridicamente sólido com base nos dados do formulário e na pesquisa de modelos.

        ESTRUTURA OBRIGATÓRIA DO CONTRATO:
        1.  **TÍTULO:** Ex: "CONTRATO DE PRESTAÇÃO DE SERVIÇOS".
        2.  **QUALIFICAÇÃO DAS PARTES:** Identifique o CONTRATANTE e o CONTRATADO.
        3.  **CLÁUSULA PRIMEIRA - DO OBJETO:** Descreva detalhadamente o objeto do contrato.
        4.  **CLÁUSULA SEGUNDA - DO VALOR E DA FORMA DE PAGAMENTO:** Especifique o valor e como será pago.
        5.  **CLÁUSULA TERCEIRA - DOS PRAZOS:** Detalhe os prazos de início, etapas e conclusão.
        6.  **CLÁUSULA QUARTA - DAS OBRIGAÇÕES DAS PARTES:** Liste as responsabilidades do Contratante e do Contratado.
        7.  **CLÁUSULA QUINTA - DAS PENALIDADES:** Descreva as multas por atraso ou descumprimento.
        8.  **CLÁUSULA SEXTA - DA RESCISÃO:** Condições para rescindir o contrato.
        9.  **CLÁUSULA SÉTIMA - DO FORO:** Especifique o foro de eleição.
        10. **FECHO E ASSINATURAS:** Local, data e linhas para as assinaturas.

        DADOS DO FORMULÁRIO:
        {json.dumps(dados_formulario, ensure_ascii=False, indent=2)}

        PESQUISA DE MODELOS E CLÁUSULAS (use como referência e inspiração):
        {pesquisas.get('pesquisa_formatada', 'Nenhuma pesquisa de referência foi encontrada.')}

        REGRAS DE FORMATAÇÃO:
        - A resposta DEVE ser um bloco de código HTML.
        - Use `<h1>` para o título do contrato, `<h2>` para a qualificação das partes, e `<h3>` para os títulos das cláusulas (CLÁUSULA PRIMEIRA, etc.).
        - Use `<p>` para o texto das cláusulas e `<strong>` para negrito.
        - NÃO use Markdown.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-chat", messages=[{"role": "user", "content": prompt_completo}],
                max_tokens=8192, temperature=0.2
            )
            return re.sub(r'^```html|```$', '', response.choices[0].message.content.strip())
        except Exception as e:
            print(f"❌ ERRO na API ao gerar o contrato: {e}")
            return f"<h1>Erro na Geração do Contrato</h1><p>{e}</p>"

    def redigir_peticao_completa(self, dados_estruturados: Dict, pesquisa_juridica: Dict) -> Dict:
        try:
            return {"documento_html": asyncio.run(self.gerar_documento_html_puro_async(dados_estruturados, pesquisa_juridica))}
        except Exception as e:
            return {"status": "erro", "erro": str(e)}
