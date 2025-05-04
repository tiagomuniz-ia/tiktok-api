FROM python:3.12-slim

# Configuração básica do ambiente
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV TZ=America/Sao_Paulo

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app/

# Instala as dependências Python
RUN pip install --no-cache-dir flask==3.1.1 flask-cors==5.0.1 selenium==4.18.1 undetected-chromedriver==3.5.5 requests==2.31.0 packaging==23.2 setuptools==69.0.3 websockets==12.0 webdriver-manager==4.0.1

# Configura o timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Cria diretório de configuração para o Chrome
RUN mkdir -p /app/.config/chromium /app/.cache

# Script de inicialização simples
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &\nsleep 2\npython api.py' > /app/start.sh \
    && chmod +x /app/start.sh

# Expõe a porta da API
EXPOSE 3090

# Inicia a aplicação
CMD ["/app/start.sh"]