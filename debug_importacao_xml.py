#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para debugar a importação do XML específico fornecido pelo usuário
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Minha_autopecas_web.logica_banco import importar_produtos_de_xml_avancado, listar_produtos

def testar_xml_usuario():
    """
    Testa a importação com o XML específico fornecido pelo usuário
    """
    xml_usuario = '''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
<infNFe Id="NFe21251037512586000183550010000048381963032471" versao="4.00">
<ide>
<cUF>21</cUF>
<cNF>96303247</cNF>
<natOp>VENDA DE MERCADORIAS</natOp>
<mod>55</mod>
<serie>1</serie>
<nNF>4838</nNF>
<dhEmi>2025-10-02T10:04:15-03:00</dhEmi>
<dhSaiEnt>2025-10-02T10:19:15-03:00</dhSaiEnt>
<tpNF>1</tpNF>
<idDest>1</idDest>
<cMunFG>2111300</cMunFG>
<tpImp>1</tpImp>
<tpEmis>1</tpEmis>
<cDV>1</cDV>
<tpAmb>1</tpAmb>
<finNFe>1</finNFe>
<indFinal>0</indFinal>
<indPres>9</indPres>
<indIntermed>0</indIntermed>
<procEmi>0</procEmi>
<verProc>FLEXTOTAL 6.1.0.23</verProc>
</ide>
<emit>
<CNPJ>37512586000183</CNPJ>
<xNome>13 - AUTOGIRO AUTOPECAS SAO LUIS LTDA</xNome>
<xFant>13 - AUTOGIRO AUTOPECAS SAO LUIS LTDA</xFant>
<enderEmit>
<xLgr>AV. GUAJAJARAS</xLgr>
<nro>011</nro>
<xCpl>LETRA E</xCpl>
<xBairro>JARDIM SAO CRISTOVAO</xBairro>
<cMun>2111300</cMun>
<xMun>SAO LUIS</xMun>
<UF>MA</UF>
<CEP>65056045</CEP>
<cPais>1058</cPais>
<xPais>BRASIL</xPais>
<fone>9830208922</fone>
</enderEmit>
<IE>126490210</IE>
<CRT>3</CRT>
</emit>
<dest>
<CNPJ>51608257000161</CNPJ>
<xNome>SILVA AUTOPECAS LTDA</xNome>
<enderDest>
<xLgr>RUA AVENIDA 01</xLgr>
<nro>029</nro>
<xBairro>PARANA III</xBairro>
<cMun>2107506</cMun>
<xMun>PACO DO LUMIAR</xMun>
<UF>MA</UF>
<CEP>65130000</CEP>
<cPais>1058</cPais>
<xPais>BRASIL</xPais>
<fone>98984796947</fone>
</enderDest>
<indIEDest>1</indIEDest>
<IE>128161299</IE>
<email>loja.silva.autopecas@gmail.com</email>
</dest>
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
<det nItem="3">
<prod>
<cProd>76351</cProd>
<cEAN>7891252763514</cEAN>
<xProd>JUNTA TAMPA VALVULA</xProd>
<NCM>40169300</NCM>
<CEST>0100700</CEST>
<CFOP>5405</CFOP>
<uCom>PC</uCom>
<qCom>5.0000</qCom>
<vUnCom>26.1940000000</vUnCom>
<vProd>130.97</vProd>
<cEANTrib>7891252763514</cEANTrib>
<uTrib>PC</uTrib>
<qTrib>5.0000</qTrib>
<vUnTrib>26.1940000000</vUnTrib>
<indTot>1</indTot>
<nItemPed>3</nItemPed>
</prod>
</det>
<det nItem="4">
<prod>
<cProd>905495</cProd>
<cEAN>7908087436701</cEAN>
<xProd>MANGOTE SUSPIRO</xProd>
<NCM>40091290</NCM>
<CEST>0199900</CEST>
<CFOP>5405</CFOP>
<uCom>PC</uCom>
<qCom>5.0000</qCom>
<vUnCom>15.5480000000</vUnCom>
<vProd>77.74</vProd>
<cEANTrib>7908087436701</cEANTrib>
<uTrib>PC</uTrib>
<qTrib>5.0000</qTrib>
<vUnTrib>15.5480000000</vUnTrib>
<indTot>1</indTot>
<nItemPed>4</nItemPed>
</prod>
</det>
<det nItem="5">
<prod>
<cProd>4220136100</cProd>
<cEAN>4005108981288</cEAN>
<xProd>BALANCIM VALVULA (UND)</xProd>
<NCM>84099190</NCM>
<CEST>0103000</CEST>
<CFOP>5405</CFOP>
<uCom>PC</uCom>
<qCom>8.0000</qCom>
<vUnCom>31.0000000000</vUnCom>
<vProd>248.00</vProd>
<cEANTrib>4005108981288</cEANTrib>
<uTrib>PC</uTrib>
<qTrib>8.0000</qTrib>
<vUnTrib>31.0000000000</vUnTrib>
<indTot>1</indTot>
<nItemPed>5</nItemPed>
</prod>
</det>
<det nItem="6">
<prod>
<cProd>MG024</cProd>
<cEAN>7908162300330</cEAN>
<xProd>TUBO MANGUEIRA COLETOR ADMISSAO</xProd>
<NCM>39174090</NCM>
<CEST>0100200</CEST>
<CFOP>5405</CFOP>
<uCom>PC</uCom>
<qCom>5.0000</qCom>
<vUnCom>18.0000000000</vUnCom>
<vProd>90.00</vProd>
<cEANTrib>7908162300330</cEANTrib>
<uTrib>PC</uTrib>
<qTrib>5.0000</qTrib>
<vUnTrib>18.0000000000</vUnTrib>
<indTot>1</indTot>
<nItemPed>6</nItemPed>
</prod>
</det>
</infNFe>
</NFe>
</nfeProc>'''

    print("🔍 DIAGNÓSTICO DA IMPORTAÇÃO XML")
    print("=" * 60)
    
    # Verificar produtos existentes antes da importação
    print("\n1️⃣ PRODUTOS EXISTENTES ANTES DA IMPORTAÇÃO:")
    try:
        produtos_antes = listar_produtos()
        print(f"   📊 Total de produtos no banco: {len(produtos_antes)}")
        
        for produto in produtos_antes[:10]:  # Mostrar apenas os primeiros 10
            print(f"   - ID {produto['id']}: {produto['nome']} (Código: {produto.get('codigo_fornecedor', 'N/A')})")
            
        if len(produtos_antes) > 10:
            print(f"   ... e mais {len(produtos_antes) - 10} produtos")
            
    except Exception as e:
        print(f"   ❌ Erro ao listar produtos: {e}")

    print("\n2️⃣ TESTANDO IMPORTAÇÃO XML:")
    try:
        # Testar com configurações padrão
        resultado = importar_produtos_de_xml_avancado(
            conteudo_xml=xml_usuario,
            margem_padrao=100,  # 100% de margem
            estoque_minimo=5,
            usar_preco_nfe=True,
            acao_existente='atualizar_estoque'  # Mudando para testar
        )
        
        print(f"   ✅ Resultado da importação:")
        print(f"      - Sucesso: {resultado['sucesso']}")
        print(f"      - Produtos importados: {resultado['produtos_importados']}")
        print(f"      - Produtos atualizados: {resultado['produtos_atualizados']}")
        print(f"      - Produtos ignorados: {resultado['produtos_ignorados']}")
        
        if resultado['erros']:
            print("   ⚠️  ERROS ENCONTRADOS:")
            for i, erro in enumerate(resultado['erros'], 1):
                print(f"      {i}. {erro}")
        
        if not resultado['sucesso']:
            print(f"   ❌ ERRO GERAL: {resultado.get('erro', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"   ❌ ERRO DURANTE IMPORTAÇÃO: {str(e)}")
        import traceback
        print("   📋 Detalhes do erro:")
        traceback.print_exc()

    print("\n3️⃣ PRODUTOS APÓS IMPORTAÇÃO:")
    try:
        produtos_depois = listar_produtos()
        print(f"   📊 Total de produtos no banco: {len(produtos_depois)}")
        
        # Verificar se algum produto novo foi adicionado
        novos_produtos = []
        if len(produtos_depois) > len(produtos_antes):
            novos_produtos = produtos_depois[len(produtos_antes):]
            print(f"   🆕 Novos produtos adicionados: {len(novos_produtos)}")
            for produto in novos_produtos:
                print(f"      - {produto['nome']} (Código: {produto.get('codigo_fornecedor', 'N/A')})")
        else:
            print("   ℹ️  Nenhum produto novo foi adicionado")
            
        # Verificar produtos específicos do XML
        print("\n   🔍 VERIFICANDO PRODUTOS ESPECÍFICOS DO XML:")
        codigos_xml = ['02178BRAGS', '02539BRGP', '76351', '905495', '4220136100', 'MG024']
        
        for codigo in codigos_xml:
            produto_encontrado = None
            for produto in produtos_depois:
                if produto.get('codigo_fornecedor') == codigo or produto.get('codigo_barras') == codigo:
                    produto_encontrado = produto
                    break
            
            if produto_encontrado:
                print(f"      ✅ {codigo}: {produto_encontrado['nome']} (ID: {produto_encontrado['id']})")
            else:
                print(f"      ❌ {codigo}: NÃO ENCONTRADO")
                
    except Exception as e:
        print(f"   ❌ Erro ao listar produtos após importação: {e}")

    print("\n" + "=" * 60)
    return True

if __name__ == "__main__":
    testar_xml_usuario()