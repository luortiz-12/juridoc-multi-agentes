print("DEBUG: Iniciando a aplicação Flask...")
from flask import Flask

app = Flask(__name__)

@app.route("/api/juridoc/status")
def status():
    return {"status": "ativo", "mensagem": "Serviço JuriDoc Multi-Agentes (Simplificado) está funcionando.", "versao": "1.0.0"}
