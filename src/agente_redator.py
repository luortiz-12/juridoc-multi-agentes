# agente_redator_ia_pura.py - Agente Redator que SEMPRE usa IA

import json
import logging
import openai
import os
from typing import Dict, List, Any
import re
from datetime import datetime

class AgenteRedator:
    """
    Agente Redator Inteligente que:
    1. Analisa o conteúdo do formulário e das pesquisas
    2. Decide inteligentemente quando transcrever na íntegra vs quando usar como base
    3. Para leis: entende e cita com resumo (não transcrição completa)
    4. Para jurisprudência: decide caso a caso se transcreve ou resume
    5. Para doutrina: sempre usa como base para elaborar texto próprio
    6. Retorna APENAS HTML puro do documento
    7. É superior a um advogado na qualidade dos documentos
        SEMPRE USA IA - SEM FALLBACKS
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurar OpenAI com logs claros
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ ERRO: OPENAI_API_KEY não encontrada nas variáveis de ambiente")
            raise ValueError("OPENAI_API_KEY não configurada")
        
        print(f"✅ OPENAI_API_KEY encontrada: {api_key[:10]}...{api_key[-4:]}")
        
        self.client = openai.OpenAI(api_key=api_key)
        print("✅ Cliente OpenAI inicializado com sucesso")
        
    def redigir_peticao_completa(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal chamado pelo orquestrador.
        Redige petição completa usando SEMPRE IA.
        """
        try:
            print("✍️ Iniciando redação inteligente da petição com IA...")
            print("🤖 Modo: SEMPRE IA - SEM FALLBACKS")
            
            # Gerar documento HTML usando SEMPRE IA
            documento_html = self.gerar_documento_html_puro(dados_estruturados, pesquisa_juridica)
            
            # Calcular estatísticas
            tamanho_documento = len(documento_html)
            score_qualidade = self._calcular_score_qualidade(documento_html, dados_estruturados, pesquisa_juridica)
            
            print(f"✅ Petição redigida com IA: {tamanho_documento} caracteres")
            print(f"📊 Score de qualidade: {score_qualidade}")
            
            # Retornar no formato esperado pelo orquestrador e main.py
            return {
                "status": "sucesso",
                "documento_html": documento_html,
                "dados_estruturados": dados_estruturados,
                "metadados": {
                    "timestamp": datetime.now().isoformat(),
                    "tamanho_caracteres": tamanho_documento,
                    "score_qualidade": score_qualidade,
                    "pesquisas_utilizadas": {
                        "legislacao": len(pesquisa_juridica.get('legislacao', [])),
                        "jurisprudencia": len(pesquisa_juridica.get('jurisprudencia', [])),
                        "doutrina": len(pesquisa_juridica.get('doutrina', []))
                    },
                    "estrategia_aplicada": "inteligencia_juridica_ia_pura",
                    "ia_funcionou": True
                }
            }
        
        except Exception as e:
            print(f"❌ ERRO na redação da petição: {e}")
            self.logger.error(f"Erro na redação da petição: {e}")
            
            # SEM FALLBACK - Retorna erro
            return {
                "status": "erro",
                "erro": str(e),
                "documento_html": "",
                "dados_estruturados": dados_estruturados,
                "metadados": {
                    "timestamp": datetime.now().isoformat(),
                    "erro_ocorrido": True,
                    "ia_funcionou": False,
                    "motivo_erro": str(e)
                }
            }

    def _calcular_score_qualidade(self, documento_html: str, dados_estruturados: Dict, pesquisas: Dict) -> int:
        """Calcula score de qualidade do documento gerado."""
        score = 60  # Base
        
        # Tamanho adequado
        if len(documento_html) > 25000: score += 15
        elif len(documento_html) > 20000: score += 10
        elif len(documento_html) > 15000: score += 5
        
        # Uso das pesquisas
        if pesquisas.get('legislacao'): score += 5
        if pesquisas.get('jurisprudencia'): score += 5
        if pesquisas.get('doutrina'): score += 5
        
        # Estrutura HTML
        if '<h1>' in documento_html or '<h2>' in documento_html: score += 5
        if 'style=' in documento_html or '<style>' in documento_html: score += 5
        
        return min(score, 100)

    def _chamar_openai_com_log(self, prompt: str, model: str = "gpt-4", max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """
        Método centralizado para chamar OpenAI com logs claros.
        """
        try:
            print(f"🤖 Chamando OpenAI - Modelo: {model}, Tokens: {max_tokens}")
            print(f"📝 Prompt (primeiros 100 chars): {prompt[:100]}...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            resultado = response.choices[0].message.content.strip()
            print(f"✅ OpenAI respondeu com sucesso: {len(resultado)} caracteres")
            
            return resultado
        
        except Exception as e:
            print(f"❌ ERRO na chamada OpenAI: {e}")
            print(f"🔧 Modelo: {model}, Tokens: {max_tokens}")
            raise e

    def analisar_contexto_juridico(self, dados_formulario: Dict, pesquisas: Dict) -> Dict:
        """
        Analisa o contexto jurídico usando IA para determinar estratégias inteligentes.
        """
        try:
            print("🧠 Analisando contexto jurídico com IA...")
            
            # Preparar dados para análise
            fatos = dados_formulario.get('fatos', '')
            area_direito = dados_formulario.get('area_direito', '')
            tipo_acao = dados_formulario.get('tipo_acao', '')
            valor_causa = dados_formulario.get('valor_causa', 0)
            
            # Usar IA para analisar contexto
            prompt_analise = f"""
            Você é um advogado expert. Analise este caso jurídico e determine estratégias inteligentes:

            DADOS DO CASO:
            - Área do direito: {area_direito}
            - Tipo de ação: {tipo_acao}
            - Fatos: {fatos[:1000]}
            - Valor da causa: {valor_causa}

            PESQUISAS DISPONÍVEIS:
            - Legislação: {len(pesquisas.get('legislacao', []))} itens
            - Jurisprudência: {len(pesquisas.get('jurisprudencia', []))} itens
            - Doutrina: {len(pesquisas.get('doutrina', []))} itens

            Retorne um JSON com estratégias para:
            1. legislacao: como usar (citacao_inteligente/citacao_simples, max_artigos, transcrever_integral: false)
            2. jurisprudencia: como usar (transcricao_seletiva/resumo_elaborado/citacao_resumida, max_casos)
            3. doutrina: como usar (elaboracao_propria sempre, max_autores)
            4. complexidade: muito_alta/alta/media/baixa
            5. tamanho_alvo: número de caracteres alvo

            Seja inteligente na análise. Para leis NUNCA transcrever integral, sempre resumir.
            Para jurisprudência decidir caso a caso se transcreve ou resume.
            Para doutrina SEMPRE elaborar texto próprio.
            """
            
            resposta_ia = self._chamar_openai_com_log(prompt_analise, "gpt-4", 800, 0.2)
            
            # Tentar parsear JSON da resposta
            try:
                estrategias = json.loads(resposta_ia)
                print("✅ Estratégias analisadas pela IA com sucesso")
                return estrategias
            except:
                print("⚠️ IA não retornou JSON válido, usando estratégias padrão")
                return self._estrategias_padrao()
        
        except Exception as e:
            print(f"❌ ERRO na análise de contexto: {e}")
            raise e

    def _estrategias_padrao(self) -> Dict:
        """Estratégias padrão quando IA não consegue analisar."""
        return {
            'legislacao': {'modo': 'citacao_inteligente', 'max_artigos': 4, 'transcrever_integral': False},
            'jurisprudencia': {'modo': 'resumo_elaborado', 'max_casos': 3},
            'doutrina': {'modo': 'elaboracao_propria', 'max_autores': 3},
            'complexidade': 'media',
            'tamanho_alvo': 25000
        }

    def processar_legislacao_inteligente(self, legislacao: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Processa legislação usando IA - NUNCA transcreve na íntegra.
        """
        try:
            print("⚖️ Processando legislação com IA...")
            
            if not legislacao:
                return "<div class='fundamentacao-legal'><p>Fundamentação legal será aplicada conforme legislação vigente.</p></div>"
            
            # Preparar textos da legislação
            textos_legislacao = []
            for item in legislacao[:estrategia.get('max_artigos', 4)]:
                texto = item.get('texto', '')[:1000]  # Limitar para não exceder tokens
                url = item.get('url', '')
                textos_legislacao.append(f"Texto: {texto}\nURL: {url}")
            
            prompt_legislacao = f"""
            Você é um advogado expert. Processe esta legislação para o caso:

            CASO: {contexto_caso[:500]}

            LEGISLAÇÃO ENCONTRADA:
            {chr(10).join(textos_legislacao)}

            INSTRUÇÕES:
            1. NUNCA transcreva leis na íntegra
            2. SEMPRE cite e resuma com suas próprias palavras
            3. Extraia números dos artigos (Art. X)
            4. Explique como cada lei se aplica ao caso específico
            5. Use linguagem jurídica formal

            Retorne HTML formatado com:
            - <div class="fundamentacao-legal"> para cada lei
            - <h4> para título com número do artigo
            - <p> para explicação da aplicação
            - <p class="fonte-legal"> para fonte

            Seja superior a um advogado na qualidade da análise.
            """
            
            resultado_ia = self._chamar_openai_com_log(prompt_legislacao, "gpt-4", 1200, 0.3)
            print("✅ Legislação processada pela IA")
            
            return resultado_ia
        
        except Exception as e:
            print(f"❌ ERRO no processamento de legislação: {e}")
            raise e

    def processar_jurisprudencia_inteligente(self, jurisprudencia: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Processa jurisprudência usando IA - decide quando transcrever vs resumir.
        """
        try:
            print("🏛️ Processando jurisprudência com IA...")
            
            if not jurisprudencia:
                return "<div class='jurisprudencia'><p>Jurisprudência aplicável será considerada conforme precedentes.</p></div>"
            
            # Preparar textos da jurisprudência
            textos_jurisprudencia = []
            for item in jurisprudencia[:estrategia.get('max_casos', 3)]:
                texto = item.get('texto', '')[:1500]  # Limitar para não exceder tokens
                url = item.get('url', '')
                textos_jurisprudencia.append(f"Decisão: {texto}\nURL: {url}")
            
            modo = estrategia.get('modo', 'resumo_elaborado')
            
            prompt_jurisprudencia = f"""
            Você é um advogado expert. Processe esta jurisprudência para o caso:

            CASO: {contexto_caso[:500]}
            MODO: {modo}

            JURISPRUDÊNCIA ENCONTRADA:
            {chr(10).join(textos_jurisprudencia)}

            INSTRUÇÕES:
            1. Analise cada decisão e decida inteligentemente:
               - Se for caso FUNDAMENTAL (TST/STF/STJ + muito relevante): transcreva trechos importantes
               - Se for caso RELEVANTE: resuma detalhadamente com análise
               - Se for caso COMUM: cite brevemente

            2. Para cada decisão, inclua:
               - Tribunal que decidiu
               - Resumo ou transcrição conforme relevância
               - Análise de como se aplica ao caso atual
               - Fonte

            3. Use HTML formatado:
               - <div class="jurisprudencia-integral"> para transcrições
               - <div class="jurisprudencia-analisada"> para resumos
               - <blockquote> para trechos transcritos
               - <p> para análises

            Seja superior a um advogado na análise jurisprudencial.
            """
            
            resultado_ia = self._chamar_openai_com_log(prompt_jurisprudencia, "gpt-4", 1500, 0.3)
            print("✅ Jurisprudência processada pela IA")
            
            return resultado_ia
        
        except Exception as e:
            print(f"❌ ERRO no processamento de jurisprudência: {e}")
            raise e

    def processar_doutrina_inteligente(self, doutrina: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Processa doutrina usando IA - SEMPRE elabora texto próprio.
        """
        try:
            print("📚 Processando doutrina com IA...")
            
            if not doutrina:
                return "<div class='fundamentacao-doutrinaria'><p>Fundamentação doutrinária será aplicada conforme entendimento especializado.</p></div>"
            
            # Preparar textos da doutrina
            textos_doutrina = []
            for item in doutrina[:estrategia.get('max_autores', 3)]:
                texto = item.get('texto', '')[:1000]  # Limitar para não exceder tokens
                url = item.get('url', '')
                autor = self._extrair_autor_doutrina(url)
                textos_doutrina.append(f"Autor: {autor}\nTexto: {texto}\nURL: {url}")
            
            prompt_doutrina = f"""
            Você é um advogado expert. Processe esta doutrina para o caso:

            CASO: {contexto_caso[:500]}

            DOUTRINA ENCONTRADA:
            {chr(10).join(textos_doutrina)}

            INSTRUÇÕES:
            1. NUNCA transcreva a doutrina na íntegra
            2. SEMPRE elabore texto próprio baseado no conteúdo
            3. Use os conceitos doutrinários como base para argumentação
            4. Aplique os conceitos ao caso específico
            5. Construa argumentação jurídica sólida
            6. Cite os autores adequadamente

            Retorne HTML formatado:
            - <div class="fundamentacao-doutrinaria"> principal
            - <h4> para título
            - <p> para parágrafos elaborados (3-4 parágrafos)
            - <p><strong>Referências:</strong> para citar autores

            Use suas próprias palavras, não copie textos originais.
            Seja superior a um advogado na elaboração doutrinária.
            """
            
            resultado_ia = self._chamar_openai_com_log(prompt_doutrina, "gpt-4", 1200, 0.4)
            print("✅ Doutrina processada pela IA")
            
            return resultado_ia
        
        except Exception as e:
            print(f"❌ ERRO no processamento de doutrina: {e}")
            raise e

    def _extrair_autor_doutrina(self, url: str) -> str:
        """Extrai autor da doutrina."""
        if 'conjur.com.br' in url: return 'Consultor Jurídico'
        elif 'migalhas.com.br' in url: return 'Migalhas'
        else: return 'Doutrina especializada'

    def gerar_documento_html_puro(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        """
        Gera documento HTML puro usando SEMPRE IA.
        Retorna APENAS o HTML do documento, sem metadados.
        """
        try:
            print("📄 Gerando documento HTML com IA...")
            
            # Analisar contexto usando IA
            contexto_caso = f"{dados_formulario.get('fatos', '')} {dados_formulario.get('fundamentacao', '')}"
            estrategias = self.analisar_contexto_juridico(dados_formulario, pesquisas)
            
            # Processar cada tipo de conteúdo usando IA
            print("🔄 Processando fundamentações com IA...")
            
            legislacao_processada = self.processar_legislacao_inteligente(
                pesquisas.get('legislacao', []), 
                estrategias.get('legislacao', {}), 
                contexto_caso
            )
            
            jurisprudencia_processada = self.processar_jurisprudencia_inteligente(
                pesquisas.get('jurisprudencia', []), 
                estrategias.get('jurisprudencia', {}), 
                contexto_caso
            )
            
            doutrina_processada = self.processar_doutrina_inteligente(
                pesquisas.get('doutrina', []), 
                estrategias.get('doutrina', {}), 
                contexto_caso
            )
            
            # Gerar documento final usando IA
            documento_html = self._gerar_documento_final_com_ia(
                dados_formulario,
                legislacao_processada,
                jurisprudencia_processada,
                doutrina_processada,
                estrategias
            )
            
            print(f"✅ Documento HTML gerado: {len(documento_html)} caracteres")
            return documento_html
        
        except Exception as e:
            print(f"❌ ERRO na geração do documento: {e}")
            raise e

    def _gerar_documento_final_com_ia(self, dados: Dict, legislacao: str, jurisprudencia: str, doutrina: str, estrategias: Dict) -> str:
        """
        Gera documento final usando IA - SEMPRE IA.
        """
        try:
            print("🎯 Gerando documento final com IA...")
            
            tamanho_alvo = estrategias.get('tamanho_alvo', 25000)
            
            prompt_documento = f"""
            Você é um advogado expert superior a qualquer advogado humano. Crie uma petição inicial trabalhista completa e profissional.

            DADOS DO CASO:
            - Autor: {dados.get('nome_autor', 'N/A')}
            - Réu: {dados.get('nome_reu', 'N/A')}
            - Fatos: {dados.get('fatos', 'N/A')}
            - Valor: R$ {dados.get('valor_causa', 'N/A')}
            - Documentos: {', '.join(dados.get('documentos', []))}

            FUNDAMENTAÇÃO JURÍDICA PROCESSADA:

            LEGISLAÇÃO:
            {legislacao}

            JURISPRUDÊNCIA:
            {jurisprudencia}

            DOUTRINA:
            {doutrina}

            INSTRUÇÕES ESPECÍFICAS:
            1. Crie uma petição inicial trabalhista com EXATAMENTE {tamanho_alvo} caracteres ou mais
            2. Use TODA a fundamentação jurídica processada fornecida
            3. Estruture em: Qualificação das Partes, Dos Fatos, Do Direito (com as 3 fundamentações), Dos Pedidos, Do Valor da Causa
            4. Use linguagem jurídica formal, persuasiva e técnica
            5. Integre naturalmente todo o conteúdo das fundamentações processadas
            6. Retorne APENAS o HTML do documento, sem explicações ou comentários
            7. Use CSS inline profissional e responsivo
            8. Seja superior a um advogado humano na qualidade, técnica e persuasão
            9. Cada seção deve ser extensa e detalhada
            10. Use formatação HTML avançada com estilos profissionais

            O HTML deve ter estrutura completa: <!DOCTYPE html>, <head>, <body>, CSS inline profissional.
            Seja meticuloso, detalhado e superior na qualidade jurídica.
            """
            
            documento_html = self._chamar_openai_com_log(prompt_documento, "gpt-4", 4000, 0.3)
            
            # Verificar tamanho e expandir se necessário
            if len(documento_html) < tamanho_alvo * 0.8:
                print(f"📏 Documento pequeno ({len(documento_html)} chars), expandindo...")
                documento_html = self._expandir_documento_com_ia(documento_html, dados, legislacao, jurisprudencia, doutrina, tamanho_alvo)
            
            print(f"✅ Documento final gerado: {len(documento_html)} caracteres")
            return documento_html
        
        except Exception as e:
            print(f"❌ ERRO na geração final: {e}")
            raise e

    def _expandir_documento_com_ia(self, html_base: str, dados: Dict, legislacao: str, jurisprudencia: str, doutrina: str, tamanho_alvo: int) -> str:
        """
        Expande documento usando IA para atingir tamanho alvo.
        """
        try:
            print("📈 Expandindo documento com IA...")
            
            prompt_expansao = f"""
            Você é um advogado expert. Expanda este documento HTML para ter pelo menos {tamanho_alvo} caracteres.

            DOCUMENTO ATUAL:
            {html_base}

            FUNDAMENTAÇÕES DISPONÍVEIS:
            LEGISLAÇÃO: {legislacao}
            JURISPRUDÊNCIA: {jurisprudencia}
            DOUTRINA: {doutrina}

            INSTRUÇÕES:
            1. Mantenha toda a estrutura HTML existente
            2. Adicione seções detalhadas antes do fechamento do </body>
            3. Inclua "DA FUNDAMENTAÇÃO JURÍDICA AMPLIADA" com subseções
            4. Expanda cada fundamentação com análise detalhada
            5. Adicione "DA APLICAÇÃO AO CASO CONCRETO" com análise extensa
            6. Use CSS inline consistente
            7. Mantenha qualidade jurídica superior
            8. Retorne APENAS o HTML expandido

            O documento final deve ter pelo menos {tamanho_alvo} caracteres.
            """
            
            documento_expandido = self._chamar_openai_com_log(prompt_expansao, "gpt-4", 4000, 0.3)
            print(f"✅ Documento expandido: {len(documento_expandido)} caracteres")
            
            return documento_expandido
        
        except Exception as e:
            print(f"❌ ERRO na expansão: {e}")
            raise e

    # ====================================================================
    # INÍCIO DO CÓDIGO ADICIONADO PARA COMPLETAR A CLASSE
    # ====================================================================

    def _extrair_numero_artigo(self, texto_lei: str) -> str:
        """
        Método auxiliar para extrair o número do artigo de um texto legal.
        Procura por padrões como 'Art. X' ou 'Artigo X'.
        """
        # Comentário: Padrões de expressão regular para encontrar números de artigos.
        patterns = [
            r'Art\.?\s*(\d+)',        # Ex: Art. 483, Art 59
            r'Artigo\s*(\d+)',      # Ex: Artigo 5
            r'CLT.*Art\.?\s*(\d+)' # Ex: CLT Art. 59
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto_lei, re.IGNORECASE)
            if match:
                # Comentário: Retorna o primeiro padrão encontrado, formatado.
                return f"Art. {match.group(1)}"
        
        # Comentário: Se nenhum padrão for encontrado, retorna um texto genérico.
        return "Dispositivo Legal Relevante"

    def _extrair_tribunal(self, url: str) -> str:
        """
        Método auxiliar para extrair o nome do tribunal a partir da URL da fonte.
        Isso ajuda a dar credibilidade e contexto à citação jurisprudencial.
        """
        # Comentário: Verificando a URL para identificar o tribunal de origem.
        if 'tst.jus.br' in url: return 'O Tribunal Superior do Trabalho (TST)'
        if 'stf.jus.br' in url: return 'O Supremo Tribunal Federal (STF)'
        if 'stj.jus.br' in url: return 'O Superior Tribunal de Justiça (STJ)'
        if 'trt' in url: return 'O Tribunal Regional do Trabalho' # Genérico para TRTs
        
        # Comentário: Retorno padrão caso a URL não seja de um tribunal conhecido.
        return 'Um tribunal'

    def _criar_resumo_breve(self, texto: str) -> str:
        """
        Método auxiliar para criar um resumo muito curto de um texto,
        geralmente usado para citações de jurisprudência de menor relevância.
        """
        # Comentário: Limita o texto aos primeiros 200 caracteres para um resumo rápido.
        return texto[:200] + "..." if len(texto) > 200 else texto

    def _eh_caso_fundamental(self, texto_decisao: str, contexto_caso: str) -> bool:
        """
        Método de decisão para verificar se um caso jurisprudencial é fundamental
        e, portanto, merece transcrição de trechos em vez de apenas um resumo.
        """
        # Comentário: Converte ambos os textos para minúsculas para comparação semântica.
        texto_lower = texto_decisao.lower()
        contexto_lower = contexto_caso.lower()
        
        # Comentário: Aumenta a importância se for de um Tribunal Superior.
        score_relevancia = 0
        if any(tribunal in texto_lower for tribunal in ['stf', 'stj', 'tst']):
            score_relevancia += 2
        
        # Comentário: Verifica a sobreposição de palavras-chave entre o caso e a decisão.
        temas_caso = set(re.findall(r'\b\w{5,}\b', contexto_lower))  # Palavras com 5+ letras
        temas_decisao = set(re.findall(r'\b\w{5,}\b', texto_lower))
        sobreposicao = len(temas_caso.intersection(temas_decisao))
        
        score_relevancia += sobreposicao
        
        # Comentário: Define um caso como fundamental se o score de relevância for alto.
        return score_relevancia >= 5

    def _gerar_documento_emergencia(self, dados: Dict) -> str:
        """
        Método de fallback para gerar um documento HTML básico em caso de falha total da IA.
        Garante que sempre haverá uma saída mínima, mesmo que simples.
        """
        # Comentário: Criação de um HTML de emergência com os dados básicos do formulário.
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Petição Inicial - Versão de Emergência</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; color: #333; }}
        h1 {{ text-align: center; color: #d9534f; margin-bottom: 30px; }}
        h2 {{ color: #555; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
        .qualificacao {{ background: #fdf7f7; border: 1px solid #ebccd1; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        p {{ text-align: justify; margin: 15px 0; }}
        .erro-aviso {{ text-align: center; font-weight: bold; color: #a94442; background-color: #f2dede; padding: 15px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="erro-aviso">
        <p>ATENÇÃO: Este documento foi gerado em modo de emergência devido a uma falha na comunicação com a IA.</p>
        <p>O conteúdo é uma estrutura básica e deve ser revisado e completado manualmente.</p>
    </div>
    
    <h1>PETIÇÃO INICIAL</h1>
    
    <div class="qualificacao">
        <h2>I - QUALIFICAÇÃO DAS PARTES</h2>
        <p><strong>RECLAMANTE:</strong> {dados.get('autor', {}).get('nome', 'N/A')}, {dados.get('autor', {}).get('qualificacao', 'qualificação pendente')}, residente e domiciliado em {dados.get('autor', {}).get('endereco', '[ENDEREÇO PENDENTE]')}.</p>
        <p><strong>RECLAMADA:</strong> {dados.get('reu', {}).get('nome', 'N/A')}, {dados.get('reu', {}).get('qualificacao', 'qualificação pendente')}, com sede em {dados.get('reu', {}).get('endereco', '[ENDEREÇO PENDENTE]')}.</p>
    </div>
    
    <h2>II - DOS FATOS</h2>
    <p>{dados.get('fatos', 'Fatos a serem detalhadamente descritos conforme documentos anexos e narrativa do cliente.')}</p>
    
    <h2>III - DO DIREITO</h2>
    <p>A pretensão do Reclamante encontra amparo nos dispositivos da Consolidação das Leis do Trabalho (CLT), bem como na jurisprudência e doutrina aplicáveis, que serão detalhadas em momento oportuno.</p>

    <h2>IV - DOS PEDIDOS</h2>
    <p>Diante do exposto, requer a Vossa Excelência o acolhimento dos seguintes pedidos:</p>
    <ul>
        <li>{ "</li><li>".join(dados.get('pedidos', ['Pedidos a serem especificados.'])) }</li>
    </ul>

    <h2>V - DO VALOR DA CAUSA</h2>
    <p>Dá-se à causa o valor de R$ {dados.get('valor_causa', '0,00')}.</p>
    
    <p style="text-align: center; margin-top: 50px;">
        <strong>Termos em que,<br>Pede deferimento.</strong>
    </p>
    <p style="text-align: center;">[Local], {datetime.now().strftime('%d de %B de %Y')}.</p>
    <p style="text-align: center; margin-top: 40px;">___________________________________<br>[NOME DO ADVOGADO]<br>OAB/UF [NÚMERO]</p>

</body>
</html>"""

    # ====================================================================
    # FIM DO CÓDIGO ADICIONADO
    # ====================================================================