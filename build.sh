#!/usr/bin/env bash
# Script de build para o Render

# Instalar dependências
pip install -r requirements.txt

# Criar diretórios necessários
mkdir -p static/images/produtos
mkdir -p static/images/empresa

# Inicializar banco de dados (criar tabelas e admin)
python init_db.py

echo "✅ Build concluído com sucesso!"
