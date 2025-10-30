
"""
Script para cadastrar produtos em lote no sistema
Data: 29 de outubro de 2025
"""

from Minha_autopecas_web.logica_banco import adicionar_produto, get_db_connection

# Lista de produtos a serem cadastrados
produtos = [
    {
        'codigo_barras': '2799',
        'codigo_fornecedor': '252526',
        'nome': '" T " MANGOTE LINHA FIAT - ALUMINIO',
        'estoque': 2,
        'marca': 'IMPORTADO',
        'preco': 50.00,
        'categoria': 'MANGOTES'
    },
    {
        'codigo_barras': '2800',
        'codigo_fornecedor': '25252654',
        'nome': '" T " MANGOTE LINHA GM - ALUMINIO',
        'estoque': 8,
        'marca': 'IMPORTADO',
        'preco': 50.00,
        'categoria': 'MANGOTES'
    },
    {
        'codigo_barras': '1037',
        'codigo_fornecedor': '095SP+23',
        'nome': '095SP 234H CORREIA DENTADA',
        'estoque': 2,
        'marca': 'DAYCO',
        'preco': 160.00,
        'categoria': 'CORREIAS'
    },
    {
        'codigo_barras': '3094',
        'codigo_fornecedor': '00665082000021',
        'nome': '10285 KIT KIT AMORTECEDOR DIANTEIRO (BAT COI)',
        'estoque': 4,
        'marca': '',
        'preco': 22.00,
        'categoria': 'AMORTECEDORES'
    },
    {
        'codigo_barras': '3093',
        'codigo_fornecedor': '00572082000860',
        'nome': '3143 BUCHA DIANTEIRA BANDEJA DIANTEIRA(MENOR)',
        'estoque': 2,
        'marca': '',
        'preco': 72.82,
        'categoria': 'BUCHAS'
    },
    {
        'codigo_barras': '3092',
        'codigo_fornecedor': '00313095001711',
        'nome': '75825 JUNTA TAMPA VALVULA',
        'estoque': 1,
        'marca': '',
        'preco': 182.08,
        'categoria': 'JUNTAS'
    },
    {
        'codigo_barras': '3069',
        'codigo_fornecedor': '5986100130',
        'nome': 'ABRACADEIRA NYLON - PRETA W-MAX 4W20',
        'estoque': 10,
        'marca': 'WURTH',
        'preco': 0.60,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '3068',
        'codigo_fornecedor': '5986100125',
        'nome': 'ABRACADEIRA NYLON - PRETA W-MAX 4X28',
        'estoque': 10,
        'marca': 'WURTH',
        'preco': 1.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '3067',
        'codigo_fornecedor': '5986100127',
        'nome': 'ABRACADEIRA NYLON - PRETA W-MAX 7X36',
        'estoque': 10,
        'marca': 'WURTH',
        'preco': 2.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '661',
        'codigo_fornecedor': '001500300',
        'nome': 'ABRACADEIRA PLASTICA (PRETA) 200MMX4 8MM',
        'estoque': 16,
        'marca': 'IMPORTADO',
        'preco': 0.50,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '662',
        'codigo_fornecedor': '0015005000',
        'nome': 'ABRACADEIRA PLASTICA (PRETA) 300MMX3 5MM',
        'estoque': 10,
        'marca': 'IMPORTADO',
        'preco': 0.50,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '663',
        'codigo_fornecedor': '015007000',
        'nome': 'ABRACADEIRA PLASTICA (PRETA) 400MMX4 8MM',
        'estoque': 18,
        'marca': 'IMPORTADO',
        'preco': 1.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '664',
        'codigo_fornecedor': '0015008000',
        'nome': 'ABRACADEIRA PLASTICA (PRETA) 400MMX7 5MM',
        'estoque': 47,
        'marca': 'IMPORTADO',
        'preco': 2.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '3065',
        'codigo_fornecedor': '5986311014',
        'nome': 'ABRACADEIRA SEM FIM - W-MAX 90X110',
        'estoque': 8,
        'marca': 'WURTH',
        'preco': 7.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '2882',
        'codigo_fornecedor': '5986311001',
        'nome': 'ABRACADEIRA SEM FIM ZNB W-MAX -  8X12',
        'estoque': 14,
        'marca': 'WURTH',
        'preco': 2.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '2883',
        'codigo_fornecedor': '5986311002',
        'nome': 'ABRACADEIRA SEM FIM ZNB W-MAX - 10X16',
        'estoque': 9,
        'marca': 'WURTH',
        'preco': 2.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '2885',
        'codigo_fornecedor': '5986311004',
        'nome': 'ABRACADEIRA SEM FIM ZNB W-MAX - 16X27',
        'estoque': 20,
        'marca': 'WURTH',
        'preco': 2.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '2886',
        'codigo_fornecedor': '5986311005',
        'nome': 'ABRACADEIRA SEM FIM ZNB W-MAX - 20X32',
        'estoque': 19,
        'marca': 'WURTH',
        'preco': 3.00,
        'categoria': 'ABRACADEIRAS'
    },
    {
        'codigo_barras': '2887',
        'codigo_fornecedor': '5986311006',
        'nome': 'ABRACADEIRA SEM FIM ZNB W-MAX - 25X40',
        'estoque': -1,  # Estoque negativo será cadastrado como está
        'marca': 'WURTH',
        'preco': 3.00,
        'categoria': 'ABRACADEIRAS'
    }
]

def verificar_produto_existe(codigo_barras):
    """Verifica se o produto já existe pelo código de barras"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome FROM produtos WHERE codigo_barras = %s", (codigo_barras,))
    resultado = cursor.fetchone()
    
    conn.close()
    return resultado

def cadastrar_produtos():
    """Cadastra todos os produtos da lista"""
    produtos_cadastrados = 0
    produtos_existentes = 0
    produtos_com_erro = 0
    
    print("=" * 80)
    print("INICIANDO CADASTRO DE PRODUTOS EM LOTE")
    print("=" * 80)
    print(f"Total de produtos a cadastrar: {len(produtos)}\n")
    
    for i, produto in enumerate(produtos, 1):
        try:
            codigo_barras = produto['codigo_barras']
            
            # Verificar se o produto já existe
            existe = verificar_produto_existe(codigo_barras)
            
            if existe:
                produtos_existentes += 1
                print(f"[{i}/{len(produtos)}] ⚠️  PRODUTO JÁ EXISTE")
                print(f"   Código: {codigo_barras}")
                print(f"   Nome: {existe[1]}")
                print()
                continue
            
            # Cadastrar o produto
            produto_id = adicionar_produto(
                nome=produto['nome'],
                preco=produto['preco'],
                estoque=produto['estoque'],
                estoque_minimo=1,
                codigo_barras=codigo_barras,
                descricao=None,
                categoria=produto.get('categoria', ''),
                codigo_fornecedor=produto.get('codigo_fornecedor', ''),
                preco_custo=0,
                margem_lucro=0,
                foto_url=None,
                marca=produto.get('marca', ''),
                fornecedor_id=None
            )
            
            produtos_cadastrados += 1
            print(f"[{i}/{len(produtos)}] ✅ PRODUTO CADASTRADO COM SUCESSO")
            print(f"   ID: {produto_id}")
            print(f"   Código: {codigo_barras}")
            print(f"   Nome: {produto['nome'][:60]}...")
            print(f"   Marca: {produto['marca']}")
            print(f"   Estoque: {produto['estoque']}")
            print(f"   Preço: R$ {produto['preco']:.2f}")
            print()
            
        except Exception as e:
            produtos_com_erro += 1
            print(f"[{i}/{len(produtos)}] ❌ ERRO AO CADASTRAR PRODUTO")
            print(f"   Código: {produto['codigo_barras']}")
            print(f"   Nome: {produto['nome'][:60]}...")
            print(f"   Erro: {str(e)}")
            print()
    
    # Resumo final
    print("=" * 80)
    print("RESUMO DO CADASTRO")
    print("=" * 80)
    print(f"✅ Produtos cadastrados com sucesso: {produtos_cadastrados}")
    print(f"⚠️  Produtos já existentes: {produtos_existentes}")
    print(f"❌ Produtos com erro: {produtos_com_erro}")
    print(f"📦 Total processado: {len(produtos)}")
    print("=" * 80)

if __name__ == "__main__":
    try:
        cadastrar_produtos()
    except Exception as e:
        print(f"\n❌ ERRO GERAL NO PROCESSO: {str(e)}")