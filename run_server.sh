#!/bin/bash
# Script para executar o TikTok Bot em modo servidor

# Variáveis
MODE="run"  # Modo padrão
SESSION_ID=""
VALIDATE_ONLY=false

# Função de ajuda
show_help() {
    echo "Uso: $0 [opções]"
    echo
    echo "Opções:"
    echo "  -v, --validate SESSION_ID    Apenas valida o SESSION_ID sem postar vídeo"
    echo "  -h, --help                   Mostra esta mensagem de ajuda"
    echo
    echo "Exemplos:"
    echo "  $0                           Executa o bot normalmente"
    echo "  $0 -v abc123                 Valida se o session_id 'abc123' é válido"
}

# Processa parâmetros
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--validate)
            VALIDATE_ONLY=true
            SESSION_ID="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

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

# Executa o modo escolhido
if [ "$VALIDATE_ONLY" = true ]; then
    if [ -z "$SESSION_ID" ]; then
        echo "❌ Erro: SESSION_ID não fornecido para validação"
        show_help
        exit 1
    fi
    
    echo "🔍 Executando validação de sessão..."
    python3 validate_session.py "$SESSION_ID"
else
    echo "🚀 Executando TikTok Bot em modo servidor..."
    python3 tiktok_bot.py server
fi

echo "✅ Execução concluída!" 