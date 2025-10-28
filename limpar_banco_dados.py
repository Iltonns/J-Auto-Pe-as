"""
Script para limpar todos os dados do banco de dados
Deleta: Movimentações, Vendas, Clientes, Fornecedores e Produtos
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Conecta ao banco de dados PostgreSQL usando a mesma configuração do projeto"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não encontrada! Configure o arquivo .env")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

def limpar_banco_dados():
    """Limpa todas as tabelas principais do banco de dados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("LIMPEZA COMPLETA DO BANCO DE DADOS")
    print("=" * 60)
    
    try:
        # 1. DELETAR MOVIMENTAÇÕES DE CAIXA (tem FK para vendas)
        print("\n[1/7] Deletando MOVIMENTAÇÕES DE CAIXA...")
        cursor.execute("SELECT COUNT(*) FROM caixa_movimentacoes")
        total_caixa_mov = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM caixa_movimentacoes")
        conn.commit()
        print(f"✅ {total_caixa_mov} movimentações de caixa deletadas")
        
        # 2. DELETAR MOVIMENTAÇÕES
        print("\n[2/7] Deletando MOVIMENTAÇÕES...")
        cursor.execute("SELECT COUNT(*) FROM movimentacoes")
        total_movimentacoes = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM movimentacoes")
        conn.commit()
        print(f"✅ {total_movimentacoes} movimentações deletadas")
        
        # 3. DELETAR VENDAS (itens primeiro, depois vendas)
        print("\n[3/7] Deletando VENDAS...")
        cursor.execute("SELECT COUNT(*) FROM itens_venda")
        total_itens_venda = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendas")
        total_vendas = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM itens_venda")
        cursor.execute("DELETE FROM vendas")
        conn.commit()
        print(f"✅ {total_itens_venda} itens de venda deletados")
        print(f"✅ {total_vendas} vendas deletadas")
        
        # 4. DELETAR ORÇAMENTOS (itens primeiro, depois orçamentos)
        print("\n[4/7] Deletando ORÇAMENTOS...")
        cursor.execute("SELECT COUNT(*) FROM itens_orcamento")
        total_itens_orcamento = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orcamentos")
        total_orcamentos = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM itens_orcamento")
        cursor.execute("DELETE FROM orcamentos")
        conn.commit()
        print(f"✅ {total_itens_orcamento} itens de orçamento deletados")
        print(f"✅ {total_orcamentos} orçamentos deletados")
        
        # 5. DELETAR PRODUTOS
        print("\n[5/7] Deletando PRODUTOS...")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM produtos")
        conn.commit()
        print(f"✅ {total_produtos} produtos deletados")
        
        # 6. DELETAR CONTAS FINANCEIRAS (antes de clientes/fornecedores)
        print("\n[6/7] Deletando CONTAS FINANCEIRAS...")
        
        cursor.execute("SELECT COUNT(*) FROM contas_receber")
        total_contas_receber = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contas_pagar")
        total_contas_pagar = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM contas_receber")
        cursor.execute("DELETE FROM contas_pagar")
        conn.commit()
        print(f"✅ {total_contas_receber} contas a receber deletadas")
        print(f"✅ {total_contas_pagar} contas a pagar deletadas")
        
        # 7. DELETAR CLIENTES
        print("\n[7/7] Deletando CLIENTES...")
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM clientes")
        conn.commit()
        print(f"✅ {total_clientes} clientes deletados")
        
        # 8. DELETAR FORNECEDORES
        print("\n[8/8] Deletando FORNECEDORES...")
        cursor.execute("SELECT COUNT(*) FROM fornecedores")
        total_fornecedores = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM fornecedores")
        conn.commit()
        print(f"✅ {total_fornecedores} fornecedores deletados")
        
        # RESETAR SEQUENCES (AUTO_INCREMENT)
        print("\n" + "=" * 60)
        print("RESETANDO SEQUENCES (IDs)...")
        print("=" * 60)
        
        sequences = [
            ('movimentacoes_id_seq', 'movimentacoes'),
            ('vendas_id_seq', 'vendas'),
            ('itens_venda_id_seq', 'itens_venda'),
            ('orcamentos_id_seq', 'orcamentos'),
            ('itens_orcamento_id_seq', 'itens_orcamento'),
            ('produtos_id_seq', 'produtos'),
            ('clientes_id_seq', 'clientes'),
            ('fornecedores_id_seq', 'fornecedores')
        ]
        
        for seq_name, table_name in sequences:
            try:
                cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH 1")
                print(f"✅ Sequence {seq_name} resetada")
            except Exception as e:
                print(f"⚠️ Sequence {seq_name} não encontrada ou erro: {e}")
        
        conn.commit()
        
        # VERIFICAR LIMPEZA
        print("\n" + "=" * 60)
        print("VERIFICAÇÃO FINAL")
        print("=" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM movimentacoes")
        print(f"Movimentações restantes: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM vendas")
        print(f"Vendas restantes: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM orcamentos")
        print(f"Orçamentos restantes: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM produtos")
        print(f"Produtos restantes: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM clientes")
        print(f"Clientes restantes: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM fornecedores")
        print(f"Fornecedores restantes: {cursor.fetchone()[0]}")
        
        print("\n" + "=" * 60)
        print("✅ BANCO DE DADOS LIMPO COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERRO ao limpar banco de dados: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    resposta = input("\n⚠️  ATENÇÃO: Isso vai DELETAR TODOS os dados do banco!\nDeseja continuar? (digite 'SIM' para confirmar): ")
    
    if resposta.strip().upper() == 'SIM':
        limpar_banco_dados()
    else:
        print("\n❌ Operação cancelada pelo usuário.")
