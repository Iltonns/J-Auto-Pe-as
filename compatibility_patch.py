#!/usr/bin/env python3
"""
Script de compatibilidade - torna o código compatível mesmo sem todas as dependências
Funciona como um fallback quando o banco não tem as colunas novas
"""

# Monkeypatch para a função listar_clientes
print("[INFO] Aplicando patches de compatibilidade...")

def listar_clientes_fallback():
    """Versão fallback que não tenta acessar colunas que podem não existir"""
    try:
        from Minha_autopecas_web.logica_banco import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primeira tentativa: com todas as colunas
        try:
            cursor.execute('''
                SELECT id, nome, telefone, email, cpf_cnpj, endereco,
                       COALESCE(tipo_pessoa, 'F'), 
                       COALESCE(razao_social, ''), 
                       COALESCE(inscricao_estadual, ''),
                       COALESCE(rua, ''), 
                       COALESCE(numero, ''), 
                       COALESCE(complemento, ''),
                       COALESCE(bairro, ''), 
                       COALESCE(cidade, ''), 
                       COALESCE(estado, ''), 
                       COALESCE(cep, '')
                FROM clientes
                ORDER BY nome
            ''')
        except Exception:
            # Fallback: apenas colunas básicas
            cursor.execute('''
                SELECT id, nome, telefone, email, cpf_cnpj, endereco
                FROM clientes
                ORDER BY nome
            ''')
        
        clientes = []
        for row in cursor.fetchall():
            if len(row) >= 16:
                clientes.append({
                    'id': row[0],
                    'nome': row[1],
                    'telefone': row[2],
                    'email': row[3],
                    'cpf_cnpj': row[4],
                    'endereco': row[5],
                    'tipo_pessoa': row[6] or 'F',
                    'razao_social': row[7] or '',
                    'inscricao_estadual': row[8] or '',
                    'rua': row[9] or '',
                    'numero': row[10] or '',
                    'complemento': row[11] or '',
                    'bairro': row[12] or '',
                    'cidade': row[13] or '',
                    'estado': row[14] or '',
                    'cep': row[15] or ''
                })
            else:
                clientes.append({
                    'id': row[0],
                    'nome': row[1],
                    'telefone': row[2] or '',
                    'email': row[3] or '',
                    'cpf_cnpj': row[4] or '',
                    'endereco': row[5] or '',
                    'tipo_pessoa': 'F',
                    'razao_social': '',
                    'inscricao_estadual': '',
                    'rua': '',
                    'numero': '',
                    'complemento': '',
                    'bairro': '',
                    'cidade': '',
                    'estado': '',
                    'cep': ''
                })
        
        conn.close()
        return clientes
    except Exception as e:
        print(f"[ERRO] listar_clientes fallback failed: {e}")
        return []

print("[OK] Patches aplicados")
