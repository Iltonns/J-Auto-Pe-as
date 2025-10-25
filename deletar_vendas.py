#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para deletar todas as vendas do sistema
ATENÇÃO: Esta operação é irreversível!
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import deletar_todas_vendas, listar_vendas

def confirmar_operacao():
    """Solicita confirmação do usuário antes de executar"""
    print("=" * 60)
    print("🚨 DELETAR TODAS AS VENDAS DO SISTEMA 🚨")
    print("=" * 60)
    print()
    print("⚠️  ATENÇÃO: Esta operação irá:")
    print("   • Deletar TODAS as vendas registradas")
    print("   • Deletar TODOS os itens de venda")
    print("   • Deletar movimentações de caixa relacionadas")
    print("   • Deletar contas a receber de vendas")
    print("   • Restaurar o estoque dos produtos vendidos")
    print()
    print("❌ Esta operação é IRREVERSÍVEL!")
    print()
    
    # Mostrar quantas vendas existem
    try:
        vendas = listar_vendas(limit=1000)
        total_vendas = len(vendas)
        print(f"📊 Atualmente existem {total_vendas} vendas no sistema")
        
        if total_vendas > 0:
            print(f"   📅 Vendas de {vendas[-1]['data_venda']} até {vendas[0]['data_venda']}")
            total_valor = sum(venda['total'] for venda in vendas)
            print(f"   💰 Valor total: R$ {total_valor:.2f}")
    except Exception as e:
        print(f"❌ Erro ao verificar vendas: {e}")
        return False
    
    print()
    print("Para confirmar, digite exatamente: CONFIRMO DELETAR TODAS AS VENDAS")
    confirmacao = input("Confirmação: ").strip()
    
    return confirmacao == "CONFIRMO DELETAR TODAS AS VENDAS"

def main():
    """Função principal"""
    print("Sistema de Autopeças - Deletar Vendas")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Solicitar confirmação
    if not confirmar_operacao():
        print("❌ Operação cancelada pelo usuário.")
        return
    
    print()
    print("🔄 Executando operação...")
    print()
    
    # Executar a operação
    try:
        resultado = deletar_todas_vendas(restaurar_estoque=True)
        
        if resultado['erro']:
            print(f"❌ Erro ao deletar vendas: {resultado['erro']}")
            return
        
        # Mostrar resultados
        print("✅ Operação concluída com sucesso!")
        print()
        print("📊 Resumo da operação:")
        print(f"   • Vendas deletadas: {resultado['vendas_deletadas']}")
        print(f"   • Itens deletados: {resultado['itens_deletados']}")
        print(f"   • Movimentações de caixa deletadas: {resultado['movimentacoes_caixa_deletadas']}")
        
        if resultado['estoque_restaurado']:
            print()
            print("📦 Estoque restaurado:")
            for produto, quantidade in resultado['estoque_restaurado'].items():
                print(f"   • {produto}: +{quantidade} unidades")
        
        print()
        print("🎉 Todas as vendas foram removidas do sistema!")
        print("   O estoque dos produtos foi restaurado.")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")