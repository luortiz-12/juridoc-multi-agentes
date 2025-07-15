# agente_redator_corrigido_final.py - Agente Redator que USA CORRETAMENTE as pesquisas

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List
import openai

class AgenteRedator:
    def __init__(self):
        """Inicializa o Agente Redator que USA CORRETAMENTE as pesquisas"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        
        openai.api_key = self.openai_api_key
        print("✍️ Iniciando Agente Redator CORRIGIDO - USA PESQUISAS REAIS...")
        
    def redigir_peticao_completa(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redige petição completa USANDO CORRETAMENTE o conteúdo das pesquisas
        """
        try:
            print("📝 Iniciando redação USANDO PESQUISAS REAIS...")
            print(f"🔍 Dados de pesquisa recebidos: {list(pesquisa_juridica.keys())}")
            
            # Extrair textos completos das pesquisas (ESTRUTURA CORRETA)
            textos_legislacao = self._extrair_textos_legislacao_correto(pesquisa_juridica)
            textos_jurisprudencia = self._extrair_textos_jurisprudencia_correto(pesquisa_juridica)
            textos_doutrina = self._extrair_textos_doutrina_correto(pesquisa_juridica)
            
            print(f"📚 Legislação extraída: {len(textos_legislacao)} textos")
            print(f"⚖️ Jurisprudência extraída: {len(textos_jurisprudencia)} textos")
            print(f"📖 Doutrina extraída: {len(textos_doutrina)} textos")
            
            # Usar OpenAI para gerar documento inteligente
            documento_html = self._gerar_documento_inteligente_com_ia(
                dados_estruturados, 
                textos_legislacao, 
                textos_jurisprudencia, 
                textos_doutrina
            )
            
            # Garantir tamanho mínimo de 30k caracteres
            if len(documento_html) < 30000:
                documento_html = self._expandir_documento_com_ia(documento_html, dados_estruturados, textos_legislacao, textos_jurisprudencia, textos_doutrina)
            
            tamanho_final = len(documento_html)
            print(f"📄 Documento gerado com {tamanho_final} caracteres")
            
            return {
                "status": "sucesso",
                "documento_html": documento_html,
                "tamanho_caracteres": tamanho_final,
                "pesquisas_utilizadas": {
                    "legislacao": len(textos_legislacao),
                    "jurisprudencia": len(textos_jurisprudencia),
                    "doutrina": len(textos_doutrina)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro na redação: {str(e)}")
            return self._gerar_documento_emergencia(dados_estruturados)
    
    def _extrair_textos_legislacao_correto(self, pesquisa_juridica: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrai textos de legislação com a ESTRUTURA CORRETA"""
        textos = []
        
        # Verificar se há resultados de legislação
        if 'legislacao' in pesquisa_juridica:
            for item in pesquisa_juridica['legislacao']:
                if item and isinstance(item, dict) and 'texto' in item:
                    texto_limpo = self._limpar_texto_legislacao(item['texto'])
                    if len(texto_limpo) > 100:
                        textos.append({
                            'texto': texto_limpo,
                            'url': item.get('url', ''),
                            'titulo': item.get('titulo', 'Legislação')
                        })
        
        # Verificar estrutura alternativa
        if 'conteudos_extraidos' in pesquisa_juridica:
            for conteudo in pesquisa_juridica['conteudos_extraidos']:
                if conteudo.get('tipo') == 'legislacao' and 'texto' in conteudo:
                    texto_limpo = self._limpar_texto_legislacao(conteudo['texto'])
                    if len(texto_limpo) > 100:
                        textos.append({
                            'texto': texto_limpo,
                            'url': conteudo.get('url', ''),
                            'titulo': conteudo.get('titulo', 'Legislação')
                        })
        
        print(f"📚 Legislação encontrada: {len(textos)} textos válidos")
        return textos[:10]  # Máximo 10 textos
    
    def _extrair_textos_jurisprudencia_correto(self, pesquisa_juridica: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrai textos de jurisprudência com a ESTRUTURA CORRETA"""
        textos = []
        
        # Verificar se há resultados de jurisprudência
        if 'jurisprudencia' in pesquisa_juridica:
            for item in pesquisa_juridica['jurisprudencia']:
                if item and isinstance(item, dict) and 'texto' in item:
                    texto_limpo = self._limpar_texto_jurisprudencia(item['texto'])
                    if len(texto_limpo) > 100:
                        textos.append({
                            'texto': texto_limpo,
                            'url': item.get('url', ''),
                            'titulo': item.get('titulo', 'Jurisprudência')
                        })
        
        # Verificar estrutura alternativa
        if 'conteudos_extraidos' in pesquisa_juridica:
            for conteudo in pesquisa_juridica['conteudos_extraidos']:
                if conteudo.get('tipo') == 'jurisprudencia' and 'texto' in conteudo:
                    texto_limpo = self._limpar_texto_jurisprudencia(conteudo['texto'])
                    if len(texto_limpo) > 100:
                        textos.append({
                            'texto': texto_limpo,
                            'url': conteudo.get('url', ''),
                            'titulo': conteudo.get('titulo', 'Jurisprudência')
                        })
        
        print(f"⚖️ Jurisprudência encontrada: {len(textos)} textos válidos")
        return textos[:8]  # Máximo 8 textos
    
    def _extrair_textos_doutrina_correto(self, pesquisa_juridica: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrai textos de doutrina com a ESTRUTURA CORRETA"""
        textos = []
        
        # Verificar se há resultados de doutrina
        if 'doutrina' in pesquisa_juridica:
            for item in pesquisa_juridica['doutrina']:
                if item and isinstance(item, dict) and 'texto' in item:
                    texto_limpo = self._limpar_texto_doutrina(item['texto'])
                    if len(texto_limpo) > 100:
                        textos.append({
                            'texto': texto_limpo,
                            'url': item.get('url', ''),
                            'titulo': item.get('titulo', 'Doutrina')
                        })
        
        # Verificar estrutura alternativa
        if 'conteudos_extraidos' in pesquisa_juridica:
            for conteudo in pesquisa_juridica['conteudos_extraidos']:
                if conteudo.get('tipo') == 'doutrina' and 'texto' in conteudo:
                    texto_limpo = self._limpar_texto_doutrina(conteudo['texto'])
                    if len(texto_limpo) > 100:
                        textos.append({
                            'texto': texto_limpo,
                            'url': conteudo.get('url', ''),
                            'titulo': conteudo.get('titulo', 'Doutrina')
                        })
        
        print(f"📖 Doutrina encontrada: {len(textos)} textos válidos")
        return textos[:8]  # Máximo 8 textos
    
    def _limpar_texto_legislacao(self, texto: str) -> str:
        """Limpa e formata texto de legislação mantendo artigos completos"""
        if not texto:
            return ""
        
        # Remove caracteres especiais mantendo estrutura legal
        texto = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\"\'\/\°\§\ª\º]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        # Para legislação, manter texto mais extenso (até 1000 palavras)
        palavras = texto.split()
        if len(palavras) > 1000:
            return ' '.join(palavras[:1000])
        
        return texto
    
    def _limpar_texto_jurisprudencia(self, texto: str) -> str:
        """Limpa e formata texto de jurisprudência mantendo ementas completas"""
        if not texto:
            return ""
        
        # Remove caracteres especiais
        texto = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\"\'\/]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        # Para jurisprudência, manter até 800 palavras
        palavras = texto.split()
        if len(palavras) > 800:
            return ' '.join(palavras[:800])
        
        return texto
    
    def _limpar_texto_doutrina(self, texto: str) -> str:
        """Limpa e formata texto de doutrina mantendo conteúdo relevante"""
        if not texto:
            return ""
        
        # Remove caracteres especiais
        texto = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\"\'\/]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        # Para doutrina, manter até 600 palavras
        palavras = texto.split()
        if len(palavras) > 600:
            return ' '.join(palavras[:600])
        
        return texto
    
    def _gerar_documento_inteligente_com_ia(self, dados: Dict[str, Any], legislacao: List[Dict], jurisprudencia: List[Dict], doutrina: List[Dict]) -> str:
        """Gera documento usando IA para decidir quando transcrever vs parafrasear"""
        
        # Dados das partes
        autor = dados.get('autor', {})
        reu = dados.get('reu', {})
        fatos = dados.get('fatos', '')
        pedidos = dados.get('pedidos', '')
        valor_causa = dados.get('valor_causa', '')
        tipo_acao = dados.get('tipo_acao', 'Ação Judicial')
        
        # Preparar contexto para IA
        contexto_pesquisas = self._preparar_contexto_pesquisas(legislacao, jurisprudencia, doutrina)
        
        # Prompt para IA gerar documento inteligente
        prompt = f"""
Você é um advogado especialista em redação de petições. Redija uma petição inicial completa e profissional usando as pesquisas fornecidas.

DADOS DO CASO:
- Tipo: {tipo_acao}
- Autor: {autor.get('nome', '[NOME]')} - {autor.get('qualificacao', '[QUALIFICAÇÃO]')}
- Réu: {reu.get('nome', '[NOME]')} - {reu.get('qualificacao', '[QUALIFICAÇÃO]')}
- Fatos: {fatos}
- Pedidos: {pedidos}
- Valor: {valor_causa}

PESQUISAS JURÍDICAS DISPONÍVEIS:
{contexto_pesquisas}

INSTRUÇÕES IMPORTANTES:
1. USE as pesquisas fornecidas de forma inteligente:
   - LEGISLAÇÃO: Transcreva artigos na íntegra quando relevantes
   - JURISPRUDÊNCIA: Use como base e cite adequadamente
   - DOUTRINA: Parafrase e referencie os autores

2. Estruture a petição com:
   - Endereçamento formal
   - Qualificação das partes
   - Fatos detalhados
   - Fundamentação jurídica robusta (usando as pesquisas)
   - Pedidos específicos
   - Valor da causa
   - Provas

3. O documento deve ter pelo menos 25.000 caracteres
4. Use formatação HTML profissional com CSS
5. Inclua as pesquisas de forma orgânica no texto

Gere a petição completa em HTML:
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um advogado especialista em redação de petições jurídicas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            documento_ia = response.choices[0].message.content
            
            # Se a IA não gerou HTML completo, adicionar estrutura
            if not documento_ia.startswith('<!DOCTYPE html>'):
                documento_ia = self._adicionar_estrutura_html(documento_ia)
            
            return documento_ia
            
        except Exception as e:
            print(f"⚠️ Erro na IA, usando método tradicional: {e}")
            return self._gerar_documento_tradicional(dados, legislacao, jurisprudencia, doutrina)
    
    def _preparar_contexto_pesquisas(self, legislacao: List[Dict], jurisprudencia: List[Dict], doutrina: List[Dict]) -> str:
        """Prepara contexto das pesquisas para a IA"""
        contexto = ""
        
        # Legislação
        if legislacao:
            contexto += "LEGISLAÇÃO ENCONTRADA:\n"
            for i, item in enumerate(legislacao[:5], 1):
                contexto += f"{i}. {item['titulo']}\n"
                contexto += f"Texto: {item['texto'][:500]}...\n"
                contexto += f"Fonte: {item['url']}\n\n"
        
        # Jurisprudência
        if jurisprudencia:
            contexto += "JURISPRUDÊNCIA ENCONTRADA:\n"
            for i, item in enumerate(jurisprudencia[:5], 1):
                contexto += f"{i}. {item['titulo']}\n"
                contexto += f"Texto: {item['texto'][:500]}...\n"
                contexto += f"Fonte: {item['url']}\n\n"
        
        # Doutrina
        if doutrina:
            contexto += "DOUTRINA ENCONTRADA:\n"
            for i, item in enumerate(doutrina[:5], 1):
                contexto += f"{i}. {item['titulo']}\n"
                contexto += f"Texto: {item['texto'][:500]}...\n"
                contexto += f"Fonte: {item['url']}\n\n"
        
        return contexto
    
    def _adicionar_estrutura_html(self, conteudo: str) -> str:
        """Adiciona estrutura HTML se necessário"""
        css = """
        <style>
            body {
                font-family: 'Times New Roman', serif;
                font-size: 12pt;
                line-height: 1.8;
                margin: 40px;
                text-align: justify;
                color: #000;
            }
            h1 { text-align: center; font-size: 18pt; font-weight: bold; margin: 30px 0; }
            h2 { font-size: 14pt; font-weight: bold; margin: 25px 0 15px 0; }
            h3 { font-size: 12pt; font-weight: bold; margin: 20px 0 10px 0; }
            p { text-indent: 2em; margin-bottom: 15px; text-align: justify; }
            .transcricao {
                margin: 20px 0; padding: 20px; background-color: #f8f9fa;
                border-left: 5px solid #007bff; font-style: italic;
            }
        </style>
        """
        
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Petição Inicial</title>
            {css}
        </head>
        <body>
            {conteudo}
        </body>
        </html>
        """
    
    def _gerar_documento_tradicional(self, dados: Dict[str, Any], legislacao: List[Dict], jurisprudencia: List[Dict], doutrina: List[Dict]) -> str:
        """Gera documento tradicional se IA falhar"""
        
        autor = dados.get('autor', {})
        reu = dados.get('reu', {})
        fatos = dados.get('fatos', '')
        pedidos = dados.get('pedidos', '')
        valor_causa = dados.get('valor_causa', '')
        tipo_acao = dados.get('tipo_acao', 'Ação Judicial')
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Petição Inicial</title>
            <style>
                body {{ font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.8; margin: 40px; text-align: justify; }}
                h1 {{ text-align: center; font-size: 18pt; font-weight: bold; margin: 30px 0; }}
                h2 {{ font-size: 14pt; font-weight: bold; margin: 25px 0 15px 0; }}
                p {{ text-indent: 2em; margin-bottom: 15px; text-align: justify; }}
                .transcricao {{ margin: 20px 0; padding: 20px; background-color: #f8f9fa; border-left: 5px solid #007bff; }}
            </style>
        </head>
        <body>
            <h1>{tipo_acao}</h1>
            
            <h2>I - Das Partes</h2>
            <p><strong>{autor.get('nome', '[NOME]')}</strong>, {autor.get('qualificacao', '[QUALIFICAÇÃO]')}</p>
            <p><strong>{reu.get('nome', '[NOME]')}</strong>, {reu.get('qualificacao', '[QUALIFICAÇÃO]')}</p>
            
            <h2>II - Dos Fatos</h2>
            <p>{fatos}</p>
            
            <h2>III - Do Direito</h2>
        """
        
        # Adicionar legislação encontrada
        if legislacao:
            html += "<h3>Da Legislação Aplicável</h3>"
            for item in legislacao[:3]:
                html += f"""
                <div class="transcricao">
                    <h4>{item['titulo']}</h4>
                    <p>{item['texto']}</p>
                    <small>Fonte: {item['url']}</small>
                </div>
                """
        
        # Adicionar jurisprudência encontrada
        if jurisprudencia:
            html += "<h3>Da Jurisprudência</h3>"
            for item in jurisprudencia[:3]:
                html += f"""
                <div class="transcricao">
                    <h4>{item['titulo']}</h4>
                    <p>Conforme entendimento jurisprudencial: {item['texto']}</p>
                    <small>Fonte: {item['url']}</small>
                </div>
                """
        
        # Adicionar doutrina encontrada
        if doutrina:
            html += "<h3>Da Doutrina</h3>"
            for item in doutrina[:3]:
                html += f"""
                <div class="transcricao">
                    <h4>{item['titulo']}</h4>
                    <p>A doutrina especializada ensina que: {item['texto']}</p>
                    <small>Fonte: {item['url']}</small>
                </div>
                """
        
        html += f"""
            <h2>IV - Dos Pedidos</h2>
            <p>{pedidos}</p>
            
            <h2>V - Do Valor da Causa</h2>
            <p>Valor: {valor_causa}</p>
            
            <p>Pede deferimento.</p>
        </body>
        </html>
        """
        
        return html
    
    def _expandir_documento_com_ia(self, documento_html: str, dados: Dict[str, Any], legislacao: List[Dict], jurisprudencia: List[Dict], doutrina: List[Dict]) -> str:
        """Expande documento usando IA se necessário"""
        
        if len(documento_html) >= 30000:
            return documento_html
        
        # Adicionar seções extras usando as pesquisas
        secoes_extras = ""
        
        # Usar mais legislação se disponível
        if len(legislacao) > 3:
            secoes_extras += "<h2>Legislação Complementar</h2>"
            for item in legislacao[3:6]:
                secoes_extras += f"""
                <div class="transcricao">
                    <h4>{item['titulo']}</h4>
                    <p>{item['texto']}</p>
                </div>
                """
        
        # Usar mais jurisprudência se disponível
        if len(jurisprudencia) > 3:
            secoes_extras += "<h2>Jurisprudência Adicional</h2>"
            for item in jurisprudencia[3:6]:
                secoes_extras += f"""
                <div class="transcricao">
                    <h4>{item['titulo']}</h4>
                    <p>O tribunal decidiu que: {item['texto']}</p>
                </div>
                """
        
        # Inserir antes do fechamento
        documento_html = documento_html.replace('</body>', secoes_extras + '</body>')
        
        return documento_html
    
    def _gerar_documento_emergencia(self, dados_estruturados: Dict[str, Any]) -> Dict[str, Any]:
        """Gera documento de emergência se houver falha"""
        
        documento_basico = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Petição Inicial</title>
        </head>
        <body>
            <h1>PETIÇÃO INICIAL</h1>
            <h2>I - Das Partes</h2>
            <p>Autor: {dados_estruturados.get('autor', {}).get('nome', '[NOME]')}</p>
            <p>Réu: {dados_estruturados.get('reu', {}).get('nome', '[NOME]')}</p>
            <h2>II - Dos Fatos</h2>
            <p>{dados_estruturados.get('fatos', '[FATOS]')}</p>
            <h2>III - Dos Pedidos</h2>
            <p>{dados_estruturados.get('pedidos', '[PEDIDOS]')}</p>
            <p>Pede deferimento.</p>
        </body>
        </html>
        """
        
        return {
            "status": "emergencia",
            "documento_html": documento_basico,
            "tamanho_caracteres": len(documento_basico),
            "observacao": "Documento gerado em modo de emergência"
        }