# SCRIPT DE MIGRAÇÃO DE DADOS - SQLite para PostgreSQL Neon
# Execute este script APENAS UMA VEZ para migrar os dados existentes

import sqlite3
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
SQLITE_DB = 'autopecas.db'
POSTGRESQL_URL = os.getenv('DATABASE_URL')

def migrar_dados():
    """Migra todos os dados do SQLite para o PostgreSQL"""
    
    print("🔄 Iniciando migração de dados SQLite → PostgreSQL Neon...")
    
    # Verificar se o banco SQLite existe
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Banco SQLite '{SQLITE_DB}' não encontrado!")
        print("   Se você não tem dados antigos, apenas execute o sistema normalmente.")
        return
    
    # Conectar aos bancos
    print("📡 Conectando aos bancos de dados...")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    
    pg_conn = psycopg2.connect(POSTGRESQL_URL)
    pg_cursor = pg_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # Lista de tabelas para migrar (na ordem correta por causa das FKs)
        tabelas = [
            'usuarios',
            'clientes',
            'fornecedores',
            'produtos',
            'vendas',
            'itens_venda',
            'orcamentos',
            'itens_orcamento',
            'contas_pagar',
            'contas_receber',
            'configuracoes_empresa',
            'caixa',
            'movimentacoes_caixa',
            'lancamentos_financeiros'
        ]
        
        for tabela in tabelas:
            print(f"\n📦 Migrando tabela: {tabela}")
            
            try:
                # Buscar dados do SQLite
                sqlite_cursor.execute(f"SELECT * FROM {tabela}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    print(f"   ⚠️  Tabela {tabela} está vazia, pulando...")
                    continue
                
                # Pegar nomes das colunas
                colunas = [description[0] for description in sqlite_cursor.description]
                colunas_str = ', '.join(colunas)
                placeholders = ', '.join(['%s'] * len(colunas))
                
                # Inserir no PostgreSQL
                insert_sql = f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders})"
                
                count = 0
                for row in rows:
                    try:
                        pg_cursor.execute(insert_sql, tuple(row))
                        count += 1
                    except psycopg2.Error as e:
                        print(f"   ⚠️  Erro ao inserir registro: {e}")
                        continue
                
                # Atualizar sequence do PostgreSQL (importante para SERIAL)
                pg_cursor.execute(f"""
                    SELECT setval(pg_get_serial_sequence('{tabela}', 'id'), 
                                   COALESCE((SELECT MAX(id) FROM {tabela}), 1), 
                                   true)
                """)
                
                print(f"   ✅ {count} registros migrados com sucesso!")
                
            except sqlite3.OperationalError:
                print(f"   ⚠️  Tabela {tabela} não existe no SQLite, pulando...")
                continue
            except psycopg2.Error as e:
                print(f"   ❌ Erro ao migrar tabela {tabela}: {e}")
                continue
        
        # Commit final
        pg_conn.commit()
        print("\n✅ Migração concluída com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Verifique se os dados foram migrados corretamente")
        print("   2. Faça backup do autopecas.db (caso queira manter)")
        print("   3. O sistema agora usará apenas o PostgreSQL Neon")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        pg_conn.rollback()
    
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == '__main__':
    print("=" * 70)
    print("MIGRAÇÃO DE DADOS - SQLite → PostgreSQL Neon")
    print("=" * 70)
    print()
    
    resposta = input("⚠️  Tem certeza que deseja migrar os dados? (sim/não): ")
    
    if resposta.lower() in ['sim', 's', 'yes', 'y']:
        migrar_dados()
    else:
        print("❌ Migração cancelada.")
