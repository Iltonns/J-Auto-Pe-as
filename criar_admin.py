#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar usuário administrador no sistema
Execute: python criar_admin.py
"""

import psycopg2
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def criar_usuario_admin():
    """Cria ou atualiza o usuário administrador"""
    print("🔧 Conectando ao banco de dados...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Verificar se o usuário admin já existe
        cursor.execute("SELECT id, username FROM usuarios WHERE username = 'admin'")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"⚠️  Usuário 'admin' já existe (ID: {resultado[0]})")
            resposta = input("Deseja redefinir a senha para 'admin123'? (s/n): ").strip().lower()
            
            if resposta == 's':
                password_hash = generate_password_hash('admin123')
                cursor.execute('''
                    UPDATE usuarios SET 
                        password_hash = %s,
                        nome_completo = 'Administrador do Sistema',
                        email = 'admin@autopecas.com',
                        ativo = TRUE,
                        permissao_vendas = TRUE,
                        permissao_estoque = TRUE,
                        permissao_clientes = TRUE,
                        permissao_financeiro = TRUE,
                        permissao_caixa = TRUE,
                        permissao_relatorios = TRUE,
                        permissao_admin = TRUE
                    WHERE username = 'admin'
                ''', (password_hash,))
                conn.commit()
                print("✅ Senha do usuário 'admin' redefinida com sucesso!")
            else:
                print("❌ Operação cancelada.")
        else:
            print("📝 Criando novo usuário administrador...")
            password_hash = generate_password_hash('admin123')
            
            cursor.execute('''
                INSERT INTO usuarios (
                    username, password_hash, nome_completo, email, ativo,
                    permissao_vendas, permissao_estoque, permissao_clientes,
                    permissao_financeiro, permissao_caixa, permissao_relatorios, 
                    permissao_admin
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', ('admin', password_hash, 'Administrador do Sistema', 
                  'admin@autopecas.com', True, True, True, True, True, True, True, True))
            
            conn.commit()
            print("✅ Usuário administrador criado com sucesso!")
        
        print("\n" + "="*50)
        print("📋 CREDENCIAIS DE ACESSO:")
        print("="*50)
        print("Usuário: admin")
        print("Senha: admin123")
        print("="*50)
        print("\n⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao conectar/criar usuário: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    
    return True

def criar_usuario_personalizado():
    """Cria um usuário personalizado"""
    print("\n" + "="*50)
    print("📝 CRIAR NOVO USUÁRIO")
    print("="*50)
    
    username = input("Nome de usuário: ").strip()
    if not username:
        print("❌ Nome de usuário não pode ser vazio!")
        return
    
    senha = input("Senha: ").strip()
    if not senha:
        print("❌ Senha não pode ser vazia!")
        return
    
    nome_completo = input("Nome completo: ").strip()
    email = input("Email: ").strip()
    
    print("\n📋 PERMISSÕES (s/n):")
    perm_vendas = input("Vendas? (s/n): ").strip().lower() == 's'
    perm_estoque = input("Estoque? (s/n): ").strip().lower() == 's'
    perm_clientes = input("Clientes? (s/n): ").strip().lower() == 's'
    perm_financeiro = input("Financeiro? (s/n): ").strip().lower() == 's'
    perm_caixa = input("Caixa? (s/n): ").strip().lower() == 's'
    perm_relatorios = input("Relatórios? (s/n): ").strip().lower() == 's'
    perm_admin = input("Administrador? (s/n): ").strip().lower() == 's'
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Verificar se usuário já existe
        cursor.execute("SELECT username FROM usuarios WHERE username = %s", (username,))
        if cursor.fetchone():
            print(f"❌ Usuário '{username}' já existe!")
            conn.close()
            return
        
        password_hash = generate_password_hash(senha)
        
        cursor.execute('''
            INSERT INTO usuarios (
                username, password_hash, nome_completo, email, ativo,
                permissao_vendas, permissao_estoque, permissao_clientes,
                permissao_financeiro, permissao_caixa, permissao_relatorios, 
                permissao_admin
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (username, password_hash, nome_completo, email, True,
              perm_vendas, perm_estoque, perm_clientes, perm_financeiro,
              perm_caixa, perm_relatorios, perm_admin))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Usuário '{username}' criado com sucesso!")
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao criar usuário: {e}")

def listar_usuarios():
    """Lista todos os usuários do sistema"""
    print("\n" + "="*50)
    print("👥 USUÁRIOS DO SISTEMA")
    print("="*50)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nome_completo, email, ativo,
                   permissao_admin
            FROM usuarios
            ORDER BY id
        ''')
        
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("Nenhum usuário encontrado.")
        else:
            for usuario in usuarios:
                id_user, username, nome, email, ativo, is_admin = usuario
                status = "✅ Ativo" if ativo else "❌ Inativo"
                admin_badge = " [ADMIN]" if is_admin else ""
                print(f"\nID: {id_user} | {username}{admin_badge}")
                print(f"Nome: {nome}")
                print(f"Email: {email}")
                print(f"Status: {status}")
                print("-" * 50)
        
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao listar usuários: {e}")

def menu():
    """Menu principal"""
    while True:
        print("\n" + "="*50)
        print("🔧 GERENCIADOR DE USUÁRIOS - FG AUTO PEÇAS")
        print("="*50)
        print("1. Criar/Resetar usuário ADMIN")
        print("2. Criar novo usuário personalizado")
        print("3. Listar todos os usuários")
        print("0. Sair")
        print("="*50)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            criar_usuario_admin()
        elif opcao == '2':
            criar_usuario_personalizado()
        elif opcao == '3':
            listar_usuarios()
        elif opcao == '0':
            print("\n👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 SCRIPT DE GERENCIAMENTO DE USUÁRIOS")
    print("="*50)
    
    if not DATABASE_URL:
        print("❌ ERRO: DATABASE_URL não encontrada no arquivo .env")
        print("Configure o arquivo .env com as credenciais do banco de dados.")
    else:
        menu()
