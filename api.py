from flask import Flask, request, jsonify
from flask_cors import CORS
from tiktok_bot import TikTokBot
import json

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Rota para verificar se a API está funcionando"""
    return jsonify({"status": "ok", "message": "API is running"}), 200

@app.route('/post-video', methods=['POST'])
def post_video():
    """Rota principal para postar vídeo no TikTok"""
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

        # Instancia o bot com os parâmetros
        bot = TikTokBot(bot_params)
        
        try:
            # Executa o processo de postagem
            if not bot.inject_session():
                bot.close()
                return jsonify({
                    "error": "Session injection failed",
                    "message": "Could not inject session"
                }), 500

            if not bot.test_login():
                bot.close()
                return jsonify({
                    "error": "Authentication failed",
                    "message": "Invalid session ID"
                }), 401

            # Tenta postar o vídeo
            post_result = bot.post_video()
            
            # Fecha o navegador independente do resultado
            bot.close()
            
            if post_result:
                return jsonify({
                    "status": "success",
                    "message": "Video posted successfully"
                }), 200
            else:
                return jsonify({
                    "error": "Post failed",
                    "message": "Failed to post the video"
                }), 500

        finally:
            # Garante que o navegador seja fechado mesmo em caso de erro
            if bot:
                try:
                    bot.close()
                except:
                    pass

    except Exception as e:
        # Log do erro para debug
        print(f"Erro na API: {str(e)}")
        
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
    app.run(host='0.0.0.0', port=3090)