# agente_redator_jurisprudencia.py - Novo Agente Especializado em Formatar Resultados de Pesquisa

from typing import Dict, Any, List
from datetime import datetime

class AgenteRedatorJurisprudencia:
    """
    Agente Especializado com uma única responsabilidade:
    - Receber uma lista de resultados de pesquisa de jurisprudência.
    - Formatar esses resultados em um documento HTML claro, organizado e profissional.
    - Este agente não usa IA para gerar texto, apenas para formatar dados.
    """
    def __init__(self):
        print("📑 Inicializando Agente Redator de JURISPRUDÊNCIA...")
        print("✅ Agente Redator de JURISPRUDÊNCIA pronto.")

    def formatar_resultados(self, termos_pesquisados: List[str], resultados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ponto de entrada principal do agente. Recebe os resultados da pesquisa e retorna um HTML formatado.
        """
        try:
            print(f"📄 Formatando {len(resultados)} resultados de jurisprudência...")
            
            # Constrói o corpo do HTML com os resultados da pesquisa
            corpo_html = ""
            if not resultados:
                corpo_html = "<h2>Nenhum resultado de jurisprudência encontrado</h2><p>A pesquisa não retornou conteúdos relevantes para os termos solicitados.</p>"
            else:
                for item in resultados:
                    titulo = item.get('titulo', 'Título não encontrado')
                    url = item.get('url', '#')
                    texto = item.get('texto', 'Conteúdo não extraído.')
                    
                    # Limita o resumo do texto para não poluir o documento
                    resumo = texto[:1500] + '...' if len(texto) > 1500 else texto
                    
                    corpo_html += f"""
                        <div class="resultado-item">
                            <h3>{titulo}</h3>
                            <p><strong>Fonte:</strong> <a href="{url}" target="_blank">{url}</a></p>
                            <div class="resumo">
                                <p>{resumo}</p>
                            </div>
                        </div>
                        <hr>
                    """

            # Monta o documento HTML final
            documento_final = self._montar_documento_html_final(termos_pesquisados, corpo_html)
            
            print("✅ Documento de jurisprudência formatado com sucesso.")
            return {"status": "sucesso", "documento_html": documento_final}

        except Exception as e:
            print(f"❌ Erro ao formatar os resultados da jurisprudência: {e}")
            return {"status": "erro", "erro": str(e)}

    def _montar_documento_html_final(self, termos_pesquisados: List[str], corpo_html: str) -> str:
        """Cria a estrutura HTML final do documento."""
        
        termos_str = ", ".join(f"<strong>'{termo}'</strong>" for termo in termos_pesquisados)
        
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Pesquisa de Jurisprudência</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 2cm; background-color: #f9f9f9; color: #333; }}
        h1, h2, h3 {{ font-family: 'Georgia', 'Times New Roman', Times, serif; color: #2c3e50; }}
        h1 {{ text-align: center; font-size: 20pt; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 1cm; }}
        h2 {{ font-size: 16pt; margin-top: 1.5cm; }}
        h3 {{ font-size: 14pt; margin-top: 1cm; color: #3498db; }}
        p {{ text-align: justify; margin-bottom: 15px; }}
        hr {{ border: 0; border-top: 1px solid #ddd; margin: 1.5cm 0; }}
        .resultado-item {{ background-color: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .resumo {{ background-color: #f2f2f2; padding: 15px; border-radius: 4px; border-left: 4px solid #bdc3c7; }}
        a {{ color: #2980b9; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Relatório de Pesquisa de Jurisprudência</h1>
    <p>Pesquisa realizada em: <strong>{datetime.now().strftime('%d de %B de %Y às %H:%M')}</strong></p>
    <p>Termos pesquisados: {termos_str}</p>
    <hr>
    {corpo_html}
</body>
</html>
        """