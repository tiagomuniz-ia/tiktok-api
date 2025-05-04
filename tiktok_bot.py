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

# Apenas para Linux
try:
    from pyvirtualdisplay import Display
except ImportError:
    Display = None

class TikTokBot:
    def __init__(self, params, headless=False, linux_mode=None):
        """
        Inicializa o bot com os parâmetros recebidos
        params: dicionário com os parâmetros da API
        headless: se True, executa em modo headless (sem interface gráfica)
        linux_mode: força o modo Linux se True, força o modo Windows se False, auto-detecta se None
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
        
        # Novas configurações
        self.headless = headless
        
        # Detecta o sistema operacional ou usa o valor forçado
        if linux_mode is None:
            self.is_linux = platform.system().lower() == 'linux'
        else:
            self.is_linux = linux_mode
            
        self.display = None
        self.driver = None
        
        print(f"Sistema operacional: {platform.system()}")
        print(f"Modo Linux: {self.is_linux}")
        print(f"Modo Headless: {self.headless}")
        
        self.setup_browser()

    def setup_browser(self):
        """Configura o navegador com as opções necessárias para evitar detecção"""
        try:
            # Configura display virtual se estiver no Linux
            if self.is_linux and self.headless and Display:
                try:
                    self.display = Display(visible=0, size=(1920, 1080))
                    self.display.start()
                    print("✅ Display virtual iniciado")
                except Exception as e:
                    print(f"⚠️ Não foi possível iniciar o display virtual: {e}")
                    print("⚠️ Tentando continuar sem display virtual...")
            
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            
            # Adiciona user agent apropriado para o sistema
            user_agents = [
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            ] if self.is_linux else [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # Configurações para Linux
            if self.is_linux:
                options.add_argument('--disable-gpu')
                # Se estiver em modo headless mas não estiver usando o display virtual
                if self.headless and not self.display:
                    options.add_argument('--headless=new')
            
            # Localização temporária para o Chrome
            temp_dir = tempfile.mkdtemp()
            options.add_argument(f'--user-data-dir={temp_dir}')
            
            # Para Linux, especifica o caminho do driver
            if self.is_linux:
                try:
                    self.driver = uc.Chrome(options=options, version_main=135, headless=False)
                except Exception as e:
                    print(f"⚠️ Erro ao iniciar com uc.Chrome: {e}")
                    print("⚠️ Tentando iniciar com webdriver.Chrome...")
                    options = webdriver.ChromeOptions()
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--headless=new') if self.headless else None
                    
                    self.driver = webdriver.Chrome(options=options)
            else:
                # Para Windows
                self.driver = uc.Chrome(options=options, version_main=135, headless=self.headless)
                
            print("✅ Navegador iniciado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar o navegador: {e}")
            # Tenta limpar recursos se houve erro
            self.clean_up()
            return False
        
    def clean_up(self):
        """Limpa recursos abertos"""
        if self.display:
            try:
                self.display.stop()
                print("✅ Display virtual encerrado")
            except:
                pass
                
    def inject_session(self):
        """Injeta os cookies de sessão para autenticação"""
        try:
            if not self.driver:
                return False
                
            # Primeiro acessa o TikTok para garantir que o domínio está correto
            print("Acessando TikTok...")
            self.driver.get('https://www.tiktok.com')
            time.sleep(5)  # Aumentado para 5 segundos
            
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
            
            # Adiciona cada cookie
            print("Adicionando cookies...")
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                    time.sleep(1)  # Pequena pausa entre cada cookie
                except Exception as cookie_error:
                    print(f"⚠️ Aviso ao adicionar cookie {cookie['name']}: {cookie_error}")
            
            # Aguarda mais tempo após adicionar os cookies
            time.sleep(5)
            
            # Recarrega a página
            print("Recarregando a página...")
            self.driver.refresh()
            time.sleep(5)  # Aguarda a página recarregar completamente
            
            # Verifica se os cookies foram adicionados corretamente
            actual_cookies = self.driver.get_cookies()
            session_cookies = [c for c in actual_cookies if c['name'] in ['sessionid', 'sessionid_ss', 'sid_tt']]
            
            if not session_cookies:
                print("❌ Cookies de sessão não foram encontrados após a injeção")
                return False
            
            print(f"Cookies encontrados: {[c['name'] for c in session_cookies]}")    
            return True
            
        except Exception as e:
            print(f"❌ Erro ao injetar sessão: {e}")
            return False
        
    def test_login(self):
        """Verifica se a sessão está funcionando"""
        try:
            if not self.driver:
                return False

            # Primeiro verifica se temos os cookies necessários
            cookies = self.driver.get_cookies()
            session_cookies = [c for c in cookies if c['name'] in ['sessionid', 'sessionid_ss', 'sid_tt']]
            
            if not session_cookies:
                print("❌ Cookies de sessão não encontrados")
                return False
                
            # Tenta acessar a página de upload do TikTok Studio (mais seguro que /upload)
            print("Testando acesso a TikTokStudio...")
            self.driver.get('https://www.tiktok.com/tiktokstudio/upload')
            time.sleep(8)  # Aguarda mais tempo para carregar em servidores
            
            # Salva screenshot para debug
            if self.is_linux:
                try:
                    screenshot_path = os.path.join(tempfile.gettempdir(), "tiktok_debug.png")
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Screenshot salvo em: {screenshot_path}")
                except Exception as ss_error:
                    print(f"⚠️ Não foi possível salvar screenshot: {ss_error}")
            
            # Verifica se fomos redirecionados para a página de login
            current_url = self.driver.current_url.lower()
            if 'login' in current_url or 'sign-in' in current_url:
                print(f"❌ Redirecionado para página de login: {current_url}")
                return False

            try:
                # Tenta encontrar elementos que só aparecem quando logado
                print("Buscando elemento de upload...")
                upload_element = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                print("✅ Sessão válida e funcionando")
                return True
            except Exception as e:
                print(f"❌ Não foi possível encontrar elementos da página de upload: {e}")
                # Imprime mais informações sobre o estado da página
                print(f"URL atual: {self.driver.current_url}")
                return False

        except Exception as e:
            print(f"❌ Erro ao testar login: {e}")
            return False

    def download_video(self):
        """Baixa o vídeo da URL fornecida"""
        try:
            print(f"Baixando vídeo de: {self.video_url}")
            response = requests.get(self.video_url, stream=True)
            if response.status_code == 200:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        temp_file.write(chunk)
                temp_file.close()
                print(f"✅ Vídeo baixado para: {temp_file.name}")
                return temp_file.name
            else:
                print(f"❌ Erro ao baixar vídeo. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erro ao baixar vídeo: {e}")
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
            # Navega até a página de upload do TikTok Studio
            self.driver.get('https://www.tiktok.com/tiktokstudio/upload')
            time.sleep(random.uniform(3, 5))

            # Faz upload do vídeo
            video_path = self.download_video()
            if not video_path:
                return False

            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
            )
            file_input.send_keys(video_path)

            # Espera o vídeo carregar (15 segundos)
            print("⌛ Aguardando o vídeo carregar...")
            time.sleep(15)

            # Limpa e insere a legenda
            caption_field = self._clear_caption_field()
            if not caption_field:
                return False

            if self.video_caption:
                caption_field.send_keys(self.video_caption)
                caption_field.send_keys(Keys.ENTER)  # Pula uma linha após a legenda
                time.sleep(0.5)

            # Adiciona as hashtags
            for hashtag in self.hashtags:
                self._insert_hashtag(caption_field, hashtag)

            # Seleciona a música
            if self.music_name:
                if not self._select_music():
                    print("⚠️ Não foi possível selecionar a música desejada")

            # Rola a página para baixo e clica em publicar
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Clica no botão de publicar
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[4]/div/button[1]"))
            )
            post_button.click()

            # Aguarda um tempo para o upload completar
            print("⌛ Aguardando a publicação completar...")
            time.sleep(10)  # Tempo fixo de espera após clicar em publicar
            
            # Limpa o arquivo temporário
            try:
                os.unlink(video_path)
            except:
                pass

            print("✅ Processo de postagem concluído!")
            return True  # Sempre retorna True após clicar no botão de publicar

        except Exception as e:
            print(f"❌ Erro ao postar vídeo: {e}")
            return False
            
    def wait_for_user_input(self):
        """Aguarda input do usuário para continuar"""
        print("\n✨ Navegador mantido aberto para debug.")
        print("🔍 Você pode inspecionar os elementos agora.")
        print("⌨️ Pressione Enter para fechar o navegador quando terminar...")
        input()

    def close(self):
        """Fecha o navegador e limpa recursos"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ Navegador fechado com sucesso!")
                
            self.clean_up()
        except Exception as e:
            print(f"❌ Erro ao fechar recursos: {e}")

def get_params_from_env():
    """Obtém parâmetros das variáveis de ambiente para uso com Docker"""
    session_id = os.environ.get('SESSION_ID')
    
    # Só continua se tiver ao menos o session_id
    if not session_id:
        return None
        
    # Obtém demais parâmetros
    params = {
        'session_id': session_id,
        'sid_tt': os.environ.get('SID_TT', session_id),
        'video_url': os.environ.get('VIDEO_URL', ''),
        'video_caption': os.environ.get('VIDEO_CAPTION', ''),
        'music_name': os.environ.get('MUSIC_NAME', ''),
    }
    
    # Converte volume para inteiro se existir
    music_volume = os.environ.get('MUSIC_VOLUME')
    if music_volume:
        try:
            params['music_volume'] = int(music_volume)
        except:
            params['music_volume'] = 50
    
    # Processa hashtags (separadas por vírgula)
    hashtags = os.environ.get('HASHTAGS', '')
    if hashtags:
        params['hashtags'] = [tag.strip() for tag in hashtags.split(',')]
    else:
        params['hashtags'] = []
        
    return params

if __name__ == "__main__":
    bot = None
    try:
        # Detecta automaticamente o ambiente
        is_server = len(sys.argv) > 1 and sys.argv[1] == 'server'
        headless_mode = is_server or (len(sys.argv) > 1 and sys.argv[1] == 'headless')
        
        print(f"Modo: {'Servidor/Headless' if headless_mode else 'Normal'}")
        
        # Tenta obter parâmetros de variáveis de ambiente (para Docker)
        params = get_params_from_env()
        
        # Se não encontrou nas variáveis de ambiente, usa os valores padrão
        if not params:
            params = {
                'session_id': 'your_session_id',
                'video_url': 'your_video_url',
                'video_caption': 'your_video_caption',
                'hashtags': ['hashtag1', 'hashtag2'],
                'music_name': 'your_music_name',
                'music_volume': 50
            }
        
        bot = TikTokBot(params, headless=headless_mode)
        if bot.inject_session():
            if bot.test_login():
                print("✅ Bot iniciado com sucesso!")
                bot.post_video()
                # Em modo servidor não precisa aguardar input
                if not headless_mode:
                    bot.wait_for_user_input()
            else:
                print("❌ Falha ao fazer login. Verifique as credenciais.")
        else:
            print("❌ Falha ao injetar sessão.")
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
    finally:
        if bot:
            if headless_mode or input("Deseja fechar o navegador? (s/n): ").lower() == 's':
                bot.close()