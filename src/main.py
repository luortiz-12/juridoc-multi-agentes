# src/main.py

from flask import Flask
from flask_cors import CORS
import os # Adicionado o import de os para o bloco de teste local

# --- Usando Import Relativo ---
# O '.' indica para importar de uma subpasta do pacote atual 'src'.
from .routes.juridoc import juridoc_bp

def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    Este é o padrão 'Application Factory', uma boa prática em Flask.
    """
    print("DEBUG: Criando a instância da aplicação Flask...")
    
    app = Flask(__name__)
    
    # Habilita o CORS para todas as rotas da aplicação de forma global.
    CORS(app)

    # --- Registro Simplificado do Blueprint ---
    # O url_prefix já está definido no próprio blueprint.
    app.register_blueprint(juridoc_bp)

    @app.route("/")
    def index():
        # Rota raiz apenas para confirmar que o serviço está no ar
        return "Serviço JuriDoc no ar. Acesse os endpoints em /api/juridoc"

    return app

# A variável 'app' é o que o Gunicorn procura para iniciar.
app = create_app()


# --- ESTE BLOCO FOI MANTIDO ---
# A lógica abaixo é para testes locais e não é usada pelo Render, mas é importante mantê-la.
if __name__ == '__main__':
    # Define a porta para o servidor de desenvolvimento local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)