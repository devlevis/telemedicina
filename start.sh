#!/bin/sh

# Aplicar migrações
python manage.py migrate --noinput

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Iniciar o servidor
gunicorn --bind 0.0.0.0:8000 --workers 2 healing.wsgi:application
