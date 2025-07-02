# Instruções de Deploy - JuriDoc Simplificado

## 🚀 Deploy no Render

### 1. Preparação
1. Faça upload dos arquivos para um repositório Git (GitHub, GitLab, etc.)
2. Conecte o repositório ao Render

### 2. Configuração no Render
1. Crie um novo **Web Service**
2. Conecte ao seu repositório
3. Configure as seguintes opções:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`
   - **Environment**: `Python 3`

### 3. Variáveis de Ambiente
Configure a seguinte variável de ambiente no Render:
- `OPENAI_API_KEY`: Sua chave da API do OpenAI

### 4. Deploy Automático
O deploy será automático após a configuração. O Render irá:
1. Instalar as dependências do `requirements.txt`
2. Executar o `start.py` que inicia o Gunicorn
3. Disponibilizar o serviço na URL fornecida

## 🔧 Configuração Local para Desenvolvimento

### 1. Instalação
```bash
# Clonar o repositório
git clone [seu-repositorio]
cd juridoc-simplificado

# Instalar dependências
pip install -r requirements.txt

# Configurar variável de ambiente
export OPENAI_API_KEY="sua_chave_aqui"
```

### 2. Execução Local
```bash
# Modo desenvolvimento
cd src
python main.py

# Modo produção local
python start.py
```

### 3. Teste
```bash
# Executar testes básicos
python test_basic.py

# Testar sem API key
cd src
python main_test.py
```

## 🌐 Integração com n8n

### 1. Configuração do Webhook
1. No n8n, adicione um nó **HTTP Request**
2. Configure:
   - **Method**: POST
   - **URL**: `https://seu-app.onrender.com/api/gerar-peticao`
   - **Headers**: `Content-Type: application/json`

### 2. Estrutura de Dados
Envie um JSON com a seguinte estrutura:
```json
{
  "tipo_acao": "Ação de Cobrança",
  "autor": {
    "nome": "Nome do Autor",
    "cpf": "123.456.789-00",
    "endereco": "Endereço completo"
  },
  "reu": {
    "nome": "Nome do Réu",
    "cnpj": "12.345.678/0001-90",
    "endereco": "Endereço do réu"
  },
  "fatos": "Descrição dos fatos",
  "pedidos": ["Pedido 1", "Pedido 2"],
  "valor_causa": "R$ 10.000,00"
}
```

### 3. Resposta Esperada
```json
{
  "status": "sucesso",
  "documento_html": "<h1>PETIÇÃO INICIAL</h1>...",
  "dados_estruturados": {...},
  "pesquisa_realizada": "Resumo da pesquisa",
  "timestamp": "2025-07-02 10:30:00"
}
```

## 📋 Endpoints Disponíveis

- `GET /` - Informações do serviço
- `GET /api/status` - Status do serviço
- `POST /api/gerar-peticao` - Gerar petição inicial

## 🔍 Funcionalidades

### Pesquisa Jurídica Automática
- Busca legislação em sites oficiais
- Consulta jurisprudência dos tribunais superiores
- Pesquisa doutrina em portais especializados

### Geração de Petição
- Estrutura formal brasileira
- Fundamentação legal automática
- Placeholders para dados não fornecidos
- Saída em HTML formatado

## 🛠️ Troubleshooting

### Erro: "OPENAI_API_KEY não definida"
- Verifique se a variável de ambiente está configurada no Render
- Para testes locais, use `export OPENAI_API_KEY="sua_chave"`

### Erro de timeout
- O timeout está configurado para 120 segundos no Gunicorn
- Para casos complexos, pode ser necessário aumentar

### Erro na pesquisa DuckDuckGo
- Verifique a conexão com a internet
- O sistema continua funcionando mesmo com falhas na pesquisa

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs no Render
2. Teste localmente primeiro
3. Consulte a documentação da API do OpenAI

