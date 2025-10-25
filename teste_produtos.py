#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar funcionalidades de produtos no sistema de autopeças
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import (
    init_db, 
    deletar_todos_os_produtos, 
    limpar_completamente_produtos,
    listar_produtos,
    adicionar_produto
)

def main():
    print("🔧 Sistema de Teste - Autopeças")
    print("=" * 50)
    
    # Inicializar banco de dados
    print("📄 Inicializando banco de dados...")
    init_db()
    
    while True:
        print("\n🔧 MENU DE TESTE:")
        print("1. 📋 Listar produtos atuais")
        print("2. 🗑️  Deletar todos os produtos (marcar como inativos)")
        print("3. 💥 Limpar completamente produtos do banco")
        print("4. ➕ Adicionar produto de teste")
        print("5. 🚪 Sair")
        
        opcao = input("\n🔢 Escolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            listar_produtos_teste()
        elif opcao == "2":
            deletar_todos_teste()
        elif opcao == "3":
            limpar_completamente_teste()
        elif opcao == "4":
            adicionar_produto_teste()
        elif opcao == "5":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida!")

def listar_produtos_teste():
    print("\n📋 LISTANDO PRODUTOS:")
    print("-" * 30)
    
    try:
        produtos = listar_produtos()
        
        if produtos:
            print(f"✅ {len(produtos)} produto(s) encontrado(s):")
            for i, produto in enumerate(produtos, 1):
                print(f"{i:2d}. ID: {produto['id']:3d} | {produto['nome'][:40]:40s} | R$ {produto['preco']:8.2f} | Estoque: {produto['estoque']:3d}")
        else:
            print("📭 Nenhum produto encontrado.")
    except Exception as e:
        print(f"❌ Erro ao listar produtos: {e}")

def deletar_todos_teste():
    print("\n🗑️  DELETAR TODOS OS PRODUTOS:")
    print("-" * 30)
    
    confirma = input("⚠️  Tem certeza? Digite 'SIM' para confirmar: ").strip().upper()
    
    if confirma == "SIM":
        try:
            total = deletar_todos_os_produtos()
            print(f"✅ {total} produtos marcados como inativos com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao deletar produtos: {e}")
    else:
        print("❌ Operação cancelada.")

def limpar_completamente_teste():
    print("\n💥 LIMPAR COMPLETAMENTE PRODUTOS:")
    print("-" * 30)
    print("⚠️  CUIDADO: Esta operação remove completamente os produtos do banco!")
    
    confirma1 = input("Digite 'DELETAR' para continuar: ").strip().upper()
    
    if confirma1 == "DELETAR":
        confirma2 = input("🚨 ÚLTIMA CHANCE! Digite 'CONFIRMO' para prosseguir: ").strip().upper()
        
        if confirma2 == "CONFIRMO":
            try:
                limpar_completamente_produtos()
                print("✅ Todos os produtos removidos completamente do banco!")
            except Exception as e:
                print(f"❌ Erro ao limpar produtos: {e}")
        else:
            print("❌ Operação cancelada.")
    else:
        print("❌ Operação cancelada.")

def adicionar_produto_teste():
    print("\n➕ ADICIONAR PRODUTO DE TESTE:")
    print("-" * 30)
    
    try:
        # Adicionar alguns produtos de teste
        produtos_teste = [
            {
                'nome': 'Vela de Ignição NGK - Teste 1',
                'preco_custo': 15.00,
                'margem_lucro': 100,
                'estoque': 10,
                'codigo_barras': '7891234567890',
                'marca': 'NGK',
                'categoria': 'Ignição'
            },
            {
                'nome': 'Filtro de Óleo Mann - Teste 2', 
                'preco_custo': 25.00,
                'margem_lucro': 80,
                'estoque': 5,
                'codigo_barras': '7891234567891',
                'marca': 'Mann',
                'categoria': 'Filtros'
            },
            {
                'nome': 'Pastilha de Freio Bosch - Teste 3',
                'preco_custo': 45.00,
                'margem_lucro': 60,
                'estoque': 8,
                'codigo_barras': '7891234567892',
                'marca': 'Bosch',
                'categoria': 'Freios'
            }
        ]
        
        for produto in produtos_teste:
            # Calcular preço de venda
            preco_venda = produto['preco_custo'] + (produto['preco_custo'] * produto['margem_lucro'] / 100)
            
            adicionar_produto(
                nome=produto['nome'],
                preco=preco_venda,
                estoque=produto['estoque'],
                estoque_minimo=5,
                codigo_barras=produto['codigo_barras'],
                descricao=f"Produto de teste - {produto['categoria']}",
                categoria=produto['categoria'],
                codigo_fornecedor=f"TESTE{produto['codigo_barras'][-3:]}",
                preco_custo=produto['preco_custo'],
                margem_lucro=produto['margem_lucro'],
                foto_url=None,
                marca=produto['marca']
            )
            
            print(f"✅ Adicionado: {produto['nome']} - R$ {preco_venda:.2f}")
        
        print(f"\n🎉 {len(produtos_teste)} produtos de teste adicionados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar produtos de teste: {e}")

if __name__ == "__main__":
    main()