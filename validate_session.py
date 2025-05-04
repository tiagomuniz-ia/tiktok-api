#!/usr/bin/env python3
"""
Script para validar se um session_id do TikTok está funcionando corretamente.
Útil para verificar antes de tentar postar vídeos.
"""

import argparse
import requests
import time
import json
from tiktok_bot import TikTokBot

def validate_session(session_id):
    """Valida um session_id do TikTok usando o bot"""
    print(f"🔍 Validando session_id: {session_id[:5]}...{session_id[-5:]} (mascarado)")
    
    # Configuração mínima para teste
    params = {
        'session_id': session_id,
        'video_url': 'https://example.com/dummy.mp4',  # URL fictícia, não será usada no teste
    }
    
    # Criar o bot em modo servidor
    bot = TikTokBot(params, server_mode=True)
    
    try:
        # Injetar sessão e testar login
        if bot.inject_session():
            if bot.test_login():
                print("✅ Sessão válida! Login bem-sucedido.")
                return True
            else:
                print("❌ Falha no teste de login. Session_id inválido ou expirado.")
                return False
        else:
            print("❌ Falha ao injetar sessão.")
            return False
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        return False
    finally:
        # Sempre fechar o navegador no final
        if bot:
            bot.close()

def validate_session_api(session_id):
    """Tenta validar a sessão realizando uma requisição para a API do TikTok"""
    print("ℹ️ Tentando validação alternativa via API...")
    
    headers = {
        'cookie': f'sessionid={session_id}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }
    
    try:
        # Tenta acessar informações de usuário via API
        response = requests.get(
            'https://www.tiktok.com/api/user/detail/',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('userInfo'):
                user_info = data['userInfo']
                print(f"✅ Validação via API bem-sucedida!")
                print(f"👤 Usuário: {user_info['user'].get('uniqueId', 'N/A')}")
                print(f"📝 Nome: {user_info['user'].get('nickname', 'N/A')}")
                return True
        
        print(f"❌ Validação via API falhou. Status: {response.status_code}")
        return False
    except Exception as e:
        print(f"❌ Erro na validação via API: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validador de sessão do TikTok')
    parser.add_argument('session_id', help='O session_id do TikTok para validar')
    args = parser.parse_args()
    
    # Executa ambos os métodos de validação
    result_api = validate_session_api(args.session_id)
    
    if not result_api:
        print("\n⚠️ Falha na validação via API. Tentando via navegador...\n")
        result_browser = validate_session(args.session_id)
        
        if result_browser:
            print("\n✅ Sessão validada via navegador!")
        else:
            print("\n❌ Sessão inválida ou expirada!")
    else:
        print("\n✅ Sessão validada via API!") 