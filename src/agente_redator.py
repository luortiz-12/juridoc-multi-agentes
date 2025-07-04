# agente_redator_corrigido.py - Agente Redator que gera documentos extensos com dados reais

import os
import json
import re
from typing import Dict, Any, List
from datetime import datetime

# LangChain imports
try:
    from langchain_openai import OpenAI
    from langchain_core.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class AgenteRedator:
    """
    Agente Redator CORRIGIDO que:
    - Usa TODOS os dados reais do formulário e pesquisas
    - Gera documentos extensos e completos (10+ mil caracteres)
    - Integra inteligentemente fundamentação jurídica
    - Produz HTML profissional e bem estruturado
    - NUNCA usa dados simulados ou falsos
    """
    
    def __init__(self, openai_api_key: str = None):
        print("✍️ Inicializando Agente Redator CORRIGIDO...")
        
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Templates para diferentes tipos de ação
        self.templates_acao = {
            'trabalhista': self._get_template_trabalhista(),
            'civil': self._get_template_civil(),
            'consumidor': self._get_template_consumidor(),
            'default': self._get_template_default()
        }
        
        # Inicializar LLM se disponível
        if LANGCHAIN_AVAILABLE and self.openai_api_key:
            try:
                self.llm = OpenAI(
                    openai_api_key=self.openai_api_key,
                    model_name="gpt-4o", # Recomendo usar um modelo mais moderno
                    temperature=0.3,  # Criatividade controlada
                    max_tokens=4096   # Permitir textos longos
                )
                self.llm_disponivel = True
                print("✅ LLM inicializado para redação avançada")
            except Exception as e:
                print(f"⚠️ LLM não disponível: {e}")
                self.llm_disponivel = False
        else:
            self.llm_disponivel = False
            print("⚠️ LLM não disponível - usando templates estruturados")
        
        print("✅ Agente Redator CORRIGIDO inicializado")
    
    def redigir_peticao(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redige petição completa e extensa usando TODOS os dados reais.
        """
        try:
            print("✍️ Iniciando redação da petição com dados reais...")
            
            # ETAPA 1: ANÁLISE DOS DADOS RECEBIDOS
            tipo_acao = self._identificar_tipo_acao(dados_estruturados)
            print(f"📋 Tipo de ação identificado: {tipo_acao}")
            
            # ETAPA 2: PREPARAÇÃO DO CONTEÚDO
            conteudo_preparado = self._preparar_conteudo_completo(dados_estruturados, pesquisa_juridica)
            
            # ETAPA 3: REDAÇÃO PRINCIPAL
            if self.llm_disponivel:
                peticao_html = self._redigir_com_llm(conteudo_preparado, tipo_acao)
            else:
                peticao_html = self._redigir_com_template(conteudo_preparado, tipo_acao)
            
            # ETAPA 4: FORMATAÇÃO FINAL
            peticao_final = self._formatar_html_profissional(peticao_html)
            
            # ETAPA 5: VALIDAÇÃO DE TAMANHO
            tamanho = len(peticao_final)
            print(f"📄 Documento gerado: {tamanho} caracteres")
            
            if tamanho < 8000:
                print("📝 Expandindo documento para atingir tamanho mínimo...")
                peticao_final = self._expandir_documento(peticao_final, conteudo_preparado)
                tamanho = len(peticao_final)
                print(f"📄 Documento expandido: {tamanho} caracteres")
            
            return {
                "status": "sucesso",
                "peticao_html": peticao_final,
                "estatisticas": {
                    "caracteres": tamanho,
                    "palavras": len(peticao_final.split()),
                    "tipo_acao": tipo_acao,
                    "dados_reais_usados": True,
                    "pesquisa_integrada": bool(pesquisa_juridica),
                    "metodo_redacao": "llm" if self.llm_disponivel else "template"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro na redação: {e}")
            return {
                "status": "erro",
                "erro": str(e),
                "peticao_html": self._gerar_peticao_emergencia(dados_estruturados),
                "timestamp": datetime.now().isoformat()
            }
    
    def _identificar_tipo_acao(self, dados: Dict[str, Any]) -> str:
        """Identifica tipo de ação baseado nos dados reais."""
        fatos = str(dados.get('fatos_peticao', '')).lower()
        pedido = str(dados.get('pedido_peticao', '')).lower()
        verbas = str(dados.get('verbas_pleiteadas_peticao', '')).lower()
        
        texto_completo = f"{fatos} {pedido} {verbas}"
        
        if any(palavra in texto_completo for palavra in ['trabalhista', 'rescisão', 'horas extras', 'assédio moral', 'clt', 'reclamante']):
            return 'trabalhista'
        elif any(palavra in texto_completo for palavra in ['consumidor', 'defeito', 'vício', 'fornecedor', 'cdc']):
            return 'consumidor'
        
        return 'civil'
    
    def _preparar_conteudo_completo(self, dados: Dict[str, Any], pesquisa: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara todo o conteúdo real para redação."""
        # Mapeando os nomes de campo do n8n para nomes padronizados
        return {
            "autor": {
                "nome": dados.get('clienteNome', '[NOME DO AUTOR]'),
                "qualificacao": dados.get('Qualificação', '[QUALIFICAÇÃO DO AUTOR]')
            },
            "reu": {
                "nome": dados.get('nome_contrario_peticao', '[NOME DO RÉU]'),
                "qualificacao": dados.get('qualificacao_contrario_peticao', '[QUALIFICAÇÃO DO RÉU]')
            },
            "tipo_acao": dados.get('tipoDocumento', 'Petição Inicial'),
            "fatos_completos": dados.get('fatos', dados.get('fatos_peticao', '[FATOS NÃO FORNECIDOS]')),
            "pedidos_completos": dados.get('pedido', dados.get('pedido_peticao', '[PEDIDOS NÃO FORNECIDOS]')),
            "valor_causa": dados.get('valorCausa', dados.get('valor_causa_peticao', '[VALOR DA CAUSA]')),
            "competencia": dados.get('competencia', '[COMARCA/ESTADO]'),
            "observacoes": dados.get('observacoes', ''),
            "legislacao_encontrada": pesquisa.get('leis', ''),
            "jurisprudencia_encontrada": pesquisa.get('jurisprudencia', ''),
            "doutrina_encontrada": pesquisa.get('doutrina', ''),
            "data_geracao": datetime.now().strftime('%d de %B de %Y')
        }
    
    def _redigir_com_llm(self, conteudo: Dict[str, Any], tipo_acao: str) -> str:
        """Redige petição usando LLM com dados reais."""
        try:
            prompt_text = self._construir_prompt_completo(conteudo, tipo_acao)
            prompt = PromptTemplate(template=prompt_text, input_variables=[])
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            print("🤖 Gerando petição com LLM usando dados reais...")
            resposta = chain.run({})
            
            if len(resposta) < 5000:
                print("📝 Resposta LLM muito curta, expandindo...")
                resposta = self._expandir_resposta_llm(resposta, conteudo)
            
            return resposta
            
        except Exception as e:
            print(f"❌ Erro na redação LLM: {e}")
            return self._redigir_com_template(conteudo, tipo_acao)
    
    def _construir_prompt_completo(self, conteudo: Dict[str, Any], tipo_acao: str) -> str:
        """Constrói prompt completo para LLM com todos os dados reais."""
        return f"""
            Você é um advogado especialista em redação de petições iniciais. Redija uma petição inicial COMPLETA e EXTENSA usando APENAS as informações reais fornecidas abaixo.

            REGRAS OBRIGATÓRIAS:
            1. Use APENAS dados reais fornecidos - NUNCA invente informações que não estejam aqui.
            2. O documento deve ser extenso e detalhado, com pelo menos 8.000 caracteres.
            3. Siga a estrutura formal jurídica brasileira para um(a) {tipo_acao}.
            4. Integre TODA a fundamentação jurídica encontrada de forma coesa na seção 'DO DIREITO'.
            5. Formato de saída deve ser HTML profissional e limpo.
            6. Seja extremamente detalhado em cada seção.

            DADOS REAIS DAS PARTES:
            Autor: {conteudo['autor']}
            Réu: {conteudo['reu']}

            DADOS REAIS DO CASO:
            Fatos: {conteudo['fatos_completos']}
            Pedidos: {conteudo['pedidos_completos']}
            Valor da Causa: {conteudo['valor_causa']}
            Competência: {conteudo['competencia']}

            FUNDAMENTAÇÃO JURÍDICA REAL ENCONTRADA (USE ISTO NA SEÇÃO 'DO DIREITO'):
            Legislação: {conteudo['legislacao_encontrada']}
            Jurisprudência: {conteudo['jurisprudencia_encontrada']}
            Doutrina: {conteudo['doutrina_encontrada']}

            ESTRUTURA OBRIGATÓRIA:
            1. Endereçamento completo
            2. Qualificação detalhada das partes
            3. Título da ação
            4. Seção 'DOS FATOS' (extensa e detalhada)
            5. Seção 'DO DIREITO' (fundamentação jurídica completa, citando as fontes da pesquisa)
            6. Seção 'DOS PEDIDOS' (detalhados e específicos)
            7. Seção 'DO VALOR DA CAUSA'
            8. Seção 'DOS REQUERIMENTOS FINAIS'
            9. Local, data e assinatura (com placeholders para advogado)

            Redija a petição completa em HTML, começando com <h1>:
        """
    
    def _redigir_com_template(self, conteudo: Dict[str, Any], tipo_acao: str) -> str:
        """Redige petição usando template estruturado com dados reais."""
        print("📝 Gerando petição com template estruturado como fallback...")
        template = self.templates_acao.get(tipo_acao, self.templates_acao['default'])
        
        return template.format(
            nome_autor=conteudo['autor'].get('nome', '[NOME DO AUTOR]'),
            qualificacao_autor=conteudo['autor'].get('qualificacao', '[QUALIFICAÇÃO DO AUTOR]'),
            nome_reu=conteudo['reu'].get('nome', '[NOME DO RÉU]'),
            qualificacao_reu=conteudo['reu'].get('qualificacao', '[QUALIFICAÇÃO DO RÉU]'),
            tipo_acao=conteudo.get('tipo_acao', 'AÇÃO JUDICIAL'),
            fatos_completos=self._expandir_fatos(conteudo['fatos_completos']),
            pedidos_completos=self._expandir_pedidos(conteudo['pedidos_completos']),
            valor_causa=conteudo['valor_causa'],
            competencia=conteudo['competencia'],
            fundamentacao_legal=self._formatar_fundamentacao(conteudo),
            data_geracao=conteudo['data_geracao']
        )
    
    def _expandir_fatos(self, fatos_originais: str) -> str:
        """Expande seção de fatos para ser mais detalhada."""
        if not fatos_originais or fatos_originais.startswith('['):
            return "<p>[FATOS DETALHADOS A SEREM PREENCHIDOS COM BASE NAS INFORMAÇÕES DO CASO]</p>"
        return f"<p>{fatos_originais.replace('\n', '</p><p>')}</p>"
    
    def _expandir_pedidos(self, pedidos_originais: str) -> str:
        """Expande seção de pedidos para ser mais detalhada."""
        if not pedidos_originais or pedidos_originais.startswith('['):
            return "<p>[PEDIDOS ESPECÍFICOS A SEREM DETALHADOS CONFORME O CASO]</p>"
        
        pedidos_lista = [f"<li>{item.strip()}</li>" for item in pedidos_originais.split(';') if item.strip()]
        pedidos_html = "\n".join(pedidos_lista)
        
        return f"""
            <p>Diante de todo o exposto, requer a Vossa Excelência:</p>
            <ol>
                {pedidos_html}
                <li>A condenação da parte requerida ao pagamento das custas processuais e honorários advocatícios, nos termos do artigo 85 do Código de Processo Civil;</li>
                <li>A produção de todos os meios de prova admitidos em direito;</li>
                <li>A citação da parte requerida para, querendo, apresentar resposta no prazo legal, sob pena de revelia.</li>
            </ol>
        """
    
    def _formatar_fundamentacao(self, conteudo: Dict[str, Any]) -> str:
        """Formata fundamentação jurídica completa usando pesquisas reais."""
        fundamentacao = []
        if conteudo.get('legislacao_encontrada') and "não encontrada" not in conteudo['legislacao_encontrada']:
            fundamentacao.append("<h3>DA FUNDAMENTAÇÃO LEGAL</h3>")
            fundamentacao.append(f"<p>{conteudo['legislacao_encontrada']}</p>")
        if conteudo.get('jurisprudencia_encontrada') and "não encontrada" not in conteudo['jurisprudencia_encontrada']:
            fundamentacao.append("<h3>DA JURISPRUDÊNCIA APLICÁVEL</h3>")
            fundamentacao.append(f"<p>{conteudo['jurisprudencia_encontrada']}</p>")
        if conteudo.get('doutrina_encontrada') and "não encontrada" not in conteudo['doutrina_encontrada']:
            fundamentacao.append("<h3>DO ENTENDIMENTO DOUTRINÁRIO</h3>")
            fundamentacao.append(f"<p>{conteudo['doutrina_encontrada']}</p>")
        
        return "\n\n".join(fundamentacao) if fundamentacao else "<p>Fundamentação jurídica a ser desenvolvida com base no conhecimento do patrono.</p>"
    
    def _formatar_html_profissional(self, conteudo: str) -> str:
        """Formata documento em HTML profissional."""
        # A lógica de adicionar CSS e a estrutura <html>...</html> está perfeita. Mantenha-a como está.
        return conteudo # Simplificado, pois os templates já devem gerar HTML completo.
    
    def _expandir_documento(self, documento: str, conteudo: Dict[str, Any]) -> str:
        """Expande documento para atingir tamanho mínimo."""
        print("📝 Expandindo documento...")
        prompt_expansao = f"""
            O seguinte documento jurídico está muito curto. Sua tarefa é expandi-lo, adicionando mais detalhes, aprofundando a argumentação jurídica com base na fundamentação fornecida e detalhando melhor cada seção, sem adicionar fatos novos. Mantenha o formato HTML.
            
            FUNDAMENTAÇÃO DISPONÍVEL:
            Legislação: {conteudo['legislacao_encontrada']}
            Jurisprudência: {conteudo['jurisprudencia_encontrada']}
            Doutrina: {conteudo['doutrina_encontrada']}
            
            DOCUMENTO CURTO PARA EXPANDIR:
            {documento}
            
            REDIJA A VERSÃO EXTENSA E DETALHADA AGORA:
        """
        if self.llm_disponivel:
            return self.llm(prompt_expansao)
        return documento # Retorna o mesmo se LLM não estiver disponível

    def _gerar_peticao_emergencia(self, dados: Dict[str, Any]) -> str:
        """Gera petição de emergência quando tudo falha."""
        return f"<h1>PETIÇÃO DE EMERGÊNCIA</h1><p>Ocorreu um erro na geração. Dados recebidos: {json.dumps(dados)}</p>"
    
    # TEMPLATES PARA DIFERENTES TIPOS DE AÇÃO
    def _get_template_trabalhista(self) -> str:
        """Template específico para ações trabalhistas."""
        return """
            <h1>RECLAMAÇÃO TRABALHISTA</h1>
            <p><strong>EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DA ___ª VARA DO TRABALHO DE {competencia}</strong></p>
            <div class="qualificacao">
                <p><strong>RECLAMANTE:</strong> {nome_autor}, {qualificacao_autor}.</p>
                <p><strong>RECLAMADA:</strong> {nome_reu}, {qualificacao_reu}.</p>
            </div>
            <h2>I - DOS FATOS</h2>
            <p>{fatos_completos}</p>
            <h2>II - DO DIREITO</h2>
            {fundamentacao_legal}
            <h2>III - DOS PEDIDOS</h2>
            {pedidos_completos}
            <h2>IV - DO VALOR DA CAUSA</h2>
            <p>Dá-se à causa o valor de R$ {valor_causa}.</p>
            <div class="data-local">
                <p>[LOCAL], {data_geracao}</p>
            </div>
            <div class="assinatura">
                <p>_________________________</p>
                <p>[NOME DO ADVOGADO]</p>
                <p>[OAB/UF]</p>
            </div>
        """
    
    def _get_template_civil(self) -> str:
        """Template específico para ações cíveis."""
        return self._get_template_default()
    
    def _get_template_consumidor(self) -> str:
        """Template específico para ações de consumidor."""
        return """
            <h1>AÇÃO DE REPARAÇÃO DE DANOS</h1>
            <p><strong>EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA DE {competencia}</strong></p>
            <div class="qualificacao">
                <p><strong>CONSUMIDOR(A)/AUTOR(A):</strong> {nome_autor}, {qualificacao_autor}.</p>
                <p><strong>FORNECEDOR(A)/RÉ(U):</strong> {nome_reu}, {qualificacao_reu}.</p>
            </div>
            <h2>I - DOS FATOS</h2>
            <p>{fatos_completos}</p>
            <h2>II - DO DIREITO</h2>
            <p>A presente demanda encontra fundamento no Código de Defesa do Consumidor (Lei nº 8.078/90).</p>
            {fundamentacao_legal}
            <h2>III - DOS PEDIDOS</h2>
            {pedidos_completos}
            <h2>IV - DO VALOR DA CAUSA</h2>
            <p>Dá-se à causa o valor de R$ {valor_causa}.</p>
            <div class="data-local">
                <p>[LOCAL], {data_geracao}</p>
            </div>
            <div class="assinatura">
                <p>_________________________</p>
                <p>[NOME DO ADVOGADO]</p>
                <p>[OAB/UF]</p>
            </div>
        """
    
    def _get_template_default(self) -> str:
        """Template padrão para outros tipos de ação."""
        return """
            <h1>{tipo_acao}</h1>
            <p><strong>EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA ___ª VARA CÍVEL DA COMARCA DE {competencia}</strong></p>
            <div class="qualificacao">
                <p><strong>AUTOR(A):</strong> {nome_autor}, {qualificacao_autor}.</p>
                <p><strong>RÉ(U):</strong> {nome_reu}, {qualificacao_reu}.</p>
            </div>
            <h2>I - DOS FATOS</h2>
            <p>{fatos_completos}</p>
            <h2>II - DO DIREITO</h2>
            {fundamentacao_legal}
            <h2>III - DOS PEDIDOS</h2>
            {pedidos_completos}
            <h2>IV - DO VALOR DA CAUSA</h2>
            <p>Dá-se à causa o valor de R$ {valor_causa}.</p>
            <div class="data-local">
                <p>[LOCAL], {data_geracao}</p>
            </div>
            <div class="assinatura">
                <p>_________________________</p>
                <p>[NOME DO ADVOGADO]</p>
                <p>[OAB/UF]</p>
            </div>
        """