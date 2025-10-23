# Script para popular o banco com dados de teste
from Minha_autopecas_web.logica_banco import *
from datetime import date, timedelta

# Adicionar alguns clientes de exemplo
print("Adicionando clientes de exemplo...")
clientes_exemplo = [
    {"nome": "João Silva", "telefone": "(11) 99999-1111", "email": "joao@email.com", "cpf_cnpj": "123.456.789-10"},
    {"nome": "Maria Santos", "telefone": "(11) 99999-2222", "email": "maria@email.com", "cpf_cnpj": "987.654.321-00"},
    {"nome": "Pedro Oliveira", "telefone": "(11) 99999-3333", "email": "pedro@email.com"},
    {"nome": "Ana Costa", "telefone": "(11) 99999-4444", "email": "ana@email.com"},
    {"nome": "Auto Center Familia", "telefone": "(11) 99999-5555", "cpf_cnpj": "12.345.678/0001-90"}
]

for cliente in clientes_exemplo:
    adicionar_cliente(**cliente)

print("Adicionando produtos de exemplo...")
produtos_exemplo = [
    {"nome": "Óleo 5W30 Castrol", "preco": 45.90, "estoque": 20, "codigo_barras": "7891234567801", "categoria": "Lubrificantes"},
    {"nome": "Filtro de Óleo", "preco": 25.50, "estoque": 15, "codigo_barras": "7891234567802", "categoria": "Filtros"},
    {"nome": "Pastilha de Freio Dianteira", "preco": 89.90, "estoque": 8, "codigo_barras": "7891234567803", "categoria": "Freios"},
    {"nome": "Disco de Freio", "preco": 120.00, "estoque": 6, "codigo_barras": "7891234567804", "categoria": "Freios"},
    {"nome": "Bateria 60Ah", "preco": 280.00, "estoque": 5, "codigo_barras": "7891234567805", "categoria": "Elétrica"},
    {"nome": "Vela de Ignição", "preco": 18.90, "estoque": 30, "codigo_barras": "7891234567806", "categoria": "Motor"},
    {"nome": "Correia Dentada", "preco": 65.50, "estoque": 10, "codigo_barras": "7891234567807", "categoria": "Motor"},
    {"nome": "Amortecedor Dianteiro", "preco": 180.00, "estoque": 4, "codigo_barras": "7891234567808", "categoria": "Suspensão"},
    {"nome": "Lâmpada H4", "preco": 15.90, "estoque": 25, "codigo_barras": "7891234567809", "categoria": "Iluminação"},
    {"nome": "Fluido de Freio DOT4", "preco": 28.90, "estoque": 12, "codigo_barras": "7891234567810", "categoria": "Fluidos"}
]

for produto in produtos_exemplo:
    adicionar_produto(**produto)

print("Adicionando algumas contas a pagar...")
hoje = date.today()
contas_pagar_exemplo = [
    {"descricao": "Energia Elétrica", "valor": 450.00, "data_vencimento": hoje.isoformat(), "categoria": "Utilidades"},
    {"descricao": "Fornecedor ABC Peças", "valor": 1500.00, "data_vencimento": (hoje + timedelta(days=5)).isoformat(), "categoria": "Fornecedores"},
    {"descricao": "Aluguel da Loja", "valor": 2800.00, "data_vencimento": (hoje + timedelta(days=10)).isoformat(), "categoria": "Fixas"},
    {"descricao": "Telefone/Internet", "valor": 180.00, "data_vencimento": (hoje - timedelta(days=2)).isoformat(), "categoria": "Utilidades"}
]

for conta in contas_pagar_exemplo:
    adicionar_conta_pagar(**conta)

print("Dados de exemplo adicionados com sucesso!")
print("\nCredenciais de login:")
print("Usuário: admin")
print("Senha: admin123")