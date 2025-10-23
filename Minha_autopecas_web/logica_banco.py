# LOGICA DE BANCO DE DADOS - SISTEMA DE AUTOPEÇAS FAMÍLIA
import sqlite3
import os
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'autopecas.db')

def init_db():
    """Inicializa o banco de dados criando todas as tabelas necessárias"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            cpf_cnpj TEXT,
            endereco TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER DEFAULT 0,
            estoque_minimo INTEGER DEFAULT 5,
            codigo_barras TEXT UNIQUE,
            descricao TEXT,
            categoria TEXT,
            ativo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            total REAL NOT NULL,
            forma_pagamento TEXT NOT NULL,
            desconto REAL DEFAULT 0,
            observacoes TEXT,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de itens de venda
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    # Tabela de contas a pagar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas_pagar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_vencimento DATE NOT NULL,
            data_pagamento DATE,
            status TEXT DEFAULT 'pendente',
            categoria TEXT,
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de contas a receber
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas_receber (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_vencimento DATE NOT NULL,
            data_recebimento DATE,
            status TEXT DEFAULT 'pendente',
            cliente_id INTEGER,
            venda_id INTEGER,
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (venda_id) REFERENCES vendas (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def criar_usuario_admin():
    """Cria um usuário administrador padrão se não existir"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO usuarios (username, password_hash, email)
            VALUES (?, ?, ?)
        ''', ('admin', password_hash, 'admin@autopecas.com'))
        conn.commit()
    
    conn.close()

# FUNÇÕES DE USUÁRIOS
def verificar_usuario(username, password):
    """Verifica se o usuário e senha estão corretos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        return {'id': user[0], 'username': username}
    return None

def buscar_usuario_por_id(user_id):
    """Busca um usuário pelo ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {'id': user[0], 'username': user[1], 'email': user[2]}
    return None

# FUNÇÕES DE CLIENTES
def listar_clientes():
    """Lista todos os clientes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, telefone, email, cpf_cnpj, endereco
        FROM clientes
        ORDER BY nome
    ''')
    
    clientes = []
    for row in cursor.fetchall():
        clientes.append({
            'id': row[0],
            'nome': row[1],
            'telefone': row[2],
            'email': row[3],
            'cpf_cnpj': row[4],
            'endereco': row[5]
        })
    
    conn.close()
    return clientes

def adicionar_cliente(nome, telefone=None, email=None, cpf_cnpj=None, endereco=None):
    """Adiciona um novo cliente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO clientes (nome, telefone, email, cpf_cnpj, endereco)
        VALUES (?, ?, ?, ?, ?)
    ''', (nome, telefone, email, cpf_cnpj, endereco))
    
    cliente_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cliente_id

def editar_cliente(id, nome, telefone=None, email=None, cpf_cnpj=None, endereco=None):
    """Edita um cliente existente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE clientes 
        SET nome = ?, telefone = ?, email = ?, cpf_cnpj = ?, endereco = ?
        WHERE id = ?
    ''', (nome, telefone, email, cpf_cnpj, endereco, id))
    
    conn.commit()
    conn.close()

def deletar_cliente(id):
    """Deleta um cliente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM clientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# FUNÇÕES DE PRODUTOS
def listar_produtos():
    """Lista todos os produtos ativos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria, ativo
        FROM produtos
        WHERE ativo = 1
        ORDER BY nome
    ''')
    
    produtos = []
    for row in cursor.fetchall():
        produtos.append({
            'id': row[0],
            'nome': row[1],
            'preco': row[2],
            'estoque': row[3],
            'estoque_minimo': row[4],
            'codigo_barras': row[5],
            'descricao': row[6],
            'categoria': row[7],
            'ativo': row[8]
        })
    
    conn.close()
    return produtos

def buscar_produto(termo_busca):
    """Busca produto por nome, código de barras ou ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, preco, estoque, codigo_barras
        FROM produtos
        WHERE ativo = 1 AND (
            nome LIKE ? OR 
            codigo_barras = ? OR 
            CAST(id AS TEXT) = ?
        )
        LIMIT 10
    ''', (f'%{termo_busca}%', termo_busca, termo_busca))
    
    produtos = []
    for row in cursor.fetchall():
        produtos.append({
            'id': row[0],
            'nome': row[1],
            'preco': row[2],
            'estoque': row[3],
            'codigo_barras': row[4]
        })
    
    conn.close()
    return produtos

def adicionar_produto(nome, preco, estoque=0, estoque_minimo=5, codigo_barras=None, descricao=None, categoria=None):
    """Adiciona um novo produto"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO produtos (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria))
    
    produto_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return produto_id

def editar_produto(id, nome, preco, estoque, estoque_minimo=5, codigo_barras=None, descricao=None, categoria=None):
    """Edita um produto existente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE produtos 
        SET nome = ?, preco = ?, estoque = ?, estoque_minimo = ?, 
            codigo_barras = ?, descricao = ?, categoria = ?
        WHERE id = ?
    ''', (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria, id))
    
    conn.commit()
    conn.close()

def deletar_produto(id):
    """Marca um produto como inativo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def atualizar_estoque(produto_id, quantidade):
    """Atualiza o estoque de um produto (diminui)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE produtos 
        SET estoque = estoque - ? 
        WHERE id = ?
    ''', (quantidade, produto_id))
    
    conn.commit()
    conn.close()

# FUNÇÕES DE VENDAS
def registrar_venda(cliente_id, itens, forma_pagamento, desconto=0, observacoes=None, usuario_id=None):
    """Registra uma nova venda com seus itens"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calcula o total
    total = sum(item['quantidade'] * item['preco_unitario'] for item in itens) - desconto
    
    # Insere a venda
    cursor.execute('''
        INSERT INTO vendas (cliente_id, total, forma_pagamento, desconto, observacoes, usuario_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (cliente_id, total, forma_pagamento, desconto, observacoes, usuario_id))
    
    venda_id = cursor.lastrowid
    
    # Insere os itens da venda
    for item in itens:
        cursor.execute('''
            INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        ''', (venda_id, item['produto_id'], item['quantidade'], 
              item['preco_unitario'], item['quantidade'] * item['preco_unitario']))
        
        # Atualiza o estoque
        atualizar_estoque(item['produto_id'], item['quantidade'])
    
    # Se for venda a prazo, cria conta a receber
    if forma_pagamento == 'prazo':
        cursor.execute('''
            INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, venda_id)
            VALUES (?, ?, DATE('now', '+30 days'), ?, ?)
        ''', (f'Venda #{venda_id}', total, cliente_id, venda_id))
    
    conn.commit()
    conn.close()
    return venda_id

def listar_vendas(limit=50):
    """Lista as vendas mais recentes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.id, c.nome, v.total, v.forma_pagamento, v.data_venda
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.data_venda DESC
        LIMIT ?
    ''', (limit,))
    
    vendas = []
    for row in cursor.fetchall():
        vendas.append({
            'id': row[0],
            'cliente': row[1] or 'Cliente Avulso',
            'total': row[2],
            'forma_pagamento': row[3],
            'data_venda': row[4]
        })
    
    conn.close()
    return vendas

# FUNÇÕES DE CONTAS A PAGAR
def listar_contas_pagar_hoje():
    """Lista contas a pagar com vencimento hoje"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, descricao, valor, data_vencimento, status, categoria
        FROM contas_pagar
        WHERE date(data_vencimento) = date('now') AND status = 'pendente'
        ORDER BY valor DESC
    ''')
    
    contas = []
    for row in cursor.fetchall():
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': row[3],
            'status': row[4],
            'categoria': row[5]
        })
    
    conn.close()
    return contas

def listar_contas_pagar_em_atraso():
    """Lista contas a pagar em atraso"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, descricao, valor, data_vencimento, status, categoria
        FROM contas_pagar
        WHERE date(data_vencimento) < date('now') AND status = 'pendente'
        ORDER BY data_vencimento
    ''')
    
    contas = []
    for row in cursor.fetchall():
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': row[3],
            'status': row[4],
            'categoria': row[5]
        })
    
    conn.close()
    return contas

def adicionar_conta_pagar(descricao, valor, data_vencimento, categoria=None, observacoes=None):
    """Adiciona uma nova conta a pagar"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO contas_pagar (descricao, valor, data_vencimento, categoria, observacoes)
        VALUES (?, ?, ?, ?, ?)
    ''', (descricao, valor, data_vencimento, categoria, observacoes))
    
    conta_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conta_id

def pagar_conta(conta_id, data_pagamento=None):
    """Marca uma conta como paga"""
    if not data_pagamento:
        data_pagamento = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE contas_pagar 
        SET status = 'pago', data_pagamento = ?
        WHERE id = ?
    ''', (data_pagamento, conta_id))
    
    conn.commit()
    conn.close()

# FUNÇÕES DE CONTAS A RECEBER
def listar_contas_receber_hoje():
    """Lista contas a receber com vencimento hoje"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT cr.id, cr.descricao, cr.valor, cr.data_vencimento, cr.status, c.nome
        FROM contas_receber cr
        LEFT JOIN clientes c ON cr.cliente_id = c.id
        WHERE date(cr.data_vencimento) = date('now') AND cr.status = 'pendente'
        ORDER BY cr.valor DESC
    ''')
    
    contas = []
    for row in cursor.fetchall():
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': row[3],
            'status': row[4],
            'cliente': row[5]
        })
    
    conn.close()
    return contas

def listar_contas_receber_em_atraso():
    """Lista contas a receber em atraso"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT cr.id, cr.descricao, cr.valor, cr.data_vencimento, cr.status, c.nome
        FROM contas_receber cr
        LEFT JOIN clientes c ON cr.cliente_id = c.id
        WHERE date(cr.data_vencimento) < date('now') AND cr.status = 'pendente'
        ORDER BY cr.data_vencimento
    ''')
    
    contas = []
    for row in cursor.fetchall():
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': row[3],
            'status': row[4],
            'cliente': row[5]
        })
    
    conn.close()
    return contas

def receber_conta(conta_id, data_recebimento=None):
    """Marca uma conta como recebida"""
    if not data_recebimento:
        data_recebimento = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE contas_receber 
        SET status = 'recebido', data_recebimento = ?
        WHERE id = ?
    ''', (data_recebimento, conta_id))
    
    conn.commit()
    conn.close()

# FUNÇÕES DE ESTATÍSTICAS
def obter_estatisticas_dashboard():
    """Obtém estatísticas para o dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total de produtos
    cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1")
    total_produtos = cursor.fetchone()[0]
    
    # Total de clientes
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]
    
    # Valor do estoque
    cursor.execute("SELECT SUM(preco * estoque) FROM produtos WHERE ativo = 1")
    valor_estoque = cursor.fetchone()[0] or 0
    
    # Produtos com estoque baixo
    cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1 AND estoque <= estoque_minimo")
    produtos_estoque_baixo = cursor.fetchone()[0]
    
    # Vendas do mês
    cursor.execute('''
        SELECT COUNT(*), SUM(total) 
        FROM vendas 
        WHERE strftime('%Y-%m', data_venda) = strftime('%Y-%m', 'now')
    ''')
    vendas_mes = cursor.fetchone()
    
    # Contas a receber em atraso
    cursor.execute('''
        SELECT SUM(valor) 
        FROM contas_receber 
        WHERE date(data_vencimento) < date('now') AND status = 'pendente'
    ''')
    valor_atraso_receber = cursor.fetchone()[0] or 0
    
    # Contas a pagar em atraso
    cursor.execute('''
        SELECT SUM(valor) 
        FROM contas_pagar 
        WHERE date(data_vencimento) < date('now') AND status = 'pendente'
    ''')
    valor_atraso_pagar = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_produtos': total_produtos,
        'total_clientes': total_clientes,
        'valor_estoque': valor_estoque,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'vendas_mes_quantidade': vendas_mes[0] or 0,
        'vendas_mes_valor': vendas_mes[1] or 0,
        'valor_atraso_receber': valor_atraso_receber,
        'valor_atraso_pagar': valor_atraso_pagar
    }

def produtos_estoque_baixo():
    """Lista produtos com estoque baixo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, estoque, estoque_minimo
        FROM produtos
        WHERE ativo = 1 AND estoque <= estoque_minimo
        ORDER BY estoque
    ''')
    
    produtos = []
    for row in cursor.fetchall():
        produtos.append({
            'id': row[0],
            'nome': row[1],
            'estoque': row[2],
            'estoque_minimo': row[3]
        })
    
    conn.close()
    return produtos

# Inicialização automática
if __name__ == "__main__":
    init_db()
    criar_usuario_admin()
    print("Banco de dados inicializado com sucesso!")