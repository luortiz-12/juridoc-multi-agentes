# JuriDoc Simplificado

Versão simplificada do sistema JuriDoc focada exclusivamente em **Petições Iniciais** com integração de pesquisa jurídica via DuckDuckGo.

## 🎯 Características

- **Foco único**: Geração de petições iniciais
- **Pesquisa integrada**: Busca automática de leis, jurisprudência e doutrina via DuckDuckGo
- **Arquitetura simplificada**: Um único agente especializado
- **Compatível com n8n**: Recebe dados estruturados via webhook
- **Deploy no Render**: Configurado para deploy automático

## 🚀 Endpoints

### `POST /api/gerar-peticao`
Gera uma petição inicial completa com fundamentação jurídica.

**Exemplo de payload:**
```json
{
  "tipo_acao": "Ação de Cobrança",
  "autor": {
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "endereco": "Rua das Flores, 123, São Paulo/SP"
  },
  "reu": {
    "nome": "Empresa XYZ Ltda",
    "cnpj": "12.345.678/0001-90",
    "endereco": "Av. Paulista, 1000, São Paulo/SP"
  },
  "fatos": "Prestação de serviços não pagos no valor de R$ 5.000,00",
  "pedidos": ["Condenação ao pagamento", "Juros e correção monetária"],
  "valor_causa": "R$ 5.000,00"
}
```

### `GET /api/status`
Verifica se o serviço está funcionando.

## 🔧 Configuração

### Variáveis de Ambiente
- `OPENAI_API_KEY`: Chave da API do OpenAI (obrigatória)
- `PORT`: Porta do serviço (padrão: 5000)

### Deploy no Render

1. Conecte seu repositório ao Render
2. Configure a variável `OPENAI_API_KEY`
3. O deploy será automático usando o `Procfile`

## 📋 Funcionalidades

### Pesquisa Jurídica Automática
- **Legislação**: Busca em planalto.gov.br e sites jurídicos
- **Jurisprudência**: Consulta STF, STJ e tribunais estaduais
- **Doutrina**: Pesquisa em Conjur, Migalhas e portais especializados

### Geração de Petição
- Estrutura formal brasileira
- Fundamentação legal automática
- Placeholders para informações não fornecidas
- Saída em HTML formatado

## 🏗️ Arquitetura

```
src/
├── main.py              # Aplicação Flask principal
├── agente_peticao.py    # Agente especializado em petições
└── pesquisa_juridica.py # Módulo de pesquisa com DuckDuckGo
```

## 🔄 Integração com n8n

O sistema foi projetado para receber dados do n8n via webhook. Configure seu workflow para enviar um POST para `/api/gerar-peticao` com os dados estruturados.

## 📝 Exemplo de Resposta

```json
{
  "status": "sucesso",
  "documento_html": "<h1>PETIÇÃO INICIAL</h1><p>...</p>",
  "dados_estruturados": {...},
  "pesquisa_realizada": "Resumo da pesquisa jurídica realizada",
  "timestamp": "2025-07-02 10:30:00"
}
```

## 🛠️ Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variável de ambiente
export OPENAI_API_KEY="sua_chave_aqui"

# Executar localmente
cd src
python main.py
```

## 📞 Suporte

Para dúvidas ou problemas, consulte os logs do aplicativo ou entre em contato com a equipe de desenvolvimento.

