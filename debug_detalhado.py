#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para debugar a função de importação XML passo a passo
"""

import sys
import os
import sqlite3
import xml.etree.ElementTree as ET

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import DB_PATH

def debug_importacao_detalhada():
    """
    Debug detalhado da importação XML
    """
    xml_usuario = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
<infNFe Id="NFe21251037512586000183550010000048381963032471" versao="4.00">
<det nItem="1">
<prod>
<cProd>02178BRAGS</cProd>
<cEAN>7891252050034</cEAN>
<xProd>RETENTOR COMANDO</xProd>
<NCM>40169300</NCM>
<CEST>0100700</CEST>
<CFOP>5405</CFOP>
<uCom>PC</uCom>
<qCom>5.0000</qCom>
<vUnCom>26.1840000000</vUnCom>
<vProd>130.92</vProd>
<cEANTrib>7891252050034</cEANTrib>
<uTrib>PC</uTrib>
<qTrib>5.0000</qTrib>
<vUnTrib>26.1840000000</vUnTrib>
<indTot>1</indTot>
<nItemPed>1</nItemPed>
</prod>
</det>
<det nItem="2">
<prod>
<cProd>02539BRGP</cProd>
<cEAN>7891252025391</cEAN>
<xProd>RETENTOR COMANDO</xProd>
<NCM>40169300</NCM>
<CEST>0100700</CEST>
<CFOP>5405</CFOP>
<uCom>PC</uCom>
<qCom>5.0000</qCom>
<vUnCom>28.4720000000</vUnCom>
<vProd>142.36</vProd>
<cEANTrib>7891252025391</cEANTrib>
<uTrib>PC</uTrib>
<qTrib>5.0000</qTrib>
<vUnTrib>28.4720000000</vUnTrib>
<indTot>1</indTot>
<nItemPed>2</nItemPed>
<nFCI>B209841B-47BB-46C4-887E-20BF843849C6</nFCI>
</prod>
</det>
</infNFe>
</NFe>
</nfeProc>'''

    print("🔬 DEBUG DETALHADO DA IMPORTAÇÃO XML")
    print("=" * 70)
    
    # 1. Verificar se o XML é parseável
    print("\n1️⃣ TESTE DE PARSING XML:")
    try:
        root = ET.fromstring(xml_usuario)
        print("   ✅ XML parseado com sucesso")
        
        # Namespace da NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Buscar produtos
        produtos_xml = root.findall('.//nfe:det', ns)
        print(f"   📦 Produtos encontrados no XML: {len(produtos_xml)}")
        
        for i, det in enumerate(produtos_xml, 1):
            prod = det.find('nfe:prod', ns)
            if prod is not None:
                codigo = prod.find('nfe:cProd', ns)
                nome = prod.find('nfe:xProd', ns)
                ean = prod.find('nfe:cEAN', ns)
                
                codigo_txt = codigo.text if codigo is not None else "N/A"
                nome_txt = nome.text if nome is not None else "N/A"
                ean_txt = ean.text if ean is not None else "N/A"
                
                print(f"      {i}. {nome_txt} (Código: {codigo_txt}, EAN: {ean_txt})")
                
    except Exception as e:
        print(f"   ❌ Erro no parsing: {e}")
        return

    # 2. Verificar banco de dados
    print("\n2️⃣ VERIFICAÇÃO DO BANCO DE DADOS:")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela produtos existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='produtos'
        """)
        tabela_existe = cursor.fetchone()
        
        if tabela_existe:
            print("   ✅ Tabela 'produtos' existe")
            
            # Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(produtos)")
            colunas = cursor.fetchall()
            print(f"   📋 Colunas da tabela: {len(colunas)}")
            for coluna in colunas:
                print(f"      - {coluna[1]} ({coluna[2]})")
                
            # Contar produtos
            cursor.execute("SELECT COUNT(*) FROM produtos")
            total_produtos = cursor.fetchone()[0]
            print(f"   📊 Total de produtos: {total_produtos}")
            
        else:
            print("   ❌ Tabela 'produtos' NÃO existe!")
            return
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar banco: {e}")
        return

    # 3. Simular importação passo a passo
    print("\n3️⃣ SIMULAÇÃO DA IMPORTAÇÃO:")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        root = ET.fromstring(xml_usuario)
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        produtos_xml = root.findall('.//nfe:det', ns)
        
        for i, det in enumerate(produtos_xml, 1):
            print(f"\n   📦 PROCESSANDO PRODUTO {i}:")
            prod = det.find('nfe:prod', ns)
            
            if prod is None:
                print("      ❌ Elemento <prod> não encontrado")
                continue
                
            # Extrair dados
            codigo_produto = prod.find('nfe:cProd', ns)
            nome_produto = prod.find('nfe:xProd', ns)
            codigo_ean = prod.find('nfe:cEAN', ns)
            quantidade_elem = prod.find('nfe:qCom', ns)
            preco_unitario = prod.find('nfe:vUnCom', ns)
            
            codigo_produto_txt = codigo_produto.text if codigo_produto is not None else None
            nome_produto_txt = nome_produto.text if nome_produto is not None else None
            codigo_ean_txt = codigo_ean.text if codigo_ean is not None else None
            quantidade = float(quantidade_elem.text) if quantidade_elem is not None else 0
            preco = float(preco_unitario.text) if preco_unitario is not None else 0
            
            print(f"      📝 Dados extraídos:")
            print(f"         - Código: {codigo_produto_txt}")
            print(f"         - Nome: {nome_produto_txt}")
            print(f"         - EAN: {codigo_ean_txt}")
            print(f"         - Quantidade: {quantidade}")
            print(f"         - Preço: R$ {preco:.2f}")
            
            # Verificar se produto já existe
            produto_existente = None
            if codigo_ean_txt:
                cursor.execute('''
                    SELECT id, nome, preco, estoque 
                    FROM produtos 
                    WHERE codigo_barras = ?
                ''', (codigo_ean_txt,))
                produto_existente = cursor.fetchone()
                print(f"         🔍 Busca por EAN ({codigo_ean_txt}): {'Encontrado' if produto_existente else 'Não encontrado'}")
            
            if not produto_existente and codigo_produto_txt:
                cursor.execute('''
                    SELECT id, nome, preco, estoque 
                    FROM produtos 
                    WHERE codigo_fornecedor = ? OR nome LIKE ?
                ''', (codigo_produto_txt, f'%{codigo_produto_txt}%'))
                produto_existente = cursor.fetchone()
                print(f"         🔍 Busca por código ({codigo_produto_txt}): {'Encontrado' if produto_existente else 'Não encontrado'}")
            
            if produto_existente:
                print(f"         ✅ Produto existente encontrado (ID: {produto_existente[0]})")
                print(f"            Ação seria: atualizar_estoque")
                print(f"            Estoque atual: {produto_existente[3]} → Novo: {produto_existente[3] + quantidade}")
            else:
                print(f"         🆕 Produto novo seria criado")
                print(f"            Inserção na tabela produtos")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erro na simulação: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)

if __name__ == "__main__":
    debug_importacao_detalhada()