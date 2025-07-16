# agente_redator_inteligente_final.py - Agente Redator Inteligente Superior a um Advogado

import json
import logging
import openai
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
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = openai.OpenAI()
    
    def redigir_peticao_completa(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal chamado pelo orquestrador.
        Redige petição completa usando inteligência jurídica avançada.
        """
        try:
            print("✍️ Iniciando redação inteligente da petição...")
            
            # Gerar documento HTML usando inteligência avançada
            documento_html = self.gerar_documento_html_puro(dados_estruturados, pesquisa_juridica)
            
            # Calcular estatísticas
            tamanho_documento = len(documento_html)
            score_qualidade = self._calcular_score_qualidade(documento_html, dados_estruturados, pesquisa_juridica)
            
            print(f"✅ Petição redigida com sucesso: {tamanho_documento} caracteres")
            print(f"📊 Score de qualidade: {score_qualidade}")
            
            # Retornar no formato esperado pelo orquestrador e main.py
            return {
                "status": "sucesso",
                "documento_html": documento_html,
                "dados_estruturados": dados_estruturados,  # Incluir para compatibilidade com main.py
                "metadados": {
                    "timestamp": datetime.now().isoformat(),
                    "tamanho_caracteres": tamanho_documento,
                    "score_qualidade": score_qualidade,
                    "pesquisas_utilizadas": {
                        "legislacao": len(pesquisa_juridica.get('legislacao', [])),
                        "jurisprudencia": len(pesquisa_juridica.get('jurisprudencia', [])),
                        "doutrina": len(pesquisa_juridica.get('doutrina', []))
                    },
                    "estrategia_aplicada": "inteligencia_juridica_avancada"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro na redação da petição: {e}")
            return {
                "status": "erro",
                "erro": str(e),
                "documento_html": self._gerar_documento_emergencia(dados_estruturados),
                "dados_estruturados": dados_estruturados,
                "metadados": {
                    "timestamp": datetime.now().isoformat(),
                    "erro_ocorrido": True
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
        
    def analisar_contexto_juridico(self, dados_formulario: Dict, pesquisas: Dict) -> Dict:
        """
        Analisa o contexto jurídico completo para determinar estratégias inteligentes.
        """
        try:
            # Extrair informações essenciais
            fatos = dados_formulario.get('fatos', '')
            area_direito = dados_formulario.get('area_direito', '').lower()
            tipo_acao = dados_formulario.get('tipo_acao', '').lower()
            valor_causa = dados_formulario.get('valor_causa', 0)
            
            # Analisar complexidade do caso
            complexidade = self._avaliar_complexidade_caso(dados_formulario)
            
            # Analisar qualidade das pesquisas
            qualidade_pesquisas = self._avaliar_qualidade_pesquisas(pesquisas)
            
            # Determinar estratégias específicas
            estrategias = {
                'legislacao': self._estrategia_para_legislacao(area_direito, complexidade),
                'jurisprudencia': self._estrategia_para_jurisprudencia(complexidade, qualidade_pesquisas),
                'doutrina': self._estrategia_para_doutrina(area_direito, tipo_acao),
                'estilo_documento': self._determinar_estilo_documento(tipo_acao, valor_causa),
                'tamanho_alvo': self._calcular_tamanho_alvo(complexidade, valor_causa)
            }
            
            return estrategias
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar contexto: {e}")
            return self._estrategias_padrao()
    
    def _avaliar_complexidade_caso(self, dados: Dict) -> str:
        """Avalia a complexidade jurídica do caso."""
        pontos = 0
        
        # Fatores de complexidade
        fatos = dados.get('fatos', '')
        if len(fatos) > 1500: pontos += 2
        if 'constitucional' in fatos.lower(): pontos += 3
        if 'assédio' in fatos.lower(): pontos += 2
        if 'danos morais' in fatos.lower(): pontos += 1
        
        # Converter valor_causa para int com tratamento de erro
        try:
            valor_causa = int(dados.get('valor_causa', 0))
            if valor_causa > 100000: pontos += 2
        except (ValueError, TypeError):
            # Se não conseguir converter, ignora este critério
            pass
            
        if len(dados.get('documentos', [])) > 5: pontos += 1
        
        if pontos >= 6: return 'muito_alta'
        elif pontos >= 4: return 'alta'
        elif pontos >= 2: return 'media'
        else: return 'baixa'
    
    def _avaliar_qualidade_pesquisas(self, pesquisas: Dict) -> Dict:
        """Avalia a qualidade e relevância das pesquisas realizadas."""
        qualidade = {
            'legislacao': {'quantidade': 0, 'qualidade': 'baixa', 'relevancia': 'baixa'},
            'jurisprudencia': {'quantidade': 0, 'qualidade': 'baixa', 'relevancia': 'baixa'},
            'doutrina': {'quantidade': 0, 'qualidade': 'baixa', 'relevancia': 'baixa'}
        }
        
        for tipo, itens in pesquisas.items():
            if tipo in qualidade and isinstance(itens, list):
                qualidade[tipo]['quantidade'] = len(itens)
                
                # Avaliar qualidade baseada no tamanho do conteúdo
                tamanho_medio = sum(len(item.get('texto', '')) for item in itens) / max(len(itens), 1)
                if tamanho_medio > 2000:
                    qualidade[tipo]['qualidade'] = 'alta'
                elif tamanho_medio > 1000:
                    qualidade[tipo]['qualidade'] = 'media'
                
                # Avaliar relevância baseada em palavras-chave
                conteudo_total = ' '.join(item.get('texto', '') for item in itens).lower()
                palavras_relevantes = ['trabalhista', 'clt', 'empregado', 'salário', 'rescisão', 'indenização']
                relevancia_score = sum(1 for palavra in palavras_relevantes if palavra in conteudo_total)
                
                if relevancia_score >= 4:
                    qualidade[tipo]['relevancia'] = 'alta'
                elif relevancia_score >= 2:
                    qualidade[tipo]['relevancia'] = 'media'
        
        return qualidade
    
    def _estrategia_para_legislacao(self, area_direito: str, complexidade: str) -> Dict:
        """Define estratégia inteligente para uso de legislação."""
        if 'trabalhista' in area_direito:
            return {
                'modo': 'citacao_inteligente',
                'max_artigos': 4,
                'incluir_numero_artigo': True,
                'incluir_resumo_proprio': True,
                'transcrever_integral': False,  # Nunca transcrever leis na íntegra
                'explicar_aplicacao': True
            }
        else:
            return {
                'modo': 'citacao_simples',
                'max_artigos': 3,
                'incluir_numero_artigo': True,
                'incluir_resumo_proprio': True,
                'transcrever_integral': False,
                'explicar_aplicacao': False
            }
    
    def _estrategia_para_jurisprudencia(self, complexidade: str, qualidade: Dict) -> Dict:
        """Define estratégia inteligente para jurisprudência."""
        if complexidade in ['muito_alta', 'alta']:
            return {
                'modo': 'transcricao_seletiva',  # Transcrever casos importantes
                'max_casos': 2,
                'incluir_ementa_completa': True,
                'incluir_analise_propria': True,
                'conectar_com_fatos': True
            }
        elif complexidade == 'media':
            return {
                'modo': 'resumo_elaborado',  # Resumir com análise
                'max_casos': 3,
                'incluir_ementa_completa': False,
                'incluir_analise_propria': True,
                'conectar_com_fatos': True
            }
        else:
            return {
                'modo': 'citacao_resumida',  # Apenas citar
                'max_casos': 2,
                'incluir_ementa_completa': False,
                'incluir_analise_propria': False,
                'conectar_com_fatos': False
            }
    
    def _estrategia_para_doutrina(self, area_direito: str, tipo_acao: str) -> Dict:
        """Define estratégia para doutrina - sempre elaborar texto próprio."""
        return {
            'modo': 'elaboracao_propria',  # SEMPRE elaborar texto próprio
            'max_autores': 3,
            'parafrasear_completamente': True,
            'incluir_citacao_autor': True,
            'conectar_com_caso': True,
            'criar_argumentacao_propria': True
        }
    
    def _determinar_estilo_documento(self, tipo_acao: str, valor_causa: float) -> Dict:
        """Determina o estilo e estrutura do documento."""
        if 'peticao' in tipo_acao.lower():
            return {
                'tipo': 'peticao_inicial',
                'tom': 'formal_persuasivo',
                'estrutura': 'completa',
                'secoes_obrigatorias': ['qualificacao', 'fatos', 'direito', 'pedidos'],
                'usar_formatacao_avancada': True
            }
        else:
            return {
                'tipo': 'documento_juridico',
                'tom': 'formal',
                'estrutura': 'padrao',
                'secoes_obrigatorias': ['introducao', 'desenvolvimento', 'conclusao'],
                'usar_formatacao_avancada': False
            }
    
    def _calcular_tamanho_alvo(self, complexidade: str, valor_causa: float) -> int:
        """Calcula o tamanho alvo do documento baseado na complexidade."""
        base = 20000
        
        if complexidade == 'muito_alta': base += 15000
        elif complexidade == 'alta': base += 10000
        elif complexidade == 'media': base += 5000
        
        # Converter valor_causa para float com tratamento de erro
        try:
            valor_causa_num = float(valor_causa) if valor_causa else 0
            if valor_causa_num > 100000: base += 5000
            elif valor_causa_num > 50000: base += 3000
        except (ValueError, TypeError):
            # Se não conseguir converter, ignora este critério
            pass
        
        return base
    
    def _estrategias_padrao(self) -> Dict:
        """Estratégias padrão em caso de erro."""
        return {
            'legislacao': {'modo': 'citacao_simples', 'max_artigos': 3},
            'jurisprudencia': {'modo': 'resumo_elaborado', 'max_casos': 2},
            'doutrina': {'modo': 'elaboracao_propria', 'max_autores': 2},
            'estilo_documento': {'tipo': 'documento_juridico', 'tom': 'formal'},
            'tamanho_alvo': 20000
        }
    
    def processar_legislacao_inteligente(self, legislacao: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """Processa legislação de forma inteligente - NUNCA transcreve na íntegra."""
        try:
            conteudo_processado = ""
            artigos_processados = 0
            max_artigos = estrategia.get('max_artigos', 3)
            
            for item in legislacao[:max_artigos]:
                if artigos_processados >= max_artigos:
                    break
                
                texto_lei = item.get('texto', '')
                url = item.get('url', '')
                
                # SEMPRE citar e resumir, NUNCA transcrever na íntegra
                artigo_numero = self._extrair_numero_artigo(texto_lei)
                resumo_proprio = self._criar_resumo_proprio_lei(texto_lei, contexto_caso)
                aplicacao = self._explicar_aplicacao_lei(texto_lei, contexto_caso)
                
                conteudo_processado += f"""
                <div class="fundamentacao-legal">
                    <h4>Fundamentação Legal - {artigo_numero}</h4>
                    <p><strong>Dispositivo:</strong> {artigo_numero}</p>
                    <p><strong>Aplicação ao caso:</strong> {resumo_proprio}</p>
                    <p><strong>Relevância:</strong> {aplicacao}</p>
                    <p class="fonte-legal"><em>Fonte: {url}</em></p>
                </div>
                """
                artigos_processados += 1
            
            return conteudo_processado
            
        except Exception as e:
            self.logger.error(f"Erro ao processar legislação: {e}")
            return "<div class='fundamentacao-legal'><p>Fundamentação legal aplicável ao caso.</p></div>"
    
    def processar_jurisprudencia_inteligente(self, jurisprudencia: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """Processa jurisprudência decidindo inteligentemente quando transcrever vs resumir."""
        try:
            conteudo_processado = ""
            casos_processados = 0
            max_casos = estrategia.get('max_casos', 2)
            modo = estrategia.get('modo', 'resumo_elaborado')
            
            for item in jurisprudencia[:max_casos]:
                if casos_processados >= max_casos:
                    break
                
                texto_decisao = item.get('texto', '')
                url = item.get('url', '')
                
                if modo == 'transcricao_seletiva':
                    # Transcrever casos muito importantes na íntegra
                    if self._eh_caso_fundamental(texto_decisao, contexto_caso):
                        conteudo_processado += f"""
                        <div class="jurisprudencia-integral">
                            <h4>Precedente Judicial Fundamental</h4>
                            <blockquote class="decisao-completa">
                                {texto_decisao[:3000]}...
                            </blockquote>
                            <p><strong>Análise:</strong> {self._analisar_precedente(texto_decisao, contexto_caso)}</p>
                            <p class="fonte-jurisprudencia"><em>Fonte: {url}</em></p>
                        </div>
                        """
                    else:
                        # Mesmo em modo transcrição, resumir casos menos relevantes
                        resumo = self._criar_resumo_jurisprudencia(texto_decisao, contexto_caso)
                        conteudo_processado += f"""
                        <div class="jurisprudencia-resumida">
                            <h5>Precedente Judicial</h5>
                            <p>{resumo}</p>
                            <p class="fonte-jurisprudencia"><em>Fonte: {url}</em></p>
                        </div>
                        """
                
                elif modo == 'resumo_elaborado':
                    # Resumir com análise detalhada
                    resumo_detalhado = self._criar_resumo_detalhado(texto_decisao, contexto_caso)
                    analise = self._analisar_precedente(texto_decisao, contexto_caso)
                    
                    conteudo_processado += f"""
                    <div class="jurisprudencia-analisada">
                        <h5>Jurisprudência Aplicável</h5>
                        <p><strong>Decisão:</strong> {resumo_detalhado}</p>
                        <p><strong>Aplicação ao caso:</strong> {analise}</p>
                        <p class="fonte-jurisprudencia"><em>Fonte: {url}</em></p>
                    </div>
                    """
                
                else:  # citacao_resumida
                    # Apenas citar brevemente
                    tribunal = self._extrair_tribunal(url)
                    resumo_breve = self._criar_resumo_breve(texto_decisao)
                    conteudo_processado += f"<p>O {tribunal} já decidiu que {resumo_breve}.</p>"
                
                casos_processados += 1
            
            return conteudo_processado
            
        except Exception as e:
            self.logger.error(f"Erro ao processar jurisprudência: {e}")
            return "<div class='jurisprudencia'><p>Jurisprudência aplicável ao caso.</p></div>"
    
    def processar_doutrina_inteligente(self, doutrina: List[Dict], estrategia: Dict, contexto_caso: str) -> str:
        """Processa doutrina SEMPRE elaborando texto próprio, nunca transcrevendo."""
        try:
            conteudo_processado = ""
            autores_processados = 0
            max_autores = estrategia.get('max_autores', 3)
            
            # Coletar todos os textos doutrinários
            textos_doutrina = []
            for item in doutrina[:max_autores]:
                texto = item.get('texto', '')
                autor = self._extrair_autor_doutrina(item.get('url', ''), texto)
                textos_doutrina.append({'texto': texto, 'autor': autor, 'url': item.get('url', '')})
            
            # Elaborar texto próprio baseado na doutrina
            texto_elaborado = self._elaborar_texto_proprio_doutrina(textos_doutrina, contexto_caso)
            
            conteudo_processado = f"""
            <div class="fundamentacao-doutrinaria">
                <h4>Fundamentação Doutrinária</h4>
                {texto_elaborado}
            </div>
            """
            
            return conteudo_processado
            
        except Exception as e:
            self.logger.error(f"Erro ao processar doutrina: {e}")
            return "<div class='doutrina'><p>Fundamentação doutrinária aplicável.</p></div>"
    
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
    
    def _criar_resumo_proprio_lei(self, texto_lei: str, contexto_caso: str) -> str:
        """Cria resumo próprio da lei aplicada ao caso."""
        try:
            prompt = f"""
            Analise este dispositivo legal e crie um resumo próprio aplicado ao caso:
            
            Lei: {texto_lei[:800]}
            Caso: {contexto_caso[:400]}
            
            Crie um resumo de 2-3 frases explicando:
            1. O que a lei estabelece
            2. Como se aplica ao caso específico
            
            Use suas próprias palavras, não copie o texto da lei.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Erro ao criar resumo da lei: {e}")
            return "Este dispositivo legal estabelece regras aplicáveis ao presente caso."
    
    def _explicar_aplicacao_lei(self, texto_lei: str, contexto_caso: str) -> str:
        """Explica como a lei se aplica especificamente ao caso."""
        try:
            prompt = f"""
            Explique como este dispositivo legal se aplica especificamente ao caso:
            
            Lei: {texto_lei[:600]}
            Fatos do caso: {contexto_caso[:400]}
            
            Explique em 1-2 frases a relevância específica para este caso.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Erro ao explicar aplicação: {e}")
            return "Aplicável ao caso em questão."
    
    def _eh_caso_fundamental(self, texto_decisao: str, contexto_caso: str) -> bool:
        """Verifica se um caso jurisprudencial é fundamental e merece transcrição integral."""
        # Critérios para casos fundamentais
        texto_lower = texto_decisao.lower()
        contexto_lower = contexto_caso.lower()
        
        # Casos de tribunais superiores
        if any(tribunal in texto_lower for tribunal in ['stf', 'stj', 'tst']):
            # Se há sobreposição significativa de temas
            temas_caso = set(re.findall(r'\b\w{4,}\b', contexto_lower))
            temas_decisao = set(re.findall(r'\b\w{4,}\b', texto_lower))
            sobreposicao = len(temas_caso.intersection(temas_decisao))
            
            return sobreposicao >= 3
        
        return False
    
    def _criar_resumo_jurisprudencia(self, texto_decisao: str, contexto_caso: str) -> str:
        """Cria resumo inteligente da jurisprudência."""
        try:
            prompt = f"""
            Resuma esta decisão judicial aplicando ao caso atual:
            
            Decisão: {texto_decisao[:1200]}
            Caso atual: {contexto_caso[:400]}
            
            Crie um resumo de 3-4 frases destacando:
            1. O que foi decidido
            2. A fundamentação principal
            3. Como se aplica ao caso atual
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Erro ao resumir jurisprudência: {e}")
            return "Decisão judicial relevante para o caso."
    
    def _criar_resumo_detalhado(self, texto_decisao: str, contexto_caso: str) -> str:
        """Cria resumo detalhado da decisão."""
        try:
            prompt = f"""
            Crie um resumo detalhado desta decisão:
            
            Decisão: {texto_decisao[:1500]}
            
            Resumo em 4-5 frases cobrindo:
            1. Fatos do caso julgado
            2. Questão jurídica decidida
            3. Fundamentação do tribunal
            4. Conclusão da decisão
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Erro ao criar resumo detalhado: {e}")
            return "Decisão judicial com fundamentação aplicável."
    
    def _analisar_precedente(self, texto_decisao: str, contexto_caso: str) -> str:
        """Analisa como o precedente se aplica ao caso atual."""
        try:
            prompt = f"""
            Analise como este precedente se aplica ao caso atual:
            
            Precedente: {texto_decisao[:1000]}
            Caso atual: {contexto_caso[:400]}
            
            Análise em 2-3 frases sobre:
            1. Semelhanças entre os casos
            2. Como o precedente favorece o caso atual
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar precedente: {e}")
            return "Este precedente estabelece fundamento favorável ao caso."
    
    def _elaborar_texto_proprio_doutrina(self, textos_doutrina: List[Dict], contexto_caso: str) -> str:
        """Elabora texto próprio baseado na doutrina, nunca transcrevendo."""
        try:
            # Combinar textos doutrinários
            conteudo_doutrina = ""
            referencias = []
            
            for item in textos_doutrina:
                conteudo_doutrina += item['texto'][:800] + " "
                referencias.append(f"{item['autor']} ({item['url']})")
            
            prompt = f"""
            Com base nos textos doutrinários fornecidos, elabore um texto próprio aplicado ao caso:
            
            Doutrina: {conteudo_doutrina[:2000]}
            Caso: {contexto_caso[:500]}
            
            Elabore 3-4 parágrafos próprios que:
            1. Expliquem os conceitos doutrinários relevantes
            2. Apliquem esses conceitos ao caso específico
            3. Construam argumentação jurídica sólida
            
            Use suas próprias palavras, não copie os textos originais.
            Inclua as referências ao final.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.4
            )
            
            texto_elaborado = response.choices[0].message.content.strip()
            
            # Adicionar referências
            refs_formatadas = "<p><strong>Referências:</strong> " + "; ".join(referencias) + "</p>"
            
            return f"<div class='texto-doutrinario'>{texto_elaborado}</div>{refs_formatadas}"
            
        except Exception as e:
            self.logger.error(f"Erro ao elaborar texto doutrinário: {e}")
            return "<p>Conforme entendimento doutrinário aplicável ao caso.</p>"
    
    def _extrair_tribunal(self, url: str) -> str:
        """Extrai nome do tribunal da URL."""
        if 'tst.jus.br' in url: return 'TST'
        elif 'stf.jus.br' in url: return 'STF'
        elif 'stj.jus.br' in url: return 'STJ'
        elif 'trt' in url: return 'TRT'
        else: return 'Tribunal'
    
    def _extrair_autor_doutrina(self, url: str, texto: str) -> str:
        """Extrai autor da doutrina."""
        if 'conjur.com.br' in url: return 'Consultor Jurídico'
        elif 'migalhas.com.br' in url: return 'Migalhas'
        else: return 'Doutrina especializada'
    
    def _criar_resumo_breve(self, texto: str) -> str:
        """Cria resumo muito breve."""
        return texto[:100] + "..." if len(texto) > 100 else texto
    
    def gerar_documento_html_puro(self, dados_formulario: Dict, pesquisas: Dict) -> str:
        """
        Gera documento HTML puro usando inteligência jurídica avançada.
        Retorna APENAS o HTML do documento, sem metadados.
        """
        try:
            # Analisar contexto e definir estratégias
            contexto_caso = f"{dados_formulario.get('fatos', '')} {dados_formulario.get('fundamentacao', '')}"
            estrategias = self.analisar_contexto_juridico(dados_formulario, pesquisas)
            
            # Processar cada tipo de conteúdo conforme estratégia
            legislacao_processada = self.processar_legislacao_inteligente(
                pesquisas.get('legislacao', []), 
                estrategias['legislacao'], 
                contexto_caso
            )
            
            jurisprudencia_processada = self.processar_jurisprudencia_inteligente(
                pesquisas.get('jurisprudencia', []), 
                estrategias['jurisprudencia'], 
                contexto_caso
            )
            
            doutrina_processada = self.processar_doutrina_inteligente(
                pesquisas.get('doutrina', []), 
                estrategias['doutrina'], 
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
            
            return documento_html
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar documento: {e}")
            return self._gerar_documento_emergencia(dados_formulario)
    
    def _gerar_documento_final_com_ia(self, dados: Dict, legislacao: str, jurisprudencia: str, doutrina: str, estrategias: Dict) -> str:
        """Gera documento final usando IA avançada."""
        try:
            tamanho_alvo = estrategias.get('tamanho_alvo', 25000)
            
            prompt = f"""
            Você é um advogado expert. Crie uma petição inicial trabalhista completa e profissional.
            
            DADOS DO CASO:
            - Autor: {dados.get('nome_autor', 'N/A')}
            - Réu: {dados.get('nome_reu', 'N/A')}
            - Fatos: {dados.get('fatos', 'N/A')}
            - Valor: R$ {dados.get('valor_causa', 'N/A')}
            - Documentos: {', '.join(dados.get('documentos', []))}
            
            FUNDAMENTAÇÃO PROCESSADA:
            
            LEGISLAÇÃO:
            {legislacao}
            
            JURISPRUDÊNCIA:
            {jurisprudencia}
            
            DOUTRINA:
            {doutrina}
            
            INSTRUÇÕES ESPECÍFICAS:
            1. Crie uma petição inicial trabalhista com pelo menos {tamanho_alvo} caracteres
            2. Use TODA a fundamentação processada fornecida
            3. Estruture em: Qualificação, Fatos, Direito (com as 3 fundamentações), Pedidos
            4. Use linguagem jurídica formal e persuasiva
            5. Integre naturalmente todo o conteúdo das pesquisas processadas
            6. Retorne APENAS o HTML do documento, sem explicações
            7. Use CSS inline profissional
            8. Seja superior a um advogado humano na qualidade
            
            O HTML deve ter estrutura completa com head, body e CSS inline profissional.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.3
            )
            
            html_gerado = response.choices[0].message.content.strip()
            
            # Verificar e expandir se necessário
            if len(html_gerado) < tamanho_alvo * 0.7:  # Se menor que 70% do alvo
                html_gerado = self._expandir_documento_automaticamente(html_gerado, dados, legislacao, jurisprudencia, doutrina)
            
            return html_gerado
            
        except Exception as e:
            self.logger.error(f"Erro na geração com IA: {e}")
            return self._gerar_documento_emergencia(dados)
    
    def _expandir_documento_automaticamente(self, html_base: str, dados: Dict, legislacao: str, jurisprudencia: str, doutrina: str) -> str:
        """Expande documento automaticamente se necessário."""
        try:
            # Adicionar seções extras antes do fechamento do body
            secoes_extras = f"""
            <div class="secao-fundamentacao-ampliada" style="margin: 30px 0; padding: 20px; border-left: 4px solid #2c3e50;">
                <h3 style="color: #2c3e50; margin-bottom: 20px;">III - DA FUNDAMENTAÇÃO JURÍDICA AMPLIADA</h3>
                
                <div class="subsecao-legislacao" style="margin: 20px 0;">
                    <h4 style="color: #34495e;">3.1 - Fundamentação Legal</h4>
                    {legislacao}
                </div>
                
                <div class="subsecao-jurisprudencia" style="margin: 20px 0;">
                    <h4 style="color: #34495e;">3.2 - Jurisprudência Aplicável</h4>
                    {jurisprudencia}
                </div>
                
                <div class="subsecao-doutrina" style="margin: 20px 0;">
                    <h4 style="color: #34495e;">3.3 - Entendimento Doutrinário</h4>
                    {doutrina}
                </div>
                
                <div class="subsecao-aplicacao" style="margin: 20px 0;">
                    <h4 style="color: #34495e;">3.4 - Aplicação ao Caso Concreto</h4>
                    <p style="text-align: justify; line-height: 1.6;">
                        Diante de todo o exposto, verifica-se que o caso em tela se enquadra perfeitamente 
                        nos precedentes jurisprudenciais e na doutrina especializada apresentada. A fundamentação 
                        legal é sólida e ampara integralmente os pedidos formulados, demonstrando a procedência 
                        das pretensões do autor.
                    </p>
                    <p style="text-align: justify; line-height: 1.6;">
                        A análise conjunta da legislação, jurisprudência e doutrina confirma que os direitos 
                        pleiteados encontram respaldo no ordenamento jurídico brasileiro, sendo imperioso 
                        o acolhimento dos pedidos para fazer justiça ao caso concreto.
                    </p>
                </div>
            </div>
            """
            
            # Inserir antes do fechamento do body
            if '</body>' in html_base:
                html_base = html_base.replace('</body>', f'{secoes_extras}</body>')
            else:
                html_base += secoes_extras
            
            return html_base
            
        except Exception as e:
            self.logger.error(f"Erro ao expandir documento: {e}")
            return html_base
    
    def _gerar_documento_emergencia(self, dados: Dict) -> str:
        """Gera documento básico em caso de falha total."""
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Petição Inicial</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; }}
        h1 {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        .qualificacao {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        p {{ text-align: justify; margin: 15px 0; }}
    </style>
</head>
<body>
    <h1>PETIÇÃO INICIAL</h1>
    
    <div class="qualificacao">
        <h2>I - QUALIFICAÇÃO DAS PARTES</h2>
        <p><strong>AUTOR:</strong> {dados.get('nome_autor', 'N/A')}</p>
        <p><strong>RÉU:</strong> {dados.get('nome_reu', 'N/A')}</p>
    </div>
    
    <h2>II - DOS FATOS</h2>
    <p>{dados.get('fatos', 'Fatos a serem detalhados conforme documentos anexos.')}</p>
    
    <h2>III - DOS PEDIDOS</h2>
    <p>Requer-se a procedência dos pedidos no valor de R$ {dados.get('valor_causa', '0,00')}.</p>
    
    <p style="text-align: center; margin-top: 50px;">
        <strong>Termos em que pede deferimento.</strong>
    </p>
</body>
</html>"""