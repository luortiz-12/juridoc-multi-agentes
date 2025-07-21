# agente_redator.py - Agente Redator Inteligente e Otimizado

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
    1. Analisa o conteúdo do formulário e das pesquisas usando IA.
    2. Pré-processa legislação, jurisprudência e doutrina em blocos de HTML fundamentados.
    3. Usa os blocos pré-processados para redigir um documento final coeso e de alta qualidade.
    4. Retorna APENAS o HTML puro do documento.
    5. É superior a um advogado na qualidade dos documentos.
    
    SEMPRE USA IA - SEM FALLBACKS - COM TIMEOUTS AJUSTADOS
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # --- COMENTÁRIO: Configuração do cliente OpenAI ---
        # Garante que a chave de API seja carregada e define um timeout global
        # como uma camada de segurança, embora cada chamada terá seu próprio timeout.
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
            
            # --- COMENTÁRIO: Execução do fluxo principal de redação ---
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
        for i, item in enumerate(pesquisas[:3]):  # Limita a 3 itens para o resumo
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
              "legislacao": {{"modo": "citacao_inteligente", "max_artigos": 3, "transcrever_integral": false}},
              "jurisprudencia": {{"modo": "resumo_elaborado", "max_casos": 2}},
              "doutrina": {{"modo": "elaboracao_propria", "max_autores": 2}},
              "complexidade": "media",
              "tamanho_alvo": 20000
            }}

            Instruções para a decisão:
            - Se os fatos envolverem assédio ou dano moral, a complexidade é 'alta'.
            - Se a jurisprudência do TST/STF for muito relevante, o modo deve ser 'transcricao_seletiva'.
            - O 'tamanho_alvo' deve ser no mínimo 20000. Se a complexidade for 'alta', aumente para 30000.
            - Retorne APENAS o objeto JSON.
            """
            
            resposta_ia = self._chamar_openai_com_log(prompt_analise, "gpt-4", 800, 0.1, 90)
            
            # Extrai o JSON da resposta da IA, mesmo que tenha texto adicional.
            match = re.search(r'\{.*\}', resposta_ia, re.DOTALL)
            if match:
                estrategias = json.loads(match.group(0))
                print("✅ Estratégias analisadas pela IA com sucesso")
                return estrategias
            else:
                print("⚠️ IA não retornou JSON válido, usando estratégias padrão")
                return self._estrategias_padrao()
        
        except Exception as e:
            print(f"❌ ERRO na análise de contexto com IA: {e}")
            raise e

    def processar_legislacao_inteligente(self, legislacao: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Usa a IA para criar um bloco HTML com resumos e aplicação da legislação ao caso.
        """
        try:
            print("⚖️ Processando legislação com IA...")
            if not legislacao: return ""

            textos_legislacao = [f"FONTE: {item.get('url', '')}\nTEXTO: {item.get('texto', '')[:4000]}" for item in legislacao[:estrategia.get('max_artigos', 3)]]
            
            prompt_legislacao = f"""
            Você é um advogado sênior. Analise os dispositivos legais abaixo e sua aplicação a um caso concreto.

            CASO CONCRETO: "{contexto_caso[:1000]}"

            DISPOSITIVOS LEGAIS:
            {chr(10).join(textos_legislacao)}

            INSTRUÇÕES:
            1. Para cada dispositivo, escreva um parágrafo explicando sua essência.
            2. Em seguida, escreva um segundo parágrafo conectando o dispositivo diretamente aos fatos do caso.
            3. NUNCA transcreva a lei. Crie um texto próprio.
            4. Retorne um único bloco de HTML formatado profissionalmente, contendo todos os artigos analisados.
            
            Exemplo de formato para UM artigo:
            <div class='fundamentacao-item'>
              <h4>Do Art. 483 da CLT – A Rescisão Indireta</h4>
              <p>O artigo 483 da Consolidação das Leis do Trabalho (CLT) estabelece as hipóteses em que o empregado pode considerar o contrato de trabalho rescindido por falta grave do empregador...</p>
              <p class='aplicacao-caso'>No presente caso, a conduta da Reclamada de não pagar as horas extras e de permitir um ambiente com assédio moral se enquadra diretamente na alínea 'd' do referido artigo...</p>
            </div>
            """
            
            return self._chamar_openai_com_log(prompt_legislacao, "gpt-4", 1500, 0.3, 120)
        
        except Exception as e:
            print(f"❌ ERRO no processamento de legislação: {e}")
            raise e

    def processar_jurisprudencia_inteligente(self, jurisprudencia: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Usa a IA para criar um bloco HTML com análise da jurisprudência, decidindo se resume ou transcreve trechos.
        """
        try:
            print("🏛️ Processando jurisprudência com IA...")
            if not jurisprudencia: return ""

            textos_jurisprudencia = [f"FONTE: {item.get('url', '')}\nDECISÃO: {item.get('texto', '')[:4000]}" for item in jurisprudencia[:estrategia.get('max_casos', 2)]]
            
            prompt_jurisprudencia = f"""
            Você é um advogado especialista em jurisprudência. Analise as decisões abaixo e sua aplicação a um caso concreto.

            CASO CONCRETO: "{contexto_caso[:1000]}"

            DECISÕES ENCONTRADAS:
            {chr(10).join(textos_jurisprudencia)}

            INSTRUÇÕES:
            1. Para cada decisão, identifique o tribunal e o ponto principal.
            2. Se a decisão for de um Tribunal Superior (TST, STF) e diretamente aplicável, transcreva o trecho mais relevante dentro de um `<blockquote>`.
            3. Para todas as decisões, escreva um parágrafo de análise, explicando como o precedente fortalece a tese do caso concreto.
            4. Retorne um único bloco de HTML formatado profissionalmente.

            Exemplo de formato:
            <div class='fundamentacao-item'>
              <h4>Entendimento do Tribunal Superior do Trabalho sobre Assédio Moral</h4>
              <p>O TST possui entendimento consolidado de que o assédio moral, caracterizado por condutas abusivas, gera o dever de indenizar...</p>
              <blockquote>"A prática de assédio moral pelo empregador gera direito à indenização por danos morais..."</blockquote>
              <p class='aplicacao-caso'>Tal precedente é diretamente aplicável ao caso, uma vez que a Reclamante foi submetida a cobranças vexatórias e humilhantes de forma contínua...</p>
            </div>
            """
            
            return self._chamar_openai_com_log(prompt_jurisprudencia, "gpt-4", 1500, 0.3, 120)
        
        except Exception as e:
            print(f"❌ ERRO no processamento de jurisprudência: {e}")
            raise e

    def processar_doutrina_inteligente(self, doutrina: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """
        Usa a IA para criar um bloco HTML com um texto autoral baseado na doutrina pesquisada.
        """
        try:
            print("📚 Processando doutrina com IA...")
            if not doutrina: return ""

            textos_doutrina = [f"AUTOR: {self._extrair_autor_doutrina(item.get('url', ''))}\nTEXTO: {item.get('texto', '')[:4000]}" for item in doutrina[:estrategia.get('max_autores', 2)]]
            
            prompt_doutrina = f"""
            Você é um jurista renomado. Com base nos textos doutrinários abaixo, elabore um texto autoral sobre os temas abordados e sua aplicação ao caso concreto.

            CASO CONCRETO: "{contexto_caso[:1000]}"

            TEXTOS DOUTRINÁRIOS DE BASE:
            {chr(10).join(textos_doutrina)}

            INSTRUÇÕES:
            1. NUNCA transcreva os textos. Use-os como inspiração e base conceitual.
            2. Elabore um texto autoral de 3 a 4 parágrafos, construindo uma argumentação coesa sobre os temas (ex: rescisão indireta, dano moral).
            3. Conecte sua argumentação doutrinária diretamente aos fatos do caso.
            4. Retorne um único bloco de HTML formatado profissionalmente.

            Exemplo de formato:
            <div class='fundamentacao-item'>
              <h4>Da Configuração do Assédio Moral e o Dever de Indenizar</h4>
              <p>A doutrina pátria é uníssona ao definir o assédio moral como a exposição prolongada e repetitiva do trabalhador a situações humilhantes e constrangedoras...</p>
              <p class='aplicacao-caso'>No caso da Reclamante, as cobranças vexatórias realizadas pelo Sr. Gerson, de forma pública e reiterada, configuram um exemplo clássico da conduta descrita pela doutrina, atentando contra sua dignidade e tornando o ambiente de trabalho insustentável...</p>
            </div>
            """
            
            return self._chamar_openai_com_log(prompt_doutrina, "gpt-4", 1500, 0.4, 120)
        
        except Exception as e:
            print(f"❌ ERRO no processamento de doutrina: {e}")
            raise e

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
            
            # --- COMENTÁRIO: Log de depuração para verificar a saída do processamento ---
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
            
            print(f"✅ Documento HTML final gerado: {len(documento_html)} caracteres")
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
            
            tamanho_alvo = estrategias.get('tamanho_alvo', 25000)
            
            prompt_documento = f"""
            Você é um advogado sênior, especialista em redação de petições. Sua tarefa é redigir uma petição inicial trabalhista completa, coesa e persuasiva, utilizando os blocos de informação fornecidos.

            DADOS DO CASO:
            - Autor: {json.dumps(dados.get('autor', {}), ensure_ascii=False)}
            - Réu: {json.dumps(dados.get('reu', {}), ensure_ascii=False)}
            - Fatos: {dados.get('fatos', '')}
            - Pedidos: {dados.get('pedidos', '')}
            - Valor da Causa: {dados.get('valor_causa', '')}

            BLOCOS DE FUNDAMENTAÇÃO JURÍDICA (JÁ PROCESSADOS):
            
            BLOCO DE LEGISLAÇÃO:
            {legislacao}

            BLOCO DE JURISPRUDÊNCIA:
            {jurisprudencia}

            BLOCO DE DOUTRINA:
            {doutrina}

            INSTRUÇÕES FINAIS DE REDAÇÃO:
            1. Crie uma petição inicial completa com no mínimo {tamanho_alvo} caracteres.
            2. Use os dados do caso para preencher as seções de Qualificação e Fatos.
            3. Na seção "DO DIREITO", integre os três blocos de fundamentação (Legislação, Jurisprudência, Doutrina) de forma natural e coesa. Não apenas copie e cole, mas crie uma narrativa jurídica fluida.
            4. Formule a seção "DOS PEDIDOS" de forma clara e objetiva, baseada nos pedidos fornecidos.
            5. Retorne APENAS o código HTML completo do documento. Não inclua explicações, comentários ou a palavra "HTML".
            6. Utilize um CSS inline profissional e elegante, com boa tipografia (ex: 'Times New Roman', serif), espaçamento adequado e uma estrutura limpa.

            O resultado deve ser um documento HTML pronto para ser salvo e utilizado, de qualidade superior à de um advogado humano.
            """
            
            return self._chamar_openai_com_log(prompt_documento, "gpt-4", 4000, 0.3, 240)
        
        except Exception as e:
            print(f"❌ ERRO na geração final do documento: {e}")
            raise e

    # --- COMENTÁRIO: Métodos auxiliares mantidos para extração de dados e fallback ---
    def _extrair_numero_artigo(self, texto_lei: str) -> str:
        patterns = [r'Art\.?\s*(\d+)', r'Artigo\s*(\d+)', r'CLT.*Art\.?\s*(\d+)']
        for pattern in patterns:
            match = re.search(pattern, texto_lei, re.IGNORECASE)
            if match:
                return f"Art. {match.group(1)}"
        return "Dispositivo Legal"

    def _gerar_documento_emergencia(self, dados: Dict) -> str:
        # Este método agora só seria chamado se a exceção não fosse capturada antes.
        # É uma última camada de segurança.
        print("🚨 ATENÇÃO: Gerando documento de emergência. A IA falhou em todas as etapas.")
        autor = dados.get('autor', {})
        reu = dados.get('reu', {})
        pedidos_lista = dados.get('pedidos', 'Pedidos a serem especificados.')
        if isinstance(pedidos_lista, str):
            pedidos_lista = [pedidos_lista] # Garante que seja uma lista para o join

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Petição Inicial - MODO DE EMERGÊNCIA</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; color: #333; }}
        h1 {{ text-align: center; color: #d9534f; }}
        h2 {{ color: #555; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
        .erro-aviso {{ text-align: center; font-weight: bold; color: #a94442; background-color: #f2dede; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="erro-aviso"><p>ATENÇÃO: Este documento foi gerado em modo de emergência devido a uma falha crítica no sistema de IA.</p></div>
    <h1>PETIÇÃO INICIAL</h1>
    <h2>I - QUALIFICAÇÃO DAS PARTES</h2>
    <p><strong>RECLAMANTE:</strong> {autor.get('nome', 'N/A')}, {autor.get('qualificacao', 'qualificação pendente')}.</p>
    <p><strong>RECLAMADA:</strong> {reu.get('nome', 'N/A')}, {reu.get('qualificacao', 'qualificação pendente')}.</p>
    <h2>II - DOS FATOS</h2>
    <p>{dados.get('fatos', 'Fatos a serem detalhados.')}</p>
    <h2>III - DOS PEDIDOS</h2>
    <ul><li>{"</li><li>".join(pedidos_lista)}</li></ul>
    <h2>IV - DO VALOR DA CAUSA</h2>
    <p>Dá-se à causa o valor de R$ {dados.get('valor_causa', '0,00')}.</p>
    <p style="text-align: center; margin-top: 50px;">Termos em que, pede deferimento.</p>
</body>
</html>"""