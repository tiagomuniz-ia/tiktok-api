from selenium import webdriver
import undetected_chromedriver as uc
import time
import random
import requests
import tempfile
import json
import os
import sys
import platform
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from difflib import SequenceMatcher

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
        
        # Novos parâmetros de configuração
        self.use_proxy = params.get('use_proxy', False)
        self.proxy = params.get('proxy', None)
        self.headless = params.get('headless', False)
        self.wait_time_multiplier = params.get('wait_time_multiplier', 1.0)  # Para ajustar tempos de espera
        
        self.driver = None
        self.setup_browser()

    def setup_browser(self):
        """Configura o navegador com as opções necessárias para evitar detecção"""
        try:
            # Verificar a configuração do display
            is_server = not self._is_display_available()
            print(f"Detecção de ambiente: {'Servidor' if is_server else 'Desktop'}")
            
            options = uc.ChromeOptions()
            
            # Configurações Stealth
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--ignore-certificate-errors')
            
            # Configurações para servidor
            if is_server or self.headless:
                # Configurações específicas para execução headless
                options.add_argument('--headless=new')  # Nova versão de headless do Chrome
                options.add_argument('--disable-gpu')
                options.add_argument('--remote-debugging-port=9222')
                print("✅ Modo headless ativado para ambiente de servidor")
            
            # Configurações adicionais de privacidade
            options.add_argument('--incognito')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            
            # Adiciona um user agent aleatório de alta qualidade
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
            ]
            selected_agent = random.choice(user_agents)
            options.add_argument(f'user-agent={selected_agent}')
            print(f"✅ User Agent configurado: {selected_agent}")
            
            # Configurar proxy se fornecido
            if self.use_proxy and self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
                print(f"✅ Proxy configurado: {self.proxy}")
            
            # Configurações para adicionar aleatoriedade ao fingerprint
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Iniciando Chrome com as configurações
            self.driver = uc.Chrome(options=options, version_main=135, headless=is_server or self.headless)
            
            # Configurações adicionais via JavaScript
            self._apply_stealth_js()
            
            print("✅ Navegador iniciado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar o navegador: {e}")
            return False
    
    def _is_display_available(self):
        """Verifica se há um display disponível (útil para detectar ambiente de servidor)"""
        if platform.system() == 'Windows':
            return True  # No Windows, geralmente há um display
        
        # No Linux, verifica a variável DISPLAY
        return bool(os.environ.get('DISPLAY', ''))
    
    def _apply_stealth_js(self):
        """Aplica configurações JavaScript para evitar detecção"""
        try:
            # Scripts de evasão de fingerprinting
            stealth_js = """
            // Oculta sinais de automação
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            
            // Simula plugins aleatórios (número variável)
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [];
                    const numPlugins = Math.floor(Math.random() * 8) + 2;
                    for (let i = 0; i < numPlugins; i++) {
                        plugins.push({
                            name: `Plugin ${i}`,
                            description: `Random Plugin ${i}`,
                            filename: `plugin${i}.dll`,
                            length: 1
                        });
                    }
                    return plugins;
                }
            });
            
            // Simula linguagens aleatórias
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            
            // Remove o property navigator.webdriver
            delete navigator.__proto__.webdriver;
            
            // Sobrescreve a função toString do navigator
            const _originalToString = Function.prototype.toString;
            Function.prototype.toString = function() {
                if (this === navigator.permissions.query) {
                    return "function query() { [native code] }";
                }
                return _originalToString.apply(this, arguments);
            };
            """
            
            # Executa os scripts de evasão
            self.driver.execute_script(stealth_js)
            print("✅ Scripts de evasão de detecção aplicados")
        except Exception as e:
            print(f"⚠️ Aviso ao aplicar scripts stealth: {e}")
            
    def _adaptive_sleep(self, base_time, randomize=True):
        """Implementa um tempo de espera adaptativo baseado no ambiente"""
        # Calcula o tempo ajustado pelo multiplicador
        adjusted_time = base_time * self.wait_time_multiplier
        
        # Adiciona aleatoriedade se solicitado
        if randomize:
            # Variação de até 30% para mais ou para menos
            random_factor = random.uniform(0.7, 1.3)
            final_time = adjusted_time * random_factor
        else:
            final_time = adjusted_time
            
        # Aplica um mínimo de 0.5 segundos
        final_time = max(0.5, final_time)
        
        # Log em modo verboso
        # print(f"⏱️ Aguardando {final_time:.2f}s (base: {base_time}s)")
        
        # Efetua a pausa
        time.sleep(final_time)
    
    def _safe_click(self, element, use_js=False, attempts=3):
        """Tenta clicar em um elemento de forma segura, com retentativas"""
        for attempt in range(attempts):
            try:
                # Rola até o elemento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                self._adaptive_sleep(0.5, randomize=False)
                
                if use_js:
                    # Clique via JavaScript
                    self.driver.execute_script("arguments[0].click();", element)
                else:
                    # Tenta primeiro com ActionChains para simular comportamento humano
                    actions = ActionChains(self.driver)
                    actions.move_to_element(element)
                    actions.pause(random.uniform(0.1, 0.3))
                    actions.click()
                    actions.perform()
                
                return True
            except Exception as e:
                if attempt == attempts - 1:
                    print(f"❌ Erro ao clicar no elemento após {attempts} tentativas: {e}")
                    return False
                
                # Espera um pouco antes de tentar novamente
                self._adaptive_sleep(1)
        
        return False
        
    def inject_session(self):
        """Injeta os cookies de sessão para autenticação"""
        try:
            if not self.driver:
                return False
                
            # Primeiro acessa o TikTok com uma abordagem anti-detecção
            print("⏳ Acessando TikTok com abordagem stealth...")
            self.driver.get('https://www.tiktok.com')
            
            # Espera adaptativa
            self._adaptive_sleep(5)
            
            # Adiciona cookies essenciais
            cookies = [
                {
                    'name': 'sessionid',
                    'value': self.session_id,
                    'domain': '.tiktok.com',
                    'path': '/'
                },
                {
                    'name': 'sessionid_ss',
                    'value': self.session_id,
                    'domain': '.tiktok.com',
                    'path': '/'
                },
                {
                    'name': 'sid_tt',
                    'value': self.sid_tt,  # Usando o sid_tt fornecido
                    'domain': '.tiktok.com',
                    'path': '/'
                }
            ]
            
            # Adiciona cada cookie com pausa adaptativa
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                    self._adaptive_sleep(1)  # Pausa adaptativa
                except Exception as cookie_error:
                    print(f"⚠️ Aviso ao adicionar cookie {cookie['name']}: {cookie_error}")
            
            # Pausa adaptativa mais longa após adicionar os cookies
            self._adaptive_sleep(5)
            
            # Técnica anti-detecção: navegação natural antes de recarregar
            try:
                # Tenta fazer algumas interações naturais
                body = self.driver.find_element(By.TAG_NAME, 'body')
                actions = ActionChains(self.driver)
                actions.move_to_element(body)
                actions.send_keys(Keys.PAGE_DOWN)
                actions.perform()
                self._adaptive_sleep(2)
            except:
                pass
            
            # Recarrega a página com uma técnica anti-cache
            reload_url = 'https://www.tiktok.com/?_t=' + str(int(time.time()))
            self.driver.get(reload_url)
            self._adaptive_sleep(5)  # Espera adaptativa para recarga
            
            # Verifica se os cookies foram adicionados corretamente
            actual_cookies = self.driver.get_cookies()
            session_cookies = [c for c in actual_cookies if c['name'] in ['sessionid', 'sessionid_ss', 'sid_tt']]
            
            if not session_cookies:
                print("❌ Cookies de sessão não foram encontrados após a injeção")
                return False
                
            print("✅ Cookies de sessão injetados com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao injetar sessão: {e}")
            return False
        
    def test_login(self):
        """Verifica se a sessão está funcionando com métodos aprimorados"""
        try:
            if not self.driver:
                return False

            # Primeiro verifica se temos os cookies necessários
            cookies = self.driver.get_cookies()
            session_cookies = [c for c in cookies if c['name'] in ['sessionid', 'sessionid_ss', 'sid_tt']]
            
            if not session_cookies:
                print("❌ Cookies de sessão não encontrados")
                return False
            
            # Realiza uma navegação natural para a área de upload em várias etapas
            try:
                # Primeiro acessa a página inicial
                self.driver.get('https://www.tiktok.com')
                self._adaptive_sleep(3)
                
                # Enriquece o histórico de navegação, simulando comportamento humano
                profile_urls = [
                    'https://www.tiktok.com/foryou',
                    'https://www.tiktok.com/explore',
                ]
                
                # Visita algumas páginas aleatórias para criar histórico natural
                for _ in range(random.randint(1, 2)):
                    url = random.choice(profile_urls)
                    print(f"🔍 Visitando URL para enriquecer histórico: {url}")
                    self.driver.get(url)
                    self._adaptive_sleep(2)
                    
                    # Simula alguma interação aleatória
                    try:
                        body = self.driver.find_element(By.TAG_NAME, 'body')
                        actions = ActionChains(self.driver)
                        actions.move_to_element(body)
                        for _ in range(random.randint(1, 3)):
                            actions.send_keys(Keys.PAGE_DOWN)
                            actions.pause(0.5)
                        actions.perform()
                        self._adaptive_sleep(2)
                    except:
                        pass
                
                # Finalmente tenta acessar a página de upload
                print("⏳ Tentando acessar página de upload...")
                self.driver.get('https://www.tiktok.com/upload?lang=pt-BR')
                self._adaptive_sleep(5)
                
                # Se chegamos aqui e não fomos redirecionados para login
                current_url = self.driver.current_url.lower()
                if 'login' in current_url or 'sign-in' in current_url:
                    print("❌ Redirecionado para página de login")
                    return False
                
                # Verifica se elementos específicos da página de upload estão presentes
                upload_elements = [
                    (By.XPATH, "//div[contains(@class, 'upload') or contains(@class, 'uploader')]"),
                    (By.CSS_SELECTOR, "input[type='file']"),
                    (By.XPATH, "//div[contains(text(), 'Upload') or contains(text(), 'Carregar')]")
                ]
                
                # Tenta encontrar pelo menos um dos elementos
                for selector_type, selector in upload_elements:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((selector_type, selector))
                        )
                        print(f"✅ Sessão válida e funcionando - elemento encontrado: {selector}")
                        return True
                    except:
                        continue
                
                # Verifica pelo título da página ou URL específica
                if "upload" in self.driver.current_url.lower() and "login" not in self.driver.current_url.lower():
                    print("✅ Sessão válida (verificação baseada em URL)")
                    return True
                
                print("❌ Não foi possível confirmar acesso à página de upload")
                return False
                
            except Exception as nav_error:
                print(f"❌ Erro durante navegação para teste: {nav_error}")
                return False

        except Exception as e:
            print(f"❌ Erro ao testar login: {e}")
            return False

    def download_video(self):
        """Baixa o vídeo da URL fornecida com tratamento de erros aprimorado"""
        try:
            print(f"⏳ Iniciando download do vídeo: {self.video_url}")
            
            # Configuração de headers para evitar bloqueios
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Accept': 'video/webm,video/mp4,video/*;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/'
            }
            
            # Primeiro verifica se o URL está acessível
            head_response = requests.head(self.video_url, headers=headers)
            if head_response.status_code != 200:
                print(f"❌ URL do vídeo não acessível. Status code: {head_response.status_code}")
                return None
                
            # Verifica se o content-type é de vídeo
            content_type = head_response.headers.get('Content-Type', '')
            if not ('video' in content_type or 'octet-stream' in content_type):
                print(f"⚠️ O content-type não parece ser de vídeo: {content_type}, mas continuando...")
            
            # Baixa o vídeo com suporte a streaming
            response = requests.get(self.video_url, headers=headers, stream=True, timeout=60)
            
            if response.status_code == 200:
                # Gera um nome de arquivo temporário único
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                file_size = 0
                
                # Escreve o conteúdo do vídeo em chunks para eficiência
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        file_size += len(chunk)
                        
                temp_file.close()
                
                # Verifica se o arquivo tem um tamanho mínimo (1KB)
                if os.path.getsize(temp_file.name) < 1024:
                    print("❌ O arquivo baixado é muito pequeno para ser um vídeo válido")
                    os.remove(temp_file.name)
                    return None
                
                print(f"✅ Vídeo baixado com sucesso: {temp_file.name} ({file_size/1024/1024:.2f} MB)")
                return temp_file.name
            else:
                print(f"❌ Erro ao baixar vídeo. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro ao baixar vídeo: {e}")
            return None

    def _clear_caption_field(self):
        """Limpa o campo de legenda com método aprimorado"""
        try:
            # Seletores para o campo de legenda (múltiplas estratégias)
            caption_selectors = [
                (By.XPATH, "//div[contains(@class, 'caption') or contains(@class, 'text-input')]//div[@role='textbox']"),
                (By.XPATH, "//div[contains(@class, 'caption') or contains(@class, 'editor')]"),
                (By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[3]/div[1]/div[2]/div[1]/div[2]/div[1]/div/div/div/div/div/div"),
                (By.CSS_SELECTOR, "div[role='textbox']"),
                (By.XPATH, "//div[contains(text(), 'Descreva seu vídeo') or contains(text(), 'Describe your video')]/..//div[@role='textbox']")
            ]
            
            caption_field = None
            for selector_type, selector in caption_selectors:
                try:
                    caption_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((selector_type, selector))
                    )
                    print(f"✅ Campo de legenda encontrado com seletor: {selector}")
                    break
                except:
                    continue
            
            if not caption_field:
                print("❌ Não foi possível encontrar o campo de legenda")
                return None
            
            # Garante que o campo está interativo
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, caption_field.get_attribute("xpath")))
            )
            
            # Primeiro clica no campo para garantir o foco
            self._safe_click(caption_field)
            self._adaptive_sleep(1)
            
            # Abordagem 1: Ctrl+A e Delete
            try:
                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                self._adaptive_sleep(0.5)
                actions.send_keys(Keys.DELETE).perform()
                self._adaptive_sleep(0.5)
            except:
                pass
            
            # Abordagem 2: Limpa diretamente via JavaScript
            try:
                self.driver.execute_script("arguments[0].textContent = '';", caption_field)
                self._adaptive_sleep(0.5)
            except:
                pass
            
            # Abordagem 3: Envia uma série de backspaces
            try:
                actions = ActionChains(self.driver)
                for _ in range(50):  # Número suficiente de backspaces para garantir
                    actions.send_keys(Keys.BACKSPACE)
                actions.perform()
                self._adaptive_sleep(0.5)
            except:
                pass
            
            return caption_field
        except Exception as e:
            print(f"❌ Erro ao limpar campo de legenda: {e}")
            return None

    def _insert_hashtag(self, caption_field, hashtag):
        """Insere uma hashtag com método aprimorado"""
        try:
            # Digite a hashtag sem espaço
            caption_field.send_keys(f"#{hashtag}")
            self._adaptive_sleep(2)  # Aguarda as sugestões carregarem
            
            # Procura pelo elemento da hashtag sugerida
            try:
                # Abordagem 1: Usando teclas de seta
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ARROW_DOWN)  # Seleciona a primeira sugestão
                actions.perform()
                self._adaptive_sleep(1)
                
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ENTER)  # Confirma a seleção
                actions.perform()
                self._adaptive_sleep(1)
                
                # Verifica se a hashtag foi inserida corretamente
                if not f"#{hashtag}" in caption_field.get_attribute("textContent"):
                    # Abordagem 2: Tenta clicar diretamente na sugestão
                    hashtag_selectors = [
                        (By.XPATH, f"//div[contains(text(), '#{hashtag}')]"),
                        (By.XPATH, f"//span[contains(text(), '#{hashtag}')]"),
                        (By.XPATH, f"//div[contains(@class, 'hashtag') and contains(., '#{hashtag}')]")
                    ]
                    
                    for selector_type, selector in hashtag_selectors:
                        try:
                            hashtag_element = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((selector_type, selector))
                            )
                            self._safe_click(hashtag_element, use_js=True)
                            self._adaptive_sleep(1)
                            break
                        except:
                            continue
                
                # Se mesmo assim a hashtag não foi inserida, adiciona um espaço para usar como texto normal
                if not f"#{hashtag}" in caption_field.get_attribute("textContent"):
                    caption_field.send_keys(" ")
                    self._adaptive_sleep(0.5)
                
                return True
            except Exception as hashtag_error:
                print(f"⚠️ Erro ao selecionar hashtag sugerida: {hashtag_error}")
                # Falha silenciosa, apenas adiciona um espaço para continuar
                caption_field.send_keys(" ")
                self._adaptive_sleep(0.5)
                return False
                
        except Exception as e:
            print(f"❌ Erro ao inserir hashtag: {e}")
            caption_field.send_keys(" ")  # Adiciona espaço para permitir continuação
            self._adaptive_sleep(0.5)
            return False

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
        """Seleciona uma música com método aprimorado"""
        try:
            # Localiza o botão de adicionar música com múltiplas estratégias
            music_button_selectors = [
                (By.XPATH, "//div[contains(text(), 'Adicionar som') or contains(text(), 'Add sound')]"),
                (By.XPATH, "//button[contains(@class, 'music') or contains(@class, 'sound')]"),
                (By.XPATH, "//div[contains(@class, 'music-icon') or contains(@class, 'sound-icon')]"),
                (By.XPATH, "//button[.//*[name()='svg' and (contains(@class, 'music') or contains(@class, 'sound'))]]")
            ]
            
            music_button = None
            for selector_type, selector in music_button_selectors:
                try:
                    music_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    print(f"✅ Botão de música encontrado com seletor: {selector}")
                    break
                except:
                    continue
            
            if not music_button:
                print("❌ Não foi possível encontrar o botão de adicionar música")
                return False
            
            # Clica no botão de música
            if not self._safe_click(music_button, use_js=True):
                print("❌ Falha ao clicar no botão de adicionar música")
                return False
            
            # Aguarda o painel de músicas abrir
            self._adaptive_sleep(5)
            
            # Procura pelo campo de pesquisa de música
            search_selectors = [
                (By.XPATH, "//input[contains(@placeholder, 'Pesquisar') or contains(@placeholder, 'Search')]"),
                (By.CSS_SELECTOR, "input[type='search']"),
                (By.XPATH, "//div[contains(@class, 'search')]//input"),
                (By.XPATH, "//input[contains(@class, 'search')]")
            ]
            
            search_field = None
            for selector_type, selector in search_selectors:
                try:
                    search_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    print(f"✅ Campo de pesquisa de música encontrado com seletor: {selector}")
                    break
                except:
                    continue
            
            if not search_field:
                print("❌ Não foi possível encontrar o campo de pesquisa de música")
                
                # Tenta fechar o painel e retornar
                try:
                    close_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'close')]")
                    if close_buttons:
                        self._safe_click(close_buttons[0], use_js=True)
                except:
                    pass
                    
                return False
            
            # Clica e limpa o campo de pesquisa
            self._safe_click(search_field)
            search_field.clear()
            self._adaptive_sleep(1)
            
            # Digita o nome da música
            search_field.send_keys(self.music_name)
            self._adaptive_sleep(1)
            
            # Pressiona Enter para pesquisar
            search_field.send_keys(Keys.ENTER)
            
            # Aguarda os resultados de pesquisa
            self._adaptive_sleep(5)
            
            # Tenta localizar o primeiro resultado
            result_selectors = [
                (By.XPATH, "//div[contains(@class, 'music-item') or contains(@class, 'sound-item')]"),
                (By.XPATH, "//div[contains(@class, 'music-card') or contains(@class, 'sound-card')]"),
                (By.XPATH, "//div[contains(@class, 'recommend-item')]"),
                (By.XPATH, "//li[contains(@class, 'search-result-item')]")
            ]
            
            result_item = None
            for selector_type, selector in result_selectors:
                try:
                    result_items = self.driver.find_elements(selector_type, selector)
                    if result_items:
                        result_item = result_items[0]  # Pega o primeiro resultado
                        print(f"✅ Resultado de música encontrado com seletor: {selector}")
                        break
                except:
                    continue
            
            if not result_item:
                print("❌ Não foram encontrados resultados para a música")
                
                # Tenta fechar o painel e retornar
                try:
                    close_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'close')]")
                    if close_buttons:
                        self._safe_click(close_buttons[0], use_js=True)
                except:
                    pass
                    
                return False
            
            # Clica no resultado encontrado
            if not self._safe_click(result_item, use_js=True):
                print("❌ Falha ao clicar no resultado da música")
                return False
            
            # Aguarda a música ser aplicada
            self._adaptive_sleep(5)
            
            # Verifica se a música foi aplicada com sucesso
            try:
                # Tenta encontrar indicadores de que a música foi adicionada
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'music-info') or contains(@class, 'sound-info')]"))
                )
                print("✅ Música adicionada com sucesso")
                return True
            except:
                # Se não encontrou indicadores claros, verifica se voltamos à tela de edição
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Post') or contains(text(), 'Postar')]"))
                    )
                    print("✅ Música provavelmente adicionada (retorno à tela de edição)")
                    return True
                except:
                    print("❌ Não foi possível confirmar a adição da música")
                    return False
        
        except Exception as e:
            print(f"❌ Erro ao selecionar música: {e}")
            return False
    
    def _configure_music_settings(self):
        """Configura o volume da música com método aprimorado"""
        try:
            # Tenta encontrar botão de configurações de áudio ou ícone similar
            volume_selectors = [
                (By.XPATH, "//div[contains(@class, 'volume') or contains(@class, 'audio-settings')]"),
                (By.XPATH, "//button[.//*[name()='svg' and (contains(@class, 'volume') or contains(@class, 'audio'))]]"),
                (By.XPATH, "//div[contains(@class, 'music-info')]//button"),
                (By.XPATH, "//div[contains(@class, 'sound-info')]//button")
            ]
            
            volume_button = None
            for selector_type, selector in volume_selectors:
                try:
                    volume_elements = self.driver.find_elements(selector_type, selector)
                    if volume_elements:
                        # Tenta encontrar o botão mais provável que controla volume
                        for element in volume_elements:
                            if 'volume' in element.get_attribute('class').lower() or \
                               'audio' in element.get_attribute('class').lower():
                                volume_button = element
                                break
                        
                        # Se não achou por classe, usa o primeiro encontrado
                        if not volume_button and volume_elements:
                            volume_button = volume_elements[0]
                            
                        print(f"✅ Botão de volume encontrado com seletor: {selector}")
                        break
                except:
                    continue
            
            if not volume_button:
                print("❌ Não foi possível encontrar o controle de volume")
                return False
            
            # Clica no botão de volume
            if not self._safe_click(volume_button, use_js=True):
                print("❌ Falha ao clicar no controle de volume")
                return False
            
            # Aguarda o painel de volume abrir
            self._adaptive_sleep(2)
            
            # Tenta encontrar o controle deslizante (slider) de volume
            slider_selectors = [
                (By.XPATH, "//input[@type='range']"),
                (By.XPATH, "//div[contains(@class, 'slider')]"),
                (By.XPATH, "//div[contains(@class, 'volume-slider')]")
            ]
            
            volume_slider = None
            for selector_type, selector in slider_selectors:
                try:
                    volume_slider = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector))
                    )
                    print(f"✅ Slider de volume encontrado com seletor: {selector}")
                    break
                except:
                    continue
            
            if not volume_slider:
                print("❌ Não foi possível encontrar o slider de volume")
                return False
            
            # Define o valor do volume
            try:
                # Se for um input range, define diretamente
                if volume_slider.tag_name.lower() == 'input' and volume_slider.get_attribute('type') == 'range':
                    # Define o valor diretamente via JavaScript
                    self.driver.execute_script(f"arguments[0].value = {self.music_volume};", volume_slider)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", volume_slider)
                    self._adaptive_sleep(1)
                    
                    # Confirma com uma interação do usuário
                    actions = ActionChains(self.driver)
                    actions.move_to_element(volume_slider)
                    actions.click()
                    actions.perform()
                else:
                    # Para sliders personalizados, tenta clicar na posição relativa
                    # Obtém o tamanho e posição do slider
                    slider_width = volume_slider.size['width']
                    
                    # Calcula a posição X baseada no percentual do volume (0-100)
                    # Converte de 0-100 para 0-1 e multiplica pela largura
                    target_x = (self.music_volume / 100) * slider_width
                    
                    # Move para o início do slider e depois para a posição desejada
                    actions = ActionChains(self.driver)
                    actions.move_to_element_with_offset(volume_slider, 0, 0)  # Move para o início
                    actions.click_and_hold()
                    actions.move_by_offset(target_x, 0)  # Move para a posição do volume
                    actions.release()
                    actions.perform()
                
                self._adaptive_sleep(1)
                
                # Procura e clica em qualquer botão de confirmar/aplicar se existir
                confirm_selectors = [
                    (By.XPATH, "//button[contains(text(), 'Confirmar') or contains(text(), 'Confirm') or contains(text(), 'Apply') or contains(text(), 'Aplicar')]"),
                    (By.XPATH, "//button[contains(@class, 'confirm') or contains(@class, 'apply')]")
                ]
                
                for selector_type, selector in confirm_selectors:
                    try:
                        confirm_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((selector_type, selector))
                        )
                        self._safe_click(confirm_button, use_js=True)
                        self._adaptive_sleep(1)
                        break
                    except:
                        continue
                
                print(f"✅ Volume da música ajustado para {self.music_volume}%")
                return True
            
            except Exception as slider_error:
                print(f"❌ Erro ao ajustar o volume: {slider_error}")
                return False
        
        except Exception as e:
            print(f"❌ Erro ao configurar volume da música: {e}")
            return False

    def post_video(self):
        """Método principal para realizar a postagem do vídeo com abordagem robusta"""
        try:
            if not self.driver:
                print("❌ Driver não inicializado")
                return False
                
            # Baixa o vídeo
            print("⏳ Baixando vídeo...")
            video_path = self.download_video()
            if not video_path:
                print("❌ Falha ao baixar o vídeo")
                return False
                
            try:
                # Acessa a página de upload de forma natural
                print("⏳ Acessando página de upload...")
                self.driver.get('https://www.tiktok.com/upload?lang=pt-BR')
                self._adaptive_sleep(7)  # Espera maior para carregamento completo
                
                # Verifica se estamos realmente na página de upload
                current_url = self.driver.current_url.lower()
                if 'login' in current_url or 'sign-in' in current_url:
                    print("❌ Redirecionado para página de login durante tentativa de upload")
                    return False
                
                # Procura o elemento de input do arquivo com múltiplas estratégias
                file_input_selectors = [
                    (By.CSS_SELECTOR, "input[type='file']"),
                    (By.XPATH, "//input[@type='file']"),
                    (By.XPATH, "//div[contains(@class, 'upload')]//input[@type='file']")
                ]
                
                file_input = None
                for selector_type, selector in file_input_selectors:
                    try:
                        file_input = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((selector_type, selector))
                        )
                        print(f"✅ Input de arquivo encontrado com seletor: {selector}")
                        break
                    except:
                        continue
                
                if not file_input:
                    print("❌ Não foi possível encontrar o campo de upload de arquivos")
                    return False
                
                # Enviando o arquivo com abordagem robusta
                try:
                    print(f"⏳ Enviando vídeo: {video_path}")
                    # Usa caminho absoluto para maior compatibilidade
                    abs_path = os.path.abspath(video_path)
                    
                    # Scroll para o elemento de input ficar visível
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_input)
                    self._adaptive_sleep(1)
                    
                    # Envia o arquivo
                    file_input.send_keys(abs_path)
                    
                    # Espera adaptativa maior para o upload completo (baseado no tamanho do arquivo)
                    file_size_mb = os.path.getsize(abs_path) / (1024 * 1024)
                    upload_wait = max(10, min(60, file_size_mb * 2))  # Entre 10s e 60s
                    print(f"⏳ Aguardando upload do vídeo ({file_size_mb:.1f} MB)...")
                    self._adaptive_sleep(upload_wait, False)
                    
                    # Verifica se o upload teve sucesso
                    try:
                        # Tenta encontrar elementos que indicam sucesso no upload
                        upload_success_indicators = [
                            (By.XPATH, "//div[contains(@class, 'progress') and contains(@class, 'complete')]"),
                            (By.XPATH, "//div[contains(text(), 'carregado com sucesso') or contains(text(), 'uploaded successfully')]"),
                            (By.XPATH, "//div[contains(@class, 'success')]")
                        ]
                        
                        upload_success = False
                        for selector_type, selector in upload_success_indicators:
                            try:
                                WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((selector_type, selector))
                                )
                                upload_success = True
                                break
                            except:
                                continue
                        
                        if not upload_success:
                            # Verificação alternativa: verifica se campos de edição estão disponíveis
                            try:
                                WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'caption') or contains(@class, 'description')]"))
                                )
                                upload_success = True
                            except:
                                pass
                        
                        if not upload_success:
                            print("⚠️ Não foi possível confirmar sucesso do upload, mas continuando...")
                    except Exception as upload_verify_error:
                        print(f"⚠️ Erro ao verificar sucesso do upload: {upload_verify_error}")
                    
                    # Configurando a legenda e hashtags
                    self._adaptive_sleep(5)  # Espera para a interface de edição aparecer
                    
                    # Adiciona legenda
                    print("⏳ Configurando legenda e hashtags...")
                    caption_field = self._clear_caption_field()
                    if caption_field:
                        # Insere a legenda
                        if self.video_caption:
                            caption_field.send_keys(self.video_caption)
                            self._adaptive_sleep(1)
                        
                        # Adiciona hashtags
                        if self.hashtags:
                            for hashtag in self.hashtags:
                                if caption_field.get_attribute("textContent"):
                                    # Adiciona um espaço se já houver conteúdo
                                    caption_field.send_keys(" ")
                                    self._adaptive_sleep(0.5)
                                
                                self._insert_hashtag(caption_field, hashtag)
                    else:
                        print("⚠️ Não foi possível encontrar o campo de legenda")
                    
                    # Configura música se necessário
                    if self.music_name:
                        print(f"⏳ Configurando música: {self.music_name}")
                        music_added = self._select_music()
                        if music_added:
                            print("✅ Música adicionada com sucesso")
                            
                            # Configura volume se música foi adicionada
                            volume_set = self._configure_music_settings()
                            if volume_set:
                                print(f"✅ Volume da música ajustado para {self.music_volume}%")
                            else:
                                print("⚠️ Não foi possível ajustar o volume da música")
                        else:
                            print("⚠️ Não foi possível adicionar a música solicitada")
                    
                    # Clica no botão de postar com múltiplas estratégias
                    print("⏳ Finalizando postagem...")
                    self._adaptive_sleep(5)  # Espera para garantir que tudo está pronto
                    
                    post_button_selectors = [
                        (By.XPATH, "//button[contains(text(), 'Post') or contains(text(), 'Postar')]"),
                        (By.XPATH, "//div[contains(@class, 'btn-post') or contains(@class, 'button-post')]"),
                        (By.XPATH, "//button[contains(@class, 'confirm') or contains(@class, 'submit')]")
                    ]
                    
                    post_button = None
                    for selector_type, selector in post_button_selectors:
                        try:
                            post_button = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((selector_type, selector))
                            )
                            print(f"✅ Botão de postar encontrado com seletor: {selector}")
                            break
                        except:
                            continue
                    
                    if post_button:
                        # Tenta clicar com método seguro
                        if self._safe_click(post_button, use_js=True):
                            print("✅ Botão de postar clicado com sucesso")
                            
                            # Aguarda a postagem ser concluída
                            self._adaptive_sleep(15)  # Tempo maior para garantir a postagem
                            
                            # Verifica se a postagem foi bem-sucedida
                            success_indicators = [
                                (By.XPATH, "//div[contains(text(), 'sucesso') or contains(text(), 'success')]"),
                                (By.XPATH, "//div[contains(@class, 'success')]"),
                                # Também pode verificar se voltamos para a tela inicial de upload
                                (By.CSS_SELECTOR, "input[type='file']")
                            ]
                            
                            for selector_type, selector in success_indicators:
                                try:
                                    WebDriverWait(self.driver, 10).until(
                                        EC.presence_of_element_located((selector_type, selector))
                                    )
                                    print("✅ Vídeo postado com sucesso!")
                                    return True
                                except:
                                    continue
                            
                            # Se nenhum indicador for encontrado, mas não houve erro, considera sucesso
                            print("✅ Considerando postagem bem-sucedida (sem confirmação explícita)")
                            return True
                        else:
                            print("❌ Não foi possível clicar no botão de postar")
                    else:
                        print("❌ Botão de postar não encontrado")
                
                except Exception as upload_error:
                    print(f"❌ Erro ao fazer upload do vídeo: {upload_error}")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro durante o processo de postagem: {e}")
                return False
            finally:
                # Limpa o arquivo temporário
                try:
                    if video_path and os.path.exists(video_path):
                        os.remove(video_path)
                        print(f"✅ Arquivo temporário removido: {video_path}")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Erro geral no processo de postagem: {e}")
            return False
            
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