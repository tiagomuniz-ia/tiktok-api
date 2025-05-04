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
                options.add_argument('--headless')
                options.add_argument('--window-size=1920,1080')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--lang=pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7')
                
                # User Agent Linux compatível
                options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36')
                
                return options

            # Primeira tentativa com a versão mais recente do Chrome
            try:
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
                    self.driver = uc.Chrome(
                        options=create_options(),
                        headless=True,
                        use_subprocess=True,
                        driver_executable_path=None,
                        browser_executable_path=None
                    )
                except Exception as e2:
                    print(f"⚠️ Segunda tentativa falhou: {e2}")
                    raise e2
            
            # Configura timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Script anti-detecção básico
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['pt-BR', 'pt', 'en-US', 'en']
                    });
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
            
            if len(session_cookies) >= 2:
                # Navega para uma página intermediária antes do upload
                print("🌐 Navegando para página intermediária...")
                self.driver.get('https://www.tiktok.com/@' + self.session_id.split(':')[0])
                time.sleep(random.uniform(3, 5))
                
                print("✅ Cookies de sessão verificados com sucesso")
                return True
            else:
                print("❌ Número insuficiente de cookies de sessão encontrados")
                return False
            
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
            self.driver.get('https://www.tiktok.com/tiktokstudio/upload')
            time.sleep(5)  # Aguarda mais tempo para carregar
            
            # Verifica se fomos redirecionados para a página de login
            current_url = self.driver.current_url.lower()
            if 'login' in current_url or 'sign-in' in current_url:
                print("❌ Redirecionado para página de login")
                return False

            try:
                # Tenta encontrar elementos que só aparecem quando logado
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                print("✅ Sessão válida e funcionando")
                return True
            except:
                print("❌ Não foi possível encontrar elementos da página de upload")
                return False

        except Exception as e:
            print(f"❌ Erro ao testar login: {e}")
            return False

    def download_video(self):
        """Baixa o vídeo da URL fornecida"""
        try:
            response = requests.get(self.video_url, stream=True)
            if response.status_code == 200:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        temp_file.write(chunk)
                temp_file.close()
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