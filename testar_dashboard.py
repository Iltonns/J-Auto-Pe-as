import traceback
from Minha_autopecas_web.logica_banco import (
    obter_estatisticas_dashboard,
    produtos_estoque_baixo,
    listar_vendas,
    listar_contas_pagar_hoje,
    listar_contas_receber_hoje
)

print("=" * 60)
print("TESTANDO FUNÇÕES DO DASHBOARD")
print("=" * 60)

# Teste 1: Estatísticas
print("\n1. Testando obter_estatisticas_dashboard()...")
try:
    estatisticas = obter_estatisticas_dashboard()
    print("   [OK] Estatísticas obtidas com sucesso!")
    print(f"   Total de produtos: {estatisticas.get('total_produtos', 'N/A')}")
    print(f"   Total de clientes: {estatisticas.get('total_clientes', 'N/A')}")
    print(f"   Vendas do dia: {estatisticas.get('vendas_dia_quantidade', 'N/A')}")
except Exception as e:
    print(f"   [ERRO] Falha ao obter estatísticas!")
    print(f"   Erro: {e}")
    traceback.print_exc()

# Teste 2: Produtos com estoque baixo
print("\n2. Testando produtos_estoque_baixo()...")
try:
    produtos = produtos_estoque_baixo()
    print(f"   [OK] {len(produtos)} produtos com estoque baixo")
except Exception as e:
    print(f"   [ERRO] Falha ao buscar produtos com estoque baixo!")
    print(f"   Erro: {e}")
    traceback.print_exc()

# Teste 3: Vendas recentes
print("\n3. Testando listar_vendas(limit=10)...")
try:
    vendas = listar_vendas(limit=10)
    print(f"   [OK] {len(vendas)} vendas encontradas")
except Exception as e:
    print(f"   [ERRO] Falha ao listar vendas!")
    print(f"   Erro: {e}")
    traceback.print_exc()

# Teste 4: Contas a pagar hoje
print("\n4. Testando listar_contas_pagar_hoje()...")
try:
    contas_pagar = listar_contas_pagar_hoje()
    print(f"   [OK] {len(contas_pagar)} contas a pagar hoje")
except Exception as e:
    print(f"   [ERRO] Falha ao listar contas a pagar!")
    print(f"   Erro: {e}")
    traceback.print_exc()

# Teste 5: Contas a receber hoje
print("\n5. Testando listar_contas_receber_hoje()...")
try:
    contas_receber = listar_contas_receber_hoje()
    print(f"   [OK] {len(contas_receber)} contas a receber hoje")
except Exception as e:
    print(f"   [ERRO] Falha ao listar contas a receber!")
    print(f"   Erro: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
