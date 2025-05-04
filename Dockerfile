FROM python:3.12-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    wget \
    gnupg \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Configura o diretório de trabalho
WORKDIR /app

# Copia os arquivos necessários
COPY requirements.txt .
COPY tiktok_bot.py .
COPY api.py .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Configura o display virtual
ENV DISPLAY=:99

# Script de inicialização
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]