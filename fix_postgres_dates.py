import re

# Ler o arquivo
with open('Minha_autopecas_web/logica_banco.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituições para PostgreSQL
# 1. date('now') -> CURRENT_DATE
content = re.sub(r"date\('now'\)", 'CURRENT_DATE', content)

# 2. DATE('now', '+X days') -> (CURRENT_DATE + INTERVAL 'X days')
content = re.sub(r"DATE\('now', '\+(\d+) days'\)", r"(CURRENT_DATE + INTERVAL '\1 days')", content)
content = re.sub(r"date\('now', '\+(\d+) days'\)", r"(CURRENT_DATE + INTERVAL '\1 days')", content)

# 3. DATE(coluna) -> coluna::date (conversão explícita)
# Não vamos fazer isso ainda, pois pode afetar outras coisas

# Salvar o arquivo
with open('Minha_autopecas_web/logica_banco.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Funções de data SQLite convertidas para PostgreSQL!")
print("  - date('now') -> CURRENT_DATE")
print("  - DATE('now', '+X days') -> (CURRENT_DATE + INTERVAL 'X days')")
