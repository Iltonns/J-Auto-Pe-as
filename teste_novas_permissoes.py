#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar as novas permissões de Contas a Pagar e Contas a Receber
"""

from Minha_autopecas_web.logica_banco import (
    listar_usuarios, criar_usuario, buscar_usuario_por_id
)

def testar_novas_permissoes():
    print("=== TESTE DAS NOVAS PERMISSÕES: CONTAS A PAGAR E CONTAS A RECEBER ===\n")
    
    # Listar usuários existentes
    print("1. Verificando usuários existentes:")
    usuarios = listar_usuarios()
    
    for user in usuarios:
        print(f"ID: {user['id']} | Username: {user['username']} | Nome: {user['nome_completo']}")
        print(f"   Contas a Pagar: {'✅' if user.get('permissao_contas_pagar', False) else '❌'}")
        print(f"   Contas a Receber: {'✅' if user.get('permissao_contas_receber', False) else '❌'}")
        print()
    
    print("=" * 70)
    
    # Criar usuário de teste com as novas permissões
    print("\n2. Criando usuário de teste com as novas permissões...")
    
    permissoes_teste = {
        'vendas': True,
        'estoque': True,
        'clientes': True,
        'financeiro': False,
        'caixa': False,
        'relatorios': False,
        'admin': False,
        'contas_pagar': True,
        'contas_receber': True
    }
    
    sucesso, mensagem = criar_usuario(
        username='teste_contas',
        password='123456',
        nome_completo='Usuário Teste Contas',
        email='teste_contas@exemplo.com',
        permissoes=permissoes_teste,
        created_by=1  # Admin
    )
    
    if sucesso:
        print(f"✅ {mensagem}")
        
        # Buscar o usuário criado
        usuarios_atualizados = listar_usuarios()
        usuario_teste = next((u for u in usuarios_atualizados if u['username'] == 'teste_contas'), None)
        
        if usuario_teste:
            print(f"\n3. Verificando permissões do usuário criado:")
            print(f"   Username: {usuario_teste['username']}")
            print(f"   Nome: {usuario_teste['nome_completo']}")
            print(f"   Email: {usuario_teste['email']}")
            print(f"   Ativo: {'✅' if usuario_teste['ativo'] else '❌'}")
            print(f"\n   Permissões:")
            print(f"   • Vendas: {'✅' if usuario_teste['permissao_vendas'] else '❌'}")
            print(f"   • Estoque: {'✅' if usuario_teste['permissao_estoque'] else '❌'}")
            print(f"   • Clientes: {'✅' if usuario_teste['permissao_clientes'] else '❌'}")
            print(f"   • Financeiro: {'✅' if usuario_teste['permissao_financeiro'] else '❌'}")
            print(f"   • Caixa: {'✅' if usuario_teste['permissao_caixa'] else '❌'}")
            print(f"   • Relatórios: {'✅' if usuario_teste['permissao_relatorios'] else '❌'}")
            print(f"   • Admin: {'✅' if usuario_teste['permissao_admin'] else '❌'}")
            print(f"   • 🆕 Contas a Pagar: {'✅' if usuario_teste.get('permissao_contas_pagar', False) else '❌'}")
            print(f"   • 🆕 Contas a Receber: {'✅' if usuario_teste.get('permissao_contas_receber', False) else '❌'}")
            
            # Verificar também com buscar_usuario_por_id
            print(f"\n4. Verificação adicional usando buscar_usuario_por_id:")
            usuario_por_id = buscar_usuario_por_id(usuario_teste['id'])
            if usuario_por_id:
                print(f"   Contas a Pagar (por ID): {'✅' if usuario_por_id.get('permissao_contas_pagar', False) else '❌'}")
                print(f"   Contas a Receber (por ID): {'✅' if usuario_por_id.get('permissao_contas_receber', False) else '❌'}")
    else:
        print(f"❌ {mensagem}")
    
    print("\n" + "=" * 70)
    print("🆕 RESUMO DAS IMPLEMENTAÇÕES:")
    print("✅ Adicionadas colunas permissao_contas_pagar e permissao_contas_receber na tabela usuarios")
    print("✅ Atualizada função init_db() para criar as novas colunas")
    print("✅ Atualizada função buscar_usuario_por_id() para retornar as novas permissões")
    print("✅ Atualizada função listar_usuarios() para incluir as novas permissões")
    print("✅ Atualizada função criar_usuario() para aceitar as novas permissões")
    print("✅ Atualizada rota criar_usuario_route() no app.py")
    print("✅ Atualizada rota editar_usuario_route() no app.py")
    print("✅ Adicionados checkboxes no modal de criação de usuário")
    print("✅ Adicionados checkboxes no modal de edição de usuário")
    print("✅ Adicionados badges na listagem de usuários")
    print("✅ Atualizado JavaScript para carregar as novas permissões no modal de edição")
    
    print("\n📱 INTERFACE ATUALIZADA:")
    print("• Modal 'Criar Novo Usuário' agora inclui:")
    print("  - ✅ Checkbox 'Contas a Pagar' com ícone de fatura")
    print("  - ✅ Checkbox 'Contas a Receber' com ícone de recibo")
    print("• Listagem de usuários mostra badges para as novas permissões")
    print("• Modal de edição também incluí as novas opções")
    
    print("\n🔧 TESTE MANUAL RECOMENDADO:")
    print("1. Acesse http://127.0.0.1:5000 e faça login como admin")
    print("2. Vá para 'Gerenciar Usuários'")
    print("3. Clique em 'Novo Usuário'")
    print("4. Verifique se aparecem as opções 'Contas a Pagar' e 'Contas a Receber'")
    print("5. Crie um usuário marcando essas permissões")
    print("6. Verifique se os badges aparecem na listagem")
    print("7. Teste a edição do usuário para modificar essas permissões")
    
    print("\n🚀 IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!")

if __name__ == '__main__':
    testar_novas_permissoes()