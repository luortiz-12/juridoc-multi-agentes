# start.py

import os
import subprocess
import sys

print("DEBUG: Script start.py iniciado.")
port = os.environ.get("PORT", "5000")

# --- ALTERAÇÃO DEFINITIVA ---
# Usamos '--chdir src' para dizer ao Gunicorn para rodar de DENTRO da pasta src.
# Com isso, o nome do módulo da aplicação volta a ser simplesmente 'main:app'.
# Mantemos o timeout de 120 segundos.
command = [
    "gunicorn",
    "--chdir", "src",
    "--timeout", "120",
    "--bind", f"0.0.0.0:{port}",
    "main:app"
]

try:
    print(f"DEBUG: Executando comando: {' '.join(command)}")
    subprocess.run(command, check=True)
except Exception as e:
    print(f"ERRO AO INICIAR GUNICORN: {e}")
    sys.exit(1)