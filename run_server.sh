#!/bin/bash
# Script para executar o TikTok Bot em modo servidor

# Verifica se as dependências estão instaladas
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não está instalado. Instalando..."
    apt-get update && apt-get install -y python3 python3-pip
fi

if ! command -v google-chrome &> /dev/null; then
    echo "❌ Google Chrome não está instalado. Instalando..."
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    apt-get update
    apt-get install -y google-chrome-stable
fi

# Instala pacotes necessários para o display virtual
if ! pip3 show pyvirtualdisplay &> /dev/null; then
    echo "📦 Instalando PyVirtualDisplay..."
    apt-get install -y xvfb
    pip3 install pyvirtualdisplay
fi

# Instala outras dependências Python
echo "📦 Instalando dependências Python..."
pip3 install -r requirements.txt

echo "🚀 Executando TikTok Bot em modo servidor..."
python3 tiktok_bot.py server

echo "✅ Execução concluída!" 