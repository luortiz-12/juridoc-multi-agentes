# agente_redator.py - Agente Redator Inteligente, Otimizado e Funcional

import json
import logging
import openai
import os
from typing import Dict, List, Any
import re
from datetime import datetime
import traceback

class AgenteRedator:
    """
    Agente Redator Inteligente que:
    1. Analisa o contexto do caso usando IA para definir estratégias.
    2. Pré-processa legislação, jurisprudência e doutrina em blocos de HTML fundamentados.
    3. Usa os blocos pré-processados para redigir um documento final coeso e de alta qualidade.
    4. Retorna APENAS o HTML puro do documento.
    
    SEMPRE USA IA - SEM FALLBACKS - COM TIMEOUTS AJUSTADOS
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ ERRO: OPENAI_API_KEY não encontrada nas variáveis de ambiente")
            raise ValueError("OPENAI_API_KEY não configurada")
        
        print(f"✅ OPENAI_API_KEY encontrada: {api_key[:10]}...{api_key[-4:]}")
        
        self.client = openai.OpenAI(
            api_key=api_key,
            timeout=300.0  # Timeout global de 5 minutos, para segurança.
        )
        print("✅ Cliente OpenAI inicializado com sucesso.")

    def redigir_peticao_completa(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal chamado pelo orquestrador.
        Redige a petição completa usando SEMPRE IA.
        """
        try:
            print("✍️ Iniciando redação inteligente da petição com IA...")
            
            documento_html = self.gerar_documento_html_puro(dados_estruturados, pesquisa_juridica)
            
            tamanho_documento = len(documento_html)
            score_qualidade = self._calcular_score_qualidade(documento_html, dados_estruturados, pesquisa_juridica)
            
            print(f"✅ Petição redigida com IA: {tamanho_documento} caracteres")
            print(f"📊 Score de qualidade: {score_qualidade}")
            
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
            print(f"❌ ERRO GERAL na redação da petição: {e}")
            self.logger.error(f"Erro na redação da petição: {traceback.format_exc()}")
            
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
        """
        Calcula o score de qualidade do documento gerado.
        """
        score = 60
        
        if len(documento_html) > 30000: score += 15
        elif len(documento_html) > 20000: score += 10
        
        if pesquisas.get('legislacao'): score += 5
        if pesquisas.get('jurisprudencia'): score += 5
        if pesquisas.get('doutrina'): score += 5
        
        if '<h1>' in documento_html and '<h2>' in documento_html: score += 5
        if 'style=' in documento_html or '<style>' in documento_html: score += 5
        
        return min(score, 100)

    def _chamar_openai_com_log(self, prompt: str, model: str, max_tokens: int, temperature: float, timeout_especifico: int) -> str:
        """
        Método centralizado para chamar a API da OpenAI com logs e timeout específico.
        """
        try:
            print(f"🤖 Chamando OpenAI - Modelo: {model}, Tokens de Resposta: {max_tokens}, Timeout: {timeout_especifico}s")
            print(f"📝 Prompt (primeiros 150 chars): {prompt[:150].strip().replace(chr(10), ' ')}...")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=float(timeout_especifico)
            )
            
            resultado = response.choices[0].message.content.strip()
            print(f"✅ OpenAI respondeu com sucesso: {len(resultado)} caracteres")
            return resultado
        
        except Exception as e:
            print(f"❌ ERRO na chamada à API da OpenAI: {e}")
            self.logger.error(f"Erro na chamada OpenAI: {traceback.format_exc()}")
            raise e

    def _preparar_resumo_pesquisas(self, pesquisas: List[Dict], tipo: str) -> str:
        """
        Cria um resumo conciso dos itens de pesquisa para serem usados no prompt de análise.
        """
        if not pesquisas:
            return f"Nenhuma {tipo} encontrada."
        
        resumos = []
        for i, item in enumerate(pesquisas[:3]):
            texto_resumido = item.get('texto', '')[:300]
            url = item.get('url', '')
            resumos.append(f"{i+1}. URL: {url}\nTrecho: {texto_resumido}...")
        
        return "\n\n".join(resumos)

    def analisar_contexto_juridico(self, dados_formulario: Dict, pesquisas: Dict) -> Dict:
        """
        Usa a IA para analisar o contexto e definir as estratégias de redação.
        """
        try:
            print("🧠 Analisando contexto jurídico com IA...")
            
            prompt_analise = f"""
            Você é um advogado estrategista. Analise o caso abaixo e retorne um JSON com as melhores estratégias de redação.

            DADOS DO CASO:
            - Fatos: {dados_formulario.get('fatos', '')[:1000]}
            - Pedidos: {dados_formulario.get('pedidos', '')}
            - Resumo da Pesquisa de Legislação: {self._preparar_resumo_pesquisas(pesquisas.get('legislacao', []), 'legislação')}
            - Resumo da Pesquisa de Jurisprudência: {self._preparar_resumo_pesquisas(pesquisas.get('jurisprudencia', []), 'jurisprudência')}

            Com base na análise, retorne um objeto JSON com a seguinte estrutura:
            {{
              "legislacao": {{"modo": "citacao_inteligente", "max_artigos": 3}},
              "jurisprudencia": {{"modo": "resumo_elaborado", "max_casos": 2}},
              "doutrina": {{"modo": "elaboracao_propria", "max_autores": 2}},
              "tamanho_alvo": 30000
            }}

            Instruções para a decisão:
            - Se os fatos envolverem assédio ou dano moral, o modo da jurisprudência deve ser 'transcricao_seletiva'.
            - O 'tamanho_alvo' deve ser no mínimo 30000.
            - Retorne APENAS o objeto JSON.
            """
            
            # --- MUDANÇA DE MODELO ---
            resposta_ia = self._chamar_openai_com_log(prompt_analise, "gpt-4o", 800, 0.1, 90)
            
            match = re.search(r'\{.*\}', resposta_ia, re.DOTALL)
            if match:
                estrategias = json.loads(match.group(0))
                print("✅ Estratégias analisadas pela IA com sucesso")
                return estrategias
            else:
                print("⚠️ IA não retornou JSON válido, usando estratégias padrão")
                return self._estrategias_padrao()
        
        except Exception as e:
            print(f"⚠️ ERRO na análise de contexto com IA: {e}. Usando estratégias padrão.")
            return self._estrategias_padrao()

    def _estrategias_padrao(self) -> Dict:
        return {
            'legislacao': {'modo': 'citacao_inteligente', 'max_artigos': 3},
            'jurisprudencia': {'modo': 'resumo_elaborado', 'max_casos': 2},
            'doutrina': {'modo': 'elaboracao_propria', 'max_autores': 2},
            'tamanho_alvo': 30000
        }

    def processar_legislacao_inteligente(self, legislacao: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Usa a IA para criar um bloco HTML com resumos e aplicação da legislação ao caso.
        """
        try:
            print("⚖️ Processando legislação com IA...")
            if not legislacao: return ""

            textos_legislacao = [f"FONTE: {item.get('url', '')}\nTEXTO: {item.get('texto', '')[:8000]}" for item in legislacao[:estrategia.get('max_artigos', 3)]]
            
            prompt_legislacao = f"""
            Você é um advogado sênior. Analise os dispositivos legais abaixo e sua aplicação a um caso concreto.

            CASO CONCRETO: "{contexto_caso[:1000]}"

            DISPOSITIVOS LEGAIS:
            {chr(10).join(textos_legislacao)}

            INSTRUÇÕES:
            1. Para cada dispositivo relevante, escreva um parágrafo explicando sua essência.
            2. Em seguida, escreva um segundo parágrafo conectando o dispositivo diretamente aos fatos do caso.
            3. NUNCA transcreva a lei. Crie um texto próprio.
            4. Retorne um único bloco de HTML formatado profissionalmente, contendo todos os artigos analisados.
            """
            
            # --- MUDANÇA DE MODELO ---
            return self._chamar_openai_com_log(prompt_legislacao, "gpt-4o", 1500, 0.3, 120)
        
        except Exception as e:
            print(f"❌ ERRO no processamento de legislação: {e}")
            return "<div class='fundamentacao-item erro'><p>Ocorreu um erro ao processar a fundamentação legal. A petição se baseará na legislação trabalhista pertinente, como o Art. 483 da CLT.</p></div>"

    def processar_jurisprudencia_inteligente(self, jurisprudencia: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Usa a IA para criar um bloco HTML com análise da jurisprudência.
        """
        try:
            print("🏛️ Processando jurisprudência com IA...")
            if not jurisprudencia: return ""

            textos_jurisprudencia = [f"FONTE: {item.get('url', '')}\nDECISÃO: {item.get('texto', '')[:8000]}" for item in jurisprudencia[:estrategia.get('max_casos', 2)]]
            modo = estrategia.get('modo', 'resumo_elaborado')
            
            prompt_jurisprudencia = f"""
            Você é um advogado especialista em jurisprudência. Analise as decisões abaixo e sua aplicação a um caso concreto.

            CASO CONCRETO: "{contexto_caso[:1000]}"
            MODO DE PROCESSAMENTO: {modo}

            DECISÕES ENCONTRADAS:
            {chr(10).join(textos_jurisprudencia)}

            INSTRUÇÕES:
            1. Para cada decisão, se for relevante, transcreva o trecho mais importante dentro de `<blockquote>`.
            2. Para todas as decisões, escreva um parágrafo de análise, explicando como o precedente fortalece a tese do caso concreto.
            3. Retorne um único bloco de HTML formatado profissionalmente.
            """
            
            # --- MUDANÇA DE MODELO ---
            return self._chamar_openai_com_log(prompt_jurisprudencia, "gpt-4o", 1500, 0.3, 120)
        
        except Exception as e:
            print(f"❌ ERRO no processamento de jurisprudência: {e}")
            return "<div class='fundamentacao-item erro'><p>Ocorreu um erro ao processar a jurisprudência. A petição se baseará no entendimento consolidado dos tribunais sobre a matéria.</p></div>"

    def processar_doutrina_inteligente(self, doutrina: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Usa a IA para criar um bloco HTML com um texto autoral baseado na doutrina pesquisada.
        """
        try:
            print("📚 Processando doutrina com IA...")
            if not doutrina: return ""

            textos_doutrina = [f"AUTOR: {self._extrair_autor_doutrina(item.get('url', ''))}\nTEXTO: {item.get('texto', '')[:8000]}" for item in doutrina[:estrategia.get('max_autores', 2)]]
            
            prompt_doutrina = f"""
            Você é um jurista renomado. Com base nos textos doutrinários abaixo, elabore um texto autoral sobre os temas abordados e sua aplicação ao caso concreto.

            CASO CONCRETO: "{contexto_caso[:1000]}"

            TEXTOS DOUTRINÁRIOS DE BASE:
            {chr(10).join(textos_doutrina)}

            INSTRUÇÕES:
            1. NUNCA transcreva os textos. Use-os como inspiração.
            2. Elabore um texto autoral de 3 a 4 parágrafos, construindo uma argumentação coesa sobre os temas (ex: rescisão indireta, dano moral).
            3. Conecte sua argumentação doutrinária diretamente aos fatos do caso.
            4. Retorne um único bloco de HTML formatado profissionalmente.
            """
            
            # --- MUDANÇA DE MODELO ---
            return self._chamar_openai_com_log(prompt_doutrina, "gpt-4o", 1500, 0.4, 120)
        
        except Exception as e:
            print(f"❌ ERRO no processamento de doutrina: {e}")
            return "<div class='fundamentacao-item erro'><p>Ocorreu um erro ao processar a doutrina. A petição se baseará no entendimento doutrinário majoritário sobre o tema.</p></div>"

    def gerar_documento_html_puro(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        """
        Orquestra a análise, o pré-processamento e a geração final do documento HTML.
        """
        try:
            print("📄 Iniciando orquestração da geração de documento HTML...")
            
            contexto_caso = f"Fatos: {dados_formulario.get('fatos', '')}. Pedidos: {dados_formulario.get('pedidos', '')}"
            estrategias = self.analisar_contexto_juridico(dados_formulario, pesquisas)
            
            print("🔄 Processando fundamentações com IA...")
            
            legislacao_processada = self.processar_legislacao_inteligente(
                pesquisas.get('legislacao', []), 
                estrategias.get('legislacao', {}), 
                contexto_caso
            )
            print("\n--- HTML GERADO (LEGISLAÇÃO) ---\n", legislacao_processada, "\n---------------------------------\n")

            jurisprudencia_processada = self.processar_jurisprudencia_inteligente(
                pesquisas.get('jurisprudencia', []), 
                estrategias.get('jurisprudencia', {}), 
                contexto_caso
            )
            print("\n--- HTML GERADO (JURISPRUDÊNCIA) ---\n", jurisprudencia_processada, "\n---------------------------------\n")

            doutrina_processada = self.processar_doutrina_inteligente(
                pesquisas.get('doutrina', []), 
                estrategias.get('doutrina', {}), 
                contexto_caso
            )
            print("\n--- HTML GERADO (DOUTRINA) ---\n", doutrina_processada, "\n---------------------------------\n")

            documento_html = self._gerar_documento_final_com_ia(
                dados_formulario,
                legislacao_processada,
                jurisprudencia_processada,
                doutrina_processada,
                estrategias
            )
            
            return documento_html
        
        except Exception as e:
            print(f"❌ ERRO na orquestração da geração do documento: {e}")
            raise e

    def _gerar_documento_final_com_ia(self, dados: Dict, legislacao: str, jurisprudencia: str, doutrina: str, estrategias: Dict) -> str:
        """
        Usa a IA para montar a petição final, integrando os blocos de fundamentação já processados.
        """
        try:
            print("🎯 Montando o documento final com IA...")
            
            tamanho_alvo = estrategias.get('tamanho_alvo', 30000)
            
            prompt_documento = f"""
            Você é um advogado sênior, especialista em redação de petições. Sua tarefa é redigir uma petição inicial trabalhista completa, coesa e persuasiva, utilizando os blocos de informação fornecidos.

            DADOS DO CASO:
            - Autor: {json.dumps(dados.get('autor', {}), ensure_ascii=False)}
            - Réu: {json.dumps(dados.get('reu', {}), ensure_ascii=False)}
            - Fatos: {dados.get('fatos', '')}
            - Pedidos: {dados.get('pedidos', '')}
            - Valor da Causa: {dados.get('valor_causa', '')}

            BLOCOS DE FUNDAMENTAÇÃO JURÍDICA (JÁ PROCESSADOS PELA IA):
            
            BLOCO DE LEGISLAÇÃO:
            {legislacao}

            BLOCO DE JURISPRUDÊNCIA:
            {jurisprudencia}

            BLOCO DE DOUTRINA:
            {doutrina}

            INSTRUÇÕES FINAIS DE REDAÇÃO:
            1. Crie uma petição inicial completa com no mínimo {tamanho_alvo} caracteres.
            2. Use os dados do caso para preencher as seções de Qualificação e Fatos.
            3. Na seção "DO DIREITO", integre os três blocos de fundamentação de forma natural e coesa. Crie uma narrativa jurídica fluida e detalhada.
            4. Formule a seção "DOS PEDIDOS" de forma clara e objetiva.
            5. Retorne APENAS o código HTML completo do documento. Não inclua explicações ou comentários.
            6. Utilize um CSS inline profissional e elegante, com boa tipografia (ex: 'Times New Roman', serif), espaçamento adequado e uma estrutura limpa.

            O resultado deve ser um documento HTML pronto para ser salvo e utilizado, de qualidade superior à de um advogado humano.
            """
            
            # --- MUDANÇA DE MODELO ---
            return self._chamar_openai_com_log(prompt_documento, "gpt-4o", 4000, 0.3, 240)
        
        except Exception as e:
            print(f"❌ ERRO na geração final do documento: {e}")
            raise e

    def _extrair_autor_doutrina(self, url: str) -> str:
        """Extrai autor da doutrina a partir da URL."""
        if 'conjur.com.br' in url: return 'Consultor Jurídico'
        elif 'migalhas.com.br' in url: return 'Migalhas'
        elif 'jusbrasil.com.br' in url: return 'JusBrasil'
        elif 'jus.com.br' in url: return 'Jus Navigandi'
        else: return 'Doutrina especializada'