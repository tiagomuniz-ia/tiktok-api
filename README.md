# Bot TikTok

Este bot automatiza a publicação de vídeos no TikTok.

## Requisitos

- Python 3.8+
- Google Chrome
- Acesso à Internet
- Conta TikTok com cookies de sessão válidos

## Instalação

### Windows

1. Instale o Python 3.8 ou superior
2. Instale o Google Chrome
3. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

### Servidor Linux

1. Dê permissão de execução ao script:
```bash
chmod +x run_server.sh
```

2. Execute o script como root:
```bash
sudo ./run_server.sh
```

Este script irá:
- Instalar Python 3 (se necessário)
- Instalar Google Chrome (se necessário)
- Instalar Xvfb e PyVirtualDisplay
- Instalar as dependências Python
- Executar o bot em modo servidor

## Uso

### Windows (Ambiente de desenvolvimento)

Edite os parâmetros no arquivo `tiktok_bot.py` (ou importe a classe para seu código) e execute:

```bash
python tiktok_bot.py
```

### Servidor Linux

```bash
python tiktok_bot.py server
```

## Parâmetros de Configuração

```python
params = {
    'session_id': 'seu_session_id_tiktok',  # Obrigatório
    'sid_tt': 'seu_sid_tt_tiktok',          # Opcional (usa session_id como padrão)
    'video_url': 'url_do_video_para_upload',
    'video_caption': 'legenda do vídeo',
    'hashtags': ['hashtag1', 'hashtag2'],
    'music_name': 'nome da música para pesquisar',
    'music_volume': 50  # 0-100
}
```

## Troubleshooting

### Problemas com Cookies

Certifique-se de fornecer um `session_id` válido do TikTok. Você pode obtê-lo:
1. Faça login no TikTok em seu navegador
2. Abra as Ferramentas de Desenvolvedor (F12)
3. Vá para a aba "Aplicativo" ou "Storage" > Cookies
4. Encontre o cookie `sessionid`

### Compatibilidade de Versões

Se encontrar problemas com o ChromeDriver, modifique esta linha no código:
```python
self.driver = uc.Chrome(options=options, version_main=135, headless=False)
```

Substitua o número 135 pela versão principal do seu Chrome:
- Chrome 135.x.x.x → use 135
- Chrome 114.x.x.x → use 114 