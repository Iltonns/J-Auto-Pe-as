#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para ativar produtos inativos do XML importado
"""

import sys
import os
import sqlite3

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import DB_PATH

def ativar_produtos_xml():
    """
    Ativa os produtos que foram importados via XML mas ficaram inativos
    """
    print("🔧 ATIVANDO PRODUTOS DO XML IMPORTADO")
    print("=" * 50)
    
    # Códigos dos produtos do XML
    codigos_xml = ['02178BRAGS', '02539BRGP', '76351', '905495', '4220136100', 'MG024']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("📋 Ativando produtos do XML...")
        produtos_ativados = 0
        
        for codigo in codigos_xml:
            cursor.execute('''
                UPDATE produtos 
                SET ativo = 1 
                WHERE codigo_fornecedor = ? AND ativo = 0
            ''', (codigo,))
            
            if cursor.rowcount > 0:
                # Buscar informações do produto
                cursor.execute('''
                    SELECT id, nome FROM produtos 
                    WHERE codigo_fornecedor = ?
                ''', (codigo,))
                produto = cursor.fetchone()
                
                if produto:
                    print(f"   ✅ Ativado: {produto[1]} (ID: {produto[0]})")
                    produtos_ativados += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Total de produtos ativados: {produtos_ativados}")
        
        # Verificar resultado
        print("\n🔍 Verificando produtos ativos após ativação...")
        from Minha_autopecas_web.logica_banco import listar_produtos
        
        produtos = listar_produtos()
        print(f"📊 Total de produtos ativos agora: {len(produtos)}")
        
        print("\n📦 PRODUTOS DO XML AGORA ATIVOS:")
        for produto in produtos:
            if produto.get('codigo_fornecedor') in codigos_xml:
                print(f"   📦 {produto['nome']}")
                print(f"      ID: {produto['id']} | Código: {produto.get('codigo_fornecedor')}")
                print(f"      Estoque: {produto['estoque']} | Preço: R$ {produto['preco']:.2f}")
                print()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ativar_produtos_xml()