FROM python:3.12-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    libnss3 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia os arquivos
COPY . .

# Atualiza pip e instala setuptools primeiro
RUN pip install --no-cache-dir --upgrade pip setuptools

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Configura variáveis de ambiente
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Expõe a porta
EXPOSE 3090

# Comando para iniciar
CMD ["bash", "-c", "Xvfb :99 -screen 0 1920x1080x24 & sleep 2 && python api.py"]