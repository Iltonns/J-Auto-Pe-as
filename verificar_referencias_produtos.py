#!/usr/bin/env python3
"""Script para verificar todas as referências à tabela produtos"""

from Minha_autopecas_web.logica_banco import get_db_connection

def verificar_referencias_produtos():
    """Verifica todas as tabelas que referenciam produtos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar todas as foreign keys que referenciam produtos
        query = """
            SELECT 
                tc.table_name, 
                kcu.column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu 
                ON tc.constraint_name = kcu.constraint_name 
            JOIN information_schema.constraint_column_usage AS ccu 
                ON ccu.constraint_name = tc.constraint_name 
            WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND ccu.table_name = 'produtos'
        """
        
        cursor.execute(query)
        referencias = cursor.fetchall()
        
        print("\n📊 Tabelas que referenciam 'produtos':")
        print("=" * 60)
        
        for ref in referencias:
            tabela, coluna, constraint = ref
            print(f"  📌 Tabela: {tabela}")
            print(f"     Coluna: {coluna}")
            print(f"     Constraint: {constraint}")
            
            # Contar quantos registros existem
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            total = cursor.fetchone()[0]
            print(f"     Total de registros: {total}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_referencias_produtos()
