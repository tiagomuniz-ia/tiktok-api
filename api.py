from flask import Flask, request, jsonify
from flask_cors import CORS
from tiktok_bot import TikTokBot
import json
import logging
import traceback
import time
import sys

# Configurando log com formatação detalhada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("tiktok-api")

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Rota para verificar se a API está funcionando"""
    logger.info("Health check recebido")
    return jsonify({"status": "ok", "message": "API is running"}), 200

@app.route('/post-video', methods=['POST'])
def post_video():
    """Rota principal para postar vídeo no TikTok"""
    request_id = f"req_{int(time.time())}"
    logger.info(f"[{request_id}] Recebida nova requisição post-video")
    
    try:
        # Pega os dados do request
        data = request.get_json()
        if not data:
            logger.error(f"[{request_id}] Payload JSON inválido ou vazio")
            return jsonify({
                "error": "Invalid JSON payload",
                "message": "Request body must be a valid JSON"
            }), 400
            
        logger.info(f"[{request_id}] Payload: {json.dumps({k: '***' if k in ['session_id', 'sid_tt'] else v for k, v in data.items()})}")
        
        # Validação dos campos obrigatórios
        required_fields = ['session_id', 'video_url']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.error(f"[{request_id}] Campos obrigatórios ausentes: {missing_fields}")
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        # Configuração dos parâmetros com valores padrão
        bot_params = {
            'session_id': data['session_id'],
            'sid_tt': data.get('sid_tt', data['session_id']),
            'video_url': data['video_url'],
            'video_caption': data.get('video_caption', ''),
            'hashtags': data.get('hashtags', []),
            'music_name': data.get('music_name', ''),
            'music_volume': data.get('music_volume', 50)
        }

        # Validações adicionais
        if not isinstance(bot_params['hashtags'], list):
            logger.error(f"[{request_id}] Formato inválido para hashtags: {type(bot_params['hashtags'])}")
            return jsonify({
                "error": "Invalid hashtags format",
                "message": "Hashtags must be a list of strings"
            }), 400

        if not isinstance(bot_params['music_volume'], (int, float)) or \
           not 0 <= bot_params['music_volume'] <= 100:
            logger.error(f"[{request_id}] Volume de música inválido: {bot_params['music_volume']}")
            return jsonify({
                "error": "Invalid music volume",
                "message": "Music volume must be a number between 0 and 100"
            }), 400
            
        # Verificação da URL do vídeo
        if not bot_params['video_url'].startswith(('http://', 'https://')):
            logger.error(f"[{request_id}] URL do vídeo inválida: {bot_params['video_url']}")
            return jsonify({
                "error": "Invalid video URL",
                "message": "Video URL must start with http:// or https://"
            }), 400

        # Instancia o bot com os parâmetros
        logger.info(f"[{request_id}] Inicializando TikTokBot")
        bot = None
        
        try:
            # Medição de tempo para análise de performance
            start_time = time.time()
            
            bot = TikTokBot(bot_params)
            logger.info(f"[{request_id}] Bot inicializado com sucesso")
            
            # Executa o processo de postagem
            if not bot.inject_session():
                elapsed = time.time() - start_time
                logger.error(f"[{request_id}] Falha na injeção de sessão após {elapsed:.2f}s")
                bot.close()
                return jsonify({
                    "error": "Session injection failed",
                    "message": "Could not inject session"
                }), 500

            if not bot.test_login():
                elapsed = time.time() - start_time
                logger.error(f"[{request_id}] Falha na autenticação após {elapsed:.2f}s")
                bot.close()
                return jsonify({
                    "error": "Authentication failed",
                    "message": "Invalid session ID"
                }), 401

            # Tenta postar o vídeo
            logger.info(f"[{request_id}] Iniciando postagem do vídeo")
            post_result = bot.post_video()
            elapsed = time.time() - start_time
            
            # Fecha o navegador independente do resultado
            bot.close()
            
            if post_result:
                logger.info(f"[{request_id}] Vídeo postado com sucesso em {elapsed:.2f}s")
                return jsonify({
                    "status": "success",
                    "message": "Video posted successfully",
                    "processing_time": f"{elapsed:.2f}s"
                }), 200
            else:
                logger.error(f"[{request_id}] Falha ao postar vídeo após {elapsed:.2f}s")
                return jsonify({
                    "error": "Post failed",
                    "message": "Failed to post the video",
                    "processing_time": f"{elapsed:.2f}s"
                }), 500

        except Exception as bot_error:
            error_traceback = traceback.format_exc()
            logger.error(f"[{request_id}] Erro na execução do bot: {str(bot_error)}\n{error_traceback}")
            
            # Garante que o navegador seja fechado mesmo em caso de erro
            if bot:
                try:
                    bot.close()
                except Exception as close_error:
                    logger.error(f"[{request_id}] Erro adicional ao fechar o navegador: {str(close_error)}")
            
            return jsonify({
                "error": "Bot execution error",
                "message": str(bot_error)
            }), 500

    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"[{request_id}] Erro geral na API: {str(e)}\n{error_traceback}")
        
        # Garante que o bot seja fechado em caso de erro
        if 'bot' in locals():
            try:
                bot.close()
            except:
                pass
        
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Iniciando servidor TikTok Poster API na porta 3090")
    try:
        app.run(host='0.0.0.0', port=3090)
    except Exception as e:
        logger.critical(f"Falha ao iniciar servidor: {str(e)}")
        sys.exit(1)