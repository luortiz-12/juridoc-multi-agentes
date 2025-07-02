# agente_redator.py - Agente Redator Especializado em Petições

import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

class AgenteRedator:
    """
    Agente especializado na redação de petições iniciais com base em dados
    estruturados e pesquisa jurídica realizada.
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            openai_api_key=openai_api_key, 
            temperature=0.2
        )
        
        # Template principal para redação de petições
        self.prompt_peticao = PromptTemplate(
            input_variables=["dados_estruturados", "pesquisa_juridica"],
            template="""
            Você é um advogado processualista sênior com vasta experiência em redação de petições iniciais.
            
            DADOS ESTRUTURADOS DO CASO:
            {dados_estruturados}
            
            FUNDAMENTAÇÃO JURÍDICA PESQUISADA:
            {pesquisa_juridica}
            
            TAREFA: Redija uma petição inicial completa e profissional em HTML, seguindo rigorosamente a estrutura formal brasileira.
            
            ESTRUTURA OBRIGATÓRIA DA PETIÇÃO:
            
            1. ENDEREÇAMENTO
            - Dirigir ao Excelentíssimo Senhor Doutor Juiz de Direito
            - Mencionar a vara/comarca competente
            
            2. QUALIFICAÇÃO DAS PARTES
            - Autor: nome completo, nacionalidade, estado civil, profissão, CPF, endereço
            - Réu: nome completo, qualificação, CPF/CNPJ, endereço
            
            3. TÍTULO DA AÇÃO
            - Nome da ação de forma clara e específica
            
            4. DOS FATOS (seção <h2>)
            - Narrativa cronológica e clara dos fatos
            - Incluir datas, valores e circunstâncias relevantes
            - Mencionar documentos que comprovam os fatos
            
            5. DO DIREITO (seção <h2>)
            - Fundamentação legal baseada na pesquisa realizada
            - Citar leis, artigos específicos
            - Incluir jurisprudência relevante encontrada
            - Mencionar doutrina quando aplicável
            - Argumentação jurídica sólida
            
            6. DOS PEDIDOS (seção <h2>)
            - Pedidos principais de forma clara e específica
            - Pedidos alternativos se houver
            - Pedidos cautelares se aplicável
            - Condenação em honorários advocatícios e custas
            
            7. DO VALOR DA CAUSA
            - Especificar o valor da causa
            
            8. REQUERIMENTOS FINAIS
            - Citação do réu
            - Procedência dos pedidos
            - Outros requerimentos processuais
            
            9. TERMOS EM QUE
            - Fórmula de encerramento formal
            
            10. LOCAL, DATA E ASSINATURA
            - Cidade, data
            - Espaço para assinatura do advogado
            - Placeholder para nome e OAB
            
            REGRAS DE REDAÇÃO:
            
            1. LINGUAGEM TÉCNICA: Use linguagem jurídica formal e técnica
            2. FUNDAMENTAÇÃO SÓLIDA: Base todos os argumentos na pesquisa jurídica fornecida
            3. PLACEHOLDERS INTELIGENTES: Para informações não fornecidas, use placeholders claros:
               - [NOME DO ADVOGADO]
               - [OAB/UF]
               - [ENDEREÇO COMPLETO]
               - [TELEFONE]
               - [EMAIL]
               - [CIDADE]
               - [DATA]
            4. CITAÇÕES LEGAIS: Cite especificamente as leis e artigos encontrados na pesquisa
            5. JURISPRUDÊNCIA: Inclua as decisões judiciais relevantes da pesquisa
            6. ESTRUTURA HTML: Use tags semânticas (<h1>, <h2>, <p>, <strong>, <em>)
            7. FORMATAÇÃO: Mantenha formatação profissional e legível
            8. COMPLETUDE: A petição deve estar completa e pronta para protocolo
            
            EXEMPLO DE CITAÇÃO LEGAL:
            "Conforme dispõe o artigo 927 do Código Civil..."
            "Nesse sentido, o Superior Tribunal de Justiça..."
            "A doutrina de [autor] ensina que..."
            
            FORMATO DE SAÍDA: HTML puro, começando com <h1> e sem tags <html>, <head> ou <body>.
            
            IMPORTANTE: A petição deve ser profissional, completa e baseada integralmente na fundamentação jurídica pesquisada.
            """
        )
        
        # Template para revisão e melhoria
        self.prompt_revisao = PromptTemplate(
            input_variables=["peticao_inicial", "pontos_melhoria"],
            template="""
            Você é um advogado revisor especializado em aperfeiçoar petições iniciais.
            
            PETIÇÃO PARA REVISÃO:
            {peticao_inicial}
            
            PONTOS DE MELHORIA IDENTIFICADOS:
            {pontos_melhoria}
            
            TAREFA: Revise e aprimore a petição, corrigindo os pontos identificados e melhorando:
            
            1. CLAREZA: Torne a linguagem mais clara e objetiva
            2. FUNDAMENTAÇÃO: Fortaleça a argumentação jurídica
            3. ESTRUTURA: Melhore a organização e fluxo do texto
            4. TÉCNICA: Aperfeiçoe a técnica processual
            5. COMPLETUDE: Garanta que nada importante foi omitido
            
            REGRAS:
            - Mantenha a estrutura HTML original
            - Preserve todas as citações legais e jurisprudência
            - Melhore sem alterar o sentido original
            - Mantenha placeholders onde necessário
            
            FORMATO: HTML puro, versão melhorada da petição.
            """
        )
        
        self.chain_peticao = LLMChain(llm=self.llm, prompt=self.prompt_peticao)
        self.chain_revisao = LLMChain(llm=self.llm, prompt=self.prompt_revisao)
    
    def redigir_peticao(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal para redigir uma petição inicial.
        
        Args:
            dados_estruturados: Dados processados pelo agente coletor
            pesquisa_juridica: Resultados da pesquisa jurídica
            
        Returns:
            Dict com a petição redigida e metadados
        """
        try:
            print("✍️ Iniciando redação da petição...")
            
            # Etapa 1: Redação inicial
            peticao_inicial = self._redigir_versao_inicial(dados_estruturados, pesquisa_juridica)
            
            # Etapa 2: Análise de qualidade
            pontos_melhoria = self._analisar_qualidade(peticao_inicial, dados_estruturados)
            
            # Etapa 3: Revisão e melhoria (se necessário)
            peticao_final = self._revisar_se_necessario(peticao_inicial, pontos_melhoria)
            
            # Etapa 4: Validação final
            resultado = self._validar_peticao_final(peticao_final, dados_estruturados)
            
            print("✅ Petição redigida com sucesso")
            return resultado
            
        except Exception as e:
            print(f"❌ Erro na redação da petição: {e}")
            return {
                "status": "erro",
                "mensagem": f"Erro na redação: {str(e)}",
                "peticao_html": self._gerar_peticao_erro(dados_estruturados, str(e))
            }
    
    def _redigir_versao_inicial(self, dados: Dict[str, Any], pesquisa: Dict[str, Any]) -> str:
        """Redige a versão inicial da petição."""
        try:
            dados_formatados = json.dumps(dados, indent=2, ensure_ascii=False)
            pesquisa_formatada = json.dumps(pesquisa, indent=2, ensure_ascii=False)
            
            peticao = self.chain_peticao.run(
                dados_estruturados=dados_formatados,
                pesquisa_juridica=pesquisa_formatada
            )
            
            return peticao
            
        except Exception as e:
            print(f"⚠️ Erro na redação inicial: {e}")
            return self._gerar_peticao_basica(dados)
    
    def _analisar_qualidade(self, peticao: str, dados: Dict[str, Any]) -> List[str]:
        """Analisa a qualidade da petição e identifica pontos de melhoria."""
        pontos_melhoria = []
        
        # Verificar se tem as seções obrigatórias
        secoes_obrigatorias = ["DOS FATOS", "DO DIREITO", "DOS PEDIDOS"]
        for secao in secoes_obrigatorias:
            if secao not in peticao.upper():
                pontos_melhoria.append(f"Adicionar seção '{secao}'")
        
        # Verificar se tem fundamentação legal
        if "artigo" not in peticao.lower() and "lei" not in peticao.lower():
            pontos_melhoria.append("Incluir mais fundamentação legal específica")
        
        # Verificar se tem citações jurisprudenciais
        tribunais = ["STF", "STJ", "TRIBUNAL", "ACÓRDÃO"]
        if not any(tribunal in peticao.upper() for tribunal in tribunais):
            pontos_melhoria.append("Incluir jurisprudência relevante")
        
        # Verificar se tem pedidos específicos
        if "PEDIDOS" in peticao.upper() and len(peticao.split("PEDIDOS")[1]) < 200:
            pontos_melhoria.append("Detalhar melhor os pedidos")
        
        # Verificar se tem valor da causa
        if "VALOR DA CAUSA" not in peticao.upper():
            pontos_melhoria.append("Incluir seção do valor da causa")
        
        return pontos_melhoria
    
    def _revisar_se_necessario(self, peticao: str, pontos_melhoria: List[str]) -> str:
        """Revisa a petição se houver pontos de melhoria significativos."""
        if len(pontos_melhoria) <= 2:  # Poucos pontos, não precisa revisar
            return peticao
        
        try:
            print(f"🔍 Revisando petição ({len(pontos_melhoria)} pontos de melhoria)")
            pontos_formatados = "\n".join([f"- {ponto}" for ponto in pontos_melhoria])
            
            peticao_revisada = self.chain_revisao.run(
                peticao_inicial=peticao,
                pontos_melhoria=pontos_formatados
            )
            
            return peticao_revisada
            
        except Exception as e:
            print(f"⚠️ Erro na revisão: {e}")
            return peticao  # Retorna versão original se revisão falhar
    
    def _validar_peticao_final(self, peticao: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Validação final da petição."""
        # Verificar se é HTML válido básico
        if not peticao.strip().startswith('<'):
            peticao = f"<div>{peticao}</div>"
        
        # Calcular estatísticas
        palavras = len(peticao.split())
        caracteres = len(peticao)
        
        # Verificar completude
        completude = self._calcular_completude(peticao)
        
        return {
            "status": "sucesso",
            "peticao_html": peticao,
            "estatisticas": {
                "palavras": palavras,
                "caracteres": caracteres,
                "completude": completude
            },
            "metadados": {
                "tipo_documento": "Petição Inicial",
                "autor": dados.get("autor", {}).get("nome", "Não informado"),
                "reu": dados.get("reu", {}).get("nome", "Não informado"),
                "tipo_acao": dados.get("tipo_acao", "Não especificado")
            }
        }
    
    def _calcular_completude(self, peticao: str) -> float:
        """Calcula um score de completude da petição."""
        elementos_essenciais = [
            "PETIÇÃO INICIAL",
            "DOS FATOS",
            "DO DIREITO", 
            "DOS PEDIDOS",
            "VALOR DA CAUSA",
            "artigo",
            "lei",
            "código"
        ]
        
        elementos_presentes = sum(1 for elemento in elementos_essenciais 
                                if elemento.lower() in peticao.lower())
        
        return (elementos_presentes / len(elementos_essenciais)) * 100
    
    def _gerar_peticao_basica(self, dados: Dict[str, Any]) -> str:
        """Gera uma petição básica em caso de erro no LLM."""
        autor = dados.get("autor", {})
        reu = dados.get("reu", {})
        tipo_acao = dados.get("tipo_acao", "Ação")
        fatos = dados.get("fatos", {}).get("resumo", "Fatos não especificados")
        pedidos = dados.get("pedidos", {}).get("principais", ["Pedido não especificado"])
        valor_causa = dados.get("valor_causa", "A ser arbitrado")
        
        return f"""
        <h1>PETIÇÃO INICIAL</h1>
        
        <p>Excelentíssimo Senhor Doutor Juiz de Direito da {dados.get('competencia', 'Vara Competente')}</p>
        
        <p><strong>{autor.get('nome', '[NOME DO AUTOR]')}</strong>, {autor.get('tipo_pessoa', 'pessoa física')}, 
        portador do CPF/CNPJ {autor.get('cpf_cnpj', '[CPF/CNPJ]')}, residente e domiciliado em 
        {autor.get('endereco', '[ENDEREÇO]')}, vem respeitosamente à presença de Vossa Excelência, 
        por intermédio de seu advogado que esta subscreve, propor a presente</p>
        
        <h1>{tipo_acao.upper()}</h1>
        
        <p>em face de <strong>{reu.get('nome', '[NOME DO RÉU]')}</strong>, 
        {reu.get('tipo_pessoa', 'pessoa física')}, portador do CPF/CNPJ {reu.get('cpf_cnpj', '[CPF/CNPJ]')}, 
        com endereço em {reu.get('endereco', '[ENDEREÇO]')}, pelos fatos e fundamentos jurídicos a seguir expostos:</p>
        
        <h2>DOS FATOS</h2>
        <p>{fatos}</p>
        
        <h2>DO DIREITO</h2>
        <p>O presente caso encontra amparo legal no ordenamento jurídico brasileiro, 
        conforme será demonstrado a seguir.</p>
        
        <h2>DOS PEDIDOS</h2>
        <p>Diante do exposto, requer-se:</p>
        <ul>
        {"".join([f"<li>{pedido}</li>" for pedido in pedidos])}
        </ul>
        
        <p><strong>DO VALOR DA CAUSA:</strong> {valor_causa}</p>
        
        <p>Termos em que pede deferimento.</p>
        
        <p>[CIDADE], [DATA]</p>
        
        <p>_________________________<br>
        [NOME DO ADVOGADO]<br>
        OAB/[UF] [NÚMERO]</p>
        """
    
    def _gerar_peticao_erro(self, dados: Dict[str, Any], erro: str) -> str:
        """Gera uma petição de erro quando tudo falha."""
        return f"""
        <h1>PETIÇÃO INICIAL</h1>
        <p><strong>ERRO NA GERAÇÃO:</strong> {erro}</p>
        <p>Dados recebidos: {json.dumps(dados, indent=2, ensure_ascii=False)}</p>
        <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
        """

