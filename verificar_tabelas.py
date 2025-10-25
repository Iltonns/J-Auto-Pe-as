import sqlite3
import os

# Conectar ao banco
db_path = 'autopecas.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tabelas existentes no banco de dados:")
for table in tables:
    print(f"- {table[0]}")

# Verificar especificamente se a tabela itens_venda existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='itens_venda'")
itens_venda_exists = cursor.fetchone()

if itens_venda_exists:
    print("\n✓ Tabela 'itens_venda' existe!")
    
    # Mostrar estrutura da tabela
    cursor.execute("PRAGMA table_info(itens_venda)")
    columns = cursor.fetchall()
    print("\nEstrutura da tabela itens_venda:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\n✗ Tabela 'itens_venda' NÃO existe!")

conn.close()