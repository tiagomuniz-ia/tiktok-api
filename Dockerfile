FROM python:3.12-slim

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    xvfb \
    dbus \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    x11-utils \
    python3-distutils \
    python3-setuptools \
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

# Configura o display virtual
ENV DISPLAY=:99

# Script de inicialização
RUN echo '#!/bin/bash \n\
# Inicia o servidor X virtual \n\
Xvfb :99 -screen 0 1920x1080x24 -ac & \n\
# Aguarda o servidor X iniciar \n\
sleep 2 \n\
# Inicia a API \n\
python api.py \n\
' > /app/start.sh && chmod +x /app/start.sh

# Expõe a porta da API
EXPOSE 3090

# Inicia a API com o display virtual
CMD ["/app/start.sh"]