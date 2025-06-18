import os
import subprocess
import sys

# Mensagem de debug para verificar se o script está sendo executado
print("DEBUG: Script start.py iniciado.")

# Obtém a porta da variável de ambiente 'PORT' fornecida pelo Render.
port = os.environ.get("PORT", "5000")

# --- ALTERAÇÃO PARA TESTE ---
# Removemos temporariamente '--workers' e '--worker-class gevent'
# para usar o 'sync worker' padrão do Gunicorn e isolar a causa do erro.
# Mantivemos o timeout, que é essencial.
command = [
    "gunicorn",
    "--timeout", "120",
    "--bind", f"0.0.0.0:{port}",
    "src.main:app"
]

try:
    # Executa o comando Gunicorn
    print(f"DEBUG: Executando comando: {' '.join(command)}")
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    # Tratamento de erro
    print(f"ERRO: Gunicorn falhou com código {e.returncode}")
    if e.stdout:
        print(f"Saída padrão: {e.stdout.decode()}")
    if e.stderr:
        print(f"Saída de erro: {e.stderr.decode()}")
    sys.exit(1)
except Exception as e:
    print(f"ERRO INESPERADO: {e}")
    sys.exit(1)