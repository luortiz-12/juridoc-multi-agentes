import os
import subprocess
import sys

# Mensagem de debug para verificar se o script está sendo executado
print("DEBUG: Script start.py iniciado.")

# Obtém a porta da variável de ambiente 'PORT' fornecida pelo Render.
# Usa 5000 como fallback para desenvolvimento local, se 'PORT' não estiver definida.
port = os.environ.get("PORT", "5000")

# Comando Gunicorn para iniciar a aplicação Flask
# Certifique-se de que src.main:app está correto e que a porta é dinâmica
command = ["gunicorn", "--bind", f"0.0.0.0:{port}", "src.main:app"]

try:
    # Executa o comando Gunicorn
    print(f"DEBUG: Executando comando: {' '.join(command)}")
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    print(f"ERRO: Gunicorn falhou com código {e.returncode}")
    print(f"Saída padrão: {e.stdout.decode()}")
    print(f"Saída de erro: {e.stderr.decode()}")
    sys.exit(1)
except Exception as e:
    print(f"ERRO INESPERADO: {e}")
    sys.exit(1)