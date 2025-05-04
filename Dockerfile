FROM python:3.12-slim

# Configuração do ambiente
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV TZ=America/Sao_Paulo
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV CHROME_DRIVER_VERSION=latest

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
    procps \
    curl \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Obtém a versão do Chrome instalado
RUN CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]{2,3}" | head -1) \
    && echo "Versão do Chrome instalado: $CHROME_VERSION"

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos necessários
COPY requirements.txt .
COPY api.py .
COPY tiktok_bot.py .

# Instala setuptools primeiro
RUN pip install --no-cache-dir setuptools wheel pip --upgrade

# Instala as dependências Python com retry em caso de falha
RUN for i in $(seq 1 3); do \
        pip install --no-cache-dir -r requirements.txt && break || sleep 5; \
    done

# Configura o timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Cria diretório para Chrome e configura permissões
RUN mkdir -p /app/.config/chromium /app/.cache /app/downloads \
    && chown -R root:root /app \
    && chmod -R 755 /app

# Script de inicialização para verificar ambiente antes de iniciar
RUN echo '#!/bin/bash\n\
echo "Verificando ambiente..."\n\
echo "Versão do Chrome: $(google-chrome --version)"\n\
echo "Python: $(python --version)"\n\
echo "Listando dependências Python:"\n\
pip list\n\
echo "Iniciando Xvfb..."\n\
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &\n\
echo "Aguardando Xvfb iniciar..."\n\
sleep 2\n\
echo "Iniciando API com retry..."\n\
until python api.py; do\n\
    echo "API crashed with exit code $?. Respawning in 5 seconds..." >&2\n\
    sleep 5\n\
done\n' > /app/start.sh \
    && chmod +x /app/start.sh

# Expõe a porta da API
EXPOSE 3090

# Usa o script de inicialização
CMD ["/app/start.sh"]