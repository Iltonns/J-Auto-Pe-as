#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar com XML completo e verificar produtos existentes
"""

import sys
import os
import sqlite3

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import importar_produtos_de_xml_avancado, listar_produtos, DB_PATH

def verificar_produtos_existentes():
    """
    Verifica quais produtos do XML já existem no banco
    """
    print("🔍 VERIFICAÇÃO DE PRODUTOS EXISTENTES")
    print("=" * 50)
    
    # Códigos dos produtos do XML
    produtos_xml = [
        {'codigo': '02178BRAGS', 'ean': '7891252050034', 'nome': 'RETENTOR COMANDO'},
        {'codigo': '02539BRGP', 'ean': '7891252025391', 'nome': 'RETENTOR COMANDO'},
        {'codigo': '76351', 'ean': '7891252763514', 'nome': 'JUNTA TAMPA VALVULA'},
        {'codigo': '905495', 'ean': '7908087436701', 'nome': 'MANGOTE SUSPIRO'},
        {'codigo': '4220136100', 'ean': '4005108981288', 'nome': 'BALANCIM VALVULA (UND)'},
        {'codigo': 'MG024', 'ean': '7908162300330', 'nome': 'TUBO MANGUEIRA COLETOR ADMISSAO'}
    ]
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("\n📋 STATUS DOS PRODUTOS DO XML:")
        for i, produto in enumerate(produtos_xml, 1):
            print(f"\n{i}. {produto['nome']} (Código: {produto['codigo']})")
            
            # Buscar por EAN
            cursor.execute('''
                SELECT id, nome, estoque, preco, codigo_fornecedor, codigo_barras
                FROM produtos 
                WHERE codigo_barras = ?
            ''', (produto['ean'],))
            resultado_ean = cursor.fetchone()
            
            if resultado_ean:
                print(f"   ✅ EXISTE (busca por EAN)")
                print(f"      ID: {resultado_ean[0]}")
                print(f"      Nome no banco: {resultado_ean[1]}")
                print(f"      Estoque: {resultado_ean[2]}")
                print(f"      Preço: R$ {resultado_ean[3]:.2f}")
                print(f"      Código fornecedor: {resultado_ean[4]}")
                continue
            
            # Buscar por código
            cursor.execute('''
                SELECT id, nome, estoque, preco, codigo_fornecedor, codigo_barras
                FROM produtos 
                WHERE codigo_fornecedor = ?
            ''', (produto['codigo'],))
            resultado_codigo = cursor.fetchone()
            
            if resultado_codigo:
                print(f"   ✅ EXISTE (busca por código)")
                print(f"      ID: {resultado_codigo[0]}")
                print(f"      Nome no banco: {resultado_codigo[1]}")
                print(f"      Estoque: {resultado_codigo[2]}")
                print(f"      Preço: R$ {resultado_codigo[3]:.2f}")
                print(f"      Código de barras: {resultado_codigo[5]}")
                continue
            
            # Buscar por nome similar
            cursor.execute('''
                SELECT id, nome, estoque, preco, codigo_fornecedor, codigo_barras
                FROM produtos 
                WHERE nome LIKE ?
            ''', (f'%{produto["nome"]}%',))
            resultado_nome = cursor.fetchone()
            
            if resultado_nome:
                print(f"   ⚠️  EXISTE (busca por nome similar)")
                print(f"      ID: {resultado_nome[0]}")
                print(f"      Nome no banco: {resultado_nome[1]}")
                print(f"      Estoque: {resultado_nome[2]}")
                print(f"      Preço: R$ {resultado_nome[3]:.2f}")
                continue
            
            print(f"   ❌ NÃO EXISTE - seria criado como novo produto")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_importacao_com_acao_diferente():
    """
    Testa importação forçando criação de novos produtos
    """
    print("\n\n🧪 TESTE COM AÇÃO 'IGNORAR' (para ver produtos novos)")
    print("=" * 50)
    
    xml_completo = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
<infNFe Id="NFe21251037512586000183550010000048381963032471" versao="4.00">
<det nItem="3">
<prod>
<cProd>76351</cProd>
<cEAN>7891252763514</cEAN>
<xProd>JUNTA TAMPA VALVULA</xProd>
<NCM>40169300</NCM>
<uCom>PC</uCom>
<qCom>5.0000</qCom>
<vUnCom>26.1940000000</vUnCom>
<vProd>130.97</vProd>
</prod>
</det>
<det nItem="4">
<prod>
<cProd>905495</cProd>
<cEAN>7908087436701</cEAN>
<xProd>MANGOTE SUSPIRO</xProd>
<NCM>40091290</NCM>
<uCom>PC</uCom>
<qCom>5.0000</qCom>
<vUnCom>15.5480000000</vUnCom>
<vProd>77.74</vProd>
</prod>
</det>
</infNFe>
</NFe>
</nfeProc>'''
    
    try:
        resultado = importar_produtos_de_xml_avancado(
            conteudo_xml=xml_completo,
            margem_padrao=100,
            estoque_minimo=5,
            usar_preco_nfe=True,
            acao_existente='ignorar'  # Ignorar existentes, só criar novos
        )
        
        print(f"📊 Resultado:")
        print(f"   - Produtos importados: {resultado['produtos_importados']}")
        print(f"   - Produtos ignorados: {resultado['produtos_ignorados']}")
        print(f"   - Produtos atualizados: {resultado['produtos_atualizados']}")
        
        if resultado['erros']:
            print("⚠️  Erros:")
            for erro in resultado['erros']:
                print(f"   - {erro}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_produtos_existentes()
    testar_importacao_com_acao_diferente()