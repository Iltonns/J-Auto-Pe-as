#!/usr/bin/env python3
"""
Script para testar login e APIs autenticadas
"""
import requests
import json

# URL base da aplicação
BASE_URL = "http://127.0.0.1:5000"

def fazer_login():
    """Faz login e retorna session com cookies"""
    session = requests.Session()
    
    # Fazer login
    login_data = {
        'username': 'Eleilton',
        'password': '123456'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200 and '/login' not in response.url:
        print("✓ Login realizado com sucesso!")
        return session
    else:
        print("✗ Falha no login")
        print(f"Response URL: {response.url}")
        return None

def testar_apis_autenticadas(session):
    """Testa as APIs com sessão autenticada"""
    print("\n=== TESTANDO APIs AUTENTICADAS ===")
    
    # Teste 1: Busca de produtos
    try:
        response = session.get(f"{BASE_URL}/api/produtos/buscar?q=oleo")
        print(f"Busca produtos status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
            produtos = response.json()
            print(f"✓ Produtos encontrados: {len(produtos)}")
            if produtos:
                print(f"  Primeiro: {produtos[0].get('nome', 'N/A')}")
        else:
            print(f"✗ Erro na busca de produtos")
            print(f"Response text (100 chars): {response.text[:100]}")
    except Exception as e:
        print(f"✗ Erro na busca: {e}")
    
    print()
    
    # Teste 2: Dados da venda
    try:
        response = session.get(f"{BASE_URL}/api/venda/6")
        print(f"Venda status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
            venda = response.json()
            print(f"✓ Venda carregada: ID {venda.get('id')}, Total: R$ {venda.get('total', 0):.2f}")
        else:
            print(f"✗ Erro ao carregar venda")
            print(f"Response text (100 chars): {response.text[:100]}")
    except Exception as e:
        print(f"✗ Erro na venda: {e}")
    
    print()
    
    # Teste 3: Configurações
    try:
        response = session.get(f"{BASE_URL}/api/configuracoes-empresa")
        print(f"Config status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
            config = response.json()
            print(f"✓ Configurações: {config.get('nome_empresa', 'N/A')}")
        else:
            print(f"✗ Erro nas configurações")
            print(f"Response text (100 chars): {response.text[:100]}")
    except Exception as e:
        print(f"✗ Erro nas configurações: {e}")

if __name__ == "__main__":
    session = fazer_login()
    if session:
        testar_apis_autenticadas(session)