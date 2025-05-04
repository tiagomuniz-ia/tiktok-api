#!/bin/bash
# Script para executar o bot TikTok via Docker

# Cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Criando imagem Docker para TikTok Bot...${NC}"
docker build -t tiktok-bot .

echo -e "${YELLOW}⚠️  Lembre-se de preencher os parâmetros corretos antes de executar!${NC}"
echo -e "${GREEN}🚀 Executando o TikTok Bot no Docker...${NC}"

# Substitua estas variáveis com seus valores reais
SESSION_ID="seu_session_id_aqui"
VIDEO_URL="sua_url_do_video_aqui"
VIDEO_CAPTION="sua_legenda_aqui"
HASHTAGS="hashtag1,hashtag2,hashtag3"
MUSIC_NAME="nome_da_musica_aqui"
MUSIC_VOLUME="50"

# Execute o contêiner com variáveis de ambiente
docker run --rm -it \
  -e SESSION_ID="$SESSION_ID" \
  -e VIDEO_URL="$VIDEO_URL" \
  -e VIDEO_CAPTION="$VIDEO_CAPTION" \
  -e HASHTAGS="$HASHTAGS" \
  -e MUSIC_NAME="$MUSIC_NAME" \
  -e MUSIC_VOLUME="$MUSIC_VOLUME" \
  tiktok-bot

echo -e "${GREEN}✅ Execução concluída!${NC}" 