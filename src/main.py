# src/main.py

from flask import Flask
from flask_cors import CORS
import os

# --- ALTERAÇÃO: Voltando para o import absoluto a partir de 'src' ---
from src.routes.juridoc import juridoc_bp

def create_app():
    print("DEBUG: Criando a instância da aplicação Flask...")
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(juridoc_bp)

    @app.route("/")
    def index():
        return "Serviço JuriDoc no ar. Acesse os endpoints em /api/juridoc"

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

