# TESTE DE CONEXÃO COM NEON POSTGRESQL
# Execute este script para verificar se a configuração está correta

import os
from dotenv import load_dotenv

print("=" * 70)
print("TESTE DE CONEXÃO - NEON POSTGRESQL")
print("=" * 70)
print()

# Carregar .env
load_dotenv()

# Verificar se DATABASE_URL existe
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("❌ ERRO: DATABASE_URL não encontrada no arquivo .env")
    print()
    print("📝 Passos para resolver:")
    print("   1. Verifique se o arquivo .env existe na raiz do projeto")
    print("   2. Abra o arquivo .env e adicione:")
    print("      DATABASE_URL=postgresql://seu-usuario:senha@host/database?sslmode=require")
    print()
    print("💡 Consulte o arquivo CONFIGURAR_NEON.txt para ajuda!")
    exit(1)

print("✅ DATABASE_URL encontrada no .env")
print()

# Mascarar a senha na exibição
masked_url = database_url
if '@' in masked_url:
    parts = masked_url.split('@')
    if ':' in parts[0]:
        user_pass = parts[0].split('://')
        if len(user_pass) > 1:
            credentials = user_pass[1].split(':')
            if len(credentials) > 1:
                masked_url = f"{user_pass[0]}://{credentials[0]}:****@{parts[1]}"

print(f"📡 Tentando conectar ao Neon...")
print(f"   URL: {masked_url[:50]}...")
print()

# Tentar importar psycopg2
try:
    import psycopg2
    print("✅ psycopg2 instalado corretamente")
except ImportError:
    print("❌ ERRO: psycopg2 não está instalado")
    print()
    print("📝 Execute:")
    print("   pip install psycopg2-binary")
    print()
    exit(1)

# Tentar conectar
try:
    print("⏳ Conectando ao banco de dados...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Testar uma query simples
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    
    print()
    print("=" * 70)
    print("🎉 CONEXÃO BEM-SUCEDIDA!")
    print("=" * 70)
    print()
    print(f"📊 Versão do PostgreSQL:")
    print(f"   {version[:80]}...")
    print()
    
    # Listar tabelas existentes
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"📋 Tabelas encontradas no banco ({len(tables)}):")
        for table in tables:
            print(f"   • {table[0]}")
    else:
        print("📋 Nenhuma tabela encontrada ainda")
        print("   Execute 'python app.py' para criar as tabelas!")
    
    print()
    print("✅ Tudo pronto! Você pode iniciar o sistema com:")
    print("   python app.py")
    print()
    
    conn.close()
    
except psycopg2.OperationalError as e:
    print()
    print("=" * 70)
    print("❌ ERRO DE CONEXÃO")
    print("=" * 70)
    print()
    print(f"Detalhes: {str(e)}")
    print()
    print("📝 Possíveis causas:")
    print("   1. Credenciais incorretas no .env")
    print("   2. Projeto Neon não está ativo")
    print("   3. Sem conexão com a internet")
    print("   4. String de conexão mal formatada")
    print()
    print("💡 Verifique:")
    print("   • Se a DATABASE_URL está correta")
    print("   • Se seu projeto Neon está ativo em https://neon.tech")
    print("   • Se você está conectado à internet")
    print()
    
except Exception as e:
    print()
    print(f"❌ ERRO: {str(e)}")
    print()

print("=" * 70)
