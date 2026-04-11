#!/usr/bin/env python
"""Script para garantir que as colunas necessárias existem no banco de dados"""
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar a função de conexão
from Minha_autopecas_web.logica_banco import get_db_connection

def add_column_safe(cursor, conn, table_name, column_name, column_definition):
    """Adiciona uma coluna de forma segura se não existir"""
    try:
        # Verificar se a coluna já existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name=%s AND column_name=%s
        """, (table_name, column_name))
        
        if cursor.fetchone() is None:
            # Coluna não existe, adicionar
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
            conn.commit()
            print(f"✓ Coluna criada: {table_name}.{column_name}")
        else:
            print(f"✓ Coluna já existe: {table_name}.{column_name}")
    except Exception as e:
        print(f"✗ Erro ao adicionar coluna {column_name}: {e}")
        conn.rollback()

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Verificando colunas da tabela 'clientes'...")
    
    columns_to_add = [
        ("tipo_pessoa", "tipo_pessoa VARCHAR(1) DEFAULT 'F'"),
        ("razao_social", "razao_social TEXT"),
        ("inscricao_estadual", "inscricao_estadual TEXT"),
        ("rua", "rua TEXT"),
        ("numero", "numero TEXT"),
        ("complemento", "complemento TEXT"),
        ("bairro", "bairro TEXT"),
        ("cidade", "cidade TEXT"),
        ("estado", "estado VARCHAR(2)"),
        ("cep", "cep TEXT"),
    ]
    
    for col_name, col_def in columns_to_add:
        add_column_safe(cursor, conn, 'clientes', col_name, col_def)
    
    conn.close()
    print("\n✓ Todas as colunas verificadas com sucesso!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Erro fatal: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
