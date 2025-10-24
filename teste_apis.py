#!/usr/bin/env python3
"""
Script para testar as funcionalidades de busca e impressão de vendas
"""
import requests
import json

# URL base da aplicação
BASE_URL = "http://127.0.0.1:5000"

def testar_busca_produtos():
    """Testa a API de busca de produtos"""
    print("=== TESTANDO BUSCA DE PRODUTOS ===")
    
    # Teste 1: Busca simples
    try:
        response = requests.get(f"{BASE_URL}/api/produtos/buscar?q=oleo")
        print(f"Status da busca por 'oleo': {response.status_code}")
        if response.status_code == 200:
            produtos = response.json()
            print(f"Produtos encontrados: {len(produtos)}")
            if produtos:
                print("Primeiro produto:")
                print(f"  ID: {produtos[0].get('id')}")
                print(f"  Nome: {produtos[0].get('nome')}")
                print(f"  Preço: R$ {produtos[0].get('preco', 0):.2f}")
                print(f"  Estoque: {produtos[0].get('estoque', 0)}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na busca: {e}")
    
    print()

def testar_venda_e_impressao():
    """Testa as APIs de venda e impressão"""
    print("=== TESTANDO VENDA E IMPRESSÃO ===")
    
    # Teste 1: Buscar dados de uma venda
    try:
        response = requests.get(f"{BASE_URL}/api/venda/6")  # Venda ID 6
        print(f"Status da busca da venda 6: {response.status_code}")
        if response.status_code == 200:
            venda = response.json()
            print("Dados da venda:")
            print(f"  ID: {venda.get('id')}")
            print(f"  Total: R$ {venda.get('total', 0):.2f}")
            print(f"  Cliente: {venda.get('cliente_nome', 'Cliente Avulso')}")
            print(f"  Itens: {len(venda.get('itens', []))}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro ao buscar venda: {e}")
    
    print()
    
    # Teste 2: Buscar configurações da empresa
    try:
        response = requests.get(f"{BASE_URL}/api/configuracoes-empresa")
        print(f"Status das configurações: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print("Configurações da empresa:")
            print(f"  Nome: {config.get('nome_empresa')}")
            print(f"  Telefone: {config.get('telefone')}")
            print(f"  Email: {config.get('email')}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro ao buscar configurações: {e}")

if __name__ == "__main__":
    testar_busca_produtos()
    testar_venda_e_impressao()