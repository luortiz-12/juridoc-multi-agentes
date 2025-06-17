# Agente de Formatação Final

"""
Este script implementa o Agente de Formatação Final, responsável por aplicar o layout,
numeração, cabeçalho, rodapé e outros elementos visuais ao documento jurídico gerado.
"""

import json
from datetime import datetime

class AgenteFormatacaoFinal:
    def __init__(self):
        pass # Não precisa de LLM API Key aqui, pois não interage com LLMs

    def formatar_documento(self, documento_texto: str, dados_processados: dict) -> str:
        """Aplica a formatação final ao documento, incluindo cabeçalho, rodapé e estilos HTML/CSS."""
        
        # Extrair informações para o rodapé, usando .get() para segurança
        contratante_nome = dados_processados.get("contratante_nome", "")
        contratante_cpf = dados_processados.get("contratante_cpf", "")
        
        # Para petições, 'contratado' seria a 'parte contrária'
        # Em um sistema mais complexo, você pode precisar de lógica condicional aqui
        # baseada em tipo_documento para usar os nomes corretos (requerente/requerido, autor/réu)
        contratado_nome = dados_processados.get("contratado_nome", "") # Nome genérico para "segunda parte"
        contratado_cpf = dados_processados.get("contratado_cpf", "")   # CPF genérico para "segunda parte"

        # Obter a data atual para o rodapé
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        # Tenta pegar a cidade do foro de eleição, ou usa "Local" como padrão
        cidade = dados_processados.get("foro_eleicao", "Local").split(',')[0].strip()
        if not cidade: # Caso a string esteja vazia após split/strip
            cidade = "Local"


        # Construir o rodapé HTML
        # Apenas inclui contratante e contratado se os nomes estiverem presentes
        rodape_html_partes = ""
        if contratante_nome:
            rodape_html_partes += f'<p style="font-size: 15px;"><strong>{contratante_nome}</strong>'
            if contratante_cpf:
                rodape_html_partes += f'<br>CPF: {contratante_cpf}'
            rodape_html_partes += '</p>\n'
        
        # Adiciona o contratado/segunda parte apenas se houver nome e for diferente do contratante
        # Isso evita duplicar info em casos onde o mesmo é contratante e contratado (improvável em juridico, mas defensivo)
        if contratado_nome and contratado_nome != contratante_nome:
            rodape_html_partes += f'<p style="font-size: 15px;"><strong>{contratado_nome}</strong>'
            if contratado_cpf:
                rodape_html_partes += f'<br>CPF: {contratado_cpf}'
            rodape_html_partes += '</p>\n'
        
        rodape_final = f"""
<p style="font-size: 15px; margin-top: 30px;">{cidade}, {data_atual}</p>
{rodape_html_partes}
"""

        # Aplicar estilos HTML/CSS
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Documento Jurídico Gerado</title>
<style>
    body {{
        font-family: 'Times New Roman', serif;
        font-size: 12pt;
        line-height: 1.5;
        margin: 2.5cm; /* Margens padrão ABNT */
    }}
    h1 {{
        font-family: Arial, sans-serif;
        font-size: 16pt;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1em;
    }}
    h2 {{
        font-family: Arial, sans-serif;
        font-size: 14pt;
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }}
    p {{
        margin-bottom: 1em; /* Espaçamento entre parágrafos */
        text-align: justify; /* Justifica o texto do parágrafo */
    }}
    /* Para subcláusulas numeradas (ex: 1.1, 1.2), o redator deve usar <p> e talvez <span>
       com indentação se o LLM conseguir. Caso contrário, seria mais complexo com CSS. */
    .notas-rodape {{
        font-family: Arial, sans-serif;
        font-size: 10pt;
        font-style: italic;
        /* Alinhamento não especificado no prompt original, geralmente justificado ou à esquerda */
    }}
    .rodape {{
        font-family: Arial, sans-serif;
        font-size: 10pt; /* No prompt original está 15px para o texto do rodapé. Ajustado para 10pt aqui para consistência com as notas de rodapé no prompt do n8n. Mantenha 15px se preferir. */
        text-align: left; /* Alinhamento do rodapé pode ser à esquerda */
        margin-top: 50px; /* Espaçamento antes do rodapé */
    }}
    .rodape p {{
        margin-bottom: 0.5em; /* Espaçamento menor entre os parágrafos do rodapé */
    }}
</style>
</head>
<body>
"""
        
        # O documento_texto já deve vir formatado pelo AgenteRedacaoJuridica (com H1, H2, P, etc.)
        # A lógica de inferir H1 foi removida para confiar que o redator já o criou.
        html_content += documento_texto
        
        html_content += f"\n<div class=\"rodape\">{rodape_final}</div>" # Usa o rodape_final construído
        html_content += "\n</body>\n</html>"

        return html_content

# Exemplo de uso
if __name__ == '__main__':
    formatador = AgenteFormatacaoFinal()

    # Simulação de um documento gerado pelo Agente de Redação Jurídica
    # Observe que o H1 já está no documento_exemplo, como esperado do AgenteRedacaoJuridica
    documento_exemplo = """
<h1>AÇÃO DE REPARAÇÃO DE DANOS MORAIS</h1>

EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO DA XXX VARA CÍVEL DA COMARCA DE CIDADE– ESTADO

<p>Maria Joaquina, nacionalidade, estado civil, portador do RG nº xxx, inscrito no CPF sob nº xxx, domiciliada na cidade de xxx, Estado de xxx, vem, respeitosamente, à presença de Vossa Excelência, por seu advogado que ao final subscreve – procuração anexa (DOC. 01) –, com fulcro na Constituição Federal, nos artigos 5º, inciso V e X, pelos artigos 186, 927 e seguintes do Código Civil, artigos 282 do Código de Processo Civil, artigos 138, 139, 140 do Código Penal, com supedâneo na Lei 12.550 de 15 de Dezembro de 2011 e demais normas pertinentes, para propor a presente</p>

<h2>DOS FATOS</h2>
<p>Em 30 de abril de 2021 a requerente, em comemoração a aprovação no concurso público de delegada da policia civil do estado do Ceará, estava com amigos e familiares em um restaurante.</p>
<p>Momentos depois, João Liborio, diante das pessoas presentes no local, sem motivo ou razão aparente, se aproximou de Maria Joaquina e proferiu insultos, alegando, que “ Maria Joaquina tinha passado em tal concurso pois fraudou a prova”.</p>
<p>Em alto tom de voz, João Liborio chamou a requerente de “exibida”, “charlatã”, “ladrona” e “discarada”.</p>
<p>Ocorre que, Maria constrangida com os insultos proferidos na frente de toda a sua família e de todo o restaurante, a mesma pagou a conta e se retirou do estabelecimento de forma discreta junto de seus familiares.</p>

<h2>DOS DIREITOS</h2>
<p>Na Constituição Federal de 1988, aplica-se a tutela do direito à indenização por dano material ou moral decorrente da violação de direitos fundamentais, tais como a honra e a imagem das pessoas:</p>
<p>"Art. 5º ( CF/88), X - São invioláveis a intimidade, a vida privada, a honra e a imagem das pessoas, assegurado o direito a indenização pelo dano material ou moral decorrente de sua violação;(...)"</p>
<p>O art. 186 do Código Civil trata da reparação do dano causado por ação agente:</p>
<p>"Art. 186 ( CC)- Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito".</p>
<p>O artigo 927 do Código Civil, retrata que aquele que causar dano a outrem é obrigado a repará-lo. Neste caso, é evidente que a requerente foi lesada, devido aos insultos proferidos pelo requerido publicamente.</p>
<p>“Art. 927 ( CC)- Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repara-lo."</p>
<p>Os artigos 138, 139 e 140 do Código Penal Brasileiro, que trata dos crimes de Calúnia, Difamação e Injúria, respectivamente, é sabido que houve, no ato em tela.</p>
<p>Calúnia, pois o requerido acusou o requerente de “fraude contra Concurso Público”, crime previsto na Lei 12.550 de 2011, Capitulo 5º, Título 10º do Código Penal, que trata de crimes contra a fé pública o artigo 311-A.</p>
<p>Difamação, pois o requerido palavras de baixo calão e incriminou a requerente em um ato que a mesma não cometeu, desonrando a imagem personalíssima da mesma.</p>
<p>Injúria, pois o requerido, proferiu palavras de baixo calão e incriminou a requerente por atos que não cometeu,.</p>
<p>Ademais, para que possa diminuir a dor e a vergonha imposta pelo insultos proferidos pelo requerido, o dinheiro trará a requerente uma satisfação e a certeza que o mesmo pagou pela ofensa proferida a ela.</p>

<h2>DA QUANTIA DEVIDA</h2>
<p>Sendo comprovada a conduta danosa do requerido, assim como o dano moral sofrido e o nexo causal, deverá ser apurado um valor para indenizar a requerente pelos atos de João Liborio.</p>
<p>Devendo tal indenização ser proporcional ao grau de culpa, á gravidade da ofensa e ao nível econômico do requerido, levando em consideração que a indenização tem o intuito de diminuir o efeito causado do dano que a requerente sofreu.</p>
<p>Assim, levando em consideração os para apuração bem como o grande ato lesivo e crimes em regime strictu sensu, entende-se que é razoável o valor R$ 16.000,00 (dezesseis mil reais).</p>

<h2>DOS PEDIDOS</h2>
<p>1. Que o réu seja citado, no endereço no qual foi inicialmente referido, para que o mesmo compareça a audiência de instrução e julgamento, para apresentação de resposta, sob pena de revelia e confissão quanto á mérito de fato;</p>
<p>2. Que Vossa Excelência considere como procedente o pedido com o intuito de condenar o réu a pagar indenização no valor de $ 16.000,00 (dezesseis mil reais) pelos danos morais;</p>
<p>3. Que o réu seja condenado a pagar as custa processuais e os honorário advocatícios;</p>

<h2>DAS PROVAS</h2>
<p>Protesta por todos os meios de prova em direito admitidos, depoimentos de testemunhas, bem como novas provas, documentais e outras, que eventualmente venham a surgir.</p>

<h2>DO VALOR DA CAUSA</h2>
<p>Dá-se à causa o valor de R$ xxxxx (Valor).</p>
<p>Termos em que</p>
<p>Pede Deferimento.</p>
<p>(Local, data, ano).</p>
<p>Advogado</p>
<p>OAB</p>
"""

    # Dados processados simulados do Agente Coletor de Dados (para informações do rodapé)
    dados_processados_exemplo = {
        "tipo_documento": "peticao",
        "contratante_nome": "Maria Joaquina",
        "contratante_cpf": "123.456.789-00",
        "contratado_nome": "João Liborio",
        "contratado_cpf": "000.987.654-32",
        "foro_eleicao": "São Paulo, SP"
    }

    documento_final_html = formatador.formatar_documento(documento_exemplo, dados_processados_exemplo)
    print("\n--- Documento Final Formatado (HTML) ---")
    print(documento_final_html)

    # Para salvar em um arquivo HTML para visualização
    with open("documento_final.html", "w", encoding="utf-8") as f:
        f.write(documento_final_html)
    print("\nDocumento HTML salvo em: documento_final.html")