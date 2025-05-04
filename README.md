# TikTok Poster API

API para automação de postagem de vídeos no TikTok, projetada para funcionar em ambientes de servidor.

## Requisitos

- Python 3.8+
- Google Chrome
- Xvfb (para servidores Linux)
- Dependências do Python listadas em `requirements.txt`

## Instalação

### Em servidor Linux (Debian/Ubuntu)

1. Instale as dependências do sistema:

```bash
sudo apt-get update
sudo apt-get install -y wget gnupg2 xvfb python3-pip python3-venv
```

2. Instale o Google Chrome:

```bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

3. Clone o repositório ou copie os arquivos para o servidor

4. Instale as dependências Python:

```bash
pip install -r requirements.txt
```

## Execução

### Método 1: Script auxiliar

Use o script auxiliar para iniciar automaticamente a API com as configurações corretas:

```bash
chmod +x run_server.sh
./run_server.sh
```

Para modo de produção com Gunicorn:

```bash
./run_server.sh --production
```

### Método 2: Docker

Construa e execute o contêiner Docker:

```bash
docker build -t tiktok-poster-api .
docker run -p 3090:3090 tiktok-poster-api
```

### Método 3: Manual

1. Inicie o display virtual:

```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -ac &
```

2. Inicie a API:

```bash
python api.py
```

## Uso da API

### Endpoint principal: POST /post-video

Exemplo de payload:

```json
{
  "session_id": "sua_session_id_do_tiktok",
  "sid_tt": "seu_sid_tt_opcional",
  "video_url": "https://exemplo.com/seu-video.mp4",
  "video_caption": "Legenda do seu vídeo",
  "hashtags": ["hashtag1", "hashtag2"],
  "music_name": "Nome da música a pesquisar",
  "music_volume": 50,
  "headless": true,
  "wait_time_multiplier": 1.5,
  "use_proxy": false,
  "proxy": null
}
```

#### Parâmetros obrigatórios:
- `session_id`: ID de sessão do TikTok (cookie)
- `video_url`: URL do vídeo a ser postado

#### Parâmetros opcionais:
- `sid_tt`: Cookie sid_tt do TikTok (se não informado, usa session_id)
- `video_caption`: Legenda do vídeo
- `hashtags`: Lista de hashtags (sem o #)
- `music_name`: Nome da música para pesquisar
- `music_volume`: Volume da música (0-100)
- `headless`: Se deve executar em modo headless (recomendado true para servidores)
- `wait_time_multiplier`: Multiplicador de tempo de espera (útil para servidores com latência)
- `use_proxy`: Se deve usar proxy
- `proxy`: URL do proxy (ex: "http://user:pass@host:port")

### Endpoint de verificação: GET /health

Use para verificar se a API está funcionando e obter informações sobre o ambiente.

## Solução de problemas

### Problemas com Xvfb

Se estiver tendo problemas com o display virtual:

```bash
# Verificar se Xvfb está rodando
ps aux | grep Xvfb

# Reiniciar display virtual
pkill Xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -ac &
```

### Chrome trava ou falha ao iniciar

Verifique se todas as dependências do Chrome estão instaladas:

```bash
sudo apt-get install -y fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release xdg-utils
```

### Problemas com a API

Verifique os logs para mais detalhes sobre erros específicos.

## Notas

- A API usa técnicas avançadas para evitar detecção de automação
- Cookie de sessão do TikTok geralmente expira após alguns dias
- Use proxies residenciais para melhorar as taxas de sucesso em servidores 