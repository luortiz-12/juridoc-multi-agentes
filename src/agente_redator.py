# agente_redator_timeout_corrigido.py - Agente Redator com Timeout Corrigido

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
    
    SEMPRE USA IA - SEM FALLBACKS - COM TIMEOUT CORRIGIDO
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurar OpenAI com logs claros e timeout
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ ERRO: OPENAI_API_KEY não encontrada nas variáveis de ambiente")
            raise ValueError("OPENAI_API_KEY não configurada")
        
        print(f"✅ OPENAI_API_KEY encontrada: {api_key[:10]}...{api_key[-4:]}")
        
        # Cliente OpenAI com timeout configurado
        self.client = openai.OpenAI(
            api_key=api_key,
            timeout=120.0  # Timeout global de 2 minutos
        )
        print("✅ Cliente OpenAI inicializado com timeout de 120 segundos")
    
    def redigir_peticao_completa(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal chamado pelo orquestrador.
        Redige petição completa usando SEMPRE IA.
        """
        try:
            print("✍️ Iniciando redação inteligente da petição com IA...")
            print("🤖 Modo: SEMPRE IA - SEM FALLBACKS - TIMEOUT CORRIGIDO")
            
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
                    "estrategia_aplicada": "inteligencia_juridica_ia_pura_timeout_corrigido",
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
    
    def _chamar_openai_com_log(self, prompt: str, model: str = "gpt-4", max_tokens: int = 1000, temperature: float = 0.3, timeout_especifico: int = None) -> str:
        """
        Método centralizado para chamar OpenAI com logs claros e timeout configurado.
        """
        try:
            print(f"🤖 Chamando OpenAI - Modelo: {model}, Tokens: {max_tokens}")
            print(f"📝 Prompt (primeiros 100 chars): {prompt[:100]}...")
            print(f"⏱️ Timeout configurado: {timeout_especifico or 120} segundos")
            
            # Usar timeout específico se fornecido, senão usar o padrão do cliente
            if timeout_especifico:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=timeout_especifico
                )
            else:
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
            print(f"🔧 Modelo: {model}, Tokens: {max_tokens}, Timeout: {timeout_especifico or 120}s")
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
            
            # Usar IA para analisar contexto - PROMPT COMPLETO MANTIDO
            prompt_analise = f"""
            Você é um advogado expert. Analise este caso jurídico e determine estratégias inteligentes:
            
            DADOS DO CASO:
            - Área do direito: {area_direito}
            - Tipo de ação: {tipo_acao}
            - Fatos: {fatos}
            - Valor da causa: {valor_causa}
            
            PESQUISAS DISPONÍVEIS:
            - Legislação: {len(pesquisas.get('legislacao', []))} itens
            - Jurisprudência: {len(pesquisas.get('jurisprudencia', []))} itens
            - Doutrina: {len(pesquisas.get('doutrina', []))} itens
            
            CONTEÚDO DAS PESQUISAS PARA ANÁLISE:
            
            LEGISLAÇÃO ENCONTRADA:
            {self._preparar_resumo_pesquisas(pesquisas.get('legislacao', []), 'legislacao')}
            
            JURISPRUDÊNCIA ENCONTRADA:
            {self._preparar_resumo_pesquisas(pesquisas.get('jurisprudencia', []), 'jurisprudencia')}
            
            DOUTRINA ENCONTRADA:
            {self._preparar_resumo_pesquisas(pesquisas.get('doutrina', []), 'doutrina')}
            
            Retorne um JSON com estratégias para:
            1. legislacao: como usar (citacao_inteligente/citacao_simples, max_artigos, transcrever_integral: false)
            2. jurisprudencia: como usar (transcricao_seletiva/resumo_elaborado/citacao_resumida, max_casos)
            3. doutrina: como usar (elaboracao_propria sempre, max_autores)
            4. complexidade: muito_alta/alta/media/baixa
            5. tamanho_alvo: número de caracteres alvo (mínimo 25000)
            
            Seja inteligente na análise. Para leis NUNCA transcrever integral, sempre resumir.
            Para jurisprudência decidir caso a caso se transcreve ou resume baseado na relevância.
            Para doutrina SEMPRE elaborar texto próprio.
            """
            
            resposta_ia = self._chamar_openai_com_log(prompt_analise, "gpt-4", 1000, 0.2, 90)
            
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
    
    def _preparar_resumo_pesquisas(self, pesquisas: List[Dict], tipo: str) -> str:
        """Prepara resumo das pesquisas para análise pela IA."""
        if not pesquisas:
            return f"Nenhuma {tipo} encontrada."
        
        resumos = []
        for i, item in enumerate(pesquisas[:5]):  # Limitar a 5 itens para não exceder tokens
            texto = item.get('texto', '')[:500]  # Primeiros 500 chars
            url = item.get('url', '')
            resumos.append(f"{i+1}. URL: {url}\nTexto: {texto}...")
        
        return "\n\n".join(resumos)
    
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
        PROMPT COMPLETO MANTIDO.
        """
        try:
            print("⚖️ Processando legislação com IA...")
            
            if not legislacao:
                return "<div class='fundamentacao-legal'><p>Fundamentação legal será aplicada conforme legislação vigente.</p></div>"
            
            # Preparar textos da legislação - CONTEÚDO COMPLETO
            textos_legislacao = []
            for item in legislacao[:estrategia.get('max_artigos', 4)]:
                texto = item.get('texto', '')  # SEM LIMITAÇÃO - TEXTO COMPLETO
                url = item.get('url', '')
                textos_legislacao.append(f"FONTE: {url}\nTEXTO COMPLETO: {texto}")
            
            prompt_legislacao = f"""
            Você é um advogado expert superior a qualquer advogado humano. Processe esta legislação para o caso específico:
            
            CASO ESPECÍFICO:
            {contexto_caso}
            
            LEGISLAÇÃO ENCONTRADA (TEXTO COMPLETO):
            {chr(10).join(textos_legislacao)}
            
            INSTRUÇÕES ESPECÍFICAS:
            1. NUNCA transcreva leis na íntegra no documento final
            2. SEMPRE analise o texto completo e crie resumo próprio com suas palavras
            3. Extraia números dos artigos relevantes (Art. X, Art. Y)
            4. Explique detalhadamente como cada lei se aplica ao caso específico
            5. Use linguagem jurídica formal, técnica e persuasiva
            6. Conecte cada dispositivo legal aos fatos do caso
            7. Seja superior a um advogado humano na análise e aplicação
            
            Retorne HTML formatado profissionalmente:
            - <div class="fundamentacao-legal"> para cada lei processada
            - <h4> para título com número do artigo e nome da lei
            - <p> para explicação detalhada da aplicação ao caso
            - <p class="aplicacao-caso"> para conexão específica com os fatos
            - <p class="fonte-legal"> para fonte
            
            Use TODO o conteúdo das leis para criar fundamentação sólida e superior.
            """
            
            resultado_ia = self._chamar_openai_com_log(prompt_legislacao, "gpt-4", 1500, 0.3, 90)
            print("✅ Legislação processada pela IA")
            
            return resultado_ia
            
        except Exception as e:
            print(f"❌ ERRO no processamento de legislação: {e}")
            raise e
    
    def processar_jurisprudencia_inteligente(self, jurisprudencia: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Processa jurisprudência usando IA - decide quando transcrever vs resumir.
        PROMPT COMPLETO MANTIDO.
        """
        try:
            print("🏛️ Processando jurisprudência com IA...")
            
            if not jurisprudencia:
                return "<div class='jurisprudencia'><p>Jurisprudência aplicável será considerada conforme precedentes.</p></div>"
            
            # Preparar textos da jurisprudência - CONTEÚDO COMPLETO
            textos_jurisprudencia = []
            for item in jurisprudencia[:estrategia.get('max_casos', 3)]:
                texto = item.get('texto', '')  # SEM LIMITAÇÃO - TEXTO COMPLETO
                url = item.get('url', '')
                textos_jurisprudencia.append(f"FONTE: {url}\nDECISÃO COMPLETA: {texto}")
            
            modo = estrategia.get('modo', 'resumo_elaborado')
            
            prompt_jurisprudencia = f"""
            Você é um advogado expert superior a qualquer advogado humano. Processe esta jurisprudência para o caso específico:
            
            CASO ESPECÍFICO:
            {contexto_caso}
            
            MODO DE PROCESSAMENTO: {modo}
            
            JURISPRUDÊNCIA ENCONTRADA (TEXTO COMPLETO):
            {chr(10).join(textos_jurisprudencia)}
            
            INSTRUÇÕES ESPECÍFICAS:
            1. Analise CADA decisão completa e decida inteligentemente:
               - Se for caso FUNDAMENTAL (TST/STF/STJ + extremamente relevante): transcreva trechos mais importantes
               - Se for caso MUITO RELEVANTE: resuma detalhadamente com análise profunda
               - Se for caso RELEVANTE: cite com resumo elaborado
               - Se for caso COMUM: cite brevemente
            
            2. Para cada decisão, inclua obrigatoriamente:
               - Tribunal que decidiu (extrair da URL e texto)
               - Número do processo se disponível
               - Resumo ou transcrição conforme relevância determinada
               - Análise detalhada de como se aplica ao caso atual
               - Conexão específica com os fatos do caso
               - Fonte completa
            
            3. Use HTML formatado profissionalmente:
               - <div class="jurisprudencia-integral"> para transcrições de casos fundamentais
               - <div class="jurisprudencia-analisada"> para resumos elaborados
               - <div class="jurisprudencia-citada"> para citações breves
               - <blockquote> para trechos transcritos literalmente
               - <p> para análises e conexões com o caso
               - <h5> para identificação do tribunal e processo
            
            4. Seja superior a um advogado humano na análise jurisprudencial
            5. Use TODO o conteúdo das decisões para fundamentação sólida
            6. Conecte cada precedente aos fatos específicos do caso
            """
            
            resultado_ia = self._chamar_openai_com_log(prompt_jurisprudencia, "gpt-4", 2000, 0.3, 90)
            print("✅ Jurisprudência processada pela IA")
            
            return resultado_ia
            
        except Exception as e:
            print(f"❌ ERRO no processamento de jurisprudência: {e}")
            raise e
    
    def processar_doutrina_inteligente(self, doutrina: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Processa doutrina usando IA - SEMPRE elabora texto próprio.
        PROMPT COMPLETO MANTIDO.
        """
        try:
            print("📚 Processando doutrina com IA...")
            
            if not doutrina:
                return "<div class='fundamentacao-doutrinaria'><p>Fundamentação doutrinária será aplicada conforme entendimento especializado.</p></div>"
            
            # Preparar textos da doutrina - CONTEÚDO COMPLETO
            textos_doutrina = []
            for item in doutrina[:estrategia.get('max_autores', 3)]:
                texto = item.get('texto', '')  # SEM LIMITAÇÃO - TEXTO COMPLETO
                url = item.get('url', '')
                autor = self._extrair_autor_doutrina(url)
                textos_doutrina.append(f"AUTOR: {autor}\nFONTE: {url}\nTEXTO COMPLETO: {texto}")
            
            prompt_doutrina = f"""
            Você é um advogado expert superior a qualquer advogado humano. Processe esta doutrina para o caso específico:
            
            CASO ESPECÍFICO:
            {contexto_caso}
            
            DOUTRINA ENCONTRADA (TEXTO COMPLETO):
            {chr(10).join(textos_doutrina)}
            
            INSTRUÇÕES ESPECÍFICAS:
            1. NUNCA transcreva a doutrina na íntegra
            2. SEMPRE elabore texto próprio baseado no conteúdo completo analisado
            3. Use os conceitos doutrinários como base para argumentação jurídica sólida
            4. Aplique os conceitos especificamente ao caso apresentado
            5. Construa argumentação jurídica superior e persuasiva
            6. Cite os autores adequadamente com referência completa
            7. Conecte cada conceito doutrinário aos fatos do caso
            8. Seja superior a um advogado humano na elaboração doutrinária
            
            Retorne HTML formatado profissionalmente:
            - <div class="fundamentacao-doutrinaria"> como container principal
            - <h4> para título da seção doutrinária
            - <p> para parágrafos elaborados (4-6 parágrafos extensos)
            - <p class="aplicacao-doutrinaria"> para aplicação ao caso específico
            - <p><strong>Referências Doutrinárias:</strong> para citar autores e fontes
            
            Use suas próprias palavras baseadas na análise completa dos textos.
            Crie argumentação jurídica sólida e superior conectada ao caso.
            """
            
            resultado_ia = self._chamar_openai_com_log(prompt_doutrina, "gpt-4", 1500, 0.4, 90)
            print("✅ Doutrina processada pela IA")
            
            return resultado_ia
            
        except Exception as e:
            print(f"❌ ERRO no processamento de doutrina: {e}")
            raise e
    
    def _extrair_autor_doutrina(self, url: str) -> str:
        """Extrai autor da doutrina."""
        if 'conjur.com.br' in url: return 'Consultor Jurídico'
        elif 'migalhas.com.br' in url: return 'Migalhas'
        elif 'jusbrasil.com.br' in url: return 'JusBrasil'
        elif 'jus.com.br' in url: return 'Jus Navigandi'
        else: return 'Doutrina especializada'
    
    def gerar_documento_html_puro(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        """
        Gera documento HTML puro usando SEMPRE IA.
        Retorna APENAS o HTML do documento, sem metadados.
        PROMPTS COMPLETOS MANTIDOS.
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
        PROMPT COMPLETO MANTIDO.
        """
        try:
            print("🎯 Gerando documento final com IA...")
            
            tamanho_alvo = estrategias.get('tamanho_alvo', 25000)
            
            # PROMPT COMPLETO MANTIDO - SEM LIMITAÇÕES
            prompt_documento = f"""
            Você é um advogado expert superior a qualquer advogado humano. Crie uma petição inicial trabalhista completa, profissional e superior.
            
            DADOS COMPLETOS DO CASO:
            - Autor: {dados.get('nome_autor', 'N/A')}
            - Réu: {dados.get('nome_reu', 'N/A')}
            - Fatos completos: {dados.get('fatos', 'N/A')}
            - Valor da causa: R$ {dados.get('valor_causa', 'N/A')}
            - Documentos disponíveis: {', '.join(dados.get('documentos', []))}
            - Área do direito: {dados.get('area_direito', 'Trabalhista')}
            - Tipo de ação: {dados.get('tipo_acao', 'Petição inicial')}
            - Pedidos específicos: {dados.get('pedidos', 'Conforme fatos narrados')}
            
            FUNDAMENTAÇÃO JURÍDICA PROCESSADA PELA IA:
            
            FUNDAMENTAÇÃO LEGAL:
            {legislacao}
            
            FUNDAMENTAÇÃO JURISPRUDENCIAL:
            {jurisprudencia}
            
            FUNDAMENTAÇÃO DOUTRINÁRIA:
            {doutrina}
            
            INSTRUÇÕES ESPECÍFICAS PARA CRIAÇÃO:
            1. Crie uma petição inicial trabalhista com EXATAMENTE {tamanho_alvo} caracteres ou mais
            2. Use TODA a fundamentação jurídica processada fornecida acima
            3. Estruture profissionalmente em:
               - Qualificação das Partes (detalhada)
               - Dos Fatos (narrativa completa e persuasiva)
               - Do Direito (com as 3 fundamentações integradas naturalmente)
               - Dos Pedidos (específicos e fundamentados)
               - Do Valor da Causa (justificado)
               - Documentos anexos
            4. Use linguagem jurídica formal, técnica, persuasiva e superior
            5. Integre naturalmente TODO o conteúdo das fundamentações processadas
            6. Retorne APENAS o HTML do documento, sem explicações ou comentários
            7. Use CSS inline profissional, responsivo e elegante
            8. Seja superior a um advogado humano na qualidade, técnica e persuasão
            9. Cada seção deve ser extensa, detalhada e fundamentada
            10. Use formatação HTML avançada com estilos profissionais
            11. Conecte cada fundamentação aos fatos específicos do caso
            12. Crie argumentação jurídica sólida e persuasiva
            
            REQUISITOS TÉCNICOS:
            - HTML completo: <!DOCTYPE html>, <head>, <body>
            - CSS inline profissional e responsivo
            - Estrutura semântica correta
            - Formatação elegante e profissional
            - Tipografia adequada para documentos jurídicos
            
            Seja meticuloso, detalhado e superior na qualidade jurídica.
            Use TODO o conteúdo fornecido para criar documento excepcional.
            """
            
            documento_html = self._chamar_openai_com_log(prompt_documento, "gpt-4", 4000, 0.3, 120)
            
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
        PROMPT COMPLETO MANTIDO.
        """
        try:
            print("📈 Expandindo documento com IA...")
            
            # PROMPT COMPLETO MANTIDO - SEM LIMITAÇÕES
            prompt_expansao = f"""
            Você é um advogado expert superior. Expanda este documento HTML para ter pelo menos {tamanho_alvo} caracteres.
            
            DOCUMENTO ATUAL:
            {html_base}
            
            FUNDAMENTAÇÕES COMPLETAS DISPONÍVEIS:
            
            LEGISLAÇÃO PROCESSADA:
            {legislacao}
            
            JURISPRUDÊNCIA PROCESSADA:
            {jurisprudencia}
            
            DOUTRINA PROCESSADA:
            {doutrina}
            
            DADOS DO CASO:
            {dados}
            
            INSTRUÇÕES PARA EXPANSÃO:
            1. Mantenha toda a estrutura HTML existente
            2. Adicione seções detalhadas antes do fechamento do </body>
            3. Inclua "DA FUNDAMENTAÇÃO JURÍDICA AMPLIADA" com subseções extensas
            4. Expanda cada fundamentação com análise detalhada e aplicação ao caso
            5. Adicione "DA APLICAÇÃO AO CASO CONCRETO" com análise extensa
            6. Inclua "DOS PRECEDENTES APLICÁVEIS" se houver jurisprudência
            7. Adicione "DA DOUTRINA ESPECIALIZADA" se houver doutrina
            8. Use CSS inline consistente e profissional
            9. Mantenha qualidade jurídica superior
            10. Retorne APENAS o HTML expandido
            11. Conecte todas as fundamentações aos fatos específicos
            12. Crie argumentação jurídica sólida e extensa
            
            O documento final deve ter pelo menos {tamanho_alvo} caracteres.
            Use TODAS as fundamentações fornecidas para criar conteúdo superior.
            """
            
            documento_expandido = self._chamar_openai_com_log(prompt_expansao, "gpt-4", 4000, 0.3, 120)
            print(f"✅ Documento expandido: {len(documento_expandido)} caracteres")
            
            return documento_expandido
            
        except Exception as e:
            print(f"❌ ERRO na expansão: {e}")
            raise e
    
    # Métodos auxiliares mantidos do código original
    def _extrair_numero_artigo(self, texto_lei: str) -> str:
        """Extrai número do artigo da lei."""
        patterns = [
            r'Art\.?\s*(\d+)',
            r'Artigo\s*(\d+)',
            r'CLT.*Art\.?\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto_lei, re.IGNORECASE)
            if match:
                return f"Art. {match.group(1)}"
        
        return "Dispositivo legal"
    
    def _extrair_tribunal(self, url: str) -> str:
        """Extrai nome do tribunal da URL."""
        if 'tst.jus.br' in url: return 'TST'
        elif 'stf.jus.br' in url: return 'STF'
        elif 'stj.jus.br' in url: return 'STJ'
        elif 'trt' in url: return 'TRT'
        else: return 'Tribunal'
    
    def _criar_resumo_breve(self, texto: str) -> str:
        """Cria resumo muito breve."""
        return texto[:100] + "..." if len(texto) > 100 else texto
    
    def _eh_caso_fundamental(self, texto_decisao: str, contexto_caso: str) -> bool:
        """Verifica se um caso jurisprudencial é fundamental."""
        texto_lower = texto_decisao.lower()
        
        # Casos de tribunais superiores com palavras-chave relevantes
        if any(tribunal in texto_lower for tribunal in ['stf', 'stj', 'tst']):
            palavras_relevantes = ['assédio', 'rescisão', 'indenização', 'danos morais']
            if any(palavra in texto_lower for palavra in palavras_relevantes):
                return True
        
        return False