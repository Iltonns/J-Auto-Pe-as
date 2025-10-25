#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar uma venda mais completa para testar o recibo com logo
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import registrar_venda, listar_produtos, listar_clientes

def criar_venda_completa():
    """Cria uma venda mais completa com cliente e desconto"""
    try:
        print("🛒 Criando venda completa para testar recibo com logo...")
        
        # Buscar produtos e clientes
        produtos = listar_produtos()
        clientes = listar_clientes()
        
        if not produtos:
            print("❌ Nenhum produto encontrado!")
            return False
            
        # Criar itens da venda (3-4 produtos)
        itens = []
        produtos_selecionados = produtos[:4] if len(produtos) >= 4 else produtos
        
        for i, produto in enumerate(produtos_selecionados):
            quantidade = i + 1  # 1, 2, 3, 4
            itens.append({
                'produto_id': produto['id'],
                'quantidade': quantidade,
                'preco_unitario': produto['preco']
            })
        
        # Usar primeiro cliente se existir
        cliente_id = clientes[0]['id'] if clientes else None
        cliente_nome = clientes[0]['nome'] if clientes else 'Cliente Avulso'
        
        # Registrar venda com desconto
        venda_id = registrar_venda(
            cliente_id=cliente_id,
            itens=itens,
            forma_pagamento='cartao_credito',
            desconto=5.50,  # Desconto de R$ 5,50
            observacoes=f'Venda para {cliente_nome} - Teste de recibo com logo da empresa',
            usuario_id=1  # Admin
        )
        
        subtotal = sum(item['quantidade'] * item['preco_unitario'] for item in itens)
        total = subtotal - 5.50
        
        print(f"✅ Venda completa #{venda_id} criada com sucesso!")
        print(f"   👤 Cliente: {cliente_nome}")
        print(f"   📦 {len(itens)} itens variados")
        print(f"   💰 Subtotal: R$ {subtotal:.2f}")
        print(f"   💸 Desconto: R$ 5,50")
        print(f"   💰 Total: R$ {total:.2f}")
        print(f"   💳 Forma: Cartão de Crédito")
        print()
        print(f"🖨️  Para ver o recibo com logo:")
        print(f"   Acesse: http://127.0.0.1:5000/vendas/{venda_id}/recibo")
        
        return venda_id
        
    except Exception as e:
        print(f"❌ Erro ao criar venda: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Teste de Recibo com Logo da Empresa")
    print("=" * 40)
    
    venda_id = criar_venda_completa()
    
    if venda_id:
        print(f"\n🎉 Venda #{venda_id} criada com sucesso!")
        print("Agora você pode ver o recibo com a logo da empresa.")
    else:
        print("\n❌ Falha ao criar venda de teste.")

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")