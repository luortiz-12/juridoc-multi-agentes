# agente_redator_final.py - Versão final, completa e robusta para deploy.

import os
import re
import html
from datetime import datetime
from typing import Dict, Any, List, Optional

class AgenteRedatorFinal:
    """
    Agente Redator que recebe os dados estruturados e a pesquisa jurídica para redigir 
    uma petição completa. Esta versão é ajustada para ser 100% compatível com a saída 
    do 'PesquisaJuridica' e é robusta contra falhas de entrada de dados.
    """
    # Constantes para chaves e configurações
    CHAVE_CONTEUDOS = 'conteudos_extraidos'
    CHAVE_TIPO = 'tipo'
    CHAVE_TEXTO = 'texto'
    
    TIPO_LEGISLACAO = 'legislacao'
    TIPO_JURISPRUDENCIA = 'jurisprudencia'
    TIPO_DOUTRINA = 'doutrina'

    # Limites de conteúdo a serem incluídos na petição
    MAX_LEGISLACAO = 5
    MAX_JURISPRUDENCIA = 5
    MAX_DOUTRINA = 3

    def __init__(self):
        """Inicializa o Agente Redator."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        print("✍️  Iniciando Agente Redator (Versão Final)...")

    def redigir_peticao_completa(self, dados_estruturados: Optional[Dict[str, Any]], pesquisa_juridica: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ponto de entrada principal para redigir a petição completa.
        Trata dados de entrada que possam ser nulos ou incompletos para evitar erros.
        """
        try:
            print("📝 Iniciando redação final da petição...")
            
            # Garante que as variáveis de entrada sejam sempre dicionários, mesmo que vazios.
            dados_estruturados = dados_estruturados or {}
            pesquisa_juridica = pesquisa_juridica or {}

            # Extrai os textos da pesquisa bruta, já formatando-os para HTML.
            textos_legislacao = self._extrair_textos_por_tipo(pesquisa_juridica, self.TIPO_LEGISLACAO, self.MAX_LEGISLACAO)
            textos_jurisprudencia = self._extrair_textos_por_tipo(pesquisa_juridica, self.TIPO_JURISPRUDENCIA, self.MAX_JURISPRUDENCIA)
            textos_doutrina = self._extrair_textos_por_tipo(pesquisa_juridica, self.TIPO_DOUTRINA, self.MAX_DOUTRINA)

            # Gera o documento HTML completo a partir dos dados processados.
            documento_html = self._gerar_documento_html(
                dados_estruturados,
                textos_legislacao,
                textos_jurisprudencia,
                textos_doutrina
            )
            
            tamanho_final = len(documento_html)
            print(f"📄 Documento final gerado com sucesso ({tamanho_final} caracteres).")

            return {
                "status": "sucesso",
                "documento_html": documento_html,
                "tamanho_caracteres": tamanho_final,
                "transcricoes_incluidas": {
                    self.TIPO_LEGISLACAO: len(textos_legislacao),
                    self.TIPO_JURISPRUDENCIA: len(textos_jurisprudencia),
                    self.TIPO_DOUTRINA: len(textos_doutrina)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Erro crítico durante a redação: {e}")
            return self._gerar_documento_emergencia(dados_estruturados or {})

    def _extrair_textos_por_tipo(self, pesquisa_juridica: Dict[str, Any], tipo_conteudo: str, limite: int) -> List[Dict[str, str]]:
        """Extrai, limpa e limita os textos de um tipo específico da pesquisa."""
        textos_extraidos = []
        for conteudo in pesquisa_juridica.get(self.CHAVE_CONTEUDOS, []):
            if conteudo and conteudo.get(self.CHAVE_TIPO) == tipo_conteudo:
                texto_bruto = conteudo.get(self.CHAVE_TEXTO, '')
                texto_limpo = self._limpar_e_formatar_texto(texto_bruto)
                
                if len(texto_limpo) > 150:
                    textos_extraidos.append({
                        "titulo": conteudo.get('titulo', f'{tipo_conteudo.capitalize()} sem título'),
                        "texto": texto_limpo
                    })
        print(f"🔎 Encontrados e processados {len(textos_extraidos)} conteúdos do tipo '{tipo_conteudo}'.")
        return textos_extraidos[:limite]

    def _limpar_e_formatar_texto(self, texto: str) -> str:
        """Limpa o texto bruto, escapa caracteres HTML e preserva parágrafos."""
        if not texto:
            return ""
        
        texto_escapado = html.escape(texto)
        texto_sem_espacos_extras = re.sub(r'[ \t\r\f\v]+', ' ', texto_escapado)
        texto_com_paragrafos = re.sub(r'\n\s*\n', '\n\n', texto_sem_espacos_extras)
        
        return texto_com_paragrafos.strip()

    def _gerar_documento_html(self, dados: Dict[str, Any], legislacao: List[Dict], jurisprudencia: List[Dict], doutrina: List[Dict]) -> str:
        """Estrutura o documento HTML final chamando funções auxiliares para cada seção."""
        autor = dados.get('autor', {})
        reu = dados.get('reu', {})
        cabecalho = self._gerar_cabecalho_html(dados.get('tipo_acao', 'Ação Judicial'))
        secao_partes = self._gerar_secao_partes_html(autor, reu, dados.get('tipo_acao', 'Ação Judicial'))
        secao_fatos = self._gerar_secao_fatos_html(dados.get('fatos', ''))
        secao_direito = self._gerar_secao_direito_html(legislacao, jurisprudencia, doutrina)
        secao_pedidos = self._gerar_secao_pedidos_html(dados.get('pedidos', ''))
        secao_final = self._gerar_secoes_finais_html(dados.get('valor_causa', ''))
        rodape = self._gerar_rodape_html()

        # Concatena todas as partes para formar o documento completo.
        return f"{cabecalho}<body>{secao_partes}{secao_fatos}{secao_direito}{secao_pedidos}{secao_final}{rodape}</body></html>"

    def _gerar_cabecalho_html(self, tipo_acao: str) -> str:
        """Gera a tag <head> do HTML, incluindo o título e todo o CSS para formatação."""
        css = """
        <style>
            body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; margin: 2cm; text-align: justify; color: #000; }
            h1 { text-align: center; font-size: 16pt; font-weight: bold; margin: 30px 0; text-transform: uppercase; }
            h2 { font-size: 14pt; font-weight: bold; margin: 25px 0 15px 0; text-align: left; text-transform: uppercase; }
            h3 { font-size: 12pt; font-weight: bold; margin: 20px 0 10px 0; text-align: left; text-transform: uppercase; }
            p { text-indent: 2em; margin-bottom: 15px; text-align: justify; }
            .enderecamento { margin-bottom: 30px; text-align: justify; }
            .assinatura { text-align: center; margin-top: 50px; }
            .transcricao { margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #ccc; font-style: italic; white-space: pre-wrap; word-wrap: break-word; }
            .transcricao h4 { margin-top: 0; font-style: normal; font-weight: bold; }
            .transcricao-legislacao { border-left-color: #28a745; }
            .transcricao-jurisprudencia { border-left-color: #dc3545; }
            .transcricao-doutrina { border-left-color: #ffc107; }
        </style>
        """
        return f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>{tipo_acao}</title>{css}</head>'

    def _gerar_secao_partes_html(self, autor: Dict, reu: Dict, tipo_acao: str) -> str:
        """Gera a seção de endereçamento e qualificação das partes."""
        return f"""
        <div class="enderecamento">
            <p><strong>EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DO TRABALHO DA ___ª VARA DO TRABALHO DE [COMARCA]</strong></p>
        </div>
        <h1>{tipo_acao}</h1>
        <h2>I - DAS PARTES</h2>
        <h3>DO(A) RECLAMANTE</h3>
        <p><strong>{autor.get('nome', '[NOME DO AUTOR]')}</strong>, {autor.get('qualificacao', '[QUALIFICAÇÃO]')}, residente e domiciliado(a) no {autor.get('endereco', '[ENDEREÇO]')}, vem, por seu advogado que esta subscreve, propor a presente AÇÃO TRABALHISTA.</p>
        <h3>DO(A) RECLAMADO(A)</h3>
        <p><strong>{reu.get('nome', '[NOME DO RÉU]')}</strong>, {reu.get('qualificacao', '[QUALIFICAÇÃO]')}, com sede em {reu.get('endereco', '[ENDEREÇO]')}, pelos fatos e fundamentos a seguir.</p>
        """

    def _gerar_secao_fatos_html(self, fatos: str) -> str:
        """Gera a seção 'Dos Fatos' da petição."""
        return f"<h2>II - DOS FATOS</h2><p>{fatos if fatos else 'FATOS A SEREM DETALHADOS.'}</p>"

    def _gerar_secao_direito_html(self, legislacao: List[Dict], jurisprudencia: List[Dict], doutrina: List[Dict]) -> str:
        """Gera a seção 'Do Direito', inserindo as transcrições coletadas."""
        direito_html = "<h2>III - DO DIREITO</h2>"
        
        if not legislacao and not jurisprudencia and not doutrina:
            direito_html += "<p>A fundamentação jurídica detalhada, com base na legislação, jurisprudência e doutrina aplicáveis, será apresentada em momento oportuno, corroborando os fatos narrados e os pedidos formulados.</p>"
            return direito_html

        if legislacao:
            direito_html += "<h3>DA LEGISLAÇÃO APLICÁVEL</h3>"
            for item in legislacao:
                direito_html += f"""<div class="transcricao transcricao-legislacao"><h4>Fonte: {item['titulo']}</h4><p>{item['texto']}</p></div>"""
        
        if jurisprudencia:
            direito_html += "<h3>DA JURISPRUDÊNCIA PERTINENTE</h3>"
            for item in jurisprudencia:
                direito_html += f"""<div class="transcricao transcricao-jurisprudencia"><h4>Fonte: {item['titulo']}</h4><p>{item['texto']}</p></div>"""

        if doutrina:
            direito_html += "<h3>DA DOUTRINA ESPECIALIZADA</h3>"
            for item in doutrina:
                direito_html += f"""<div class="transcricao transcricao-doutrina"><h4>Fonte: {item['titulo']}</h4><p>{item['texto']}</p></div>"""
        
        return direito_html

    def _gerar_secao_pedidos_html(self, pedidos: str) -> str:
        """Gera a seção 'Dos Pedidos' com formatação de lista."""
        pedidos_html = "<h2>IV - DOS PEDIDOS</h2><p>Ante o exposto, requer a Vossa Excelência:</p>"
        # Formata os pedidos para que fiquem mais parecidos com uma lista
        lista_pedidos = [p.strip() for p in pedidos.split(',') if p.strip()]
        pedidos_html += "<ul>"
        for pedido in lista_pedidos:
            pedidos_html += f"<li>{pedido.capitalize()};</li>"
        pedidos_html += "</ul>"
        return pedidos_html

    def _gerar_secoes_finais_html(self, valor_causa: str) -> str:
        """Gera as seções finais da petição (Valor da Causa e Provas)."""
        return f"""
        <h2>V - DO VALOR DA CAUSA</h2>
        <p>Dá-se à causa o valor de {valor_causa if valor_causa else '[VALOR DA CAUSA]'}.</p>
        <h2>VI - DAS PROVAS</h2>
        <p>Protesta provar o alegado por todos os meios de prova em direito admitidos, em especial a documental, testemunhal e pericial, caso necessário.</p>
        """
        
    def _gerar_rodape_html(self) -> str:
        """Gera o rodapé com local, data e assinatura."""
        return f"""
        <p>Termos em que,<br>Pede deferimento.</p>
        <div class="assinatura">
            <p>[Local], {datetime.now().strftime('%d de %B de %Y')}</p>
            <br><br>
            <p>_________________________________</p>
            <p><strong>[NOME DO ADVOGADO]</strong></p>
            <p>OAB/[UF] nº [NÚMERO]</p>
        </div>
        """

    def _gerar_documento_emergencia(self, dados_estruturados: Dict[str, Any]) -> Dict[str, Any]:
        """Gera um documento HTML básico em caso de falha no processo principal."""
        autor_info = dados_estruturados.get('autor', {})
        reu_info = dados_estruturados.get('reu', {})
        documento_basico = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head><meta charset="UTF-8"><title>Petição Inicial de Emergência</title></head>
        <body>
            <h1>PETIÇÃO INICIAL</h1>
            <h2>I - Das Partes</h2>
            <p>Autor: {autor_info.get('nome', '[NOME A SER PREENCHIDO]')}</p>
            <p>Réu: {reu_info.get('nome', '[NOME A SER PREENCHIDO]')}</p>
            <h2>II - Dos Fatos</h2>
            <p>{dados_estruturados.get('fatos', '[FATOS A SEREM PREENCHIDOS]')}</p>
            <h2>III - Dos Pedidos</h2>
            <p>{dados_estruturados.get('pedidos', '[PEDIDOS A SEREM PREENCHIDOS]')}</p>
            <p>Pede deferimento.</p>
        </body>
        </html>
        """
        return {
            "status": "emergencia",
            "documento_html": documento_basico,
            "tamanho_caracteres": len(documento_basico),
            "observacao": "Documento gerado em modo de emergência devido a erro no processamento principal."
        }