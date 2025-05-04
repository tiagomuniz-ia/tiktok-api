from flask import Flask, request, jsonify
from flask_cors import CORS
from tiktok_bot import TikTokBot
import json
import os
import traceback
import platform
import subprocess
import sys

# Configuração de ambiente para servidores Linux
def setup_display_if_needed():
    """Configura um display virtual se necessário"""
    if platform.system() == "Linux" and not os.environ.get('DISPLAY'):
        try:
            # Verifica se Xvfb está instalado
            subprocess.run(["which", "Xvfb"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Configura um display virtual
            display_num = 99
            os.environ['DISPLAY'] = f":{display_num}"
            
            # Inicia o Xvfb em background
            subprocess.Popen([
                "Xvfb", f":{display_num}", "-screen", "0", "1920x1080x24", "-ac"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"✅ Display virtual configurado: DISPLAY={os.environ['DISPLAY']}")
            return True
        except subprocess.CalledProcessError:
            print("⚠️ Xvfb não encontrado. Execute: apt-get install -y xvfb")
            return False
        except Exception as e:
            print(f"⚠️ Erro ao configurar display virtual: {e}")
            return False
    return True

# Configura o display virtual se necessário
setup_display_if_needed()

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Rota para verificar se a API está funcionando"""
    # Verifica se estamos em um ambiente de servidor
    is_server = platform.system() == "Linux" and not os.environ.get('DISPLAY', '').startswith(':0')
    
    return jsonify({
        "status": "ok", 
        "message": "API is running",
        "environment": {
            "os": platform.system(),
            "display": os.environ.get('DISPLAY', 'None'),
            "is_server": is_server
        }
    }), 200

@app.route('/post-video', methods=['POST'])
def post_video():
    """Rota principal para postar vídeo no TikTok"""
    bot = None
    try:
        # Log de início da requisição
        print(f"🔄 Nova requisição recebida em {request.path}")
        
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
            'music_volume': data.get('music_volume', 50),
            
            # Novos parâmetros
            'use_proxy': data.get('use_proxy', False),
            'proxy': data.get('proxy', None),
            'headless': data.get('headless', True),  # Por padrão, usa headless em servidores
            'wait_time_multiplier': data.get('wait_time_multiplier', 1.5)  # Aumenta tempos de espera por padrão
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
            
        # Validação de proxy se fornecido
        if bot_params['use_proxy'] and not bot_params['proxy']:
            return jsonify({
                "error": "Proxy configuration error",
                "message": "When use_proxy is true, you must provide a proxy URL"
            }), 400

        # Log de parâmetros recebidos (oculta session_id por segurança)
        safe_params = {**bot_params}
        safe_params['session_id'] = safe_params['session_id'][:5] + '...' if safe_params['session_id'] else None
        safe_params['sid_tt'] = safe_params['sid_tt'][:5] + '...' if safe_params['sid_tt'] else None
        print(f"📝 Parâmetros da requisição: {json.dumps(safe_params, indent=2)}")

        # Instancia o bot com os parâmetros
        bot = TikTokBot(bot_params)
        
        try:
            # Executa o processo de postagem
            print("🔑 Injetando sessão...")
            if not bot.inject_session():
                bot.close()
                return jsonify({
                    "error": "Session injection failed",
                    "message": "Could not inject session cookies"
                }), 500

            print("🔒 Testando autenticação...")
            if not bot.test_login():
                bot.close()
                return jsonify({
                    "error": "Authentication failed",
                    "message": "Invalid session ID or cookies rejected"
                }), 401

            # Tenta postar o vídeo
            print("📤 Iniciando processo de postagem do vídeo...")
            post_result = bot.post_video()
            
            # Fecha o navegador independente do resultado
            bot.close()
            
            if post_result:
                print("✅ Vídeo postado com sucesso!")
                return jsonify({
                    "status": "success",
                    "message": "Video posted successfully"
                }), 200
            else:
                print("❌ Falha ao postar o vídeo")
                return jsonify({
                    "error": "Post failed",
                    "message": "Failed to post the video. Check server logs for details."
                }), 500

        finally:
            # Garante que o navegador seja fechado mesmo em caso de erro
            if bot:
                try:
                    bot.close()
                except Exception as close_error:
                    print(f"⚠️ Erro ao fechar navegador: {close_error}")

    except Exception as e:
        # Log do erro detalhado para debug
        error_trace = traceback.format_exc()
        print(f"❌ Erro na API: {str(e)}")
        print(f"📑 Stacktrace:\n{error_trace}")
        
        # Garante que o bot seja fechado em caso de erro
        if 'bot' in locals() and bot:
            try:
                bot.close()
            except:
                pass
        
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Determina a porta padrão ou usa 3090
    port = int(os.environ.get('PORT', 3090))
    
    # Mostra informações sobre o ambiente
    print(f"🚀 Iniciando API TikTok Poster")
    print(f"💻 Sistema: {platform.system()} {platform.release()}")
    print(f"🖥️ Display: {os.environ.get('DISPLAY', 'Nenhum')}")
    print(f"🌐 Porta: {port}")
    
    # Executa a API
    app.run(host='0.0.0.0', port=port, threaded=True)