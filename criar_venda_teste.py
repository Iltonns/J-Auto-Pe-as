#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar uma venda de teste para validar a impressão
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import registrar_venda, listar_produtos

def criar_venda_teste():
    """Cria uma venda de teste"""
    try:
        print("🛒 Criando venda de teste para validar impressão...")
        
        # Buscar produtos disponíveis
        produtos = listar_produtos()
        if not produtos:
            print("❌ Nenhum produto encontrado no sistema!")
            return False
            
        # Pegar os primeiros produtos disponíveis
        produtos_teste = produtos[:2]  # Pegar 2 produtos
        
        # Criar itens da venda
        itens = []
        for i, produto in enumerate(produtos_teste):
            quantidade = i + 1  # 1, 2, etc.
            itens.append({
                'produto_id': produto['id'],
                'quantidade': quantidade,
                'preco_unitario': produto['preco']
            })
        
        # Registrar a venda
        venda_id = registrar_venda(
            cliente_id=None,  # Cliente avulso
            itens=itens,
            forma_pagamento='dinheiro',
            desconto=0,
            observacoes='Venda de teste para validar impressão de recibo',
            usuario_id=1  # Admin
        )
        
        print(f"✅ Venda de teste #{venda_id} criada com sucesso!")
        print(f"   📦 {len(itens)} itens adicionados")
        
        total = sum(item['quantidade'] * item['preco_unitario'] for item in itens)
        print(f"   💰 Total: R$ {total:.2f}")
        print()
        print(f"🖨️  Para testar a impressão:")
        print(f"   1. Acesse: http://127.0.0.1:5000/vendas")
        print(f"   2. Clique no botão de impressão da venda #{venda_id}")
        print(f"   3. Ou acesse diretamente: http://127.0.0.1:5000/vendas/{venda_id}/recibo")
        
        return venda_id
        
    except Exception as e:
        print(f"❌ Erro ao criar venda de teste: {e}")
        return False

def main():
    print("Script de Teste - Impressão de Recibo")
    print("=" * 40)
    
    venda_id = criar_venda_teste()
    
    if venda_id:
        print("\n🎉 Teste criado com sucesso!")
        print("Agora você pode testar a funcionalidade de impressão.")
    else:
        print("\n❌ Falha ao criar teste.")

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")