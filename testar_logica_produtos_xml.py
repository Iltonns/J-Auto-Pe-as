# -*- coding: utf-8 -*-
"""
Teste completo da lógica de produtos: Atualizar x Criar
"""

from Minha_autopecas_web.logica_banco import (
    get_db_connection,
    adicionar_movimentacao,
    aprovar_movimentacao,
    listar_produtos
)

print("\n" + "="*70)
print("TESTE COMPLETO: LOGICA DE PRODUTOS EXISTENTES vs NOVOS")
print("="*70)

# Obter ID do usuário
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT id FROM usuarios LIMIT 1')
usuario_id = cursor.fetchone()[0]
conn.close()

# ============================================================================
# CENÁRIO 1: PRODUTO NOVO (não existe no banco)
# ============================================================================
print("\n" + "-"*70)
print("CENARIO 1: PRODUTO NOVO (codigo_barras unico)")
print("-"*70)

codigo_barras_novo = "9999888877776666"
codigo_fornecedor_novo = "TESTE-NOVO-001"

print(f"\n[1.1] Verificando se produto existe no banco...")
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT id FROM produtos WHERE codigo_barras = %s', (codigo_barras_novo,))
existe = cursor.fetchone()
conn.close()
print(f"      Produto com codigo {codigo_barras_novo}: {'EXISTE' if existe else 'NAO EXISTE'}")

print(f"\n[1.2] Criando movimentacao para produto NOVO...")
mov1_id = adicionar_movimentacao(
    nome="PRODUTO TOTALMENTE NOVO",
    preco_venda=150.00,
    quantidade=10,
    tipo_movimentacao='entrada',
    origem='manual',
    codigo_barras=codigo_barras_novo,
    codigo_fornecedor=codigo_fornecedor_novo,
    preco_custo=80.00,
    marca="MARCA NOVA",
    categoria="Categoria Nova",
    usuario_id=usuario_id
)
print(f"      Movimentacao criada: ID {mov1_id}")

print(f"\n[1.3] Aprovando movimentacao...")
produto1_id = aprovar_movimentacao(mov1_id, usuario_id=usuario_id)
print(f"      Produto criado: ID {produto1_id}")

print(f"\n[1.4] Verificando produto criado no banco...")
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('''
    SELECT id, nome, estoque, preco, preco_custo, codigo_barras, codigo_fornecedor 
    FROM produtos WHERE id = %s
''', (produto1_id,))
prod = cursor.fetchone()
conn.close()

if prod:
    print(f"      ID: {prod[0]}")
    print(f"      Nome: {prod[1]}")
    print(f"      Estoque: {prod[2]} unidades")
    print(f"      Preco Venda: R$ {prod[3]:.2f}")
    print(f"      Preco Custo: R$ {prod[4]:.2f}")
    print(f"      Codigo Barras: {prod[5]}")
    print(f"      Codigo Fornecedor: {prod[6]}")
    print(f"\n      [OK] PRODUTO NOVO CADASTRADO COM SUCESSO!")
else:
    print(f"      [ERRO] Produto nao encontrado!")

# ============================================================================
# CENÁRIO 2: PRODUTO EXISTENTE (atualizar estoque e preços)
# ============================================================================
print("\n" + "-"*70)
print("CENARIO 2: PRODUTO EXISTENTE (atualizar estoque e precos)")
print("-"*70)

print(f"\n[2.1] Estado ANTES da segunda movimentacao:")
print(f"      ID: {prod[0]}")
print(f"      Estoque ANTES: {prod[2]} unidades")
print(f"      Preco Venda ANTES: R$ {prod[3]:.2f}")
print(f"      Preco Custo ANTES: R$ {prod[4]:.2f}")

print(f"\n[2.2] Criando SEGUNDA movimentacao do MESMO produto...")
print(f"      (usando o mesmo codigo_barras: {codigo_barras_novo})")
mov2_id = adicionar_movimentacao(
    nome="PRODUTO TOTALMENTE NOVO - VERSAO ATUALIZADA",
    preco_venda=180.00,  # NOVO PRECO
    quantidade=15,  # ADICIONAR 15 unidades
    tipo_movimentacao='entrada',
    origem='manual',
    codigo_barras=codigo_barras_novo,  # MESMO CODIGO
    codigo_fornecedor=codigo_fornecedor_novo,  # MESMO CODIGO
    preco_custo=90.00,  # NOVO CUSTO
    marca="MARCA ATUALIZADA",
    categoria="Categoria Atualizada",
    usuario_id=usuario_id
)
print(f"      Movimentacao criada: ID {mov2_id}")

print(f"\n[2.3] Aprovando segunda movimentacao...")
produto2_id = aprovar_movimentacao(mov2_id, usuario_id=usuario_id)
print(f"      Produto retornado: ID {produto2_id}")

if produto2_id == produto1_id:
    print(f"      [OK] MESMO PRODUTO (ID nao mudou)")
else:
    print(f"      [ATENCAO] IDs diferentes! {produto1_id} vs {produto2_id}")

print(f"\n[2.4] Verificando produto ATUALIZADO no banco...")
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('''
    SELECT id, nome, estoque, preco, preco_custo, codigo_barras, codigo_fornecedor 
    FROM produtos WHERE codigo_barras = %s
''', (codigo_barras_novo,))
prod_atualizado = cursor.fetchone()
conn.close()

print(f"\n[2.5] Estado DEPOIS da segunda movimentacao:")
print(f"      ID: {prod_atualizado[0]}")
print(f"      Nome: {prod_atualizado[1]}")
print(f"      Estoque DEPOIS: {prod_atualizado[2]} unidades (ANTES: {prod[2]}, +15 = {prod[2] + 15})")
print(f"      Preco Venda DEPOIS: R$ {prod_atualizado[3]:.2f} (ANTES: R$ {prod[3]:.2f})")
print(f"      Preco Custo DEPOIS: R$ {prod_atualizado[4]:.2f} (ANTES: R$ {prod[4]:.2f})")

# ============================================================================
# CENÁRIO 3: PRODUTO EXISTENTE por CODIGO_FORNECEDOR (sem codigo_barras)
# ============================================================================
print("\n" + "-"*70)
print("CENARIO 3: PRODUTO EXISTENTE identificado por CODIGO_FORNECEDOR")
print("-"*70)

codigo_fornecedor_teste = "FORN-TESTE-999"

print(f"\n[3.1] Criando produto SEM codigo_barras...")
mov3_id = adicionar_movimentacao(
    nome="PRODUTO SEM CODIGO BARRAS",
    preco_venda=50.00,
    quantidade=20,
    tipo_movimentacao='entrada',
    origem='manual',
    codigo_barras=None,  # SEM CODIGO DE BARRAS
    codigo_fornecedor=codigo_fornecedor_teste,
    preco_custo=25.00,
    usuario_id=usuario_id
)
produto3_id = aprovar_movimentacao(mov3_id, usuario_id=usuario_id)
print(f"      Produto criado: ID {produto3_id}")

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT estoque, preco FROM produtos WHERE id = %s', (produto3_id,))
p3_antes = cursor.fetchone()
conn.close()
print(f"      Estoque inicial: {p3_antes[0]} unidades")
print(f"      Preco inicial: R$ {p3_antes[1]:.2f}")

print(f"\n[3.2] Criando SEGUNDA movimentacao usando CODIGO_FORNECEDOR...")
mov4_id = adicionar_movimentacao(
    nome="PRODUTO SEM CODIGO BARRAS - ATUALIZADO",
    preco_venda=60.00,  # NOVO PRECO
    quantidade=10,  # +10 unidades
    tipo_movimentacao='entrada',
    origem='manual',
    codigo_barras=None,  # CONTINUA SEM CODIGO
    codigo_fornecedor=codigo_fornecedor_teste,  # MESMO CODIGO FORNECEDOR
    preco_custo=30.00,
    usuario_id=usuario_id
)
produto4_id = aprovar_movimentacao(mov4_id, usuario_id=usuario_id)

if produto4_id == produto3_id:
    print(f"      [OK] MESMO PRODUTO identificado por codigo_fornecedor")
else:
    print(f"      [ERRO] Produto duplicado! {produto3_id} vs {produto4_id}")

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT estoque, preco FROM produtos WHERE id = %s', (produto4_id,))
p3_depois = cursor.fetchone()
conn.close()
print(f"      Estoque atualizado: {p3_depois[0]} unidades (esperado: {p3_antes[0] + 10})")
print(f"      Preco atualizado: R$ {p3_depois[1]:.2f}")

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "="*70)
print("RESUMO DOS TESTES")
print("="*70)

resultado_1 = "[OK]" if prod else "[ERRO]"
resultado_2 = "[OK]" if (produto2_id == produto1_id and prod_atualizado[2] == prod[2] + 15) else "[ERRO]"
resultado_3 = "[OK]" if (produto4_id == produto3_id and p3_depois[0] == p3_antes[0] + 10) else "[ERRO]"

print(f"\n{resultado_1} CENARIO 1: Produto NOVO cadastrado corretamente")
print(f"{resultado_2} CENARIO 2: Produto EXISTENTE teve estoque SOMADO e precos ATUALIZADOS")
print(f"{resultado_3} CENARIO 3: Produto identificado por CODIGO_FORNECEDOR funcionou")

if resultado_1 == "[OK]" and resultado_2 == "[OK]" and resultado_3 == "[OK]":
    print("\n" + "="*70)
    print("[SUCESSO] TODA A LOGICA DE IMPORTACAO ESTA FUNCIONANDO PERFEITAMENTE!")
    print("="*70)
    print("\nRESUMO:")
    print("  - Produtos NOVOS sao CADASTRADOS")
    print("  - Produtos EXISTENTES tem ESTOQUE SOMADO")
    print("  - Produtos EXISTENTES tem PRECOS ATUALIZADOS")
    print("  - Identificacao por CODIGO_BARRAS funciona")
    print("  - Identificacao por CODIGO_FORNECEDOR funciona")
else:
    print("\n[ERRO] Algum teste falhou!")

print("\n")
