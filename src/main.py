# src/main.py - VERSÃO FINAL SIMPLIFICADA

from flask import Flask
from flask_cors import CORS
import os

# Importa o blueprint de forma direta, como já corrigimos.
from routes.juridoc import juridoc_bp

def create_app():
    """Cria e configura a instância da aplicação Flask."""
    app = Flask(__name__)
    CORS(app) # Habilita o CORS globalmente
    
    # Registra o blueprint das rotas da API
    app.register_blueprint(juridoc_bp)

    @app.route("/")
    def index():
        return "Serviço JuriDoc no ar. API de Petições pronta."

    return app

# A variável 'app' que o Gunicorn usa para iniciar o serviço.
app = create_app()

if __name__ == '__main__':
    # Bloco para testes locais
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)