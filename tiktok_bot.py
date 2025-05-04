from selenium import webdriver
import undetected_chromedriver as uc
import time
import random
import requests
import tempfile
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from difflib import SequenceMatcher
from urllib.parse import urlparse

class TikTokBot:
    def __init__(self, params):
        """
        Inicializa o bot com os parâmetros recebidos
        params: dicionário com os parâmetros da API
        """
        if not params:
            raise ValueError("Parâmetros não podem ser nulos")
            
        self.session_id = params['session_id']
        self.sid_tt = params.get('sid_tt', self.session_id)  # Usa session_id como fallback
        self.video_url = params['video_url']
        self.video_caption = params.get('video_caption', '')
        self.hashtags = params.get('hashtags', [])
        self.music_name = params.get('music_name', '')
        self.music_volume = int(params.get('music_volume', 50))
        
        self.driver = None
        self.setup_browser()

    def setup_browser(self):
        """Configura o navegador com as opções necessárias para evitar detecção"""
        try:
            def create_options():
                options = uc.ChromeOptions()
                
                # Configurações essenciais para servidor Linux
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-extensions')
                
                # Mudança para --headless=new que é mais estável em servidores
                options.add_argument('--headless=new')
                
                options.add_argument('--window-size=1920,1080')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--lang=pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7')
                
                # Configurações adicionais para evitar erros comuns
                options.add_argument('--disable-infobars')
                options.add_argument('--disable-notifications')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                
                # Configurações específicas para melhorar o desempenho headless
                options.add_argument('--hide-scrollbars')
                options.add_argument('--mute-audio')
                options.add_argument('--disable-web-security')
                options.add_argument('--disable-features=IsolateOrigins,site-per-process')
                
                # Configuração para evitar erro de webrtc
                options.add_argument('--use-fake-ui-for-media-stream')
                options.add_argument('--use-fake-device-for-media-stream')
                
                # User Agent Linux compatível
                options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36')
                
                # Configurações experimentais
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Configurações de preferências
                prefs = {
                    'profile.default_content_setting_values.notifications': 2,
                    'credentials_enable_service': False,
                    'profile.password_manager_enabled': False,
                    'profile.managed_default_content_settings.images': 1,  # 1 = permitir imagens
                    'disk-cache-size': 4096  # 4MB
                }
                options.add_experimental_option('prefs', prefs)
                
                return options

            # Primeira tentativa com a versão mais recente do Chrome
            try:
                print("🔄 Iniciando Chrome (primeira tentativa)...")
                self.driver = uc.Chrome(
                    options=create_options(),
                    version_main=136,
                    headless=True,
                    use_subprocess=True,
                    driver_executable_path=None,
                    browser_executable_path=None
                )
            except Exception as e:
                print(f"⚠️ Tentativa com Chrome 136 falhou: {e}")
                # Segunda tentativa sem especificar versão
                try:
                    print("🔄 Iniciando Chrome (segunda tentativa, sem versão específica)...")
                    self.driver = uc.Chrome(
                        options=create_options(),
                        headless=True,
                        use_subprocess=True,
                        driver_executable_path=None,
                        browser_executable_path=None
                    )
                except Exception as e2:
                    print(f"⚠️ Segunda tentativa falhou: {e2}")
                    
                    # Terceira tentativa usando método alternativo
                    try:
                        print("🔄 Iniciando Chrome (terceira tentativa, método alternativo)...")
                        options = create_options()
                        # Usando Selenium padrão como fallback
                        from selenium.webdriver.chrome.service import Service
                        self.driver = webdriver.Chrome(options=options)
                    except Exception as e3:
                        print(f"⚠️ Terceira tentativa falhou: {e3}")
                        raise e3
            
            # Configura timeouts
            self.driver.set_page_load_timeout(60)  # Aumentado para 60 segundos
            self.driver.implicitly_wait(15)  # Aumentado para 15 segundos
            
            # Script anti-detecção avançado
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    // Modifica navigator.webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Modifica navigator.languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['pt-BR', 'pt', 'en-US', 'en']
                    });
                    
                    // Emula funções de navegador regulares
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Emula função navigator.permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                    );
                    
                    // Esconde sinais de automação
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // Esconde sinais de automação no canvas
                    const originalGetContext = HTMLCanvasElement.prototype.getContext;
                    HTMLCanvasElement.prototype.getContext = function(type) {
                        if (type === '2d') {
                            const context = originalGetContext.apply(this, arguments);
                            const originalFillText = context.fillText;
                            context.fillText = function() {
                                return originalFillText.apply(this, arguments);
                            }
                            return context;
                        }
                        return originalGetContext.apply(this, arguments);
                    };
                '''
            })
            
            print("✅ Navegador iniciado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar o navegador: {e}")
            return False

    def inject_session(self):
        """Injeta os cookies de sessão para autenticação"""
        try:
            if not self.driver:
                return False

            print("🔄 Iniciando injeção de cookies...")
            
            # Primeiro acessa uma página neutra do TikTok
            print("🌐 Acessando TikTok...")
            self.driver.get('https://www.tiktok.com/explore')
            time.sleep(random.uniform(3, 5))

            # Define os cookies com todos os atributos necessários
            cookies = [
                {
                    'name': 'sessionid',
                    'value': self.session_id,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'secure': True,
                    'httpOnly': True,
                    'sameSite': 'Lax',
                    'expiry': int(time.time()) + 86400 * 30  # 30 dias
                },
                {
                    'name': 'sessionid_ss',
                    'value': self.session_id,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'secure': True,
                    'httpOnly': True,
                    'sameSite': 'Lax',
                    'expiry': int(time.time()) + 86400 * 30
                },
                {
                    'name': 'sid_tt',
                    'value': self.sid_tt,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'secure': True,
                    'httpOnly': True,
                    'sameSite': 'Lax',
                    'expiry': int(time.time()) + 86400 * 30
                },
                {
                    'name': 'tt_chain_token',
                    'value': '',
                    'domain': '.tiktok.com',
                    'path': '/',
                    'secure': True,
                    'sameSite': 'Lax'
                },
                # Cookies adicionais que podem ser necessários
                {
                    'name': 'tt_csrf_token',
                    'value': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32)),
                    'domain': '.tiktok.com',
                    'path': '/',
                    'secure': True,
                    'sameSite': 'Lax',
                    'expiry': int(time.time()) + 86400 * 30
                },
                {
                    'name': 'cmpl_token',
                    'value': ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_', k=24)),
                    'domain': '.tiktok.com',
                    'path': '/',
                    'secure': True,
                    'httpOnly': True,
                    'sameSite': 'Lax',
                    'expiry': int(time.time()) + 86400 * 30
                }
            ]

            # Simula comportamento humano com pausas aleatórias
            time.sleep(random.uniform(1, 2))
            
            # Limpa cookies existentes
            self.driver.delete_all_cookies()
            time.sleep(random.uniform(1, 2))
            
            # Adiciona cada cookie com tratamento de erro individual
            cookies_added = 0
            for cookie in cookies:
                try:
                    print(f"🍪 Adicionando cookie: {cookie['name']}")
                    self.driver.add_cookie(cookie)
                    cookies_added += 1
                    time.sleep(random.uniform(0.5, 1))  # Pausa aleatória entre cookies
                except Exception as cookie_error:
                    print(f"⚠️ Erro ao adicionar cookie {cookie['name']}: {cookie_error}")
                    continue
            
            print(f"✅ {cookies_added} cookies adicionados com sucesso")
            
            # Aguarda com tempo aleatório
            time.sleep(random.uniform(2, 3))
            
            # Recarrega a página
            print("🔄 Recarregando página para aplicar cookies...")
            self.driver.refresh()
            time.sleep(random.uniform(3, 5))
            
            # Verifica se os cookies foram adicionados corretamente
            actual_cookies = self.driver.get_cookies()
            session_cookies = [c for c in actual_cookies if c['name'] in ['sessionid', 'sessionid_ss', 'sid_tt']]
            
            print(f"ℹ️ Cookies encontrados após injeção: {[c['name'] for c in session_cookies]}")
            
            # Tenta uma segunda abordagem se não houver cookies suficientes
            if len(session_cookies) < 2:
                print("⚠️ Poucos cookies encontrados, tentando abordagem alternativa...")
                
                # Adiciona localStorage para reforçar a autenticação
                self.driver.execute_script(f"""
                    localStorage.setItem('sessionid', '{self.session_id}');
                    localStorage.setItem('sessionid_ss', '{self.session_id}');
                    localStorage.setItem('sid_tt', '{self.sid_tt}');
                """)
                
                # Tentativa com JavaScript direto
                self.driver.execute_script(f"""
                    document.cookie = "sessionid={self.session_id}; domain=.tiktok.com; path=/; secure; samesite=lax; expires=" + new Date(Date.now() + 86400 * 30 * 1000).toUTCString();
                    document.cookie = "sessionid_ss={self.session_id}; domain=.tiktok.com; path=/; secure; samesite=lax; expires=" + new Date(Date.now() + 86400 * 30 * 1000).toUTCString();
                    document.cookie = "sid_tt={self.sid_tt}; domain=.tiktok.com; path=/; secure; samesite=lax; expires=" + new Date(Date.now() + 86400 * 30 * 1000).toUTCString();
                """)
                
                time.sleep(2)
                self.driver.refresh()
                time.sleep(3)
                
                # Verifica novamente
                actual_cookies = self.driver.get_cookies()
                session_cookies = [c for c in actual_cookies if c['name'] in ['sessionid', 'sessionid_ss', 'sid_tt']]
                print(f"ℹ️ Cookies após segunda tentativa: {[c['name'] for c in session_cookies]}")
            
            if len(session_cookies) >= 2:
                # Navega para uma página intermediária antes do upload
                print("🌐 Navegando para página intermediária...")
                
                # Tenta navegar para a página do usuário
                try:
                    user_id = self.session_id.split(':')[0]
                    if len(user_id) > 0:
                        self.driver.get(f'https://www.tiktok.com/@{user_id}')
                    else:
                        # Se não conseguir extrair o user_id, vai para a home
                        self.driver.get('https://www.tiktok.com/')
                except:
                    self.driver.get('https://www.tiktok.com/')
                
                time.sleep(random.uniform(3, 5))
                
                print("✅ Cookies de sessão verificados com sucesso")
                return True
            else:
                print("❌ Cookies de sessão não encontrados após múltiplas tentativas")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao injetar cookies: {str(e)}")
            return False

    def test_login(self):
        """Testa se o login foi bem sucedido"""
        try:
            print("🔍 Verificando autenticação na conta...")
            
            # Visita a página inicial
            self.driver.get('https://www.tiktok.com/')
            time.sleep(random.uniform(3, 5))
            
            # Verifica se há elementos que indicam login com sucesso
            try:
                # Verifica se existem cookies de sessão
                cookies = self.driver.get_cookies()
                session_cookies = [c for c in cookies if c['name'] in ['sessionid', 'sessionid_ss', 'sid_tt']]
                
                if len(session_cookies) < 2:
                    print("❌ Cookies de sessão não encontrados")
                    return False
                
                print("✅ Cookies de sessão encontrados, prosseguindo...")
                
                # Verifica elementos de usuário logado na página
                logged_in_indicators = [
                    "//span[contains(text(), 'Carregar')]",
                    "//span[contains(text(), 'Upload')]",
                    "//a[contains(@href, 'upload')]",
                    "//div[contains(@data-e2e, 'upload')]",
                    "//div[@data-e2e='top-upload-icon']"
                ]
                
                for indicator in logged_in_indicators:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements and len(elements) > 0:
                        print(f"✅ Indicador de login encontrado: {indicator}")
                        return True
                
                # Verifica se existe algum elemento de perfil
                profile_indicators = [
                    "//div[contains(@data-e2e, 'profile-icon')]",
                    "//span[contains(@data-e2e, 'profile-icon')]",
                    "//img[contains(@alt, 'avatar')]",
                    "//div[@data-e2e='profile-icon']"
                ]
                
                for indicator in profile_indicators:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements and len(elements) > 0:
                        print(f"✅ Indicador de perfil encontrado: {indicator}")
                        return True
                
                # Tentativa alternativa - verificar redirecionamentos
                current_url = self.driver.current_url
                if "login" in current_url.lower():
                    print("❌ Redirecionado para página de login")
                    return False
                
                # Tentativa alternativa - verificar botão de login
                login_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Log') or contains(text(), 'Sign') or contains(text(), 'Entrar')]"
                )
                
                if login_buttons and len(login_buttons) > 0:
                    print("❌ Botão de login encontrado na página")
                    return False
                
                # Se não encontrou indicativos de não-login, assume que está logado
                # já que os cookies de sessão foram encontrados
                print("ℹ️ Não foi possível confirmar login, mas cookies estão presentes")
                
                # Tentativa final - acessar TikTok Studio
                print("🌐 Tentando acessar TikTok Studio como teste final...")
                self.driver.get('https://www.tiktok.com/tiktokstudio')
                time.sleep(5)
                
                if "login" in self.driver.current_url.lower():
                    print("❌ Redirecionado para login ao acessar TikTok Studio")
                    return False
                
                # Temos confiança suficiente que o usuário está logado
                return True
                
            except Exception as inner_error:
                print(f"❌ Erro ao verificar indicadores de login: {inner_error}")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao testar login: {e}")
            return False

    def download_video(self):
        """Baixa o vídeo da URL fornecida"""
        try:
            # Criação de nome de arquivo temporário
            import tempfile
            import os
            import requests
            
            print(f"📥 Baixando vídeo da URL: {self.video_url}")
            
            # Verifica se a URL é válida
            parsed_url = urlparse(self.video_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                print("❌ URL do vídeo inválida")
                return None
            
            # Cria um arquivo temporário com extensão .mp4
            fd, temp_path = tempfile.mkstemp(suffix='.mp4')
            os.close(fd)  # Fecha o descritor de arquivo
            
            # Configura headers para simular um navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/'
            }
            
            # Faz o download com timeout e stream
            print("⌛ Iniciando download do vídeo...")
            response = requests.get(self.video_url, headers=headers, stream=True, timeout=30)
            
            # Verifica se a requisição foi bem-sucedida
            if response.status_code != 200:
                print(f"❌ Falha ao baixar o vídeo. Status code: {response.status_code}")
                return None
            
            # Verifica o tipo de conteúdo
            content_type = response.headers.get('Content-Type', '')
            if not ('video' in content_type or 'octet-stream' in content_type):
                print(f"⚠️ Aviso: O tipo de conteúdo não é vídeo: {content_type}")
                # Continua mesmo assim, pois algumas URLs não retornam o content-type correto
            
            # Verifica o tamanho do arquivo (se disponível)
            content_length = response.headers.get('Content-Length')
            if content_length:
                file_size_mb = int(content_length) / (1024 * 1024)
                print(f"ℹ️ Tamanho do arquivo: {file_size_mb:.2f} MB")
                
                # Verifica se o arquivo é muito pequeno (pode ser um erro)
                if file_size_mb < 0.1:  # Menos de 100KB
                    print("⚠️ Arquivo muito pequeno, pode não ser um vídeo válido")
            
            # Salva o arquivo em chunks para lidar com vídeos grandes
            try:
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as save_error:
                print(f"❌ Erro ao salvar o arquivo: {save_error}")
                return None
            
            # Verifica se o arquivo foi criado e tem tamanho maior que zero
            file_stats = os.stat(temp_path)
            if file_stats.st_size == 0:
                print("❌ Arquivo baixado tem tamanho zero")
                os.unlink(temp_path)
                return None
            
            print(f"✅ Vídeo baixado com sucesso: {temp_path} ({file_stats.st_size / (1024 * 1024):.2f} MB)")
            return temp_path
            
        except Exception as e:
            print(f"❌ Erro ao baixar vídeo: {str(e)}")
            return None

    def _clear_caption_field(self):
        """Limpa o campo de legenda usando o XPath específico e uma abordagem mais robusta"""
        try:
            # Espera o campo de legenda ficar visível e clicável
            caption_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[1]/div/div/div/div/div/div"))
            )
            
            # Garante que o campo está interativo
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[1]/div/div/div/div/div/div"))
            )

            # Primeiro clica no campo para garantir o foco
            caption_field.click()
            time.sleep(1)

            # Digita um caractere temporário para garantir que o campo está ativo
            caption_field.send_keys(".")
            time.sleep(0.5)

            # Seleciona todo o texto usando Ctrl+A
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
            
            # Apaga o texto selecionado
            caption_field.send_keys(Keys.BACKSPACE)
            time.sleep(0.5)

            # Se ainda houver texto, tenta uma abordagem alternativa de limpeza caractere por caractere
            if caption_field.get_attribute("textContent"):
                actions = ActionChains(self.driver)
                for _ in range(50):  # Número suficiente de backspaces para garantir
                    actions.send_keys(Keys.BACKSPACE)
                actions.perform()
                time.sleep(0.5)

            return caption_field
        except Exception as e:
            print(f"❌ Erro ao limpar campo de legenda: {e}")
            return None

    def _insert_hashtag(self, caption_field, hashtag):
        """Insere uma hashtag usando uma abordagem simplificada com teclas de seta"""
        try:
            # Digite a hashtag sem espaço
            caption_field.send_keys(f"#{hashtag}")
            time.sleep(5)  # Aguarda as sugestões carregarem

            # Primeiro tenta usar as teclas de seta
            caption_field.send_keys(Keys.ARROW_DOWN)  # Seleciona a primeira sugestão
            time.sleep(1)
            caption_field.send_keys(Keys.ENTER)  # Confirma a seleção
            time.sleep(1)

            # Se a abordagem com teclas não funcionou, tenta clicar diretamente
            if not f"#{hashtag}" in caption_field.get_attribute("textContent"):
                try:
                    # Procura pelo elemento mais provável de ser a hashtag
                    hashtag_elements = self.driver.find_elements(By.XPATH, 
                        f"//div[contains(text(), '#{hashtag}') or contains(., '#{hashtag}')]")
                    
                    for element in hashtag_elements:
                        if element.is_displayed():
                            try:
                                self.driver.execute_script("arguments[0].click();", element)
                                time.sleep(1)
                                break
                            except:
                                continue

                except Exception as e:
                    print(f"⚠️ Erro ao tentar clicar na hashtag: {e}")

            # Adiciona um espaço após a hashtag
            caption_field.send_keys(" ")
            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ Erro ao inserir hashtag #{hashtag}: {e}")
            caption_field.send_keys(" ")

    def _force_hover_visibility(self):
        """Força todos os elementos hover a ficarem visíveis"""
        css = """
            * {
                visibility: visible !important;
                opacity: 1 !important;
                display: block !important;
            }
            *:hover {
                visibility: visible !important;
                opacity: 1 !important;
                display: block !important;
            }
            [class*="hover"] {
                visibility: visible !important;
                opacity: 1 !important;
                display: block !important;
            }
            button, 
            [role="button"],
            [class*="button"] {
                visibility: visible !important;
                opacity: 1 !important;
                display: block !important;
                pointer-events: auto !important;
            }
        """
        self.driver.execute_script(f"""
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `{css}`;
            document.head.appendChild(style);
        """)
        time.sleep(1)

    def _select_music(self):
        """Seleciona a música para o vídeo"""
        try:
            # Clica no botão de editar música
            edit_music_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div/div[3]/div/button"))
            )
            edit_music_button.click()
            time.sleep(2)

            # Pesquisa a música
            search_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Pesquisar']"))
            )
            search_field.clear()
            search_field.send_keys(self.music_name)
            search_field.send_keys(Keys.ENTER)
            time.sleep(3)

            try:
                # Encontra o container da música (primeiro resultado)
                music_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'search-result-list')]//div[contains(@class, 'music-card')]"))
                )

                # Rola até o container da música
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", music_container)
                time.sleep(1)

                # Move o mouse sobre o container para revelar o botão
                actions = ActionChains(self.driver)
                actions.move_to_element(music_container).perform()
                time.sleep(1)

                # Força o estado de hover via JavaScript
                self.driver.execute_script("""
                    var element = arguments[0];
                    var event = new MouseEvent('mouseover', {
                        'view': window,
                        'bubbles': true,
                        'cancelable': true
                    });
                    element.dispatchEvent(event);
                """, music_container)
                time.sleep(1)

                # Tenta clicar no botão "Usar" sem validações
                try:
                    use_button = music_container.find_element(By.XPATH, ".//button[contains(text(), 'Usar')]")
                    use_button.click()
                except:
                    try:
                        use_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Usar')]"))
                        )
                        use_button.click()
                    except:
                        buttons = music_container.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            try:
                                if "usar" in button.get_attribute("textContent").lower():
                                    self.driver.execute_script("arguments[0].click();", button)
                                    break
                            except:
                                continue

                time.sleep(2)
                
                # Aguarda e encontra o container correto para scroll
                music_modal = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div/div/div[3]"))
                )
                
                # Rola dentro do container correto
                self.driver.execute_script("""
                    arguments[0].scrollTo({
                        top: arguments[0].scrollHeight,
                        behavior: 'smooth'
                    });
                """, music_modal)
                time.sleep(1)

                return self._configure_music_settings()

            except Exception as e:
                print(f"⚠️ Erro ao interagir com o container da música: {e}")
                return False

        except Exception as e:
            print(f"❌ Erro ao selecionar música: {e}")
            return False

    def _configure_music_settings(self):
        try:
            # Clica na imagem específica que ativa o controle de volume
            volume_trigger = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div/div/div[3]/div[2]/div/div[1]/div/div[1]/div[3]/img"))
            )
            actions = ActionChains(self.driver)
            actions.move_to_element(volume_trigger)
            actions.click()
            actions.perform()
            time.sleep(2)

            try:
                # Encontra os containers de volume - deve haver dois
                volume_containers = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.jsx-2057176669.volume-range"))
                )
                
                # O segundo container é o "Som adicionado"
                if len(volume_containers) >= 2:
                    volume_container = volume_containers[1]  # Pegando o segundo container (Som adicionado)
                    
                    # Encontra o input range dentro do container
                    volume_input = volume_container.find_element(By.CSS_SELECTOR, "input[type='range']")
                    
                    # Pega o valor atual e o valor máximo do input
                    current_value = float(volume_input.get_attribute("value"))
                    max_value = float(volume_input.get_attribute("max") or "1")
                    min_value = float(volume_input.get_attribute("min") or "0")
                    
                    # Converte o volume desejado para a escala do input
                    target_volume = self.music_volume / 100
                    
                    # Ajusta o volume usando uma sequência de teclas de seta
                    actions = ActionChains(self.driver)
                    actions.click(volume_input)
                    actions.pause(0.5)
                    
                    # Primeiro reseta para o mínimo
                    for _ in range(100):  # Número suficiente para garantir que chegue ao mínimo
                        actions.send_keys(Keys.LEFT)
                    actions.pause(0.5)
                    
                    # Agora incrementa até o valor desejado
                    steps = int(target_volume * 100)  # Cada passo é aproximadamente 1%
                    for _ in range(steps):
                        actions.send_keys(Keys.RIGHT)
                        actions.pause(0.02)  # Pequena pausa entre cada incremento
                    
                    actions.perform()
                    time.sleep(1)

                    # Verifica se o valor foi ajustado corretamente
                    final_value = float(volume_input.get_attribute("value"))
                    if abs(final_value - target_volume) > 0.02:  # tolerância de 2%
                        print(f"⚠️ Volume pode não ter sido ajustado precisamente.")
                        print(f"Valor atual: {final_value * 100}%")
                        print(f"Valor esperado: {self.music_volume}%")

                else:
                    print("⚠️ Não foi possível encontrar o controle de 'Som adicionado'")

            except Exception as e:
                print(f"⚠️ Aviso ao ajustar volume: {e}")

            # Clica no botão "Salvar edição"
            save_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[4]/button[2]"))
            )
            save_button.click()
            time.sleep(2)

            return True

        except Exception as e:
            print(f"⚠️ Aviso ao configurar áudio: {e}")
            return False

    def post_video(self):
        """Posta o vídeo no TikTok"""
        try:
            # Baixa o vídeo primeiro
            video_path = self.download_video()
            if not video_path:
                return False

            # Usa apenas a URL do TikTok Studio
            print("🌐 Acessando TikTok Studio...")
            self.driver.get('https://www.tiktok.com/tiktokstudio/upload')
            
            # Aguarda mais tempo para carregamento completo da página
            print("⌛ Aguardando página carregar completamente...")
            time.sleep(10)
            
            # Força a página a ficar completamente carregada
            self.driver.execute_script("return document.readyState") 
            
            # Verifica se precisamos autenticar novamente
            if "login" in self.driver.current_url.lower():
                print("⚠️ Redirecionado para página de login, tentando autenticar novamente...")
                self.inject_session()
                self.driver.get('https://www.tiktok.com/tiktokstudio/upload')
                time.sleep(10)

            # Procura pelo input de arquivo com maior tolerância e vários seletores
            print("🔍 Procurando pelo input de arquivo...")
            file_input = None
            
            # Lista de seletores possíveis para o input de arquivo
            selectors = [
                'input[type="file"]',
                'input[accept*="video"]',
                'input[name*="upload"]',
                'input[class*="upload"]',
                'input[data-e2e*="upload"]'
            ]
            
            # Tenta cada seletor até encontrar o input
            for selector in selectors:
                try:
                    file_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Input de arquivo encontrado com seletor: {selector}")
                    break
                except:
                    continue
            
            # Se ainda não encontrou, tenta JavaScript para encontrar inputs escondidos
            if not file_input:
                print("ℹ️ Tentando encontrar input de arquivo via JavaScript...")
                try:
                    self.driver.execute_script("""
                        window.fileInputs = [];
                        document.querySelectorAll('input').forEach(input => {
                            if (input.type === 'file') window.fileInputs.push(input);
                        });
                    """)
                    
                    file_inputs_count = self.driver.execute_script("return window.fileInputs.length")
                    
                    if file_inputs_count > 0:
                        print(f"ℹ️ Encontrados {file_inputs_count} inputs de arquivo via JavaScript")
                        file_input = self.driver.execute_script("return window.fileInputs[0]")
                except Exception as js_error:
                    print(f"⚠️ Erro ao buscar via JavaScript: {js_error}")
            
            # Se ainda não encontrou, tenta uma abordagem mais agressiva
            if not file_input:
                print("⚠️ Tentando abordagem alternativa para upload...")
                try:
                    # Tenta clicar em qualquer elemento que pareça ser de upload
                    upload_elements = self.driver.find_elements(By.XPATH, 
                        "//*[contains(text(), 'Upload') or contains(text(), 'Carregar') or contains(text(), 'Enviar')]"
                    )
                    
                    if upload_elements:
                        print(f"ℹ️ Encontrados {len(upload_elements)} elementos de upload possíveis")
                        for elem in upload_elements:
                            try:
                                self.driver.execute_script("arguments[0].click();", elem)
                                time.sleep(3)
                                
                                # Tenta encontrar o input novamente após o clique
                                file_input = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                                )
                                if file_input:
                                    print("✅ Input de arquivo encontrado após clique!")
                                    break
                            except:
                                continue
                except Exception as alt_error:
                    print(f"⚠️ Erro na abordagem alternativa: {alt_error}")
            
            # Se encontrou o input, tenta fazer o upload
            if file_input:
                print(f"📤 Enviando arquivo: {video_path}")
                file_input.send_keys(video_path)
                
                print("⌛ Aguardando o vídeo carregar...")
                # Aumento do tempo de espera para garantir que o vídeo seja carregado
                time.sleep(25)
                
                # Tenta limpar e inserir a legenda com maior tolerância
                print("🔍 Procurando campo de legenda...")
                caption_field = None
                
                # Lista de XPaths e seletores CSS possíveis para o campo de legenda
                caption_selectors = [
                    "//div[contains(@class, 'DraftEditor-root')]//div[@data-contents='true']",
                    "//div[contains(@class, 'public-DraftEditor-content')]",
                    "//div[@role='textbox']",
                    "//div[contains(@placeholder, 'Descreva')]",
                    "//div[contains(@aria-label, 'legenda') or contains(@aria-label, 'caption')]",
                    "textarea[placeholder*='Descreva']",
                    "[data-e2e='caption-input']"
                ]
                
                for selector in caption_selectors:
                    try:
                        if selector.startswith("//"):
                            caption_field = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            caption_field = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        print(f"✅ Campo de legenda encontrado com seletor: {selector}")
                        break
                    except:
                        continue
                
                if not caption_field:
                    # Se ainda não encontrou, tenta uma busca mais genérica
                    try:
                        editable_elements = self.driver.find_elements(By.XPATH, 
                            "//div[@contenteditable='true' or @role='textbox']"
                        )
                        if editable_elements:
                            caption_field = editable_elements[0]
                            print("✅ Campo de legenda encontrado via elementos editáveis genéricos")
                    except:
                        pass
                
                if not caption_field:
                    print("⚠️ Não foi possível encontrar o campo de legenda, continuando mesmo assim...")
                else:
                    # Limpa o campo e adiciona a legenda
                    try:
                        # Clica no campo para focar
                        self.driver.execute_script("arguments[0].click();", caption_field)
                        time.sleep(1)
                        
                        # Tenta limpar o campo
                        self.driver.execute_script("arguments[0].innerHTML = '';", caption_field)
                        time.sleep(1)
                        
                        if self.video_caption:
                            print("📝 Adicionando legenda...")
                            # Tenta inserir via JavaScript e depois via send_keys
                            try:
                                self.driver.execute_script(
                                    f"arguments[0].innerHTML = '{self.video_caption}';", 
                                    caption_field
                                )
                            except:
                                ActionChains(self.driver).click(caption_field).send_keys(
                                    self.video_caption
                                ).perform()
                            time.sleep(1)

                        # Adiciona as hashtags
                        if self.hashtags:
                            print("🏷️ Adicionando hashtags...")
                            hashtag_text = " " + " ".join([f"#{tag}" for tag in self.hashtags])
                            try:
                                self.driver.execute_script(
                                    f"arguments[0].innerHTML = arguments[0].innerHTML + '{hashtag_text}';", 
                                    caption_field
                                )
                            except:
                                ActionChains(self.driver).click(caption_field).send_keys(
                                    hashtag_text
                                ).perform()
                            time.sleep(1)
                    except Exception as caption_error:
                        print(f"⚠️ Erro ao manipular legenda: {caption_error}")

                # Seleciona a música apenas se foi especificada
                if self.music_name:
                    print("🎵 Tentando adicionar música...")
                    if not self._select_music():
                        print("⚠️ Não foi possível selecionar a música, continuando sem música...")
                        # Continua mesmo se a música falhar

                # Rola a página para baixo várias vezes para garantir que veja o botão de publicar
                print("⌛ Preparando para publicar...")
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

                # Procura pelo botão de publicar com múltiplos seletores
                print("🔍 Procurando botão de publicar...")
                publish_button = None
                publish_selectors = [
                    "//button[contains(text(), 'Publicar')]",
                    "//button[contains(@class, 'publish')]",
                    "//button[contains(text(), 'Postar')]",
                    "//button[contains(text(), 'Post')]",
                    "//button[contains(@class, 'post-button')]",
                    "//div[contains(@class, 'submit')]//button",
                    "//div[contains(@class, 'footer')]//button[last()]"
                ]
                
                for selector in publish_selectors:
                    try:
                        publish_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        print(f"✅ Botão de publicar encontrado com seletor: {selector}")
                        break
                    except:
                        continue
                
                # Se encontrou o botão, tenta clicar
                if publish_button:
                    try:
                        # Tenta primeiro com JavaScript e depois com clique normal
                        try:
                            self.driver.execute_script("arguments[0].click();", publish_button)
                        except:
                            publish_button.click()
                        print("✅ Botão de publicar clicado com sucesso")
                        
                        # Aguarda um tempo para o upload completar
                        print("⌛ Aguardando a publicação completar...")
                        time.sleep(20)
                        
                        # Verifica se há mensagem de sucesso
                        success_elements = self.driver.find_elements(By.XPATH, 
                            "//*[contains(text(), 'sucesso') or contains(text(), 'success') or contains(text(), 'postado') or contains(text(), 'posted')]"
                        )
                        
                        if success_elements:
                            print("✅ Mensagem de sucesso encontrada!")
                        
                        # Limpa o arquivo temporário
                        try:
                            import os
                            os.unlink(video_path)
                        except:
                            pass

                        print("✅ Processo de postagem concluído!")
                        return True
                    except Exception as publish_error:
                        print(f"❌ Erro ao publicar: {publish_error}")
                else:
                    print("❌ Não foi possível encontrar o botão de publicar")
            else:
                print("❌ Não foi possível encontrar o input de arquivo")
                return False

        except Exception as e:
            print(f"❌ Erro ao postar vídeo: {str(e)}")
            return False

    def wait_for_user_input(self):
        """Aguarda input do usuário para continuar"""
        print("\n✨ Navegador mantido aberto para debug.")
        print("🔍 Você pode inspecionar os elementos agora.")
        print("⌨️ Pressione Enter para fechar o navegador quando terminar...")
        input()

    def close(self):
        """Fecha o navegador"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ Navegador fechado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao fechar o navegador: {e}")

if __name__ == "__main__":
    bot = None
    try:
        params = {
            'session_id': 'your_session_id',
            'video_url': 'your_video_url',
            'video_caption': 'your_video_caption',
            'hashtags': ['hashtag1', 'hashtag2'],
            'music_name': 'your_music_name',
            'music_volume': 50
        }
        bot = TikTokBot(params)
        if bot.inject_session():
            if bot.test_login():
                print("✅ Bot iniciado com sucesso!")
                bot.post_video()
                # Aguarda input do usuário antes de fechar
                bot.wait_for_user_input()
            else:
                print("❌ Falha ao fazer login. Verifique as credenciais.")
        else:
            print("❌ Falha ao injetar sessão.")
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
    finally:
        if bot and input("Deseja fechar o navegador? (s/n): ").lower() == 's':
            bot.close()