FROM python:3.12-slim

# Configuração de variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV CHROME_VERSION=136.0.7103.59-1

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

# Cria diretório para logs e define permissões
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Configurações de segurança
RUN groupadd -r botuser && useradd -r -g botuser -G audio,video botuser \
    && chown -R botuser:botuser /app

# Configurações adicionais de segurança para o Chrome
RUN mkdir -p /app/.config/google-chrome && \
    chown -R botuser:botuser /app/.config

# Define variáveis de ambiente para o Chrome
ENV CHROME_PATH=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV HOME=/app

# Muda para o usuário não-root
USER botuser

# Expõe a porta da API
EXPOSE 3090

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3090/health || exit 1

# Inicia a API com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3090", "--workers", "1", "--timeout", "300", "api:app"]