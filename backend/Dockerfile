# Use uma imagem oficial do Python como base
FROM python:3.11-slim

# Defina variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Defina o diretório de trabalho
WORKDIR /code

# Instale dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instale as dependências Python
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponha a porta 8000
EXPOSE 8000

# Cole o entrypoint
COPY ./entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

# Defina o entrypoint e execute o script de fixtures após migrações
ENTRYPOINT ["/code/entrypoint.sh"]