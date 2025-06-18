import os
import subprocess
import sys

# Mensagem de debug para verificar se o script está sendo executado
print("DEBUG: Script start.py iniciado.")

# Obtém a porta da variável de ambiente 'PORT' fornecida pelo Render.
# Usa 5000 como fallback para desenvolvimento local, se 'PORT' não estiver definida.
port = os.environ.get("PORT", "5000")

# --- ALTERAÇÃO PRINCIPAL AQUI ---
# Adicionados os parâmetros para resolver o problema de TIMEOUT.
# A lista de comando foi formatada para melhor leitura.
command = [
    "gunicorn",
    "--workers", "3",                 # Define 3 processos de trabalho para lidar com mais requisições.
    "--worker-class", "gevent",        # Usa um trabalhador assíncrono, ideal para I/O (espera de API).
    "--timeout", "120",                # AUMENTA O TEMPO LIMITE de cada trabalhador para 120 segundos.
    "--bind", f"0.0.0.0:{port}",       # Mantém a configuração de porta dinâmica.
    "src.main:app"                     # Mantém o caminho para sua aplicação Flask.
]

try:
    # Executa o comando Gunicorn
    print(f"DEBUG: Executando comando: {' '.join(command)}")
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    # Tratamento de erro aprimorado para evitar falhas se stdout/stderr não forem capturados
    print(f"ERRO: Gunicorn falhou com código {e.returncode}")
    if e.stdout:
        print(f"Saída padrão: {e.stdout.decode()}")
    if e.stderr:
        print(f"Saída de erro: {e.stderr.decode()}")
    sys.exit(1)
except Exception as e:
    print(f"ERRO INESPERADO: {e}")
    sys.exit(1)