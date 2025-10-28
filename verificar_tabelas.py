"""
Script para verificar as tabelas existentes no banco de dados
"""

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Conecta ao banco de dados PostgreSQL"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não encontrada!")
    
    return psycopg2.connect(DATABASE_URL)

def listar_tabelas():
    """Lista todas as tabelas do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    tabelas = cursor.fetchall()
    
    print("=" * 60)
    print("TABELAS EXISTENTES NO BANCO DE DADOS")
    print("=" * 60)
    
    for tabela in tabelas:
        nome_tabela = tabela[0]
        
        # Contar registros
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            total = cursor.fetchone()[0]
            print(f"📊 {nome_tabela}: {total} registros")
        except Exception as e:
            print(f"❌ {nome_tabela}: Erro ao contar - {e}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    listar_tabelas()
