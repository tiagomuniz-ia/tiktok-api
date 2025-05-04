FROM python:3.9-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    xorg \
    xserver-xorg-video-dummy \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configura diretório de trabalho
WORKDIR /app

# Copia arquivos de requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY tiktok_bot.py .

# Obtém a versão do Chrome para configurar o driver corretamente
RUN echo "export CHROME_VERSION=\$(google-chrome --version | grep -oP 'Google Chrome \K[^ ]+')" >> /root/.bashrc \
    && echo "export CHROMEDRIVER_VERSION=\$(echo \$CHROME_VERSION | cut -d '.' -f 1)" >> /root/.bashrc

# Cria script de inicialização
RUN echo '#!/bin/bash\nxvfb-run -a python tiktok_bot.py server' > /app/start.sh \
    && chmod +x /app/start.sh

# Comando padrão
CMD ["/app/start.sh"]