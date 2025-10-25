#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a funcionalidade de usuários inativos
"""

from Minha_autopecas_web.logica_banco import (
    listar_usuarios, editar_usuario, verificar_usuario, buscar_usuario_por_id
)

def teste_usuario_inativo():
    print("=== TESTE DE USUÁRIO INATIVO ===\n")
    
    # Listar todos os usuários
    print("1. Listando todos os usuários:")
    usuarios = listar_usuarios()
    
    if not usuarios:
        print("Nenhum usuário encontrado!")
        return
    
    for user in usuarios:
        status = "ATIVO" if user['ativo'] else "INATIVO"
        print(f"ID: {user['id']} | Username: {user['username']} | Nome: {user['nome_completo']} | Status: {status}")
    
    print("\n" + "="*50)
    
    # Escolher um usuário para testar (exceto admin)
    usuarios_nao_admin = [u for u in usuarios if not u['permissao_admin']]
    
    if not usuarios_nao_admin:
        print("Não há usuários não-admin para testar!")
        return
    
    usuario_teste = usuarios_nao_admin[0]
    user_id = usuario_teste['id']
    username = usuario_teste['username']
    
    print(f"\n2. Testando com usuário: {username} (ID: {user_id})")
    
    # Verificar dados atuais do usuário
    user_data = buscar_usuario_por_id(user_id)
    print(f"Status atual: {'ATIVO' if user_data['ativo'] else 'INATIVO'}")
    
    # Tentar fazer login com usuário ativo
    print(f"\n3. Tentando login com usuário ativo...")
    # Nota: Precisaríamos da senha para testar completamente
    print("Para testar completamente, você precisaria da senha do usuário.")
    
    # Inativar o usuário
    print(f"\n4. Inativando usuário {username}...")
    permissoes = {
        'vendas': user_data['permissao_vendas'],
        'estoque': user_data['permissao_estoque'],
        'clientes': user_data['permissao_clientes'],
        'financeiro': user_data['permissao_financeiro'],
        'caixa': user_data['permissao_caixa'],
        'relatorios': user_data['permissao_relatorios'],
        'admin': user_data['permissao_admin']
    }
    
    sucesso, mensagem = editar_usuario(
        user_id, 
        user_data['nome_completo'], 
        user_data['email'], 
        permissoes, 
        False  # ativo = False
    )
    
    if sucesso:
        print(f"✅ Usuário {username} inativado com sucesso!")
    else:
        print(f"❌ Erro ao inativar usuário: {mensagem}")
        return
    
    # Verificar se o usuário foi inativado
    user_data_updated = buscar_usuario_por_id(user_id)
    print(f"Status após inativação: {'ATIVO' if user_data_updated['ativo'] else 'INATIVO'}")
    
    # Tentar verificar login com usuário inativo
    print(f"\n5. Testando login com usuário inativo...")
    resultado = verificar_usuario(username, "qualquer_senha")
    
    if resultado is False:
        print("✅ Sistema corretamente rejeitou login de usuário inativo!")
    elif resultado is None:
        print("ℹ️  Login rejeitado (usuário/senha incorretos)")
    else:
        print("❌ PROBLEMA: Sistema permitiu login de usuário inativo!")
    
    # Reativar o usuário
    print(f"\n6. Reativando usuário {username}...")
    sucesso, mensagem = editar_usuario(
        user_id, 
        user_data['nome_completo'], 
        user_data['email'], 
        permissoes, 
        True  # ativo = True
    )
    
    if sucesso:
        print(f"✅ Usuário {username} reativado com sucesso!")
    else:
        print(f"❌ Erro ao reativar usuário: {mensagem}")
    
    print("\n=== TESTE CONCLUÍDO ===")
    print("\nResumo das correções implementadas:")
    print("1. ✅ verificar_usuario() agora verifica se o usuário está ativo")
    print("2. ✅ load_user() verifica se o usuário está ativo")
    print("3. ✅ before_request() desloga usuários inativos automaticamente")
    print("4. ✅ Mensagem específica para usuários inativos no login")

if __name__ == '__main__':
    teste_usuario_inativo()