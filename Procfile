# Procfile - Configuração explícita para Gunicorn na Railway

# Este comando instrui a Railway a:
# 1. Iniciar o servidor Gunicorn.
# 2. Mudar para o diretório 'src' antes de iniciar.
# 3. Usar 2 processos de trabalho (workers), o que é bom para o seu plano de recursos.
# 4. Definir um timeout de 600 segundos (10 minutos) para cada worker.
# 5. Iniciar a aplicação 'app' que está no arquivo 'main.py'.
web: gunicorn --chdir src -w 2 --timeout 600 main:app

