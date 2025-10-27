import re

# Ler o arquivo
with open('Minha_autopecas_web/logica_banco.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituições para PostgreSQL
# 1. date(campo_sem_ponto) -> campo_sem_ponto::date
content = re.sub(r'\bdate\(([a-z_]+)\)', r'\1::date', content)

# Salvar o arquivo
with open('Minha_autopecas_web/logica_banco.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Funções date() sem tabela convertidas para ::date do PostgreSQL!")
print("  - date(campo) -> campo::date")
