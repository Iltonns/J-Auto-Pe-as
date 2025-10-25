#!/usr/bin/env python3

from Minha_autopecas_web.logica_banco import listar_usuarios

usuarios = listar_usuarios()
print("Usuários encontrados:")
for u in usuarios:
    print(f"  {u['id']} - {u['username']} - {u.get('nome_completo', '')}")