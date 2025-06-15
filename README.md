# JuriDoc Multi-Agentes API

Sistema multi-agentes para geração automatizada de documentos jurídicos usando Langchain e Flask.

## Estrutura do Projeto

```
juridoc_api/
├── src/
│   ├── routes/
│   │   ├── juridoc.py          # Endpoints da API JuriDoc
│   │   └── user.py             # Endpoints de usuário (template)
│   ├── models/                 # Modelos de banco de dados
│   ├── static/                 # Arquivos estáticos
│   ├── agente_*.py            # Agentes especializados
│   ├── main_orchestrator.py   # Orquestrador principal
│   └── main.py                # Aplicação Flask principal
├── venv/                      # Ambiente virtual Python
├── requirements.txt           # Dependências Python
└── README.md                  # Este arquivo
```

## Endpoints da API

### POST /api/juridoc/gerar-documento
Gera um documento jurídico com base nos dados fornecidos.

**Exemplo de requisição:**
```json
{
  "body": {
    "tipoDocumento": "peticao",
    "contratante": "Maria Joaquina",
    "cpfContratante": "123.456.789-00",
    "contratado": "João Liborio",
    "cpfContratado": "000.987.654-32",
    "historico_peticao": "Maria Joaquina foi aprovada em concurso público para delegada.",
    "fatos_peticao": "João Liborio proferiu insultos públicos...",
    "pedido_peticao": "Indenização por danos morais no valor de R$ 16.000,00.",
    "valor_causa_peticao": "R$ 16.000,00"
  }
}
```

**Resposta de sucesso:**
```json
{
  "status": "sucesso",
  "documento_html": "<html>...</html>",
  "mensagem": "Documento gerado com sucesso."
}
```

### GET /api/juridoc/status
Verifica se o serviço está funcionando.

### GET /api/juridoc/tipos-documento
Lista os tipos de documento suportados e seus campos obrigatórios.

## Como Executar Localmente

1. Ative o ambiente virtual:
```bash
source venv/bin/activate
```

2. Execute a aplicação:
```bash
python src/main.py
```

3. A API estará disponível em: http://localhost:5000

## Configuração para Produção

- A chave da API OpenAI está configurada diretamente no código para facilitar o deployment
- O serviço escuta em 0.0.0.0:5000 para permitir acesso externo
- CORS está habilitado para permitir requisições de qualquer origem

## Integração com n8n

Para integrar com o n8n, use o nó HTTP Request com:
- Método: POST
- URL: `https://seu-dominio.com/api/juridoc/gerar-documento`
- Headers: `Content-Type: application/json`
- Body: JSON com os dados do formulário

