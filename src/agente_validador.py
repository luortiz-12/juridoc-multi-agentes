# agente_validador.py - Agente Validador e Formatador

import re
import json
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

class AgenteValidador:
    """
    Agente responsável por validar, corrigir e formatar a petição final,
    garantindo qualidade técnica e conformidade processual.
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            openai_api_key=openai_api_key, 
            temperature=0.1
        )
        
        # Template para validação e correção
        self.prompt_validacao = PromptTemplate(
            input_variables=["peticao", "problemas_identificados", "dados_caso"],
            template="""
            Você é um advogado revisor especializado em validação técnica de petições iniciais.
            
            PETIÇÃO PARA VALIDAÇÃO:
            {peticao}
            
            PROBLEMAS IDENTIFICADOS:
            {problemas_identificados}
            
            DADOS DO CASO:
            {dados_caso}
            
            TAREFA: Analise a petição e corrija os problemas identificados, garantindo:
            
            1. CONFORMIDADE PROCESSUAL:
               - Estrutura formal correta
               - Seções obrigatórias presentes
               - Linguagem técnica adequada
            
            2. QUALIDADE JURÍDICA:
               - Fundamentação legal sólida
               - Citações corretas
               - Argumentação coerente
            
            3. COMPLETUDE:
               - Todos os elementos essenciais
               - Pedidos claros e específicos
               - Qualificação adequada das partes
            
            4. FORMATAÇÃO:
               - HTML bem estruturado
               - Hierarquia de títulos correta
               - Formatação profissional
            
            REGRAS DE CORREÇÃO:
            - Mantenha o conteúdo original sempre que possível
            - Corrija apenas os problemas identificados
            - Preserve citações legais e jurisprudência
            - Mantenha placeholders onde necessário
            - Use HTML semântico e bem formatado
            
            FORMATO: HTML puro da petição corrigida, começando com <h1>.
            """
        )
        
        self.chain_validacao = LLMChain(llm=self.llm, prompt=self.prompt_validacao)
    
    def validar_e_formatar(self, peticao_html: str, dados_estruturados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal para validar e formatar a petição.
        
        Args:
            peticao_html: Petição em HTML para validar
            dados_estruturados: Dados estruturados do caso
            
        Returns:
            Dict com petição validada e relatório de qualidade
        """
        try:
            print("🔍 Iniciando validação e formatação...")
            
            # Etapa 1: Análise de problemas
            problemas = self._analisar_problemas(peticao_html, dados_estruturados)
            
            # Etapa 2: Correção se necessário
            peticao_corrigida = self._corrigir_se_necessario(peticao_html, problemas, dados_estruturados)
            
            # Etapa 3: Formatação final
            peticao_formatada = self._formatar_html_final(peticao_corrigida)
            
            # Etapa 4: Validação final
            relatorio_qualidade = self._gerar_relatorio_qualidade(peticao_formatada, dados_estruturados)
            
            print("✅ Validação e formatação concluídas")
            return {
                "status": "sucesso",
                "peticao_final": peticao_formatada,
                "problemas_encontrados": problemas,
                "relatorio_qualidade": relatorio_qualidade,
                "aprovada": len(problemas) <= 2  # Aprovada se poucos problemas
            }
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return {
                "status": "erro",
                "mensagem": f"Erro na validação: {str(e)}",
                "peticao_final": peticao_html,  # Retorna original em caso de erro
                "problemas_encontrados": [f"Erro na validação: {str(e)}"],
                "aprovada": False
            }
    
    def _analisar_problemas(self, peticao: str, dados: Dict[str, Any]) -> List[str]:
        """Analisa a petição e identifica problemas."""
        problemas = []
        
        # 1. Verificar estrutura HTML
        problemas.extend(self._verificar_estrutura_html(peticao))
        
        # 2. Verificar seções obrigatórias
        problemas.extend(self._verificar_secoes_obrigatorias(peticao))
        
        # 3. Verificar qualificação das partes
        problemas.extend(self._verificar_qualificacao_partes(peticao, dados))
        
        # 4. Verificar fundamentação legal
        problemas.extend(self._verificar_fundamentacao_legal(peticao))
        
        # 5. Verificar pedidos
        problemas.extend(self._verificar_pedidos(peticao, dados))
        
        # 6. Verificar formatação
        problemas.extend(self._verificar_formatacao(peticao))
        
        return problemas
    
    def _verificar_estrutura_html(self, peticao: str) -> List[str]:
        """Verifica a estrutura HTML básica."""
        problemas = []
        
        # Verificar se tem tags HTML
        if not re.search(r'<[^>]+>', peticao):
            problemas.append("Petição não está em formato HTML")
        
        # Verificar se tem título principal
        if not re.search(r'<h1[^>]*>.*?</h1>', peticao, re.IGNORECASE):
            problemas.append("Falta título principal (h1)")
        
        # Verificar tags não fechadas básicas
        tags_importantes = ['h1', 'h2', 'p']
        for tag in tags_importantes:
            abertura = len(re.findall(f'<{tag}[^>]*>', peticao, re.IGNORECASE))
            fechamento = len(re.findall(f'</{tag}>', peticao, re.IGNORECASE))
            if abertura != fechamento:
                problemas.append(f"Tags {tag} não estão balanceadas")
        
        return problemas
    
    def _verificar_secoes_obrigatorias(self, peticao: str) -> List[str]:
        """Verifica se tem as seções obrigatórias."""
        problemas = []
        
        secoes_obrigatorias = [
            ("DOS FATOS", "Seção 'DOS FATOS' não encontrada"),
            ("DO DIREITO", "Seção 'DO DIREITO' não encontrada"),
            ("DOS PEDIDOS", "Seção 'DOS PEDIDOS' não encontrada"),
            ("VALOR DA CAUSA", "Seção 'VALOR DA CAUSA' não encontrada")
        ]
        
        for secao, erro in secoes_obrigatorias:
            if secao not in peticao.upper():
                problemas.append(erro)
        
        return problemas
    
    def _verificar_qualificacao_partes(self, peticao: str, dados: Dict[str, Any]) -> List[str]:
        """Verifica a qualificação das partes."""
        problemas = []
        
        autor = dados.get("autor", {})
        reu = dados.get("reu", {})
        
        # Verificar se nomes das partes estão na petição
        if autor.get("nome") and autor["nome"] not in peticao:
            problemas.append("Nome do autor não encontrado na petição")
        
        if reu.get("nome") and reu["nome"] not in peticao:
            problemas.append("Nome do réu não encontrado na petição")
        
        # Verificar se tem qualificação mínima
        elementos_qualificacao = ["CPF", "CNPJ", "endereço", "residente"]
        if not any(elem.lower() in peticao.lower() for elem in elementos_qualificacao):
            problemas.append("Qualificação das partes incompleta")
        
        return problemas
    
    def _verificar_fundamentacao_legal(self, peticao: str) -> List[str]:
        """Verifica a fundamentação legal."""
        problemas = []
        
        # Verificar se tem citações legais
        citacoes_legais = ["artigo", "lei", "código", "decreto"]
        if not any(citacao in peticao.lower() for citacao in citacoes_legais):
            problemas.append("Falta fundamentação legal específica")
        
        # Verificar se tem jurisprudência
        jurisprudencia = ["STF", "STJ", "tribunal", "acórdão", "decisão"]
        if not any(juris.lower() in peticao.lower() for juris in jurisprudencia):
            problemas.append("Falta citação de jurisprudência")
        
        # Verificar se seção DO DIREITO tem conteúdo substancial
        match = re.search(r'<h2[^>]*>.*?DO DIREITO.*?</h2>(.*?)(?=<h2|$)', peticao, re.IGNORECASE | re.DOTALL)
        if match and len(match.group(1).strip()) < 200:
            problemas.append("Seção 'DO DIREITO' muito superficial")
        
        return problemas
    
    def _verificar_pedidos(self, peticao: str, dados: Dict[str, Any]) -> List[str]:
        """Verifica os pedidos da petição."""
        problemas = []
        
        pedidos_dados = dados.get("pedidos", {}).get("principais", [])
        
        # Verificar se seção DOS PEDIDOS tem conteúdo
        match = re.search(r'<h2[^>]*>.*?DOS PEDIDOS.*?</h2>(.*?)(?=<h2|$)', peticao, re.IGNORECASE | re.DOTALL)
        if not match or len(match.group(1).strip()) < 100:
            problemas.append("Seção 'DOS PEDIDOS' muito superficial")
        
        # Verificar se tem pedidos específicos dos dados
        for pedido in pedidos_dados[:3]:  # Verificar primeiros 3 pedidos
            if pedido and pedido.lower() not in peticao.lower():
                problemas.append(f"Pedido '{pedido}' não encontrado na petição")
        
        # Verificar se tem pedido de honorários
        if "honorários" not in peticao.lower():
            problemas.append("Falta pedido de honorários advocatícios")
        
        return problemas
    
    def _verificar_formatacao(self, peticao: str) -> List[str]:
        """Verifica a formatação da petição."""
        problemas = []
        
        # Verificar se tem parágrafos
        if not re.search(r'<p[^>]*>', peticao, re.IGNORECASE):
            problemas.append("Falta formatação em parágrafos")
        
        # Verificar se tem estrutura hierárquica
        if not re.search(r'<h2[^>]*>', peticao, re.IGNORECASE):
            problemas.append("Falta estrutura hierárquica (h2)")
        
        # Verificar se tem formatação de destaque
        if not re.search(r'<strong[^>]*>|<b[^>]*>', peticao, re.IGNORECASE):
            problemas.append("Falta formatação de destaque para elementos importantes")
        
        return problemas
    
    def _corrigir_se_necessario(self, peticao: str, problemas: List[str], dados: Dict[str, Any]) -> str:
        """Corrige a petição se houver problemas significativos."""
        if len(problemas) <= 2:  # Poucos problemas, não precisa correção via LLM
            return peticao
        
        try:
            print(f"🔧 Corrigindo petição ({len(problemas)} problemas)")
            
            problemas_formatados = "\n".join([f"- {problema}" for problema in problemas])
            dados_formatados = json.dumps(dados, indent=2, ensure_ascii=False)
            
            peticao_corrigida = self.chain_validacao.run(
                peticao=peticao,
                problemas_identificados=problemas_formatados,
                dados_caso=dados_formatados
            )
            
            return peticao_corrigida
            
        except Exception as e:
            print(f"⚠️ Erro na correção via LLM: {e}")
            return self._aplicar_correcoes_basicas(peticao, problemas)
    
    def _aplicar_correcoes_basicas(self, peticao: str, problemas: List[str]) -> str:
        """Aplica correções básicas sem usar LLM."""
        peticao_corrigida = peticao
        
        # Garantir que começa com h1 se não tiver
        if not re.search(r'<h1[^>]*>', peticao_corrigida, re.IGNORECASE):
            peticao_corrigida = "<h1>PETIÇÃO INICIAL</h1>\n" + peticao_corrigida
        
        # Envolver em parágrafos se não tiver
        if not re.search(r'<p[^>]*>', peticao_corrigida, re.IGNORECASE):
            # Dividir por quebras de linha e envolver em <p>
            linhas = peticao_corrigida.split('\n')
            linhas_formatadas = []
            for linha in linhas:
                linha = linha.strip()
                if linha and not re.search(r'<[^>]+>', linha):
                    linhas_formatadas.append(f"<p>{linha}</p>")
                else:
                    linhas_formatadas.append(linha)
            peticao_corrigida = '\n'.join(linhas_formatadas)
        
        return peticao_corrigida
    
    def _formatar_html_final(self, peticao: str) -> str:
        """Aplica formatação final ao HTML."""
        # Limpar espaços extras
        peticao = re.sub(r'\n\s*\n', '\n\n', peticao)
        
        # Garantir espaçamento adequado após títulos
        peticao = re.sub(r'(</h[1-6]>)\s*(<p>)', r'\1\n\n\2', peticao)
        
        # Garantir espaçamento antes de títulos
        peticao = re.sub(r'(</p>)\s*(<h[1-6])', r'\1\n\n\2', peticao)
        
        # Adicionar CSS inline básico para melhor apresentação
        css_style = """
        <style>
        body { font-family: 'Times New Roman', serif; line-height: 1.6; margin: 40px; }
        h1 { text-align: center; font-size: 18px; margin-bottom: 30px; }
        h2 { font-size: 16px; margin-top: 25px; margin-bottom: 15px; }
        p { text-align: justify; margin-bottom: 10px; }
        strong { font-weight: bold; }
        </style>
        """
        
        # Se não tem style, adicionar no início
        if '<style>' not in peticao:
            peticao = css_style + '\n' + peticao
        
        return peticao.strip()
    
    def _gerar_relatorio_qualidade(self, peticao: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório de qualidade da petição."""
        # Calcular métricas
        palavras = len(re.findall(r'\b\w+\b', peticao))
        caracteres = len(peticao)
        paragrafos = len(re.findall(r'<p[^>]*>', peticao, re.IGNORECASE))
        secoes = len(re.findall(r'<h[1-6][^>]*>', peticao, re.IGNORECASE))
        
        # Verificar elementos de qualidade
        tem_fundamentacao = bool(re.search(r'artigo|lei|código', peticao, re.IGNORECASE))
        tem_jurisprudencia = bool(re.search(r'STF|STJ|tribunal', peticao, re.IGNORECASE))
        tem_pedidos_claros = bool(re.search(r'DOS PEDIDOS', peticao, re.IGNORECASE))
        tem_valor_causa = bool(re.search(r'VALOR DA CAUSA', peticao, re.IGNORECASE))
        
        # Calcular score de qualidade
        elementos_qualidade = [
            tem_fundamentacao,
            tem_jurisprudencia, 
            tem_pedidos_claros,
            tem_valor_causa,
            palavras > 500,  # Tamanho adequado
            secoes >= 4      # Estrutura adequada
        ]
        
        score_qualidade = (sum(elementos_qualidade) / len(elementos_qualidade)) * 100
        
        return {
            "metricas": {
                "palavras": palavras,
                "caracteres": caracteres,
                "paragrafos": paragrafos,
                "secoes": secoes
            },
            "elementos_qualidade": {
                "fundamentacao_legal": tem_fundamentacao,
                "jurisprudencia": tem_jurisprudencia,
                "pedidos_claros": tem_pedidos_claros,
                "valor_causa": tem_valor_causa
            },
            "score_qualidade": round(score_qualidade, 1),
            "classificacao": self._classificar_qualidade(score_qualidade),
            "recomendacoes": self._gerar_recomendacoes(elementos_qualidade)
        }
    
    def _classificar_qualidade(self, score: float) -> str:
        """Classifica a qualidade da petição."""
        if score >= 90:
            return "Excelente"
        elif score >= 75:
            return "Boa"
        elif score >= 60:
            return "Satisfatória"
        elif score >= 40:
            return "Precisa melhorias"
        else:
            return "Inadequada"
    
    def _gerar_recomendacoes(self, elementos: List[bool]) -> List[str]:
        """Gera recomendações baseadas nos elementos de qualidade."""
        recomendacoes = []
        
        labels = [
            "Incluir mais fundamentação legal específica",
            "Adicionar jurisprudência relevante",
            "Detalhar melhor os pedidos",
            "Especificar o valor da causa",
            "Expandir o conteúdo da petição",
            "Melhorar a estrutura com mais seções"
        ]
        
        for i, presente in enumerate(elementos):
            if not presente:
                recomendacoes.append(labels[i])
        
        if not recomendacoes:
            recomendacoes.append("Petição está bem estruturada")
        
        return recomendacoes

