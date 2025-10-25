#!/usr/bin/env python3

import sqlite3
import random

DB_PATH = 'autopecas.db'

# Conectar ao banco
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Buscar todas as vendas
cursor.execute("SELECT id FROM vendas")
vendas = [row[0] for row in cursor.fetchall()]

# Buscar todos os usuários
cursor.execute("SELECT id FROM usuarios")
usuarios = [row[0] for row in cursor.fetchall()]

print(f"Encontradas {len(vendas)} vendas e {len(usuarios)} usuários")

# Atualizar as vendas com usuários aleatórios
for venda_id in vendas:
    usuario_id = random.choice(usuarios)
    cursor.execute("UPDATE vendas SET usuario_id = ? WHERE id = ?", (usuario_id, venda_id))

conn.commit()
print("Vendas atualizadas com funcionários aleatórios!")

# Verificar o resultado
cursor.execute("""
    SELECT v.id, u.username, u.nome_completo, v.total 
    FROM vendas v 
    LEFT JOIN usuarios u ON v.usuario_id = u.id 
    LIMIT 10
""")

print("\nExemplo de vendas atualizadas:")
for row in cursor.fetchall():
    nome = row[2] or row[1] or 'Sem nome'
    print(f"  Venda #{row[0]} - Funcionário: {nome} - Total: R$ {row[3]}")

conn.close()