# Use uma imagem base do Python
FROM python:3.12-slim

# Instala dependências do sistema e Chrome
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    xdg-utils \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Configuração do ambiente virtual do Python
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Configuração do Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99

# Configurações para evitar problemas com o Chrome
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Cria e define o diretório de trabalho
WORKDIR /app

# Copia os arquivos necessários
COPY requirements.txt .
COPY api.py .
COPY tiktok_bot.py .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Script de inicialização
COPY <<EOF /app/start.sh
#!/bin/bash
# Inicia o Xvfb
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

# Aguarda o Xvfb iniciar
sleep 3

# Inicia a API
python api.py
EOF

# Dá permissão de execução ao script
RUN chmod +x /app/start.sh

# Expõe a porta da API
EXPOSE 3090

# Comando para iniciar a aplicação
CMD ["/app/start.sh"]