#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar a nova funcionalidade de importação XML avançada
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import *

def testar_import_xml():
    """Testa as funcionalidades de importação XML"""
    
    print("=== TESTE DO SISTEMA DE IMPORTAÇÃO XML AVANÇADO ===\n")
    
    # Criar XML de teste NFe real
    xml_teste = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <NFe xmlns="http://www.portalfiscal.inf.br/nfe">
        <infNFe versao="4.00" Id="NFe35200714200166000187550010000000046550010500">
            <ide>
                <cUF>35</cUF>
                <cNF>05500105</cNF>
                <natOp>Venda de mercadoria</natOp>
                <mod>55</mod>
                <serie>1</serie>
                <nNF>46</nNF>
                <dhEmi>2020-07-01T10:00:00-03:00</dhEmi>
                <tpNF>1</tpNF>
                <idDest>1</idDest>
                <cMunFG>3550308</cMunFG>
                <tpImp>1</tpImp>
                <tpEmis>1</tpEmis>
                <cDV>5</cDV>
                <tpAmb>2</tpAmb>
                <finNFe>1</finNFe>
                <indFinal>1</indFinal>
                <indPres>1</indPres>
            </ide>
            <emit>
                <CNPJ>14200166000187</CNPJ>
                <xNome>AUTOPECAS TESTE LTDA</xNome>
                <enderEmit>
                    <xLgr>RUA DAS PECAS</xLgr>
                    <nro>123</nro>
                    <xBairro>CENTRO</xBairro>
                    <cMun>3550308</cMun>
                    <xMun>SAO PAULO</xMun>
                    <UF>SP</UF>
                    <CEP>01000000</CEP>
                </enderEmit>
                <IE>123456789</IE>
                <CRT>3</CRT>
            </emit>
            <dest>
                <CPF>12345678901</CPF>
                <xNome>CLIENTE TESTE</xNome>
                <enderDest>
                    <xLgr>RUA DO CLIENTE</xLgr>
                    <nro>456</nro>
                    <xBairro>VILA TESTE</xBairro>
                    <cMun>3550308</cMun>
                    <xMun>SAO PAULO</xMun>
                    <UF>SP</UF>
                    <CEP>02000000</CEP>
                </enderDest>
                <indIEDest>9</indIEDest>
            </dest>
            <det nItem="1">
                <prod>
                    <cProd>001</cProd>
                    <cEAN>7891234567890</cEAN>
                    <xProd>PASTILHA DE FREIO DIANTEIRA</xProd>
                    <NCM>87089100</NCM>
                    <CEST>0101100</CEST>
                    <uCom>UN</uCom>
                    <qCom>2.0000</qCom>
                    <vUnCom>45.5000</vUnCom>
                    <vProd>91.00</vProd>
                    <cEANTrib>7891234567890</cEANTrib>
                    <uTrib>UN</uTrib>
                    <qTrib>2.0000</qTrib>
                    <vUnTrib>45.5000</vUnTrib>
                    <indTot>1</indTot>
                </prod>
            </det>
            <det nItem="2">
                <prod>
                    <cProd>002</cProd>
                    <cEAN>7891234567891</cEAN>
                    <xProd>DISCO DE FREIO VENTILADO</xProd>
                    <NCM>87089200</NCM>
                    <CEST>0101200</CEST>
                    <uCom>UN</uCom>
                    <qCom>1.0000</qCom>
                    <vUnCom>120.0000</vUnCom>
                    <vProd>120.00</vProd>
                    <cEANTrib>7891234567891</cEANTrib>
                    <uTrib>UN</uTrib>
                    <qTrib>1.0000</qTrib>
                    <vUnTrib>120.0000</vUnTrib>
                    <indTot>1</indTot>
                </prod>
            </det>
            <det nItem="3">
                <prod>
                    <cProd>003</cProd>
                    <cEAN>SEM GTIN</cEAN>
                    <xProd>FILTRO DE AR MOTOR</xProd>
                    <NCM>84213100</NCM>
                    <uCom>UN</uCom>
                    <qCom>1.0000</qCom>
                    <vUnCom>35.0000</vUnCom>
                    <vProd>35.00</vProd>
                    <cEANTrib>SEM GTIN</cEANTrib>
                    <uTrib>UN</uTrib>
                    <qTrib>1.0000</qTrib>
                    <vUnTrib>35.0000</vUnTrib>
                    <indTot>1</indTot>
                </prod>
            </det>
        </infNFe>
    </NFe>
    <protNFe versao="4.00">
        <infProt>
            <tpAmb>2</tpAmb>
            <verAplic>SP_NFE_PL_008_V4.00</verAplic>
            <chNFe>35200714200166000187550010000000046550010500</chNFe>
            <dhRecbto>2020-07-01T10:01:00-03:00</dhRecbto>
            <nProt>135200000000000</nProt>
            <digVal>abcd1234</digVal>
            <cStat>100</cStat>
            <xMotivo>Autorizado o uso da NF-e</xMotivo>
        </infProt>
    </protNFe>
</nfeProc>'''
    
    print("1. Testando importação com configurações padrão...")
    resultado1 = importar_produtos_de_xml_avancado(
        conteudo_xml=xml_teste,
        margem_padrao=100,
        estoque_minimo=5,
        usar_preco_nfe=True,
        acao_existente='atualizar_estoque'
    )
    
    print(f"   Sucesso: {resultado1['sucesso']}")
    print(f"   Produtos importados: {resultado1['produtos_importados']}")
    print(f"   Produtos atualizados: {resultado1['produtos_atualizados']}")
    print(f"   Produtos ignorados: {resultado1['produtos_ignorados']}")
    print(f"   Erros: {len(resultado1['erros'])}")
    
    if resultado1['erros']:
        print("   Detalhes dos erros:")
        for erro in resultado1['erros']:
            print(f"   - {erro}")
    
    print("\n2. Testando importação novamente (deve atualizar estoque)...")
    resultado2 = importar_produtos_de_xml_avancado(
        conteudo_xml=xml_teste,
        margem_padrao=50,
        estoque_minimo=10,
        usar_preco_nfe=True,
        acao_existente='atualizar_estoque'
    )
    
    print(f"   Sucesso: {resultado2['sucesso']}")
    print(f"   Produtos importados: {resultado2['produtos_importados']}")
    print(f"   Produtos atualizados: {resultado2['produtos_atualizados']}")
    print(f"   Produtos ignorados: {resultado2['produtos_ignorados']}")
    
    print("\n3. Testando importação com substituição de dados...")
    resultado3 = importar_produtos_de_xml_avancado(
        conteudo_xml=xml_teste,
        margem_padrao=200,
        estoque_minimo=15,
        usar_preco_nfe=True,
        acao_existente='substituir_dados'
    )
    
    print(f"   Sucesso: {resultado3['sucesso']}")
    print(f"   Produtos importados: {resultado3['produtos_importados']}")
    print(f"   Produtos atualizados: {resultado3['produtos_atualizados']}")
    print(f"   Produtos ignorados: {resultado3['produtos_ignorados']}")
    
    print("\n4. Verificando produtos no banco...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT nome, categoria, preco_custo, preco, estoque, estoque_minimo, ncm, codigo_barras
            FROM produtos 
            WHERE codigo_fornecedor IN ('001', '002', '003')
            ORDER BY codigo_fornecedor
        """)
        
        produtos = cursor.fetchall()
        
        print(f"   Encontrados {len(produtos)} produtos:")
        for produto in produtos:
            print(f"   - Nome: {produto[0]}")
            print(f"     Categoria: {produto[1]}")
            print(f"     Preço Custo: R$ {produto[2]:.2f}")
            print(f"     Preço Venda: R$ {produto[3]:.2f}")
            print(f"     Estoque: {produto[4]}")
            print(f"     Estoque Mín: {produto[5]}")
            print(f"     NCM: {produto[6]}")
            print(f"     Código Barras: {produto[7] or 'Não informado'}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"   Erro ao verificar produtos: {str(e)}")
    
    print("=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    testar_import_xml()