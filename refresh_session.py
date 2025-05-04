#!/usr/bin/env python3
"""
Script para gerar uma nova sessão do TikTok usando credenciais fornecidas.
ATENÇÃO: Este script requer interação manual e é apenas para desenvolvimento.
"""

import argparse
import time
import os
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def generate_new_session(username, password):
    """Abre um navegador para fazer login no TikTok e extrai os cookies de sessão"""
    print(f"🔐 Iniciando processo de geração de sessão para o usuário: {username}")
    
    # Configuração do Chrome
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options, version_main=135, headless=False)
    
    try:
        # Acessa o TikTok
        driver.get("https://www.tiktok.com/login")
        print("📱 Aguardando página de login carregar...")
        time.sleep(5)
        
        # Procura pelo modo de login com username/email
        try:
            use_email_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Use phone / email / username')]"))
            )
            use_email_button.click()
            time.sleep(2)
        except:
            print("⚠️ Botão de login por email não encontrado, assumindo que já está nessa opção")
        
        # Aguarda pelo input de login
        try:
            # Tenta clicar na opção de login por email/username se estiver disponível
            login_method = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Log in with email or username')]"))
            )
            login_method.click()
            time.sleep(2)
        except:
            print("⚠️ Opção de login por email/username não encontrada, continuando...")
        
        # Aguarda input de username/email
        print("👤 Preenchendo credenciais...")
        try:
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
            )
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(1)
            
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(1)
            
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
            login_button.click()
            
            print("⌛ Aguardando login manual e possível verificação...")
            print("⚠️ IMPORTANTE: Se aparecer um captcha ou verificação, complete-o manualmente!")
            print("⚠️ Aguarde até ser redirecionado para a página principal do TikTok")
            print("⚠️ Aperte Enter quando o login estiver completo...")
            input()
            
            # Extrai cookies
            cookies = driver.get_cookies()
            session_cookies = {}
            
            for cookie in cookies:
                if cookie['name'] in ['sessionid', 'sessionid_ss', 'sid_tt']:
                    session_cookies[cookie['name']] = cookie['value']
            
            if 'sessionid' not in session_cookies:
                print("❌ Cookie de sessão não encontrado. O login foi bem-sucedido?")
                return None
            
            print("\n✅ Sessão extraída com sucesso!")
            print("\n============== DETALHES DA SESSÃO ==============")
            print(f"🔑 session_id: {session_cookies.get('sessionid')}")
            print(f"🔑 sessionid_ss: {session_cookies.get('sessionid_ss', 'N/A')}")
            print(f"🔑 sid_tt: {session_cookies.get('sid_tt', 'N/A')}")
            print("===============================================\n")
            
            # Salva em um arquivo para referência
            cookies_file = "tiktok_session.json"
            with open(cookies_file, 'w') as f:
                json.dump(session_cookies, f, indent=4)
            
            print(f"💾 Sessão salva em: {os.path.abspath(cookies_file)}")
            print("⚠️ Mantenha estes valores seguros e não os compartilhe!")
            
            return session_cookies
            
        except Exception as e:
            print(f"❌ Erro ao preencher credenciais: {e}")
            return None
    
    except Exception as e:
        print(f"❌ Erro ao gerar sessão: {e}")
        return None
    finally:
        # Aguarda antes de fechar para dar tempo de ver os resultados
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gerador de sessão do TikTok')
    parser.add_argument('username', help='Seu nome de usuário ou email do TikTok')
    parser.add_argument('password', help='Sua senha do TikTok')
    args = parser.parse_args()
    
    generate_new_session(args.username, args.password) 