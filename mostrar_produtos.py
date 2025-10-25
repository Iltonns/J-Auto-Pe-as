#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para mostrar produtos existentes e demonstrar atualização de estoque
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import listar_produtos

def mostrar_produtos_atuais():
    """
    Mostra os produtos atuais no banco
    """
    print("📦 PRODUTOS ATUAIS NO BANCO DE DADOS")
    print("=" * 60)
    
    try:
        produtos = listar_produtos()
        print(f"Total de produtos: {len(produtos)}")
        print()
        
        # Mostrar produtos do XML especificamente
        codigos_xml = ['02178BRAGS', '02539BRGP', '76351', '905495', '4220136100', 'MG024']
        nomes_xml = ['RETENTOR COMANDO', 'JUNTA TAMPA VALVULA', 'MANGOTE SUSPIRO', 
                    'BALANCIM VALVULA', 'TUBO MANGUEIRA COLETOR ADMISSAO']
        
        print("🎯 PRODUTOS DO XML IMPORTADO:")
        for produto in produtos:
            if (produto.get('codigo_fornecedor') in codigos_xml or 
                any(nome in produto.get('nome', '') for nome in nomes_xml)):
                
                print(f"   📦 {produto['nome']}")
                print(f"      ID: {produto['id']}")
                print(f"      Código: {produto.get('codigo_fornecedor', 'N/A')}")
                print(f"      Código de Barras: {produto.get('codigo_barras', 'N/A')}")
                print(f"      Estoque: {produto['estoque']}")
                print(f"      Preço: R$ {produto['preco']:.2f}")
                print(f"      Categoria: {produto.get('categoria', 'N/A')}")
                print()
        
        print("\n📋 TODOS OS PRODUTOS NO SISTEMA:")
        print("-" * 60)
        for i, produto in enumerate(produtos, 1):
            print(f"{i:2d}. {produto['nome']} (Estoque: {produto['estoque']}) - R$ {produto['preco']:.2f}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    mostrar_produtos_atuais()