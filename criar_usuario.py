#!/usr/bin/env python
"""Script alternativo para criar usuário - com suporte melhorado"""
import sys
import os
import getpass

# Tentar carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERRO: DATABASE_URL não configurada no arquivo .env!")
    sys.exit(1)

try:
    import psycopg2
    from werkzeug.security import generate_password_hash
    
    print("=" * 60)
    print("CRIAR NOVO USUÁRIO - J-AUTO PEÇAS")
    print("=" * 60)
    
    # Solicitar dados do usuário
    print("\n")
    username = input("👤 Nome de usuário: ").strip()
    if not username:
        print("❌ Nome de usuário não pode estar vazio!")
        sys.exit(1)
    
    password = getpass.getpass("🔐 Senha: ")
    if not password:
        print("❌ Senha não pode estar vazia!")
        sys.exit(1)
    
    nome_completo = input("👨 Nome completo: ").strip()
    if not nome_completo:
        print("❌ Nome completo não pode estar vazio!")
        sys.exit(1)
    
    email = input("📧 Email: ").strip()
    if not email:
        print("❌ Email não pode estar vazio!")
        sys.exit(1)
    
    print("\n--- PERMISSÕES (responda com S ou N) ---")
    permissoes = {
        'permissao_vendas': input("✅ Permitir VENDAS? (S/n): ").lower() != 'n',
        'permissao_estoque': input("✅ Permitir ESTOQUE? (S/n): ").lower() != 'n',
        'permissao_clientes': input("✅ Permitir CLIENTES? (S/n): ").lower() != 'n',
        'permissao_financeiro': input("💰 Permitir FINANCEIRO? (S/n): ").lower() != 'n',
        'permissao_caixa': input("💳 Permitir CAIXA? (S/n): ").lower() != 'n',
        'permissao_relatorios': input("📊 Permitir RELATÓRIOS? (S/n): ").lower() != 'n',
        'permissao_admin': input("⚙️  Permitir ADMIN (criar usuários)? (S/n): ").lower() != 'n',
    }
    
    print("\n⏳ Criando usuário...")
    
    # Conectar ao banco
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Hash da senha
    password_hash = generate_password_hash(password)
    
    # Inserir usuário
    try:
        cursor.execute('''
            INSERT INTO usuarios (
                username, password_hash, nome_completo, email, 
                permissao_vendas, permissao_estoque, permissao_clientes,
                permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin,
                ativo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        ''', (
            username, password_hash, nome_completo, email,
            permissoes['permissao_vendas'],
            permissoes['permissao_estoque'],
            permissoes['permissao_clientes'],
            permissoes['permissao_financeiro'],
            permissoes['permissao_caixa'],
            permissoes['permissao_relatorios'],
            permissoes['permissao_admin']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ USUÁRIO CRIADO COM SUCESSO!")
        print("="*60)
        print(f"\n👤 Usuário: {username}")
        print(f"📧 Email: {email}")
        print(f"👨 Nome: {nome_completo}")
        print(f"\n🔐 Permissões:")
        for perm, valor in permissoes.items():
            status = "✅" if valor else "❌"
            perm_nome = perm.replace('permissao_', '').upper()
            print(f"   {status} {perm_nome}")
        print(f"\n🎉 Você pode agora fazer login com essas credenciais!")
        print("="*60)
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"\n❌ ERRO: Usuário '{username}' já existe no banco de dados!")
        sys.exit(1)
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"\n❌ ERRO ao criar usuário: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
