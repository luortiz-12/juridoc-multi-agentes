{
  "name": "Projeto JuriDoc IA - Fluxo para API Render",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "juridoc-form-input",
        "responseMode": "responseNode",
        "options": {}
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 250],
      "id": "webhook_trigger",
      "name": "Webhook Trigger"
    },
    {
      "parameters": {
        "httpMethod": "POST",
        "url": "https://juridoc-multi-agentes.onrender.com/gerar-documento",
        "sendHeaders": true,
        "headerParameters": [
          {
            "name": "Content-Type",
            "value": "application/json"
          }
        ],
        "sendBody": true,
        "bodyContentType": "json",
        "jsonBody": "={{ $json.body }}",
        "options": {}
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [500, 250],
      "id": "call_juridoc_api",
      "name": "Chamar API JuriDoc"
    },
    {
      "parameters": {
        "respondWith": "text",
        "responseBody": "={{ $json.documento_html }}",
        "options": {
          "responseCode": 200
        }
      },
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [750, 250],
      "id": "respond_to_webhook",
      "name": "Responder ao Webhook"
    }
  ],
  "connections": {
    "webhook_trigger": {
      "main": [
        [
          {
            "node": "call_juridoc_api",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "call_juridoc_api": {
      "main": [
        [
          {
            "node": "respond_to_webhook",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": false,
  "settings": {
    "executionOrder": "v1"
  },
  "versionId": "generated-by-ai",
  "meta": {
    "templateCredsSetupCompleted": true
  },
  "id": "generated-workflow-id"
}