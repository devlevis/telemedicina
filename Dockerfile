ARG PYTHON_VERSION=3.12-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependências do psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
RUN mkdir -p /code
WORKDIR /code

# Copiar e instalar requisitos
COPY requirements.txt /code/
RUN pip install --upgrade pip \
    && pip install -r /code/requirements.txt \
    && rm -rf /root/.cache/

# Copiar o restante do código
COPY . /code/

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor a porta
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "healing.wsgi:application"]
