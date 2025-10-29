#!/usr/bin/env python3
"""
Script para cadastrar produtos em lote a partir de arquivo Excel
Arquivo: Produtos-_29-10-2025-10-39.xlsx
Data: 29 de outubro de 2025
"""

import pandas as pd
import time
from Minha_autopecas_web.logica_banco import adicionar_produto, get_db_connection

def processar_arquivo_excel(caminho_arquivo):
    """Lê e processa o arquivo Excel"""
    try:
        df = pd.read_excel(caminho_arquivo)
        print(f"✅ Arquivo carregado com sucesso!")
        print(f"📊 Total de produtos encontrados: {len(df)}")
        print(f"📋 Colunas: {', '.join(df.columns.tolist())}\n")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return None

def criar_produto_dict(linha):
    """Converte uma linha do DataFrame em dicionário de produto"""
    # Limpar valores NaN
    codigo = str(int(linha['Código'])) if pd.notna(linha['Código']) else None
    ref_fabricante = str(linha['Ref. Fabricante']) if pd.notna(linha['Ref. Fabricante']) else None
    descricao = str(linha['Descrição']).strip() if pd.notna(linha['Descrição']) else "Sem descrição"
    estoque = int(linha['Estoque']) if pd.notna(linha['Estoque']) else 0
    marca = str(linha['Marca']).strip() if pd.notna(linha['Marca']) else ""
    valor = float(linha['Valor']) if pd.notna(linha['Valor']) else 0.0
    
    produto = {
        'codigo_barras': codigo,
        'codigo_fornecedor': ref_fabricante,
        'nome': descricao,
        'estoque': estoque,
        'marca': marca,
        'preco': valor,
        'categoria': None,  # Pode ser extraído da descrição se necessário
        'estoque_minimo': 5,
        'preco_custo': 0,
        'margem_lucro': 0,
        'descricao': None,
        'foto_url': None,
        'fornecedor_id': None
    }
    
    return produto

def verificar_produto_existe(codigo_barras):
    """Verifica se o produto já existe pelo código de barras"""
    if not codigo_barras:
        return None
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome FROM produtos WHERE codigo_barras = %s", (codigo_barras,))
    resultado = cursor.fetchone()
    
    conn.close()
    return resultado

def cadastrar_lote_produtos(df, tamanho_lote=100):
    """Cadastra produtos em lotes"""
    total_produtos = len(df)
    produtos_cadastrados = 0
    produtos_existentes = 0
    produtos_com_erro = 0
    erros = []
    
    print("=" * 80)
    print("INICIANDO CADASTRO DE PRODUTOS EM LOTE")
    print("=" * 80)
    print(f"📦 Total de produtos a processar: {total_produtos}")
    print(f"📊 Processando em lotes de {tamanho_lote} produtos\n")
    
    for i, (index, linha) in enumerate(df.iterrows(), 1):
        try:
            # Criar dicionário do produto
            produto = criar_produto_dict(linha)
            codigo_barras = produto['codigo_barras']
            
            if not codigo_barras:
                produtos_com_erro += 1
                erro_msg = f"Linha {i}: Código de barras vazio"
                erros.append(erro_msg)
                print(f"[{i}/{total_produtos}] ⚠️  {erro_msg}")
                continue
            
            # Verificar se o produto já existe
            existe = verificar_produto_existe(codigo_barras)
            
            if existe:
                produtos_existentes += 1
                if i % 100 == 0 or i <= 10:  # Mostrar apenas alguns para não poluir
                    print(f"[{i}/{total_produtos}] ⚠️  PRODUTO JÁ EXISTE - Código: {codigo_barras}")
                continue
            
            # Cadastrar o produto
            produto_id = adicionar_produto(
                nome=produto['nome'],
                preco=produto['preco'],
                estoque=produto['estoque'],
                estoque_minimo=produto['estoque_minimo'],
                codigo_barras=codigo_barras,
                descricao=produto['descricao'],
                categoria=produto['categoria'],
                codigo_fornecedor=produto['codigo_fornecedor'],
                preco_custo=produto['preco_custo'],
                margem_lucro=produto['margem_lucro'],
                foto_url=produto['foto_url'],
                marca=produto['marca'],
                fornecedor_id=produto['fornecedor_id']
            )
            
            produtos_cadastrados += 1
            
            # Mostrar progresso a cada 100 produtos ou nos primeiros 10
            if i % 100 == 0 or i <= 10:
                print(f"[{i}/{total_produtos}] ✅ CADASTRADO - ID: {produto_id} | Código: {codigo_barras} | {produto['nome'][:50]}")
            
            # Pequena pausa a cada lote para não sobrecarregar
            if i % tamanho_lote == 0:
                print(f"\n💤 Pausa de 1 segundo... ({i}/{total_produtos} processados)\n")
                time.sleep(1)
            
        except Exception as e:
            produtos_com_erro += 1
            erro_msg = f"Linha {i} - Código {linha.get('Código', 'N/A')}: {str(e)}"
            erros.append(erro_msg)
            print(f"[{i}/{total_produtos}] ❌ ERRO: {erro_msg}")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DO CADASTRO")
    print("=" * 80)
    print(f"✅ Produtos cadastrados com sucesso: {produtos_cadastrados}")
    print(f"⚠️  Produtos já existentes (ignorados): {produtos_existentes}")
    print(f"❌ Produtos com erro: {produtos_com_erro}")
    print(f"📦 Total processado: {total_produtos}")
    print("=" * 80)
    
    # Salvar erros em arquivo se houver
    if erros:
        print(f"\n⚠️  {len(erros)} erros encontrados. Salvando em 'erros_cadastro.txt'...")
        with open("erros_cadastro.txt", "w", encoding="utf-8") as f:
            f.write("ERROS NO CADASTRO DE PRODUTOS\n")
            f.write("=" * 80 + "\n\n")
            for erro in erros:
                f.write(f"{erro}\n")
        print(f"✅ Arquivo de erros salvo!")
    
    return produtos_cadastrados, produtos_existentes, produtos_com_erro

def main():
    """Função principal"""
    # Caminho do arquivo Excel
    caminho_arquivo = "Produtos-_                  29-10-2025-10-39.xlsx"
    
    # Confirmar com o usuário
    print("\n🚀 SISTEMA DE CADASTRO EM LOTE DE PRODUTOS")
    print("=" * 80)
    print(f"📂 Arquivo: {caminho_arquivo}")
    print()
    
    confirmacao = input("⚠️  Deseja prosseguir com o cadastro? (SIM/NAO): ")
    
    if confirmacao.upper() != "SIM":
        print("❌ Operação cancelada pelo usuário.")
        return
    
    print()
    
    # Processar arquivo
    df = processar_arquivo_excel(caminho_arquivo)
    
    if df is None:
        print("❌ Falha ao processar o arquivo.")
        return
    
    # Verificar colunas necessárias
    colunas_necessarias = ['Código', 'Descrição', 'Estoque', 'Valor']
    colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
    
    if colunas_faltantes:
        print(f"❌ Colunas faltantes no arquivo: {colunas_faltantes}")
        return
    
    # Cadastrar produtos
    inicio = time.time()
    cadastrados, existentes, erros = cadastrar_lote_produtos(df, tamanho_lote=100)
    fim = time.time()
    
    tempo_total = fim - inicio
    print(f"\n⏱️  Tempo total de processamento: {tempo_total:.2f} segundos")
    print(f"⚡ Média: {tempo_total/len(df):.3f} segundos por produto")
    print("\n✨ Processo finalizado!")

if __name__ == "__main__":
    main()
