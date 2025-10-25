#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar produtos no banco incluindo inativos
"""

import sys
import os
import sqlite3

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import DB_PATH

def verificar_banco_completo():
    """
    Verifica todos os produtos no banco incluindo inativos
    """
    print("🔍 VERIFICAÇÃO COMPLETA DO BANCO DE DADOS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar produtos ativos
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1")
        produtos_ativos = cursor.fetchone()[0]
        print(f"📊 Produtos ativos: {produtos_ativos}")
        
        # Verificar produtos inativos
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 0")
        produtos_inativos = cursor.fetchone()[0]
        print(f"📊 Produtos inativos: {produtos_inativos}")
        
        # Verificar todos os produtos
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor.fetchone()[0]
        print(f"📊 Total de produtos: {total_produtos}")
        
        if total_produtos > 0:
            print("\n📋 TODOS OS PRODUTOS (incluindo inativos):")
            cursor.execute("""
                SELECT id, nome, ativo, estoque, preco, codigo_fornecedor, codigo_barras, created_at
                FROM produtos 
                ORDER BY id
            """)
            
            produtos = cursor.fetchall()
            for produto in produtos:
                status = "✅ ATIVO" if produto[2] else "❌ INATIVO"
                print(f"   {produto[0]:2d}. {produto[1]} ({status})")
                print(f"       Estoque: {produto[3]} | Preço: R$ {produto[4]:.2f}")
                print(f"       Código: {produto[5] or 'N/A'} | EAN: {produto[6] or 'N/A'}")
                print(f"       Criado: {produto[7]}")
                print()
        else:
            print("\n❌ NENHUM PRODUTO ENCONTRADO NO BANCO!")
            
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='produtos'
            """)
            tabela_existe = cursor.fetchone()
            
            if tabela_existe:
                print("✅ Tabela 'produtos' existe, mas está vazia")
            else:
                print("❌ Tabela 'produtos' NÃO existe!")
        
        # Verificar último ID
        cursor.execute("SELECT MAX(id) FROM produtos")
        ultimo_id = cursor.fetchone()[0]
        print(f"\n🆔 Último ID usado: {ultimo_id or 'Nenhum'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        import traceback
        traceback.print_exc()

def testar_importacao_simples():
    """
    Testa uma importação simples para verificar se funciona
    """
    print("\n\n🧪 TESTE DE IMPORTAÇÃO SIMPLES")
    print("=" * 50)
    
    from Minha_autopecas_web.logica_banco import importar_produtos_de_xml_avancado
    
    xml_simples = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
<infNFe>
<det nItem="1">
<prod>
<cProd>TESTE123</cProd>
<cEAN>1234567890123</cEAN>
<xProd>PRODUTO TESTE IMPORTACAO</xProd>
<NCM>40169300</NCM>
<uCom>PC</uCom>
<qCom>10.0000</qCom>
<vUnCom>25.0000000000</vUnCom>
<vProd>250.00</vProd>
</prod>
</det>
</infNFe>
</NFe>
</nfeProc>'''
    
    try:
        print("📤 Importando produto de teste...")
        resultado = importar_produtos_de_xml_avancado(
            conteudo_xml=xml_simples,
            margem_padrao=100,
            estoque_minimo=5,
            usar_preco_nfe=True,
            acao_existente='atualizar_estoque'
        )
        
        print(f"📊 Resultado:")
        print(f"   - Sucesso: {resultado['sucesso']}")
        print(f"   - Produtos importados: {resultado['produtos_importados']}")
        print(f"   - Produtos atualizados: {resultado['produtos_atualizados']}")
        print(f"   - Produtos ignorados: {resultado['produtos_ignorados']}")
        
        if resultado['erros']:
            print("⚠️  Erros:")
            for erro in resultado['erros']:
                print(f"   - {erro}")
        
        # Verificar se foi realmente criado
        print("\n🔍 Verificando se o produto foi criado...")
        verificar_banco_completo()
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_banco_completo()
    testar_importacao_simples()