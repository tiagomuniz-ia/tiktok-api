from flask import Flask, request, jsonify
from flask_cors import CORS
from tiktok_bot import TikTokBot
import json
import time
import random
from functools import wraps

app = Flask(__name__)
CORS(app)

def retry_with_backoff(max_retries=3, initial_delay=1):
    """Decorator para implementar retry com backoff exponencial"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise e
                        
                    delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"⚠️ Tentativa {attempt + 1} falhou, tentando novamente em {delay:.2f}s")
                    print(f"Erro: {str(e)}")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

@app.route('/health', methods=['GET'])
def health_check():
    """Rota para verificar se a API está funcionando"""
    return jsonify({"status": "ok", "message": "API is running"}), 200

@app.route('/post-video', methods=['POST'])
@retry_with_backoff(max_retries=3)
def post_video():
    """Rota principal para postar vídeo no TikTok"""
    bot = None
    try:
        # Pega os dados do request
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        required_fields = ['session_id', 'video_url']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
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
            return jsonify({
                "error": "Invalid hashtags format",
                "message": "Hashtags must be a list of strings"
            }), 400

        if not isinstance(bot_params['music_volume'], (int, float)) or \
           not 0 <= bot_params['music_volume'] <= 100:
            return jsonify({
                "error": "Invalid music volume",
                "message": "Music volume must be a number between 0 and 100"
            }), 400

        # Instancia o bot com os parâmetros e tenta cada operação com retry
        bot = TikTokBot(bot_params)
        
        # Tenta injetar a sessão com retry
        def inject_session_with_retry():
            if not bot.retry_with_backoff(bot.inject_session):
                raise Exception("Failed to inject session after retries")
        inject_session_with_retry()

        # Testa o login com retry
        def test_login_with_retry():
            if not bot.retry_with_backoff(bot.test_login):
                raise Exception("Failed to login after retries")
        test_login_with_retry()

        # Tenta postar o vídeo com retry
        def post_video_with_retry():
            if not bot.retry_with_backoff(bot.post_video):
                raise Exception("Failed to post video after retries")
        post_video_with_retry()
            
        return jsonify({
            "status": "success",
            "message": "Video posted successfully"
        }), 200

    except Exception as e:
        error_message = str(e)
        error_type = type(e).__name__
        
        # Mapeia diferentes tipos de erro para códigos HTTP apropriados
        status_code = 500
        if "Session" in error_message or "login" in error_message.lower():
            status_code = 401
        elif "validation" in error_message.lower():
            status_code = 400
        elif "timeout" in error_message.lower():
            status_code = 504
            
        # Log detalhado do erro
        print(f"❌ Erro ({error_type}): {error_message}")
        
        return jsonify({
            "error": error_type,
            "message": error_message
        }), status_code

    finally:
        # Garante que o bot seja fechado mesmo em caso de erro
        if bot:
            try:
                bot.close()
            except Exception as e:
                print(f"⚠️ Erro ao fechar o bot: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3090, threaded=True)