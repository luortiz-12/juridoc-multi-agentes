# src/main.py


# Imports RAG
try:
    from rag_agent_integration import RAGEnhancedTechnicalAgent, RAGEnhancedWriterAgent
    RAG_AVAILABLE = True
    print("✅ Sistema RAG carregado com sucesso")
except ImportError as e:
    print(f"⚠️ Sistema RAG não disponível: {e}")
    RAG_AVAILABLE = False

from flask import Flask
from flask_cors import CORS
import os

# --- ALTERAÇÃO: Import direto, sem 'src.' ---
from routes.juridoc import juridoc_bp

def create_app():
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