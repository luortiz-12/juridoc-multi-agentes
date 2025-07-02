# start.py - JuriDoc Simplificado
import os
import subprocess
import sys

print("🚀 Iniciando JuriDoc Simplificado...")
port = os.environ.get("PORT", "5000")

# Comando para iniciar o Gunicorn
command = [
    "gunicorn",
    "--chdir", "src",
    "--timeout", "120",
    "--bind", f"0.0.0.0:{port}",
    "main:app"
]

try:
    print(f"🔧 Executando comando: {' '.join(command)}")
    subprocess.run(command, check=True)
except Exception as e:
    print(f"❌ ERRO AO INICIAR GUNICORN: {e}")
    sys.exit(1)

