"""
Script para verificar o conteúdo da página retornada
"""

import requests

url = "http://localhost:5000/contas-a-pagar-hoje"

try:
    response = requests.get(url, allow_redirects=True, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"URL final: {response.url}")
    print(f"\nPrimeiras 1000 caracteres da resposta:\n")
    print(response.text[:1000])
    
    # Verificar se há login
    if 'login' in response.text.lower() or 'senha' in response.text.lower():
        print("\n\n⚠️ AVISO: A página parece estar redirecionando para login!")
        print("Você precisa estar logado para acessar esta página.")
    
    # Verificar elementos específicos
    print("\n\n=== VERIFICAÇÕES ===")
    print(f"Contém 'html2pdf': {'html2pdf' in response.text}")
    print(f"Contém 'Exportar PDF': {'Exportar PDF' in response.text}")
    print(f"Contém 'exportarPDF()': {'exportarPDF()' in response.text}")
    print(f"Contém 'contentToPrint': {'contentToPrint' in response.text}")
    
except Exception as e:
    print(f"Erro: {e}")
