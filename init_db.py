# Script de inicialização do banco de dados
# Execute este script uma vez após o primeiro deploy

from Minha_autopecas_web.logica_banco import init_db, criar_usuario_admin

print("🔧 Inicializando banco de dados...")

try:
    # Criar todas as tabelas
    init_db()
    print("✅ Tabelas criadas com sucesso!")
    
    # Criar usuário admin
    criar_usuario_admin()
    print("✅ Usuário admin criado!")
    print()
    print("📝 Credenciais de acesso:")
    print("   Usuário: admin")
    print("   Senha: admin123")
    print()
    print("⚠️  IMPORTANTE: Mude a senha após o primeiro login!")
    
except Exception as e:
    print(f"❌ Erro ao inicializar banco: {e}")
    print()
    print("💡 Possíveis soluções:")
    print("   1. Verifique se DATABASE_URL está configurada")
    print("   2. Confirme que o banco Neon está ativo")
    print("   3. Teste a conexão com: python testar_conexao.py")
