#!/usr/bin/env python
"""Script para inicializar o banco de dados"""
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

try:
    from Minha_autopecas_web.logica_banco import init_db
    print("Inicializando banco de dados...")
    init_db()
    print("✓ Banco de dados inicializado com sucesso!")
except Exception as e:
    print(f"✗ Erro ao inicializar banco: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
