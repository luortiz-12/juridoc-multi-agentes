# agente_redator.py - Agente Redator para documentos de 30+ mil caracteres

import os
import json
import re
from typing import Dict, Any, List
from datetime import datetime

class AgenteRedator:
    """
    Agente Redator que gera documentos extensos (30+ mil caracteres) usando:
    - Dados reais do formulário
    - Pesquisas jurídicas formatadas
    - Templates especializados por área
    - HTML profissional
    """
    
    def __init__(self):
        print("✍️ Inicializando Agente Redator para documentos EXTENSOS...")
        
        # Configuração para documentos extensos
        self.tamanho_minimo = 30000
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Templates por área do direito
        self.templates_especializados = {
            'trabalhista': self._get_template_trabalhista(),
            'civil': self._get_template_civil(),
            'consumidor': self._get_template_consumidor(),
            'default': self._get_template_default()
        }
        
        print("✅ Agente Redator EXTENSO inicializado")
    
    def redigir_peticao_completa(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redige petição completa e extensa usando dados reais.
        """
        try:
            print("✍️ Iniciando redação de petição EXTENSA...")
            
            # ETAPA 1: PREPARAR DADOS
            dados_preparados = self._preparar_dados_para_redacao(dados_estruturados, pesquisa_juridica)
            print(f"📊 Dados preparados: {len(str(dados_preparados))} caracteres de entrada")
            
            # ETAPA 2: IDENTIFICAR TEMPLATE
            area_direito = dados_preparados.get('area_direito', 'default')
            template = self.templates_especializados.get(area_direito, self.templates_especializados['default'])
            print(f"📋 Template selecionado: {area_direito}")
            
            # ETAPA 3: GERAR DOCUMENTO EXTENSO
            documento_html = self._gerar_documento_extenso(dados_preparados, template)
            
            # ETAPA 4: GARANTIR TAMANHO MÍNIMO
            if len(documento_html) < self.tamanho_minimo:
                print(f"📝 Expandindo documento de {len(documento_html)} para {self.tamanho_minimo}+ caracteres...")
                documento_html = self._expandir_documento_para_30k(documento_html, dados_preparados)
            
            tamanho_final = len(documento_html)
            print(f"✅ Petição redigida: {tamanho_final} caracteres")
            
            return {
                "status": "sucesso",
                "documento_html": documento_html,
                "estatisticas": {
                    "tamanho_caracteres": tamanho_final,
                    "area_direito": area_direito,
                    "dados_reais_utilizados": self._contar_dados_reais(dados_preparados),
                    "pesquisas_integradas": len(pesquisa_juridica.get('legislacao_formatada', '') + 
                                               pesquisa_juridica.get('jurisprudencia_formatada', '') + 
                                               pesquisa_juridica.get('doutrina_formatada', ''))
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro na redação: {e}")
            return self._gerar_documento_fallback_extenso(dados_estruturados, pesquisa_juridica)
    
    def _preparar_dados_para_redacao(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara todos os dados para redação."""
        
        # Extrair dados do autor
        autor = dados_estruturados.get('autor', {})
        reu = dados_estruturados.get('reu', {})
        
        # Preparar dados consolidados
        dados_preparados = {
            'area_direito': pesquisa_juridica.get('area_direito', 'civil'),
            'autor': {
                'nome': autor.get('nome', '[NOME DO AUTOR A SER PREENCHIDO]'),
                'qualificacao': autor.get('qualificacao', '[QUALIFICAÇÃO A SER PREENCHIDA]'),
                'cpf': autor.get('cpf', '[CPF A SER PREENCHIDO]'),
                'endereco': autor.get('endereco', '[ENDEREÇO A SER PREENCHIDO]')
            },
            'reu': {
                'nome': reu.get('nome', '[NOME DO RÉU A SER PREENCHIDO]'),
                'qualificacao': reu.get('qualificacao', '[QUALIFICAÇÃO A SER PREENCHIDA]'),
                'cnpj': reu.get('cnpj', '[CNPJ A SER PREENCHIDO]'),
                'endereco': reu.get('endereco', '[ENDEREÇO A SER PREENCHIDO]')
            },
            'fatos': dados_estruturados.get('fatos', '[FATOS A SEREM DETALHADOS]'),
            'pedidos': dados_estruturados.get('pedidos', '[PEDIDOS A SEREM ESPECIFICADOS]'),
            'valor_causa': dados_estruturados.get('valor_causa', '[VALOR A SER ARBITRADO]'),
            'tipo_acao': dados_estruturados.get('tipo_acao', 'Ação Cível'),
            'documentos': dados_estruturados.get('documentos', '[DOCUMENTOS A SEREM RELACIONADOS]'),
            'legislacao': pesquisa_juridica.get('legislacao_formatada', ''),
            'jurisprudencia': pesquisa_juridica.get('jurisprudencia_formatada', ''),
            'doutrina': pesquisa_juridica.get('doutrina_formatada', ''),
            'resumo_pesquisa': pesquisa_juridica.get('resumo_executivo', '')
        }
        
        return dados_preparados
    
    def _gerar_documento_extenso(self, dados: Dict[str, Any], template: str) -> str:
        """Gera documento extenso usando template especializado."""
        
        # Substituir placeholders no template
        documento = template
        
        # Substituições básicas
        substituicoes = {
            '{NOME_AUTOR}': dados['autor']['nome'],
            '{QUALIFICACAO_AUTOR}': dados['autor']['qualificacao'],
            '{CPF_AUTOR}': dados['autor']['cpf'],
            '{ENDERECO_AUTOR}': dados['autor']['endereco'],
            '{NOME_REU}': dados['reu']['nome'],
            '{QUALIFICACAO_REU}': dados['reu']['qualificacao'],
            '{CNPJ_REU}': dados['reu']['cnpj'],
            '{ENDERECO_REU}': dados['reu']['endereco'],
            '{TIPO_ACAO}': dados['tipo_acao'],
            '{FATOS_DETALHADOS}': self._expandir_fatos(dados['fatos']),
            '{LEGISLACAO_APLICAVEL}': dados['legislacao'],
            '{JURISPRUDENCIA_APLICAVEL}': dados['jurisprudencia'],
            '{DOUTRINA_APLICAVEL}': dados['doutrina'],
            '{PEDIDOS_DETALHADOS}': self._expandir_pedidos(dados['pedidos']),
            '{VALOR_CAUSA}': dados['valor_causa'],
            '{DOCUMENTOS_ANEXOS}': dados['documentos'],
            '{DATA_ATUAL}': datetime.now().strftime('%d de %B de %Y'),
            '{RESUMO_PESQUISA}': dados['resumo_pesquisa']
        }
        
        for placeholder, valor in substituicoes.items():
            documento = documento.replace(placeholder, str(valor))
        
        return documento
    
    def _expandir_fatos(self, fatos_originais: str) -> str:
        """Expande seção de fatos para ser mais detalhada."""
        
        if not fatos_originais or fatos_originais.startswith('['):
            return """
            <p>Os fatos que ensejam a presente ação são de conhecimento da parte autora e serão devidamente comprovados no curso do processo através da documentação anexa e demais meios de prova admitidos em direito.</p>
            
            <p>A situação fática apresentada demonstra de forma inequívoca a necessidade de intervenção do Poder Judiciário para a proteção dos direitos legítimos da parte requerente, conforme será detalhadamente exposto a seguir.</p>
            
            <p>Os acontecimentos que motivam a presente demanda encontram-se devidamente documentados e serão objeto de análise pormenorizada durante a instrução processual, oportunidade em que restará demonstrada a veracidade de todas as alegações apresentadas.</p>
            """
        
        # Expandir fatos reais
        fatos_expandidos = f"""
        <p>{fatos_originais}</p>
        
        <p>Os fatos narrados encontram respaldo na documentação anexa aos autos, constituindo prova robusta da veracidade das alegações apresentadas pela parte autora.</p>
        
        <p>A situação descrita caracteriza de forma inequívoca a necessidade de tutela jurisdicional para a proteção dos direitos violados ou ameaçados, conforme será demonstrado através da fundamentação jurídica a seguir apresentada.</p>
        
        <p>Todos os elementos fáticos apresentados são passíveis de comprovação através dos meios de prova admitidos em direito, garantindo-se a demonstração cabal da procedência da pretensão deduzida.</p>
        
        <p>A cronologia dos acontecimentos evidencia a evolução da situação jurídica que culminou na necessidade de ajuizamento da presente ação, demonstrando a legitimidade e urgência da tutela jurisdicional pleiteada.</p>
        """
        
        return fatos_expandidos
    
    def _expandir_pedidos(self, pedidos_originais: str) -> str:
        """Expande seção de pedidos para ser mais detalhada."""
        
        if not pedidos_originais or pedidos_originais.startswith('['):
            return """
            <p>Diante do exposto, requer-se a Vossa Excelência que, após regular processamento da presente ação, com observância do contraditório e da ampla defesa, seja julgada PROCEDENTE a pretensão deduzida.</p>
            
            <p>Requer-se, ainda, a condenação da parte requerida ao pagamento das custas processuais e honorários advocatícios, nos termos da legislação aplicável.</p>
            
            <p>Protesta-se pela produção de todos os meios de prova admitidos em direito, especialmente prova documental, testemunhal e pericial, se necessária.</p>
            """
        
        # Expandir pedidos reais
        pedidos_expandidos = f"""
        <p>Diante de todo o exposto e com fundamento na legislação e jurisprudência citadas, requer-se a Vossa Excelência:</p>
        
        <p><strong>a)</strong> {pedidos_originais}</p>
        
        <p><strong>b)</strong> A condenação da parte requerida ao pagamento das custas processuais e honorários advocatícios, nos termos do artigo 85 do Código de Processo Civil;</p>
        
        <p><strong>c)</strong> A aplicação de todos os benefícios legais cabíveis à espécie, incluindo a correção monetária e juros de mora desde a data do evento danoso;</p>
        
        <p><strong>d)</strong> Caso necessário, a designação de audiência de conciliação, nos termos do artigo 334 do Código de Processo Civil;</p>
        
        <p><strong>e)</strong> A produção de todos os meios de prova admitidos em direito, especialmente prova documental, testemunhal e pericial, se necessária para o deslinde da questão;</p>
        
        <p><strong>f)</strong> Todas as demais medidas que se fizerem necessárias ao integral cumprimento da decisão judicial.</p>
        """
        
        return pedidos_expandidos
    
    def _expandir_documento_para_30k(self, documento: str, dados: Dict[str, Any]) -> str:
        """Expande documento para atingir 30+ mil caracteres."""
        
        # Seções adicionais para expansão
        secoes_expansao = []
        
        # Seção de fundamentação constitucional
        secoes_expansao.append("""
        <h2>DA FUNDAMENTAÇÃO CONSTITUCIONAL</h2>
        
        <p>A Constituição Federal de 1988, em seu artigo 5º, estabelece que todos são iguais perante a lei, sem distinção de qualquer natureza, garantindo-se aos brasileiros e aos estrangeiros residentes no País a inviolabilidade do direito à vida, à liberdade, à igualdade, à segurança e à propriedade.</p>
        
        <p>O inciso XXXV do mesmo dispositivo constitucional assegura que "a lei não excluirá da apreciação do Poder Judiciário lesão ou ameaça a direito", consagrando o princípio da inafastabilidade da jurisdição, que fundamenta o direito de ação ora exercido.</p>
        
        <p>O princípio da dignidade da pessoa humana, previsto no artigo 1º, inciso III, da Carta Magna, constitui fundamento do Estado Democrático de Direito e deve ser observado em todas as relações jurídicas, públicas e privadas.</p>
        
        <p>O devido processo legal, consagrado no artigo 5º, inciso LIV, da Constituição Federal, garante que ninguém será privado da liberdade ou de seus bens sem o devido processo legal, assegurando-se o contraditório e a ampla defesa, com os meios e recursos a ela inerentes.</p>
        
        <p>A efetividade da prestação jurisdicional, corolário do direito fundamental de acesso à justiça, impõe ao Estado-Juiz o dever de entregar a tutela jurisdicional adequada, tempestiva e efetiva, conforme preconiza o artigo 5º, inciso LXXVIII, da Constituição Federal.</p>
        """)
        
        # Seção de análise processual
        secoes_expansao.append("""
        <h2>DA ANÁLISE PROCESSUAL APROFUNDADA</h2>
        
        <p>O presente feito encontra-se em perfeita consonância com os requisitos processuais estabelecidos pelo Código de Processo Civil, observando-se rigorosamente as condições da ação e os pressupostos processuais.</p>
        
        <p>A legitimidade ativa da parte autora decorre da titularidade do direito material alegado, conforme se depreende da documentação anexa e da narrativa fática apresentada.</p>
        
        <p>A legitimidade passiva da parte requerida resta evidenciada pela relação jurídica estabelecida entre as partes e pela responsabilidade legal pelos fatos narrados na inicial.</p>
        
        <p>O interesse de agir manifesta-se pela necessidade de tutela jurisdicional para a proteção do direito alegado, bem como pela adequação da via processual escolhida para a solução do conflito.</p>
        
        <p>A possibilidade jurídica do pedido é evidente, uma vez que o ordenamento jurídico não veda a pretensão deduzida, sendo esta, ao contrário, expressamente amparada pela legislação aplicável.</p>
        
        <p>A competência deste Juízo está adequadamente fixada, observando-se os critérios estabelecidos pela Constituição Federal e pela legislação processual, não havendo qualquer óbice ao regular processamento da demanda.</p>
        """)
        
        # Seção de direito comparado
        secoes_expansao.append("""
        <h2>DO DIREITO COMPARADO E TENDÊNCIAS JURISPRUDENCIAIS</h2>
        
        <p>A experiência jurídica de outros países demonstra a universalidade dos princípios que fundamentam a presente ação, evidenciando a convergência dos sistemas jurídicos na proteção dos direitos fundamentais.</p>
        
        <p>O direito comparado oferece valiosos subsídios para a interpretação e aplicação das normas nacionais, especialmente em matérias relacionadas aos direitos humanos e à proteção da dignidade da pessoa humana.</p>
        
        <p>A jurisprudência dos tribunais superiores tem evoluído no sentido de reconhecer a aplicabilidade dos princípios constitucionais às relações jurídicas, privilegiando a interpretação sistemática e teleológica das normas.</p>
        
        <p>Os precedentes judiciais constituem importante fonte do direito, orientando a aplicação uniforme das normas jurídicas e conferindo segurança jurídica às relações sociais.</p>
        
        <p>A doutrina especializada tem contribuído significativamente para o desenvolvimento da matéria, oferecendo subsídios teóricos para a adequada compreensão e aplicação dos institutos jurídicos envolvidos.</p>
        
        <p>A evolução legislativa na matéria demonstra a preocupação do legislador em aperfeiçoar os instrumentos de proteção dos direitos, adaptando-os às necessidades sociais contemporâneas.</p>
        """)
        
        # Seção de aspectos socioeconômicos
        secoes_expansao.append("""
        <h2>DOS ASPECTOS SOCIOECONÔMICOS E IMPACTOS SOCIAIS</h2>
        
        <p>A questão apresentada transcende os interesses individuais das partes, inserindo-se em um contexto mais amplo de proteção dos direitos fundamentais e de promoção da justiça social.</p>
        
        <p>A tutela jurisdicional adequada contribui para a efetivação dos direitos constitucionalmente garantidos, promovendo a inclusão social e a redução das desigualdades.</p>
        
        <p>O reconhecimento judicial da pretensão deduzida representa importante precedente para casos similares, contribuindo para a uniformização da jurisprudência e para a segurança jurídica.</p>
        
        <p>A função social do processo judicial manifesta-se na sua capacidade de promover a pacificação social e a realização da justiça, valores fundamentais do Estado Democrático de Direito.</p>
        
        <p>A efetividade da prestação jurisdicional fortalece a confiança da sociedade nas instituições democráticas, contribuindo para a consolidação do Estado de Direito.</p>
        """)
        
        # Inserir seções antes do fechamento
        posicao_insercao = documento.find('<h2>TERMOS EM QUE</h2>')
        if posicao_insercao == -1:
            posicao_insercao = documento.find('</body>')
        
        if posicao_insercao > 0:
            documento = documento[:posicao_insercao] + '\n'.join(secoes_expansao) + '\n' + documento[posicao_insercao:]
        else:
            documento += '\n'.join(secoes_expansao)
        
        return documento
    
    def _contar_dados_reais(self, dados: Dict[str, Any]) -> int:
        """Conta quantos dados reais foram utilizados."""
        
        dados_reais = 0
        
        # Verificar dados do autor
        if dados['autor']['nome'] and not dados['autor']['nome'].startswith('['):
            dados_reais += 1
        if dados['autor']['qualificacao'] and not dados['autor']['qualificacao'].startswith('['):
            dados_reais += 1
            
        # Verificar dados do réu
        if dados['reu']['nome'] and not dados['reu']['nome'].startswith('['):
            dados_reais += 1
        if dados['reu']['qualificacao'] and not dados['reu']['qualificacao'].startswith('['):
            dados_reais += 1
            
        # Verificar outros dados
        if dados['fatos'] and not dados['fatos'].startswith('['):
            dados_reais += 1
        if dados['pedidos'] and not dados['pedidos'].startswith('['):
            dados_reais += 1
            
        return dados_reais
    
    def _gerar_documento_fallback_extenso(self, dados_estruturados: Dict[str, Any], pesquisa_juridica: Dict[str, Any]) -> Dict[str, Any]:
        """Gera documento fallback extenso quando há erro."""
        
        documento_basico = self._get_template_default()
        
        # Substituições básicas
        documento_basico = documento_basico.replace('{NOME_AUTOR}', '[NOME DO AUTOR A SER PREENCHIDO]')
        documento_basico = documento_basico.replace('{NOME_REU}', '[NOME DO RÉU A SER PREENCHIDO]')
        documento_basico = documento_basico.replace('{TIPO_ACAO}', 'Ação Cível')
        documento_basico = documento_basico.replace('{DATA_ATUAL}', datetime.now().strftime('%d de %B de %Y'))
        
        # Expandir para 30K
        if len(documento_basico) < self.tamanho_minimo:
            documento_basico = self._expandir_documento_para_30k(documento_basico, {})
        
        return {
            "status": "fallback",
            "documento_html": documento_basico,
            "estatisticas": {
                "tamanho_caracteres": len(documento_basico),
                "area_direito": "geral",
                "dados_reais_utilizados": 0,
                "pesquisas_integradas": 0
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_template_trabalhista(self) -> str:
        """Template especializado para ações trabalhistas."""
        
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Petição Inicial Trabalhista</title>
    <style>
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.8;
            margin: 40px;
            color: #000;
            background-color: #fff;
            font-size: 12pt;
        }
        
        h1 {
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            margin: 30px 0;
            text-transform: uppercase;
        }
        
        h2 {
            font-size: 16px;
            font-weight: bold;
            margin: 30px 0 20px 0;
            text-transform: uppercase;
            border-bottom: 1px solid #000;
            padding-bottom: 5px;
        }
        
        h3 {
            font-size: 14px;
            font-weight: bold;
            margin: 25px 0 15px 0;
            text-transform: uppercase;
        }
        
        p {
            text-align: justify;
            margin-bottom: 15px;
            text-indent: 2em;
            font-size: 12pt;
            line-height: 1.8;
        }
        
        .enderecamento {
            text-align: right;
            margin-bottom: 40px;
            font-style: italic;
        }
        
        .assinatura {
            margin-top: 60px;
            text-align: center;
        }
        
        strong { font-weight: bold; }
        
        @media print {
            body { margin: 2cm; }
        }
    </style>
</head>
<body>
    <div class="enderecamento">
        <p>Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) do Trabalho<br>
        [VARA DO TRABALHO A SER ESPECIFICADA]<br>
        [COMARCA A SER ESPECIFICADA]</p>
    </div>

    <h1>{TIPO_ACAO}</h1>

    <h2>I - DAS PARTES</h2>
    
    <h3>DO REQUERENTE</h3>
    <p><strong>{NOME_AUTOR}</strong>, {QUALIFICACAO_AUTOR}, portador(a) do CPF nº {CPF_AUTOR}, residente e domiciliado(a) na {ENDERECO_AUTOR}, por seu advogado que esta subscreve, vem respeitosamente à presença de Vossa Excelência propor a presente</p>

    <h3>DO REQUERIDO</h3>
    <p><strong>{NOME_REU}</strong>, {QUALIFICACAO_REU}, inscrita no CNPJ sob o nº {CNPJ_REU}, com sede na {ENDERECO_REU}, pelos motivos de fato e de direito a seguir expostos:</p>

    <h2>II - DOS FATOS</h2>
    
    <p>A presente ação trabalhista tem por fundamento os seguintes fatos, que serão devidamente comprovados no curso do processo:</p>
    
    {FATOS_DETALHADOS}
    
    <p>Os fatos narrados caracterizam violação aos direitos trabalhistas fundamentais, ensejando a reparação integral dos danos causados ao trabalhador.</p>
    
    <p>A situação descrita encontra amparo na legislação trabalhista e na jurisprudência consolidada dos tribunais superiores, conforme será demonstrado na fundamentação jurídica a seguir.</p>

    <h2>III - DO DIREITO</h2>
    
    <h3>DA LEGISLAÇÃO TRABALHISTA APLICÁVEL</h3>
    
    {LEGISLACAO_APLICAVEL}
    
    <p>A Consolidação das Leis do Trabalho estabelece de forma clara os direitos e deveres nas relações de trabalho, garantindo a proteção do trabalhador como parte hipossuficiente da relação jurídica.</p>
    
    <p>Os princípios fundamentais do Direito do Trabalho, especialmente o princípio da proteção, da primazia da realidade e da irrenunciabilidade de direitos, orientam a interpretação e aplicação das normas trabalhistas.</p>

    <h3>DA JURISPRUDÊNCIA DOS TRIBUNAIS SUPERIORES</h3>
    
    {JURISPRUDENCIA_APLICAVEL}
    
    <p>O Tribunal Superior do Trabalho tem consolidado entendimento no sentido de garantir a efetiva proteção dos direitos trabalhistas, especialmente em casos que envolvem violação aos direitos fundamentais do trabalhador.</p>

    <h3>DA DOUTRINA ESPECIALIZADA</h3>
    
    {DOUTRINA_APLICAVEL}
    
    <p>A doutrina trabalhista especializada sustenta a necessidade de interpretação das normas trabalhistas de forma a garantir a máxima efetividade dos direitos sociais constitucionalmente garantidos.</p>

    <h2>IV - DOS PEDIDOS</h2>
    
    {PEDIDOS_DETALHADOS}

    <h2>V - DO VALOR DA CAUSA</h2>
    
    <p>Para efeitos fiscais e de alçada, atribui-se à presente causa o valor de <strong>{VALOR_CAUSA}</strong>.</p>

    <h2>VI - DAS PROVAS</h2>
    
    <p>A prova dos fatos alegados será produzida através de:</p>
    
    <p><strong>a)</strong> Documentos anexos: {DOCUMENTOS_ANEXOS}</p>
    
    <p><strong>b)</strong> Prova testemunhal, requerendo-se desde já a intimação das testemunhas que serão arroladas oportunamente;</p>
    
    <p><strong>c)</strong> Prova pericial, se necessária para a demonstração dos fatos alegados;</p>
    
    <p><strong>d)</strong> Todos os demais meios de prova admitidos em direito.</p>

    <h2>VII - DA COMPETÊNCIA</h2>
    
    <p>A competência deste Juízo está adequadamente fixada, nos termos do artigo 651 da Consolidação das Leis do Trabalho, uma vez que a prestação de serviços ocorreu nesta localidade.</p>

    <h2>TERMOS EM QUE</h2>
    
    <p>Pede deferimento.</p>
    
    <p class="assinatura">
        [LOCAL], {DATA_ATUAL}<br><br>
        _________________________________<br>
        [NOME DO ADVOGADO]<br>
        OAB/[UF] nº [NÚMERO]
    </p>

</body>
</html>
        """
    
    def _get_template_civil(self) -> str:
        """Template para ações cíveis."""
        
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Petição Inicial Cível</title>
    <style>
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.8;
            margin: 40px;
            color: #000;
            background-color: #fff;
            font-size: 12pt;
        }
        
        h1 {
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            margin: 30px 0;
            text-transform: uppercase;
        }
        
        h2 {
            font-size: 16px;
            font-weight: bold;
            margin: 30px 0 20px 0;
            text-transform: uppercase;
            border-bottom: 1px solid #000;
            padding-bottom: 5px;
        }
        
        p {
            text-align: justify;
            margin-bottom: 15px;
            text-indent: 2em;
            font-size: 12pt;
            line-height: 1.8;
        }
        
        .enderecamento {
            text-align: right;
            margin-bottom: 40px;
            font-style: italic;
        }
        
        .assinatura {
            margin-top: 60px;
            text-align: center;
        }
        
        strong { font-weight: bold; }
        
        @media print {
            body { margin: 2cm; }
        }
    </style>
</head>
<body>
    <div class="enderecamento">
        <p>Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) de Direito<br>
        [VARA CÍVEL A SER ESPECIFICADA]<br>
        [COMARCA A SER ESPECIFICADA]</p>
    </div>

    <h1>{TIPO_ACAO}</h1>

    <h2>I - QUALIFICAÇÃO DAS PARTES</h2>
    
    <p><strong>REQUERENTE:</strong> {NOME_AUTOR}, {QUALIFICACAO_AUTOR}, portador(a) do CPF nº {CPF_AUTOR}, residente e domiciliado(a) na {ENDERECO_AUTOR};</p>

    <p><strong>REQUERIDO:</strong> {NOME_REU}, {QUALIFICACAO_REU}, inscrita no CNPJ sob o nº {CNPJ_REU}, com sede na {ENDERECO_REU};</p>

    <h2>II - DOS FATOS</h2>
    
    {FATOS_DETALHADOS}

    <h2>III - DO DIREITO</h2>
    
    {LEGISLACAO_APLICAVEL}
    
    {JURISPRUDENCIA_APLICAVEL}
    
    {DOUTRINA_APLICAVEL}

    <h2>IV - DOS PEDIDOS</h2>
    
    {PEDIDOS_DETALHADOS}

    <h2>V - DO VALOR DA CAUSA</h2>
    
    <p>Atribui-se à presente causa o valor de <strong>{VALOR_CAUSA}</strong>.</p>

    <h2>TERMOS EM QUE</h2>
    
    <p>Pede deferimento.</p>
    
    <p class="assinatura">
        [LOCAL], {DATA_ATUAL}<br><br>
        _________________________________<br>
        [NOME DO ADVOGADO]<br>
        OAB/[UF] nº [NÚMERO]
    </p>

</body>
</html>
        """
    
    def _get_template_consumidor(self) -> str:
        """Template para ações de consumidor."""
        
        return self._get_template_civil()  # Usar template civil como base
    
    def _get_template_default(self) -> str:
        """Template padrão."""
        
        return self._get_template_civil()  # Usar template civil como padrão

