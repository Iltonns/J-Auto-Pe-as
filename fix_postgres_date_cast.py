import re

# Ler o arquivo
with open('Minha_autopecas_web/logica_banco.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituições para PostgreSQL
# 1. DATE(coluna.campo) -> coluna.campo::date
content = re.sub(r'DATE\(([a-z_]+\.[a-z_]+)\)', r'\1::date', content)
content = re.sub(r'date\(([a-z_]+\.[a-z_]+)\)', r'\1::date', content)

# Salvar o arquivo
with open('Minha_autopecas_web/logica_banco.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Funções DATE() convertidas para ::date do PostgreSQL!")
print("  - DATE(campo) -> campo::date")
