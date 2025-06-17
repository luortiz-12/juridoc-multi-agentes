import os
from flask import Flask
from src.routes.juridoc import juridoc_bp # Importa o Blueprint do seu arquivo juridoc.py

print("DEBUG: Iniciando a aplicação Flask...")

app = Flask(__name__)

# Registra o Blueprint 'juridoc_bp' na aplicação Flask
# Todas as rotas definidas em juridoc_bp (como /gerar-documento e /status)
# serão acessíveis sob o prefixo /api/juridoc.
app.register_blueprint(juridoc_bp, url_prefix='/api/juridoc')

# A rota /api/juridoc/status que existia diretamente aqui foi removida
# para evitar duplicação, já que ela agora é fornecida pelo Blueprint.

# Exemplo de como rodar a aplicação localmente (opcional, para testes de desenvolvimento)
if __name__ == '__main__':
    # No ambiente de produção (Render), o Gunicorn é quem iniciará a aplicação.
    # Esta parte é mais para testar localmente.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)