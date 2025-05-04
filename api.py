from flask import Flask, request, jsonify
from flask_cors import CORS
from tiktok_bot import TikTokBot, AutomationBlockType, DetectionResult
import json
import os
import traceback
import platform
import subprocess
import sys
import base64
import logging
from datetime import datetime

# Configuração do sistema de logs
log_dir = os.path.join(os.getcwd(), 'logs')
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except:
        pass

# Configuração do logger
logger = logging.getLogger('tiktok_api')
logger.setLevel(logging.DEBUG)

# Handler para arquivo
log_file = os.path.join(log_dir, f'tiktok_api_{datetime.now().strftime("%Y%m%d")}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formato detalhado para logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Adiciona os handlers ao logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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
            
            logger.info(f"✅ Display virtual configurado: DISPLAY={os.environ['DISPLAY']}")
            return True
        except subprocess.CalledProcessError:
            logger.warning("⚠️ Xvfb não encontrado. Execute: apt-get install -y xvfb")
            return False
        except Exception as e:
            logger.error(f"⚠️ Erro ao configurar display virtual: {e}")
            return False
    return True

# Configura o display virtual se necessário
setup_display_if_needed()

# Classe para capturar URLs e outros dados durante a execução
class TikTokSessionMonitor:
    def __init__(self):
        self.current_url = None
        self.session_state = "initialized"
        self.page_source = None
        self.last_error = None
        self.navigation_history = []
        self.log_timestamps = {}
    
    def update_url(self, url, note=None):
        """Atualiza a URL atual e registra no histórico de navegação"""
        self.current_url = url
        timestamp = datetime.now().isoformat()
        self.navigation_history.append({
            "url": url,
            "timestamp": timestamp,
            "note": note
        })
        self.log_timestamps[timestamp] = note or "URL navegada"
        logger.info(f"🔗 URL atual: {url} | Nota: {note}")
        
        # Verifica se há indicativos de captcha ou verificação na URL
        captcha_indicators = ["captcha", "verify", "verification", "security", "check", "human"]
        for indicator in captcha_indicators:
            if indicator in url.lower():
                logger.warning(f"⚠️ ALERTA: Possível verificação/captcha detectado na URL: '{indicator}' em {url}")
                self.session_state = "possible_captcha"
                break
    
    def update_state(self, state, details=None):
        """Atualiza o estado da sessão"""
        self.session_state = state
        timestamp = datetime.now().isoformat()
        self.log_timestamps[timestamp] = f"Estado: {state} - {details}"
        logger.info(f"📊 Estado da sessão: {state} | Detalhes: {details}")
    
    def log_page_info(self, driver=None, note=None):
        """Captura e loga informações da página atual"""
        if not driver:
            logger.warning("⚠️ Driver não fornecido para log_page_info")
            return
        
        try:
            current_url = driver.current_url
            self.update_url(current_url, note)
            
            # Tenta capturar o título
            try:
                page_title = driver.title
                logger.info(f"📑 Título da página: {page_title}")
            except:
                logger.warning("⚠️ Não foi possível obter o título da página")
            
            # Verifica se há indícios de CAPTCHA no título
            if page_title and any(term in page_title.lower() for term in 
                              ["captcha", "security", "verification", "human", "robot"]):
                logger.warning(f"⚠️ ALERTA: Possível captcha detectado no título: {page_title}")
                self.session_state = "possible_captcha"
            
            # Verifica elementos específicos (como iframes de CAPTCHA)
            try:
                iframes = driver.find_elements("tag name", "iframe")
                if iframes:
                    iframe_srcs = [iframe.get_attribute("src") for iframe in iframes if iframe.is_displayed()]
                    for src in iframe_srcs:
                        if src and any(term in str(src).lower() for term in 
                                    ["captcha", "security", "verification"]):
                            logger.warning(f"⚠️ ALERTA: Possível iframe de captcha detectado: {src}")
                            self.session_state = "captcha_iframe_detected"
            except Exception as e:
                logger.warning(f"⚠️ Erro ao verificar iframes: {e}")
            
            # Tenta salvar um screenshot para o log
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_screenshot_path = os.path.join(log_dir, f"screen_{timestamp}.png")
                driver.save_screenshot(log_screenshot_path)
                logger.info(f"📸 Screenshot salvo: {log_screenshot_path}")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível salvar screenshot: {e}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao capturar informações da página: {e}")
            self.last_error = str(e)

# Instância global do monitor
session_monitor = TikTokSessionMonitor()

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Rota para verificar se a API está funcionando"""
    # Verifica se estamos em um ambiente de servidor
    is_server = platform.system() == "Linux" and not os.environ.get('DISPLAY', '').startswith(':0')
    
    response = {
        "status": "ok", 
        "message": "API is running",
        "environment": {
            "os": platform.system(),
            "release": platform.release(),
            "display": os.environ.get('DISPLAY', 'None'),
            "is_server": is_server,
            "python_version": platform.python_version(),
            "timestamp": datetime.now().isoformat()
        },
        "session_monitor": {
            "current_url": session_monitor.current_url,
            "session_state": session_monitor.session_state,
            "navigation_history": session_monitor.navigation_history[-5:] if session_monitor.navigation_history else []
        }
    }
    
    logger.info(f"✅ Health check executado: {json.dumps(response, indent=2)}")
    return jsonify(response), 200

@app.route('/diagnose', methods=['POST'])
def diagnose():
    """
    Endpoint que apenas executa uma sessão de diagnóstico sem tentar postar vídeo.
    Útil para identificar problemas de acesso ou bloqueios.
    """
    bot = None
    try:
        # Log de início da requisição
        logger.info(f"🔍 Nova solicitação de diagnóstico recebida")
        
        # Limpa o monitor de sessão para esta nova requisição
        session_monitor.current_url = None
        session_monitor.session_state = "initialized"
        session_monitor.navigation_history = []
        
        # Pega os dados do request
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        required_fields = ['session_id']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"❌ Campos obrigatórios ausentes: {missing_fields}")
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        # Gera diretório de debug específico para este diagnóstico
        debug_dir = os.path.join(
            os.getcwd(), 
            'debug_data', 
            f"diag_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Configuração dos parâmetros para o diagnóstico
        bot_params = {
            'session_id': data['session_id'],
            'sid_tt': data.get('sid_tt', data['session_id']),
            'video_url': data.get('video_url', 'https://example.com/sample.mp4'),  # URL fictícia, não será usada
            'debug_dir': debug_dir,
            'use_proxy': data.get('use_proxy', False),
            'proxy': data.get('proxy', None),
            'headless': data.get('headless', False),  # Diagnóstico é melhor com headless=False
            'wait_time_multiplier': data.get('wait_time_multiplier', 1.2),
            'session_monitor': session_monitor  # Passa o monitor para o bot
        }

        # Log de parâmetros recebidos (oculta session_id por segurança)
        safe_params = {**bot_params}
        safe_params['session_id'] = safe_params['session_id'][:5] + '...' if safe_params['session_id'] else None
        safe_params['sid_tt'] = safe_params['sid_tt'][:5] + '...' if safe_params['sid_tt'] else None
        safe_params.pop('session_monitor', None)  # Remove o objeto da saída de log
        logger.info(f"📝 Parâmetros do diagnóstico: {json.dumps(safe_params, indent=2)}")

        # Inicializa o bot e coleta os resultados
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "screenshots": [],
            "is_blocked": False,
            "block_type": None,
            "recommendations": [],
            "navigation": session_monitor.navigation_history
        }
        
        # Instancia o bot com os parâmetros
        bot = TikTokBot(bot_params)
        
        try:
            # Etapa 1: Injeção de sessão
            logger.info("🔑 Injetando sessão...")
            session_result = bot.inject_session()
            
            # Captura informações da URL atual
            if bot.driver:
                session_monitor.log_page_info(bot.driver, "Após injeção de sessão")
                
            # Coleta informações da detecção
            if bot.detector and bot.detector.last_detection:
                detection = bot.detector.last_detection
                step_result = {
                    "step": "inject_session",
                    "success": session_result,
                    "is_blocked": detection.is_blocked,
                    "block_type": detection.block_type.value if detection.is_blocked else None,
                    "details": detection.details,
                    "current_url": session_monitor.current_url
                }
                
                # Adiciona screenshot se disponível
                if detection.screenshot_path and os.path.exists(detection.screenshot_path):
                    try:
                        with open(detection.screenshot_path, "rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                            results["screenshots"].append({
                                "step": "inject_session",
                                "data": base64_image,
                                "timestamp": detection.timestamp.isoformat()
                            })
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao processar screenshot: {e}")
                
                # Atualiza o status global
                if detection.is_blocked:
                    results["is_blocked"] = True
                    results["block_type"] = detection.block_type.value
                    results["recommendations"] = detection.get_recommendations()
                    logger.warning(f"🚨 Bloqueio detectado durante injeção de sessão: {detection.block_type.value}")
            else:
                step_result = {
                    "step": "inject_session",
                    "success": session_result,
                    "is_blocked": False,
                    "current_url": session_monitor.current_url
                }
            
            results["steps"].append(step_result)
            
            # Se a injeção de sessão falhou, pare aqui
            if not session_result:
                logger.error("❌ Falha na injeção de sessão")
                if bot.driver:
                    try:
                        # Captura o HTML da página atual
                        page_source = bot.driver.page_source
                        page_source_path = os.path.join(debug_dir, "failed_session_page.html")
                        with open(page_source_path, "w", encoding="utf-8") as f:
                            f.write(page_source)
                        logger.info(f"📄 HTML da página salvo em: {page_source_path}")
                    except Exception as e:
                        logger.warning(f"⚠️ Não foi possível salvar o HTML da página: {e}")
                        
                bot.close()
                results["navigation"] = session_monitor.navigation_history
                return jsonify(results), 200

            # Etapa 2: Teste de login
            logger.info("🔒 Testando autenticação...")
            login_result = bot.test_login()
            
            # Captura informações da URL atual
            if bot.driver:
                session_monitor.log_page_info(bot.driver, "Após teste de login")
            
            # Coleta informações da detecção
            if bot.detector and bot.detector.last_detection:
                detection = bot.detector.last_detection
                step_result = {
                    "step": "test_login",
                    "success": login_result,
                    "is_blocked": detection.is_blocked,
                    "block_type": detection.block_type.value if detection.is_blocked else None,
                    "details": detection.details,
                    "current_url": session_monitor.current_url
                }
                
                # Adiciona screenshot se disponível
                if detection.screenshot_path and os.path.exists(detection.screenshot_path):
                    try:
                        with open(detection.screenshot_path, "rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                            results["screenshots"].append({
                                "step": "test_login",
                                "data": base64_image,
                                "timestamp": detection.timestamp.isoformat()
                            })
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao processar screenshot: {e}")
                
                # Atualiza o status global
                if detection.is_blocked and not results["is_blocked"]:
                    results["is_blocked"] = True
                    results["block_type"] = detection.block_type.value
                    results["recommendations"] = detection.get_recommendations()
                    logger.warning(f"🚨 Bloqueio detectado durante teste de login: {detection.block_type.value}")
            else:
                step_result = {
                    "step": "test_login",
                    "success": login_result,
                    "is_blocked": False,
                    "current_url": session_monitor.current_url
                }
            
            results["steps"].append(step_result)
            
            # Se a detecção achou bloqueios, mas o teste de login passou,
            # inclui informações adicionais
            if login_result and bot.detector:
                analysis = bot.detector.analyze_page_elements()
                results["page_analysis"] = analysis
                logger.info(f"📊 Análise da página: {json.dumps(analysis, indent=2)}")
            
            # Fecha o navegador
            bot.close()
            
            # Adiciona o histórico de navegação completo
            results["navigation"] = session_monitor.navigation_history
            
            # Finaliza o diagnóstico
            logger.info("✅ Diagnóstico concluído!")
            return jsonify(results), 200

        finally:
            # Garante que o navegador seja fechado
            if bot:
                try:
                    bot.close()
                except Exception as close_error:
                    logger.warning(f"⚠️ Erro ao fechar navegador: {close_error}")

    except Exception as e:
        # Log do erro detalhado para debug
        error_trace = traceback.format_exc()
        logger.error(f"❌ Erro no diagnóstico: {str(e)}")
        logger.error(f"📑 Stacktrace:\n{error_trace}")
        
        # Garante que o bot seja fechado em caso de erro
        if 'bot' in locals() and bot:
            try:
                bot.close()
            except:
                pass
        
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "status": "error",
            "navigation": session_monitor.navigation_history
        }), 500

@app.route('/post-video', methods=['POST'])
def post_video():
    """Rota principal para postar vídeo no TikTok"""
    bot = None
    try:
        # Log de início da requisição
        logger.info(f"🔄 Nova requisição recebida em {request.path}")
        
        # Limpa o monitor de sessão para esta nova requisição
        session_monitor.current_url = None
        session_monitor.session_state = "initialized"
        session_monitor.navigation_history = []
        
        # Pega os dados do request
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        required_fields = ['session_id', 'video_url']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"❌ Campos obrigatórios ausentes: {missing_fields}")
            return jsonify({
                "error": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        # Gera diretório de debug específico para esta postagem
        debug_dir = os.path.join(
            os.getcwd(), 
            'debug_data', 
            f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

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
            'wait_time_multiplier': data.get('wait_time_multiplier', 1.5),  # Aumenta tempos de espera por padrão
            'debug_dir': debug_dir,
            'save_diagnostics': data.get('save_diagnostics', True),
            'session_monitor': session_monitor  # Passa o monitor para o bot
        }

        # Validações adicionais
        if not isinstance(bot_params['hashtags'], list):
            logger.warning("❌ Formato inválido de hashtags")
            return jsonify({
                "error": "Invalid hashtags format",
                "message": "Hashtags must be a list of strings"
            }), 400

        if not isinstance(bot_params['music_volume'], (int, float)) or \
           not 0 <= bot_params['music_volume'] <= 100:
            logger.warning("❌ Volume de música inválido")
            return jsonify({
                "error": "Invalid music volume",
                "message": "Music volume must be a number between 0 and 100"
            }), 400
            
        # Validação de proxy se fornecido
        if bot_params['use_proxy'] and not bot_params['proxy']:
            logger.warning("❌ Proxy não fornecido com use_proxy=true")
            return jsonify({
                "error": "Proxy configuration error",
                "message": "When use_proxy is true, you must provide a proxy URL"
            }), 400

        # Log de parâmetros recebidos (oculta session_id por segurança)
        safe_params = {**bot_params}
        safe_params['session_id'] = safe_params['session_id'][:5] + '...' if safe_params['session_id'] else None
        safe_params['sid_tt'] = safe_params['sid_tt'][:5] + '...' if safe_params['sid_tt'] else None
        safe_params.pop('session_monitor', None)  # Remove o objeto da saída de log
        logger.info(f"📝 Parâmetros da requisição: {json.dumps(safe_params, indent=2)}")

        # Inicializa dados de resposta
        response_data = {
            "status": "processing",
            "timestamp": datetime.now().isoformat(),
            "detection": {
                "is_blocked": False,
                "block_type": None,
                "recommendations": []
            },
            "navigation": session_monitor.navigation_history
        }

        # Instancia o bot com os parâmetros
        bot = TikTokBot(bot_params)
        
        try:
            # Executa o processo de postagem
            logger.info("🔑 Injetando sessão...")
            if not bot.inject_session():
                # Captura informações da URL atual
                if bot.driver:
                    session_monitor.log_page_info(bot.driver, "Falha na injeção de sessão")
                    
                    # Tenta capturar o HTML da página
                    try:
                        page_source = bot.driver.page_source
                        page_source_path = os.path.join(debug_dir, "failed_session_page.html")
                        with open(page_source_path, "w", encoding="utf-8") as f:
                            f.write(page_source)
                        logger.info(f"📄 HTML da página salvo em: {page_source_path}")
                    except Exception as e:
                        logger.warning(f"⚠️ Não foi possível salvar o HTML da página: {e}")
                
                # Verifica se houve detecção de bloqueio
                if bot.detector and bot.detector.last_detection and bot.detector.last_detection.is_blocked:
                    detection = bot.detector.last_detection
                    response_data["detection"] = {
                        "is_blocked": True,
                        "block_type": detection.block_type.value,
                        "recommendations": detection.get_recommendations(),
                        "details": detection.details
                    }
                    response_data["status"] = "blocked"
                    logger.warning(f"🚨 Bloqueio detectado: {detection.block_type.value}")
                else:
                    response_data["status"] = "failed"
                    logger.error("❌ Falha na injeção de sessão sem bloqueio detectado")
                
                # Adiciona o histórico de navegação
                response_data["navigation"] = session_monitor.navigation_history
                
                bot.close()
                return jsonify({
                    "error": "Session injection failed",
                    "message": "Could not inject session cookies",
                    "diagnostics": response_data
                }), 500

            logger.info("🔒 Testando autenticação...")
            if not bot.test_login():
                # Captura informações da URL atual
                if bot.driver:
                    session_monitor.log_page_info(bot.driver, "Falha no teste de login")
                    
                    # Tenta capturar o HTML da página
                    try:
                        page_source = bot.driver.page_source
                        page_source_path = os.path.join(debug_dir, "failed_login_page.html")
                        with open(page_source_path, "w", encoding="utf-8") as f:
                            f.write(page_source)
                        logger.info(f"📄 HTML da página salvo em: {page_source_path}")
                    except Exception as e:
                        logger.warning(f"⚠️ Não foi possível salvar o HTML da página: {e}")
                
                # Verifica se houve detecção de bloqueio
                if bot.detector and bot.detector.last_detection and bot.detector.last_detection.is_blocked:
                    detection = bot.detector.last_detection
                    response_data["detection"] = {
                        "is_blocked": True,
                        "block_type": detection.block_type.value,
                        "recommendations": detection.get_recommendations(),
                        "details": detection.details
                    }
                    response_data["status"] = "blocked"
                    logger.warning(f"🚨 Bloqueio detectado: {detection.block_type.value}")
                else:
                    response_data["status"] = "unauthorized"
                    logger.error("❌ Falha no teste de login sem bloqueio detectado")
                
                # Adiciona o histórico de navegação
                response_data["navigation"] = session_monitor.navigation_history
                
                bot.close()
                return jsonify({
                    "error": "Authentication failed",
                    "message": "Invalid session ID or cookies rejected",
                    "diagnostics": response_data
                }), 401

            # Tenta postar o vídeo
            logger.info("📤 Iniciando processo de postagem do vídeo...")
            post_result = bot.post_video()
            
            # Captura informações da URL atual
            if bot.driver:
                session_monitor.log_page_info(bot.driver, "Após tentativa de postagem")
            
            # Fecha o navegador independente do resultado
            bot.close()
            
            # Adiciona o histórico de navegação
            response_data["navigation"] = session_monitor.navigation_history
            
            # Verifica o resultado e se houve bloqueios durante a postagem
            if post_result:
                logger.info("✅ Vídeo postado com sucesso!")
                response_data["status"] = "success"
                return jsonify({
                    "status": "success",
                    "message": "Video posted successfully",
                    "diagnostics": response_data
                }), 200
            else:
                logger.error("❌ Falha ao postar o vídeo")
                
                # Verifica se houve detecção de bloqueio
                if bot.detector and bot.detector.last_detection and bot.detector.last_detection.is_blocked:
                    detection = bot.detector.last_detection
                    response_data["detection"] = {
                        "is_blocked": True,
                        "block_type": detection.block_type.value,
                        "recommendations": detection.get_recommendations(),
                        "details": detection.details
                    }
                    response_data["status"] = "blocked"
                    logger.warning(f"🚨 Bloqueio detectado: {detection.block_type.value}")
                else:
                    response_data["status"] = "failed"
                    logger.error("❌ Falha na postagem sem bloqueio específico detectado")
                
                return jsonify({
                    "error": "Post failed",
                    "message": "Failed to post the video. Check server logs for details.",
                    "diagnostics": response_data
                }), 500

        finally:
            # Garante que o navegador seja fechado mesmo em caso de erro
            if bot:
                try:
                    bot.close()
                except Exception as close_error:
                    logger.warning(f"⚠️ Erro ao fechar navegador: {close_error}")

    except Exception as e:
        # Log do erro detalhado para debug
        error_trace = traceback.format_exc()
        logger.error(f"❌ Erro na API: {str(e)}")
        logger.error(f"📑 Stacktrace:\n{error_trace}")
        
        # Garante que o bot seja fechado em caso de erro
        if 'bot' in locals() and bot:
            try:
                bot.close()
            except:
                pass
        
        # Adiciona o histórico de navegação se disponível
        navigation_history = session_monitor.navigation_history if hasattr(session_monitor, 'navigation_history') else []
        
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "navigation": navigation_history
        }), 500

if __name__ == '__main__':
    # Determina a porta padrão ou usa 3090
    port = int(os.environ.get('PORT', 3090))
    
    # Mostra informações sobre o ambiente
    logger.info(f"🚀 Iniciando API TikTok Poster")
    logger.info(f"💻 Sistema: {platform.system()} {platform.release()}")
    logger.info(f"🖥️ Display: {os.environ.get('DISPLAY', 'Nenhum')}")
    logger.info(f"🌐 Porta: {port}")
    logger.info(f"📝 Arquivo de log: {log_file}")
    
    # Cria diretório para diagnósticos se não existir
    debug_dir = os.path.join(os.getcwd(), 'debug_data')
    if not os.path.exists(debug_dir):
        try:
            os.makedirs(debug_dir)
            logger.info(f"📁 Diretório de diagnóstico criado: {debug_dir}")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível criar diretório de diagnóstico: {e}")
    
    # Executa a API
    app.run(host='0.0.0.0', port=port, threaded=True)