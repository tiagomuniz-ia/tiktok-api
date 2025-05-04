FROM python:3.12-slim

# Configuração básica do ambiente
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV TZ=America/Sao_Paulo
ENV PATH="/usr/local/bin:${PATH}"

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

# Instala pip atualizado
RUN python -m pip install --upgrade pip

# Instala cada pacote separadamente para facilitar diagnóstico
RUN pip install flask==3.1.0 && \
    pip install flask-cors==5.0.1 && \
    pip install selenium==4.18.1 && \
    pip install undetected-chromedriver==3.5.5 && \
    pip install requests==2.31.0 && \
    pip install packaging==23.2 && \
    pip install setuptools==69.0.3 && \
    pip install websockets==12.0 && \
    pip install webdriver-manager==4.0.1

# Verifica se o Flask foi instalado corretamente
RUN python -m pip list | grep flask

# Configura o timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Cria diretório de configuração para o Chrome
RUN mkdir -p /app/.config/chromium /app/.cache

# Script de inicialização com diagnóstico
RUN echo '#!/bin/bash\n\
echo "Iniciando diagnóstico..."\n\
echo "Python path:"\n\
which python\n\
echo "Python version:"\n\
python --version\n\
echo "Verificando pacotes instalados:"\n\
pip list\n\
echo "Verificando se Flask está instalado:"\n\
python -c "import flask; print(f\"Flask version: {flask.__version__}\")" || echo "FLASK NOT FOUND!"\n\
echo "Iniciando Xvfb..."\n\
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &\n\
sleep 2\n\
echo "Tentando instalar Flask novamente para garantir:"\n\
pip install -v flask==3.1.0 flask-cors==5.0.1\n\
echo "Verificando novamente se Flask está instalado:"\n\
python -c "import flask; print(f\"Flask version: {flask.__version__}\")" || echo "FLASK STILL NOT FOUND!"\n\
echo "Iniciando API..."\n\
python api.py\n' > /app/start.sh \
    && chmod +x /app/start.sh

# Expõe a porta da API
EXPOSE 3090

# Inicia a aplicação
CMD ["/app/start.sh"]