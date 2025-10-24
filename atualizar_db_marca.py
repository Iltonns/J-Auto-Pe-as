#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para atualizar o banco de dados e adicionar a coluna 'marca' na tabela produtos
"""

import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), 'autopecas.db')

def atualizar_banco():
    """Atualiza o banco de dados adicionando a coluna marca se ela não existir"""
    print("Iniciando atualização do banco de dados...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a coluna marca já existe
        cursor.execute("PRAGMA table_info(produtos)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        
        if 'marca' not in colunas:
            print("Adicionando coluna 'marca' na tabela produtos...")
            cursor.execute("ALTER TABLE produtos ADD COLUMN marca TEXT")
            conn.commit()
            print("✅ Coluna 'marca' adicionada com sucesso!")
        else:
            print("✅ Coluna 'marca' já existe na tabela produtos")
        
        # Verificar produtos existentes
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1")
        total_produtos = cursor.fetchone()[0]
        print(f"📊 Total de produtos ativos: {total_produtos}")
        
        # Mostrar alguns produtos como exemplo
        if total_produtos > 0:
            cursor.execute("SELECT id, nome, marca FROM produtos WHERE ativo = 1 LIMIT 5")
            produtos = cursor.fetchall()
            print("\n📋 Primeiros 5 produtos:")
            for produto in produtos:
                marca_display = produto[2] if produto[2] else "(sem marca)"
                print(f"  - ID: {produto[0]} | Nome: {produto[1]} | Marca: {marca_display}")
        
        conn.close()
        print("\n✅ Atualização concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco de dados: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SISTEMA DE AUTOPEÇAS - ATUALIZAÇÃO DE BANCO")
    print("=" * 50)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado em: {DB_PATH}")
        print("Execute o sistema principal primeiro para criar o banco de dados.")
    else:
        print(f"📁 Banco de dados encontrado: {DB_PATH}")
        atualizar_banco()
    
    print("\n" + "=" * 50)
    input("Pressione ENTER para sair...")