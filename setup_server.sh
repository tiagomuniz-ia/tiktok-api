#!/bin/bash
# Script de configuração para o bot TikTok em servidores Linux

echo "🚀 Instalando dependências do sistema..."
# Atualiza os repositórios
apt-get update

# Instala o Chrome (versão estável mais recente)
echo "📦 Instalando Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Instala Xvfb para display virtual
echo "📦 Instalando Xvfb (display virtual)..."
apt-get install -y xvfb

# Instala outras dependências do sistema
echo "📦 Instalando outras dependências do sistema..."
apt-get install -y xorg xserver-xorg-video-dummy python3-pip

# Instala dependências Python
echo "🐍 Instalando dependências Python..."
pip3 install -r requirements.txt

# Determina versão do Chrome instalada
CHROME_VERSION=$(google-chrome --version | grep -oP "Google Chrome \K[^ ]+")
echo "✅ Google Chrome versão ${CHROME_VERSION} instalado"

# Verifica versão de ChromeDriver compatível
CHROMEDRIVER_VERSION=$(echo $CHROME_VERSION | cut -d '.' -f 1)
echo "ℹ️ Versão principal do ChromeDriver necessária: ${CHROMEDRIVER_VERSION}"

echo "📢 Configuração concluída!"
echo "📢 Para executar o bot em modo servidor, use:"
echo "📢 python3 tiktok_bot.py server"
echo ""
echo "⚠️ Importante: Certifique-se de usar o parâmetro correto version_main=${CHROMEDRIVER_VERSION} no código Python" 