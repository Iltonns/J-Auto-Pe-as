#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para popular o banco de dados com dados de exemplo e configurar permissões.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), 'autopecas.db')

def criar_funcionarios_exemplo():
    """Cria funcionários de exemplo para testar o filtro por funcionário"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se já existem funcionários além do admin
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username != 'admin'")
    if cursor.fetchone()[0] > 0:
        print("Funcionários já existem no banco!")
        conn.close()
        return
    
    funcionarios = [
        ('joao.silva', 'João Silva', 'joao@autopecas.com'),
        ('maria.souza', 'Maria Souza', 'maria@autopecas.com'),
        ('carlos.pereira', 'Carlos Pereira', 'carlos@autopecas.com'),
        ('ana.costa', 'Ana Costa', 'ana@autopecas.com'),
    ]
    
    from Minha_autopecas_web.logica_banco import criar_usuario
    
    for username, nome_completo, email in funcionarios:
        # Criar o usuário
        sucesso, user_id = criar_usuario(
            username=username,
            password='123456',  # Senha padrão para teste
            nome_completo=nome_completo,
            email=email,
            permissoes={
                'vendas': True,
                'estoque': True,
                'clientes': True,
                'financeiro': False,
                'caixa': False,
                'relatorios': False,
                'admin': False
            },
            created_by=1  # Admin
        )
        
        if sucesso:
            print(f"Funcionário criado: {nome_completo} ({username})")
        else:
            print(f"Erro ao criar funcionário: {nome_completo}")
    
    conn.close()
    print("Funcionários de exemplo criados!")

def atualizar_permissoes_admin():
    """Atualiza as permissões do usuário admin para incluir relatórios"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Atualizar permissões do admin
    cursor.execute('''
        UPDATE usuarios 
        SET permissao_relatorios = 1, 
            permissao_admin = 1,
            permissao_financeiro = 1,
            permissao_caixa = 1
        WHERE username = 'admin'
    ''')
    
    conn.commit()
    conn.close()
    print("Permissões do admin atualizadas!")

def criar_vendas_exemplo():
    """Cria vendas de exemplo para os relatórios"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se já existem vendas
    cursor.execute("SELECT COUNT(*) FROM vendas")
    if cursor.fetchone()[0] > 0:
        print("Vendas já existem no banco!")
        conn.close()
        return
    
    # Buscar todos os usuários
    cursor.execute("SELECT id FROM usuarios ORDER BY id")
    usuarios = [row[0] for row in cursor.fetchall()]
    
    if not usuarios:
        print("Nenhum usuário encontrado!")
        conn.close()
        return
    
    # Buscar produtos e clientes
    cursor.execute("SELECT id FROM produtos LIMIT 10")
    produtos = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM clientes LIMIT 3")
    clientes = [row[0] for row in cursor.fetchall()]
    
    if not produtos or not clientes:
        print("Produtos ou clientes não encontrados!")
        conn.close()
        return
    
    print(f"Criando vendas de exemplo com {len(produtos)} produtos e {len(clientes)} clientes...")
    
    # Criar vendas dos últimos 30 dias
    for i in range(25):
        data_venda = datetime.now() - timedelta(days=random.randint(0, 30))
        cliente_id = random.choice(clientes)
        forma_pagamento = random.choice(['dinheiro', 'cartao_credito', 'cartao_debito', 'pix', 'prazo'])
        usuario_id = random.choice(usuarios)  # Escolher funcionário aleatório
        
        # Criar venda
        cursor.execute('''
            INSERT INTO vendas (cliente_id, total, forma_pagamento, data_venda, usuario_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (cliente_id, 0, forma_pagamento, data_venda, usuario_id))
        
        venda_id = cursor.lastrowid
        total_venda = 0
        
        # Adicionar 1-4 itens por venda
        num_itens = random.randint(1, 4)
        produtos_venda = random.sample(produtos, min(num_itens, len(produtos)))
        
        for produto_id in produtos_venda:
            quantidade = random.randint(1, 3)
            
            # Buscar preço do produto
            cursor.execute("SELECT preco FROM produtos WHERE id = ?", (produto_id,))
            preco_result = cursor.fetchone()
            if preco_result:
                preco = preco_result[0]
                subtotal = preco * quantidade
                
                cursor.execute('''
                    INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (venda_id, produto_id, quantidade, preco, subtotal))
                
                total_venda += subtotal
        
        # Atualizar total da venda
        cursor.execute("UPDATE vendas SET total = ? WHERE id = ?", (total_venda, venda_id))
    
    conn.commit()
    conn.close()
    print(f"Criadas {25} vendas de exemplo!")

def criar_contas_exemplo():
    """Cria contas a pagar/receber de exemplo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se já existem contas
    cursor.execute("SELECT COUNT(*) FROM contas_receber")
    if cursor.fetchone()[0] > 0:
        print("Contas já existem no banco!")
        conn.close()
        return
    
    # Buscar clientes
    cursor.execute("SELECT id FROM clientes")
    clientes = [row[0] for row in cursor.fetchall()]
    
    if not clientes:
        print("Clientes não encontrados!")
        conn.close()
        return
    
    # Criar contas a receber
    for i in range(10):
        cliente_id = random.choice(clientes)
        valor = random.uniform(50, 500)
        data_vencimento = datetime.now() + timedelta(days=random.randint(-15, 45))
        status = random.choice(['pendente', 'pago']) if data_vencimento < datetime.now() else 'pendente'
        
        cursor.execute('''
            INSERT INTO contas_receber (cliente_id, valor, descricao, data_vencimento, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (cliente_id, valor, f"Conta a receber {i+1}", data_vencimento, status))
    
    # Criar contas a pagar
    for i in range(8):
        valor = random.uniform(100, 1000)
        data_vencimento = datetime.now() + timedelta(days=random.randint(-10, 30))
        status = random.choice(['pendente', 'pago']) if data_vencimento < datetime.now() else 'pendente'
        
        cursor.execute('''
            INSERT INTO contas_pagar (valor, descricao, data_vencimento, status)
            VALUES (?, ?, ?, ?)
        ''', (valor, f"Conta a pagar {i+1}", data_vencimento, status))
    
    conn.commit()
    conn.close()
    print("Contas de exemplo criadas!")

if __name__ == "__main__":
    print("Configurando dados de exemplo para relatórios...")
    
    atualizar_permissoes_admin()
    criar_funcionarios_exemplo()
    criar_vendas_exemplo()
    criar_contas_exemplo()
    
    print("Configuração concluída! Agora você pode testar os relatórios e filtro por funcionários.")