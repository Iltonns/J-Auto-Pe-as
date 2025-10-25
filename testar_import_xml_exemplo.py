#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para a funcionalidade de importação de produtos via XML de NFe
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import importar_produtos_de_xml_avancado

def testar_exemplo_xml():
    """
    Testa a importação com um exemplo do XML fornecido
    """
    xml_exemplo = '''<?xml version="1.0" encoding="UTF-8"?>
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
</prod>
</det>
</infNFe>
</NFe>
</nfeProc>'''

    print("🔄 Testando importação de produtos via XML...")
    print("-" * 50)
    
    try:
        # Testar com configurações padrão
        resultado = importar_produtos_de_xml_avancado(
            conteudo_xml=xml_exemplo,
            margem_padrao=100,  # 100% de margem
            estoque_minimo=5,
            usar_preco_nfe=True,
            acao_existente='atualizar_estoque'
        )
        
        print("✅ Resultado da importação:")
        print(f"   - Sucesso: {resultado['sucesso']}")
        print(f"   - Produtos importados: {resultado['produtos_importados']}")
        print(f"   - Produtos atualizados: {resultado['produtos_atualizados']}")
        print(f"   - Produtos ignorados: {resultado['produtos_ignorados']}")
        
        if resultado['erros']:
            print("⚠️  Erros encontrados:")
            for erro in resultado['erros']:
                print(f"   - {erro}")
        
        if not resultado['sucesso']:
            print(f"❌ Erro geral: {resultado.get('erro', 'Erro desconhecido')}")
        
        print("\n🎯 Dados que seriam extraídos do XML:")
        print("   - Produto 1:")
        print("     * Código: 02178BRAGS")
        print("     * Nome: RETENTOR COMANDO")
        print("     * Código de Barras: 7891252050034")
        print("     * NCM: 40169300")
        print("     * Unidade: PC")
        print("     * Quantidade: 5.0000")
        print("     * Preço unitário: R$ 26.18")
        print("   - Produto 2:")
        print("     * Código: 02539BRGP")
        print("     * Nome: RETENTOR COMANDO")
        print("     * Código de Barras: 7891252025391")
        print("     * NCM: 40169300")
        print("     * Unidade: PC")
        print("     * Quantidade: 5.0000")
        print("     * Preço unitário: R$ 28.47")
        
        return resultado['sucesso']
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Teste da funcionalidade de importação XML")
    print("=" * 50)
    
    sucesso = testar_exemplo_xml()
    
    print("\n" + "=" * 50)
    if sucesso:
        print("✅ Teste concluído com sucesso!")
        print("💡 A funcionalidade de importação XML está funcionando.")
        print("📋 Você pode usar esta funcionalidade na área de produtos:")
        print("   1. Acesse a página de produtos")
        print("   2. Clique em 'Importar XML'")
        print("   3. Selecione um arquivo XML de NFe")
        print("   4. Configure as opções de importação")
        print("   5. Clique em 'Importar Produtos'")
    else:
        print("❌ Teste falhou!")
        print("⚠️  Verifique se a base de dados está funcionando corretamente.")