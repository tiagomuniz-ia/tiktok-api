#!/bin/bash

# Script para executar a API TikTok Poster em ambiente de servidor
# Autor: Usuário
# Data: 2023

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== TikTok Poster API - Setup de Servidor ===${NC}"

# Verifica se Xvfb está instalado
if ! command -v Xvfb &> /dev/null; then
    echo -e "${YELLOW}Xvfb não encontrado. Instalando...${NC}"
    sudo apt-get update
    sudo apt-get install -y xvfb x11-utils
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Falha ao instalar Xvfb. Por favor, instale manualmente.${NC}"
        exit 1
    fi
fi

# Verifica se Chrome está instalado
if ! command -v google-chrome-stable &> /dev/null; then
    echo -e "${YELLOW}Google Chrome não encontrado. Instalando...${NC}"
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Falha ao instalar Google Chrome. Por favor, instale manualmente.${NC}"
        exit 1
    fi
fi

# Configura o display virtual
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -ac &
XVFB_PID=$!

echo -e "${GREEN}Display virtual iniciado: DISPLAY=:99 (PID: $XVFB_PID)${NC}"

# Verifica ambiente Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 não encontrado. Por favor, instale Python 3.${NC}"
    exit 1
fi

# Instala dependências Python
echo -e "${BLUE}Instalando dependências Python...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao instalar dependências Python.${NC}"
    exit 1
fi

# Inicia a API
echo -e "${GREEN}Iniciando a API TikTok Poster...${NC}"
echo -e "${YELLOW}A API estará disponível em: http://localhost:3090${NC}"

# Opção: usar Gunicorn em produção
if [ "$1" == "--production" ]; then
    echo -e "${BLUE}Modo de produção: usando Gunicorn${NC}"
    gunicorn --bind 0.0.0.0:3090 --workers 1 --threads 2 'api:app'
else
    # Modo de desenvolvimento
    python3 api.py
fi

# Limpa recursos
kill $XVFB_PID 