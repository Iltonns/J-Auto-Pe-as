#!/usr/bin/env python3
"""
Script para deletar TODOS os produtos cadastrados no sistema
⚠️ ATENÇÃO: Esta ação é IRREVERSÍVEL!
Use --force para executar sem confirmação
"""

import sys
from Minha_autopecas_web.logica_banco import get_db_connection

def deletar_todos_produtos(forcar=False):
    """Deleta todos os produtos do banco de dados e registros relacionados"""
    
    if not forcar:
        print("⚠️  ATENÇÃO! AÇÃO IRREVERSÍVEL! ⚠️")
        print("=" * 50)
        print("Este script irá DELETAR TODOS OS PRODUTOS cadastrados!")
        print("Esta ação NÃO PODE SER DESFEITA!")
        print("=" * 50)
        print()
        print("💡 Para executar sem confirmação, use: python deletar_produtos_forcar.py --force")
        return False
    
    print("\n🔄 Conectando ao banco de dados...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primeiro, contar quantos produtos existem
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor.fetchone()[0]
        
        print(f"📊 Total de produtos encontrados: {total_produtos}")
        
        if total_produtos == 0:
            print("ℹ️  Não há produtos para deletar.")
            cursor.close()
            conn.close()
            return True
        
        print(f"\n🗑️  Deletando registros relacionados e produtos...")
        print("=" * 50)
        
        # Deletar registros relacionados em ordem
        # 1. Movimentações de estoque (DEVE SER PRIMEIRO)
        cursor.execute("SELECT COUNT(*) FROM movimentacoes")
        total_movimentacoes = cursor.fetchone()[0]
        if total_movimentacoes > 0:
            print(f"🗑️  Deletando {total_movimentacoes} movimentações de estoque...")
            cursor.execute("DELETE FROM movimentacoes")
            conn.commit()  # Commit intermediário
            print(f"   ✅ {total_movimentacoes} movimentações deletadas")
        
        # 2. Itens de venda
        cursor.execute("SELECT COUNT(*) FROM itens_venda")
        total_itens_venda = cursor.fetchone()[0]
        if total_itens_venda > 0:
            print(f"🗑️  Deletando {total_itens_venda} itens de vendas...")
            cursor.execute("DELETE FROM itens_venda")
            conn.commit()  # Commit intermediário
            print(f"   ✅ {total_itens_venda} itens deletados")
        
        # 3. Itens de orçamento
        cursor.execute("SELECT COUNT(*) FROM itens_orcamento")
        total_itens_orcamento = cursor.fetchone()[0]
        if total_itens_orcamento > 0:
            print(f"🗑️  Deletando {total_itens_orcamento} itens de orçamentos...")
            cursor.execute("DELETE FROM itens_orcamento")
            conn.commit()  # Commit intermediário
            print(f"   ✅ {total_itens_orcamento} itens deletados")
        
        # 4. Produtos NFe (se existir)
        try:
            cursor.execute("SELECT COUNT(*) FROM produtos_nfe")
            total_produtos_nfe = cursor.fetchone()[0]
            if total_produtos_nfe > 0:
                print(f"🗑️  Deletando {total_produtos_nfe} produtos de NFe...")
                cursor.execute("DELETE FROM produtos_nfe")
                conn.commit()  # Commit intermediário
                print(f"   ✅ {total_produtos_nfe} produtos NFe deletados")
        except Exception as e:
            print(f"   ℹ️  Tabela produtos_nfe não existe ou erro: {e}")
            conn.rollback()  # Rollback do erro
        
        # 5. Finalmente, deletar os produtos
        print(f"\n🗑️  Deletando {total_produtos} produtos...")
        cursor.execute("DELETE FROM produtos")
        conn.commit()  # Commit final
        print(f"   ✅ {total_produtos} produtos deletados")
        
        # Commit de todas as alterações
        conn.commit()
        
        print("\n" + "=" * 50)
        print("✅ Todos os produtos e registros relacionados foram deletados com sucesso!")
        print("✅ Operação concluída!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao deletar produtos: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("\n🔧 SISTEMA DE AUTOPEÇAS - DELETAR PRODUTOS")
    print("=" * 50)
    print()
    
    # Verificar se o argumento --force foi passado
    forcar = '--force' in sys.argv
    
    sucesso = deletar_todos_produtos(forcar=forcar)
    
    if sucesso:
        print("\n✨ Processo finalizado com sucesso!")
    else:
        print("\n⚠️  Processo não executado.")
    
    print()
