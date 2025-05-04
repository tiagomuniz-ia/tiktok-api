FROM python:3.12-slim

# Configuração do ambiente
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV TZ=America/Sao_Paulo

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    python3-distutils \
    python3-setuptools \
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

# Copia os arquivos necessários
COPY requirements.txt .
COPY api.py .
COPY tiktok_bot.py .

# Instala setuptools primeiro
RUN pip install --no-cache-dir setuptools wheel

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Configura o timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Cria diretório para Chrome e configura permissões
RUN mkdir -p /app/.config/chromium && \
    chown -R root:root /app

# Expõe a porta da API
EXPOSE 3090

# Inicia o Xvfb e a API com retry
CMD Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 & \
    until python api.py; do \
    echo "API crashed with exit code $?. Respawning.." >&2; \
    sleep 1; \
    done