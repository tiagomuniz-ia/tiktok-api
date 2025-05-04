# Bot TikTok para Servidores

Este bot automatiza a publicação de vídeos no TikTok, funcionando tanto em Windows quanto em servidores Linux.

## Requisitos

- Python 3.8+
- Google Chrome
- Acesso à Internet
- Conta TikTok com cookies de sessão válidos

## Instalação em Servidor Linux

### Método Automático

1. Dê permissão de execução ao script:
```bash
chmod +x setup_server.sh
```

2. Execute o script como root:
```bash
sudo ./setup_server.sh
```

### Instalação Manual

1. Instale Google Chrome:
```bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

2. Instale dependências para display virtual:
```bash
sudo apt-get install -y xvfb xorg xserver-xorg-video-dummy
```

3. Instale dependências Python:
```bash
pip install -r requirements.txt
```

## Uso

### Em Servidores (Headless)

```bash
python tiktok_bot.py server
```

### Em Ambiente de Desenvolvimento

```bash
python tiktok_bot.py
```

## Parâmetros de Configuração

Edite os parâmetros no script ou importe a classe para usar em seu código:

```python
params = {
    'session_id': 'seu_session_id_tiktok',
    'sid_tt': 'seu_sid_tt_tiktok',  # Opcional
    'video_url': 'url_do_video_para_upload',
    'video_caption': 'legenda do vídeo',
    'hashtags': ['hashtag1', 'hashtag2'],
    'music_name': 'nome da música para pesquisar',
    'music_volume': 50  # 0-100
}

bot = TikTokBot(params, headless=True)
```

## Troubleshooting

### Compatibilidade de Versões

Verifique a versão do Chrome instalada:
```bash
google-chrome --version
```

Use essa versão principal no código:
```python
self.driver = uc.Chrome(options=options, version_main=135, headless=self.headless)
```

### Problemas de Display

Se encontrar erros relacionados ao display, verifique se o Xvfb está instalado e funcionando:
```bash
sudo apt-get install -y xvfb
```

### Screenshots para Debug

O bot salva screenshots quando encontra problemas no servidor:
```
/tmp/tiktok_debug.png
``` 