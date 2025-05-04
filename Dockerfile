FROM python:3.12-slim

# Configuração de variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV CHROME_VERSION=136.0.7103.59-1
ENV DISPLAY=:99

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    python3-distutils \
    python3-setuptools \
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
    libxss1 \
    libxtst6 \
    libpango-1.0-0 \
    xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable=${CHROME_VERSION} \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/logs \
    && chmod 777 /app/logs

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

# Cria diretórios necessários e define permissões
RUN mkdir -p /app/logs && chmod 777 /app/logs \
    && mkdir -p /app/.config/google-chrome && chmod 777 /app/.config/google-chrome \
    && mkdir -p /app/.cache && chmod 777 /app/.cache \
    && mkdir -p /app/.pki && chmod 777 /app/.pki \
    && mkdir -p /dev/shm && chmod 777 /dev/shm

# Configurações de segurança
RUN groupadd -r botuser && useradd -r -g botuser -G audio,video botuser \
    && chown -R botuser:botuser /app

# Define variáveis de ambiente para o Chrome
ENV CHROME_PATH=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV HOME=/app

# Script de inicialização
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
# Inicia o Xvfb
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
# Aguarda o Xvfb iniciar
sleep 1
# Inicia a aplicação
exec gunicorn --bind 0.0.0.0:3090 --workers 1 --timeout 300 api:app
EOF

RUN chmod +x /app/entrypoint.sh

# Muda para o usuário não-root
USER botuser

# Expõe a porta da API
EXPOSE 3090

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3090/health || exit 1

# Inicia a API com o script de entrypoint
CMD ["/app/entrypoint.sh"]