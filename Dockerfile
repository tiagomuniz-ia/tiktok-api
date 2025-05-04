FROM python:3.12-slim

# Configuração do ambiente
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    python3-distutils \
    python3-setuptools \
    xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos necessários
COPY requirements.txt .
COPY api.py .
COPY tiktok_bot.py .

# Instala setuptools primeiro
RUN pip install --no-cache-dir setuptools

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta da API
EXPOSE 3090

# Inicia o Xvfb e a API
CMD Xvfb :99 -screen 0 1920x1080x24 & python api.py