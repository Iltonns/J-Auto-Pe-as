#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar usuários no sistema de autopeças.
Este script pode ser usado para inicializar o banco de dados e criar usuários.
"""

import sys
import os

# Adicionar o diretório pai ao path para importar o módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Minha_autopecas_web import logica_banco as db

def inicializar_sistema():
    """
    Inicializa o sistema criando as tabelas necessárias.
    """
    print("🔧 Inicializando sistema de autopeças...")
    
    # Configurar banco de dados
    if db.setup_database():
        print("✅ Banco de dados configurado com sucesso!")
    else:
        print("❌ Erro ao configurar banco de dados!")
        return False
    
    return True

def criar_usuario_admin():
    """
    Cria o usuário administrador padrão.
    """
    print("\n👤 Criando usuário administrador...")
    
    # Verificar se já existe
    admin_user = db.get_user_by_username('admin')
    if admin_user:
        print("⚠️  Usuário 'admin' já existe!")
        return True
    
    # Criar usuário admin
    sucesso, mensagem = db.add_user('admin', 'admin123')
    if sucesso:
        print("✅ Usuário 'admin' criado com sucesso!")
        print("   Usuário: admin")
        print("   Senha: admin123")
    else:
        print(f"❌ Erro ao criar usuário admin: {mensagem}")
        return False
    
    return True

def criar_dados_exemplo():
    """
    Cria alguns dados de exemplo para demonstração.
    """
    print("\n📦 Criando dados de exemplo...")
    
    # Produtos de exemplo
    produtos_exemplo = [
        ("Óleo Motor 15W40", 25.90, 50, "7891234567890"),
        ("Filtro de Ar", 35.50, 25, "7891234567891"),
        ("Pastilha de Freio", 89.90, 15, "7891234567892"),
        ("Amortecedor Dianteiro", 285.00, 8, "7891234567893"),
        ("Bateria 60Ah", 350.00, 5, "7891234567894"),
    ]
    
    for nome, preco, quantidade, codigo in produtos_exemplo:
        sucesso, mensagem = db.adicionar_produto(nome, preco, quantidade, codigo)
        if sucesso:
            print(f"✅ Produto '{nome}' adicionado")
        else:
            print(f"❌ Erro ao adicionar '{nome}': {mensagem}")
    
    # Clientes de exemplo
    clientes_exemplo = [
        ("João Silva", "(11) 99999-1111", "joao@email.com", "123.456.789-01", "Rua A, 123"),
        ("Maria Santos", "(11) 99999-2222", "maria@email.com", "987.654.321-02", "Rua B, 456"),
        ("AutoPeças Central LTDA", "(11) 3333-4444", "contato@central.com", "12.345.678/0001-90", "Av. Principal, 789"),
    ]
    
    for nome, telefone, email, cpf_cnpj, endereco in clientes_exemplo:
        sucesso, mensagem = db.adicionar_cliente(nome, telefone, email, cpf_cnpj, endereco)
        if sucesso:
            print(f"✅ Cliente '{nome}' adicionado")
        else:
            print(f"❌ Erro ao adicionar '{nome}': {mensagem}")

def mostrar_estatisticas():
    """
    Mostra estatísticas do sistema após inicialização.
    """
    print("\n📊 Estatísticas do Sistema:")
    
    try:
        estatisticas = db.get_estatisticas_gerais()
        print(f"   📦 Produtos: {estatisticas.get('total_produtos', 0)}")
        print(f"   👥 Clientes: {estatisticas.get('total_clientes', 0)}")
        print(f"   💰 Valor Estoque: R$ {estatisticas.get('valor_estoque', 0):.2f}")
        print(f"   ⚠️  Estoque Baixo: {estatisticas.get('produtos_estoque_baixo', 0)}")
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")

def main():
    """
    Função principal do script.
    """
    print("=" * 50)
    print("🚗 SISTEMA DE AUTOPEÇAS - INICIALIZAÇÃO")
    print("=" * 50)
    
    # Inicializar sistema
    if not inicializar_sistema():
        return
    
    # Criar usuário admin
    if not criar_usuario_admin():
        return
    
    # Pergunta se quer criar dados de exemplo
    resposta = input("\n❓ Deseja criar dados de exemplo? (s/N): ").lower().strip()
    if resposta in ['s', 'sim', 'y', 'yes']:
        criar_dados_exemplo()
    
    # Mostrar estatísticas
    mostrar_estatisticas()
    
    print("\n" + "=" * 50)
    print("🎉 SISTEMA INICIALIZADO COM SUCESSO!")
    print("=" * 50)
    print("\n📱 Para acessar o sistema:")
    print("   1. Execute: python app.py")
    print("   2. Acesse: http://localhost:5000")
    print("   3. Login: admin / admin123")
    print("\n🔧 Para mais informações, consulte o README.md")

if __name__ == "__main__":
    main()