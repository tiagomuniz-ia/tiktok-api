# TikTok Poster API

API para automação de postagem de vídeos no TikTok, projetada para funcionar em ambientes de servidor. Agora com sistema inteligente de detecção de bloqueios e diagnóstico.

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

Endpoint para postar vídeos no TikTok.

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
  "proxy": null,
  "save_diagnostics": true
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
- `save_diagnostics`: Se deve salvar screenshots e dados de diagnóstico

### NOVO! Endpoint de diagnóstico: POST /diagnose

Use este endpoint para verificar se sua sessão é válida e diagnosticar problemas de bloqueio sem tentar postar um vídeo.

Exemplo de payload:

```json
{
  "session_id": "sua_session_id_do_tiktok",
  "sid_tt": "seu_sid_tt_opcional",
  "headless": false,
  "use_proxy": false,
  "proxy": null,
  "wait_time_multiplier": 1.2
}
```

A resposta incluirá:
- Resultado de cada etapa de verificação
- Screenshots codificados em base64 (se disponíveis)
- Análise da página HTML
- Tipo de bloqueio detectado (se houver)
- Recomendações específicas para resolver o problema

### Endpoint de verificação: GET /health

Use para verificar se a API está funcionando e obter informações sobre o ambiente.

## Sistema de Detecção de Bloqueios

A API agora inclui um sofisticado sistema de detecção de bloqueios que pode identificar:

- **Desafios CAPTCHA**: Quando o TikTok exige verificação humana
- **Bloqueios de Sessão**: Quando os cookies de sessão expiraram ou foram invalidados
- **Limitação de Taxa (Rate Limiting)**: Quando muitas solicitações foram feitas em pouco tempo
- **Bloqueios de IP**: Quando o TikTok bloqueia o IP do servidor
- **Detecção de Automação**: Quando o TikTok detecta que é um bot
- **Atividade Suspeita**: Quando o comportamento é considerado anormal

Para cada tipo de bloqueio, o sistema fornece recomendações específicas para resolver o problema.

### Resposta de Diagnóstico

Exemplo de resposta de diagnóstico:

```json
{
  "status": "blocked",
  "timestamp": "2023-05-20T14:30:45.123456",
  "steps": [
    {
      "step": "inject_session",
      "success": true,
      "is_blocked": false
    },
    {
      "step": "test_login",
      "success": false,
      "is_blocked": true,
      "block_type": "captcha_challenge",
      "details": {"url": "https://www.tiktok.com/captcha?..."}
    }
  ],
  "screenshots": [...],
  "is_blocked": true,
  "block_type": "captcha_challenge",
  "recommendations": [
    "Use um proxy residencial diferente",
    "Reduza a frequência de solicitações",
    "Tente uma sessão mais recente/nova"
  ],
  "page_analysis": {
    "iframes_count": 2,
    "visible_errors": [],
    "security_forms": 1,
    "url": "https://www.tiktok.com/captcha?...",
    "page_title": "Security Verification"
  }
}
```

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

### Problemas de detectação de automação

Se você estiver enfrentando bloqueios frequentes:

1. **Use o endpoint `/diagnose` primeiro**: Identifique o tipo de bloqueio antes de tentar postar
2. **Utilize proxies residenciais**: IPs de datacenters são mais facilmente detectados
3. **Varie o tempo entre requisições**: Evite fazer muitas solicitações em sequência rápida
4. **Obtenha cookies de sessão recentes**: Cookies mais antigos têm maior probabilidade de serem rejeitados

## Notas

- A API usa técnicas avançadas para evitar detecção de automação
- Cookie de sessão do TikTok geralmente expira após alguns dias
- Use proxies residenciais para melhorar as taxas de sucesso em servidores
- Os arquivos de diagnóstico são salvos na pasta `debug_data` 