# LOGICA DE BANCO DE DADOS - SISTEMA DE AUTOPEÇAS FAMÍLIA
import sqlite3
import os
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'autopecas.db')

# Configurações SQLite para melhor performance e reduzir locks
def configure_sqlite_connection(conn):
    """Configura a conexão SQLite para melhor performance"""
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para melhor concorrência
    conn.execute("PRAGMA synchronous=NORMAL")  # Reduz I/O disk
    conn.execute("PRAGMA cache_size=10000")  # Aumenta cache
    conn.execute("PRAGMA temp_store=MEMORY")  # Usa memoria para tabelas temporárias
    conn.execute("PRAGMA busy_timeout=30000")  # 30 segundos de timeout para locks

def get_db_connection(timeout=30.0):
    """Cria uma conexão configurada com o banco"""
    conn = sqlite3.connect(DB_PATH, timeout=timeout)
    configure_sqlite_connection(conn)
    return conn

def init_db():
    """Inicializa o banco de dados criando todas as tabelas necessárias"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de usuários com permissões
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            email TEXT NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            permissao_vendas BOOLEAN DEFAULT 1,
            permissao_estoque BOOLEAN DEFAULT 1,
            permissao_clientes BOOLEAN DEFAULT 1,
            permissao_financeiro BOOLEAN DEFAULT 0,
            permissao_caixa BOOLEAN DEFAULT 0,
            permissao_relatorios BOOLEAN DEFAULT 0,
            permissao_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES usuarios (id)
        )
    ''')
    
    # Verificar e adicionar colunas se não existirem (para compatibilidade com DB existente)
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN nome_completo TEXT DEFAULT ''")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN DEFAULT 1")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_vendas BOOLEAN DEFAULT 1")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_estoque BOOLEAN DEFAULT 1")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_clientes BOOLEAN DEFAULT 1")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_financeiro BOOLEAN DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_caixa BOOLEAN DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_relatorios BOOLEAN DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_admin BOOLEAN DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN created_by INTEGER")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_contas_pagar BOOLEAN DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN permissao_contas_receber BOOLEAN DEFAULT 0")
    except:
        pass
    
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
    
    # Adicionar colunas para dados da NFe se não existirem
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN ncm TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN unidade TEXT DEFAULT 'UN'")
    except:
        pass
    
    # Adicionar colunas para gestão comercial
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN codigo_fornecedor TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN preco_custo REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN margem_lucro REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN fornecedor_id INTEGER")
    except:
        pass
    
    # Adicionar coluna para foto do produto se não existir
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN foto_url TEXT")
    except:
        pass
    
    # Adicionar coluna para marca do produto se não existir
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN marca TEXT")
    except:
        pass
    
    # Adicionar coluna para fornecedor na tabela contas_pagar se não existir
    try:
        cursor.execute("ALTER TABLE contas_pagar ADD COLUMN fornecedor_id INTEGER")
    except:
        pass
    
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
            fornecedor_id INTEGER,
            lancamento_financeiro_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id),
            FOREIGN KEY (lancamento_financeiro_id) REFERENCES lancamentos_financeiros (id)
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
    
    # Tabela de orçamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_orcamento TEXT UNIQUE NOT NULL,
            cliente_id INTEGER,
            total REAL NOT NULL DEFAULT 0,
            desconto REAL DEFAULT 0,
            observacoes TEXT,
            status TEXT DEFAULT 'pendente',
            data_validade DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de itens de orçamento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_orcamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (orcamento_id) REFERENCES orcamentos (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    # Tabela de caixa - movimentações financeiras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caixa_movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL, -- 'entrada', 'saida'
            categoria TEXT NOT NULL, -- 'venda', 'conta_paga', 'conta_recebida', 'despesa', 'receita'
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER NOT NULL,
            venda_id INTEGER, -- Link com venda se aplicável
            conta_pagar_id INTEGER, -- Link com conta a pagar se aplicável
            conta_receber_id INTEGER, -- Link com conta a receber se aplicável
            observacoes TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (conta_pagar_id) REFERENCES contas_pagar (id),
            FOREIGN KEY (conta_receber_id) REFERENCES contas_receber (id)
        )
    ''')
    
    # Tabela de abertura/fechamento de caixa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caixa_sessoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_abertura TIMESTAMP NOT NULL,
            data_fechamento TIMESTAMP,
            saldo_inicial REAL NOT NULL DEFAULT 0,
            saldo_final REAL,
            total_entradas REAL DEFAULT 0,
            total_saidas REAL DEFAULT 0,
            usuario_abertura INTEGER NOT NULL,
            usuario_fechamento INTEGER,
            status TEXT DEFAULT 'aberto', -- 'aberto', 'fechado'
            observacoes_abertura TEXT,
            observacoes_fechamento TEXT,
            FOREIGN KEY (usuario_abertura) REFERENCES usuarios (id),
            FOREIGN KEY (usuario_fechamento) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de lançamentos financeiros - adicionar colunas de referência
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos_financeiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL, -- 'receita', 'despesa'
            categoria TEXT NOT NULL, -- 'combustivel', 'energia', 'telefone', 'aluguel', etc
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_lancamento DATE NOT NULL,
            data_vencimento DATE,
            data_pagamento DATE,
            status TEXT DEFAULT 'pendente', -- 'pendente', 'pago', 'cancelado'
            forma_pagamento TEXT,
            numero_documento TEXT,
            fornecedor_cliente TEXT,
            usuario_id INTEGER NOT NULL,
            observacoes TEXT,
            conta_pagar_id INTEGER,
            conta_receber_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (conta_pagar_id) REFERENCES contas_pagar (id),
            FOREIGN KEY (conta_receber_id) REFERENCES contas_receber (id)
        )
    ''')
    
    # Tabela de fornecedores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cnpj TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            cidade TEXT,
            estado TEXT,
            cep TEXT,
            contato_pessoa TEXT,
            observacoes TEXT,
            ativo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de configurações da empresa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes_empresa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT NOT NULL DEFAULT 'FG AUTO PEÇAS',
            cnpj TEXT,
            endereco TEXT DEFAULT 'Rua Exemplo, 123 - Centro',
            cidade TEXT,
            estado TEXT,
            cep TEXT,
            telefone TEXT DEFAULT '(00) 0000-0000',
            email TEXT DEFAULT 'contato@fgautopecas.com.br',
            website TEXT,
            logo_path TEXT DEFAULT 'logo.jpg',
            observacoes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inserir configuração padrão se não existir
    cursor.execute("SELECT COUNT(*) FROM configuracoes_empresa")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO configuracoes_empresa (nome_empresa, endereco, telefone, email)
            VALUES (?, ?, ?, ?)
        ''', ('FG AUTO PEÇAS', 'Rua Exemplo, 123 - Centro', '(00) 0000-0000', 'contato@fgautopecas.com.br'))
    
    # Adicionar colunas para sincronização financeira se não existirem
    try:
        cursor.execute("ALTER TABLE contas_pagar ADD COLUMN fornecedor_id INTEGER")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE contas_pagar ADD COLUMN lancamento_financeiro_id INTEGER")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE lancamentos_financeiros ADD COLUMN conta_pagar_id INTEGER")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE lancamentos_financeiros ADD COLUMN conta_receber_id INTEGER")
    except:
        pass
    
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
            INSERT INTO usuarios (
                username, password_hash, nome_completo, email, 
                permissao_vendas, permissao_estoque, permissao_clientes,
                permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', password_hash, 'Administrador do Sistema', 'admin@autopecas.com',
              1, 1, 1, 1, 1, 1, 1))  # Admin tem todas as permissões
        conn.commit()
    else:
        # Atualizar usuário admin existente para ter todas as permissões
        cursor.execute('''
            UPDATE usuarios SET 
                nome_completo = COALESCE(nome_completo, 'Administrador do Sistema'),
                permissao_vendas = 1,
                permissao_estoque = 1,
                permissao_clientes = 1,
                permissao_financeiro = 1,
                permissao_caixa = 1,
                permissao_relatorios = 1,
                permissao_admin = 1
            WHERE username = 'admin'
        ''')
        conn.commit()
    
    conn.close()

def popular_dados_exemplo():
    """Popula o banco com dados de exemplo se estiver vazio"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se já existem produtos
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        # Adicionar produtos de exemplo
        produtos_exemplo = [
            ('VELA DE IGNIÇÃO GM / CORSA / AGILE', 42.50, 10, 3, 'VELA001', 'Vela de ignição para veículos GM', 'Ignição'),
            ('VELA DE IGNIÇÃO CLIO / LOGAN / SANDERO', 32.71, 15, 5, 'VELA002', 'Vela de ignição para Renault', 'Ignição'),
            ('VELA DE IGNIÇÃO FORD KA 1.0 3 CILINDROS', 38.00, 8, 3, 'VELA003', 'Vela específica para Ford KA', 'Ignição'),
            ('CABO DE VELA RENAULT CLIO / SANDERO', 77.00, 5, 2, 'CABO001', 'Cabo de vela Renault', 'Ignição'),
            ('CABO DE VELA GM / ONIX / PRISMA / AGILE', 72.00, 7, 2, 'CABO002', 'Cabo de vela GM', 'Ignição'),
            ('CABO DE VELA FIAT NOVO UNO / PALIO', 65.00, 6, 2, 'CABO003', 'Cabo de vela Fiat', 'Ignição'),
            ('CABO DE VELA FIAT FIRE 1.0 1.4 EVO 1.8', 45.00, 4, 2, 'CABO004', 'Cabo de vela Fiat Fire', 'Ignição'),
            ('CABO DE VELA GM / CORSA / CELTA / AGILE', 43.53, 12, 3, 'CABO005', 'Cabo de vela GM Corsa/Celta', 'Ignição'),
            ('VELA DE IGNIÇÃO GM / CORSA / CELTA / AGILE', 40.00, 20, 5, 'VELA004', 'Vela padrão GM', 'Ignição'),
            ('VELA DE IGNIÇÃO FIAT / UNO / PALIO / STRADA', 45.00, 18, 4, 'VELA005', 'Vela padrão Fiat', 'Ignição'),
        ]
        
        for produto in produtos_exemplo:
            cursor.execute('''
                INSERT INTO produtos (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', produto)
        
        # Adicionar alguns clientes de exemplo
        clientes_exemplo = [
            ('João Silva', '(11) 99999-9999', 'joao@email.com', '123.456.789-00', 'Rua das Flores, 123'),
            ('Maria Santos', '(11) 88888-8888', 'maria@email.com', '987.654.321-00', 'Av. Principal, 456'),
            ('Pedro Oliveira', '(11) 77777-7777', 'pedro@email.com', '456.789.123-00', 'Rua do Comércio, 789'),
        ]
        
        for cliente in clientes_exemplo:
            cursor.execute('''
                INSERT INTO clientes (nome, telefone, email, cpf_cnpj, endereco)
                VALUES (?, ?, ?, ?, ?)
            ''', cliente)
        
        # Adicionar fornecedores de exemplo
        fornecedores_exemplo = [
            ('NGK Brasil Ltda', '12.345.678/0001-90', '(11) 3456-7890', 'vendas@ngk.com.br', 
             'Rua Industrial, 1000', 'São Paulo', 'SP', '01234-567', 'Carlos Silva', 'Especialista em velas e cabos de ignição'),
            ('Bosch Sistemas Automotivos', '23.456.789/0001-01', '(11) 4567-8901', 'comercial@bosch.com.br',
             'Av. Robert Bosch, 500', 'Campinas', 'SP', '13065-900', 'Ana Santos', 'Líder mundial em tecnologia automotiva'),
            ('Mahle Brasil', '34.567.890/0001-12', '(11) 5678-9012', 'atendimento@mahle.com.br',
             'Rua Mahle, 200', 'Jundiaí', 'SP', '13213-105', 'Roberto Costa', 'Especialista em filtros e componentes'),
            ('Cofap Companhia Fabricadora de Peças', '45.678.901/0001-23', '(11) 6789-0123', 'vendas@cofap.com.br',
             'Av. das Indústrias, 300', 'São Bernardo do Campo', 'SP', '09750-700', 'Mariana Oliveira', 'Amortecedores e suspensão'),
            ('Denso do Brasil', '56.789.012/0001-34', '(11) 7890-1234', 'comercial@denso.com.br',
             'Rua Denso, 150', 'São Bernardo do Campo', 'SP', '09823-000', 'Fernando Lima', 'Sistemas de ar condicionado e eletrônicos'),
        ]
        
        for fornecedor in fornecedores_exemplo:
            cursor.execute('''
                INSERT INTO fornecedores (nome, cnpj, telefone, email, endereco, cidade, estado, cep, contato_pessoa, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', fornecedor)
        
        # Verificar se há usuário para as vendas
        cursor.execute("SELECT id FROM usuarios WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            admin_id = admin_user[0]
            
            # Adicionar algumas vendas de exemplo
            from datetime import datetime, timedelta
            import random
            
            # Vendas dos últimos 30 dias
            for i in range(20):
                data_venda = datetime.now() - timedelta(days=random.randint(0, 30))
                cliente_id = random.randint(1, 3)
                forma_pagamento = random.choice(['dinheiro', 'cartao_credito', 'cartao_debito', 'pix'])
                
                # Criar venda
                cursor.execute('''
                    INSERT INTO vendas (cliente_id, total, forma_pagamento, data_venda, usuario_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (cliente_id, 0, forma_pagamento, data_venda, admin_id))
                
                venda_id = cursor.lastrowid
                total_venda = 0
                
                # Adicionar 1-3 itens por venda
                num_itens = random.randint(1, 3)
                for j in range(num_itens):
                    produto_id = random.randint(1, 10)
                    quantidade = random.randint(1, 3)
                    
                    # Buscar preço do produto
                    cursor.execute("SELECT preco FROM produtos WHERE id = ?", (produto_id,))
                    preco_result = cursor.fetchone()
                    if preco_result:
                        preco = preco_result[0]
                        subtotal = preco * quantidade
                        
                        cursor.execute('''
                            INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (venda_id, produto_id, quantidade, preco, subtotal))
                        
                        total_venda += subtotal
                
                # Atualizar total da venda
                cursor.execute("UPDATE vendas SET total = ? WHERE id = ?", (total_venda, venda_id))
        
        conn.commit()
        print("Dados de exemplo adicionados com sucesso!")
    
    conn.close()

# FUNÇÕES DE USUÁRIOS
def verificar_usuario(username, password):
    """Verifica se o usuário e senha estão corretos e se o usuário está ativo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash, ativo FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        # Verificar se o usuário está ativo
        if user[2]:  # ativo = True
            return {'id': user[0], 'username': username}
        else:
            # Usuário existe mas está inativo
            return False
    return None

def buscar_usuario_por_id(user_id):
    """Busca um usuário pelo ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, nome_completo, ativo,
               permissao_vendas, permissao_estoque, permissao_clientes,
               permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin,
               permissao_contas_pagar, permissao_contas_receber
        FROM usuarios WHERE id = ?
    ''', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0], 
            'username': user[1], 
            'email': user[2],
            'nome_completo': user[3] or '',
            'ativo': user[4],
            'permissao_vendas': user[5],
            'permissao_estoque': user[6],
            'permissao_clientes': user[7],
            'permissao_financeiro': user[8],
            'permissao_caixa': user[9],
            'permissao_relatorios': user[10],
            'permissao_admin': user[11],
            'permissao_contas_pagar': user[12] if len(user) > 12 else False,
            'permissao_contas_receber': user[13] if len(user) > 13 else False
        }
    return None

def buscar_usuario_por_email(email):
    """Busca um usuário pelo email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, nome_completo, ativo,
               permissao_vendas, permissao_estoque, permissao_clientes,
               permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin
        FROM usuarios WHERE email = ? AND ativo = 1
    ''', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0], 
            'username': user[1], 
            'email': user[2],
            'nome_completo': user[3] or '',
            'ativo': user[4],
            'permissao_vendas': user[5],
            'permissao_estoque': user[6],
            'permissao_clientes': user[7],
            'permissao_financeiro': user[8],
            'permissao_caixa': user[9],
            'permissao_relatorios': user[10],
            'permissao_admin': user[11]
        }
    return None

def atualizar_senha_usuario(user_id, nova_senha):
    """Atualiza a senha de um usuário"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = generate_password_hash(nova_senha)
    cursor.execute('''
        UPDATE usuarios SET password_hash = ? WHERE id = ?
    ''', (password_hash, user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def criar_usuario(username, password, nome_completo, email, permissoes=None, created_by=None):
    """Cria um novo usuário com permissões específicas"""
    if permissoes is None:
        permissoes = {
            'vendas': True,
            'estoque': True,
            'clientes': True,
            'financeiro': False,
            'caixa': False,
            'relatorios': False,
            'admin': False,
            'contas_pagar': False,
            'contas_receber': False
        }
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se username já existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            return False, "Nome de usuário já existe"
        
        # Verificar se email já existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone()[0] > 0:
            return False, "Email já está em uso"
        
        password_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO usuarios (
                username, password_hash, nome_completo, email,
                permissao_vendas, permissao_estoque, permissao_clientes,
                permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin,
                permissao_contas_pagar, permissao_contas_receber, created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username, password_hash, nome_completo, email,
            permissoes.get('vendas', True),
            permissoes.get('estoque', True),
            permissoes.get('clientes', True),
            permissoes.get('financeiro', False),
            permissoes.get('caixa', False),
            permissoes.get('relatorios', False),
            permissoes.get('admin', False),
            permissoes.get('contas_pagar', False),
            permissoes.get('contas_receber', False),
            created_by
        ))
        
        conn.commit()
        return True, "Usuário criado com sucesso"
        
    except Exception as e:
        return False, f"Erro ao criar usuário: {str(e)}"
    finally:
        conn.close()

def listar_usuarios():
    """Lista todos os usuários do sistema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, nome_completo, email, ativo,
               permissao_vendas, permissao_estoque, permissao_clientes,
               permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin,
               permissao_contas_pagar, permissao_contas_receber, created_at
        FROM usuarios
        ORDER BY nome_completo
    ''')
    
    usuarios = []
    for row in cursor.fetchall():
        usuarios.append({
            'id': row[0],
            'username': row[1],
            'nome_completo': row[2] or '',
            'email': row[3],
            'ativo': row[4],
            'permissao_vendas': row[5],
            'permissao_estoque': row[6],
            'permissao_clientes': row[7],
            'permissao_financeiro': row[8],
            'permissao_caixa': row[9],
            'permissao_relatorios': row[10],
            'permissao_admin': row[11],
            'permissao_contas_pagar': row[12] if len(row) > 12 else False,
            'permissao_contas_receber': row[13] if len(row) > 13 else False,
            'created_at': row[14] if len(row) > 14 else row[12]
        })
    
    conn.close()
    return usuarios

def editar_usuario(user_id, nome_completo=None, email=None, permissoes=None, ativo=None):
    """Edita um usuário existente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Construir query de update dinamicamente
        updates = []
        params = []
        
        if nome_completo is not None:
            updates.append("nome_completo = ?")
            params.append(nome_completo)
        
        if email is not None:
            # Verificar se email já existe em outro usuário
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone()[0] > 0:
                return False, "Email já está em uso por outro usuário"
            updates.append("email = ?")
            params.append(email)
        
        if ativo is not None:
            updates.append("ativo = ?")
            params.append(ativo)
        
        if permissoes:
            for perm, value in permissoes.items():
                updates.append(f"permissao_{perm} = ?")
                params.append(value)
        
        if not updates:
            return False, "Nenhuma alteração especificada"
        
        params.append(user_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, "Usuário atualizado com sucesso"
        else:
            return False, "Usuário não encontrado"
            
    except Exception as e:
        return False, f"Erro ao editar usuário: {str(e)}"
    finally:
        conn.close()

def deletar_usuario(user_id):
    """Deleta um usuário (marca como inativo)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE usuarios SET ativo = 0 WHERE id = ?", (user_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, "Usuário desativado com sucesso"
        else:
            return False, "Usuário não encontrado"
            
    except Exception as e:
        return False, f"Erro ao desativar usuário: {str(e)}"
    finally:
        conn.close()

def verificar_permissao(user_id, permissao):
    """Verifica se um usuário tem uma permissão específica"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT permissao_{permissao}, permissao_admin FROM usuarios WHERE id = ? AND ativo = 1", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Admin tem todas as permissões
        return result[1] or result[0]
    return False

# FUNÇÕES DE CAIXA
def abrir_caixa(usuario_id, saldo_inicial=0, observacoes=""):
    """Abre uma nova sessão de caixa"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe caixa aberto
        cursor.execute("SELECT COUNT(*) FROM caixa_sessoes WHERE status = 'aberto'")
        if cursor.fetchone()[0] > 0:
            return False, "Já existe um caixa aberto. Feche o caixa atual antes de abrir um novo."
        
        cursor.execute('''
            INSERT INTO caixa_sessoes (
                data_abertura, saldo_inicial, usuario_abertura, observacoes_abertura
            )
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), saldo_inicial, usuario_id, observacoes))
        
        sessao_id = cursor.lastrowid
        conn.commit()
        return True, f"Caixa aberto com sucesso. Sessão: {sessao_id}"
        
    except Exception as e:
        return False, f"Erro ao abrir caixa: {str(e)}"
    finally:
        conn.close()

def fechar_caixa(usuario_id, observacoes=""):
    """Fecha a sessão de caixa atual"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Buscar caixa aberto
        cursor.execute("SELECT id, saldo_inicial FROM caixa_sessoes WHERE status = 'aberto'")
        caixa = cursor.fetchone()
        
        if not caixa:
            return False, "Não há caixa aberto para fechar."
        
        caixa_id, saldo_inicial = caixa
        
        # Calcular totais de entradas e saídas
        cursor.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) as total_entradas,
                COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) as total_saidas
            FROM caixa_movimentacoes 
            WHERE data_movimentacao >= (
                SELECT data_abertura FROM caixa_sessoes WHERE id = ?
            )
        ''', (caixa_id,))
        
        totais = cursor.fetchone()
        total_entradas = totais[0] if totais else 0
        total_saidas = totais[1] if totais else 0
        saldo_final = saldo_inicial + total_entradas - total_saidas
        
        # Fechar caixa
        cursor.execute('''
            UPDATE caixa_sessoes SET 
                data_fechamento = ?, 
                saldo_final = ?, 
                total_entradas = ?, 
                total_saidas = ?, 
                usuario_fechamento = ?,
                observacoes_fechamento = ?,
                status = 'fechado'
            WHERE id = ?
        ''', (datetime.now(), saldo_final, total_entradas, total_saidas, usuario_id, observacoes, caixa_id))
        
        conn.commit()
        return True, f"Caixa fechado com sucesso. Saldo final: R$ {saldo_final:,.2f}"
        
    except Exception as e:
        return False, f"Erro ao fechar caixa: {str(e)}"
    finally:
        conn.close()

def registrar_movimentacao_caixa(tipo, categoria, descricao, valor, usuario_id, venda_id=None, conta_pagar_id=None, conta_receber_id=None, observacoes=""):
    """Registra uma movimentação no caixa"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se há caixa aberto
        cursor.execute("SELECT COUNT(*) FROM caixa_sessoes WHERE status = 'aberto'")
        if cursor.fetchone()[0] == 0:
            return False, "Não há caixa aberto. Abra o caixa antes de registrar movimentações."
        
        cursor.execute('''
            INSERT INTO caixa_movimentacoes (
                tipo, categoria, descricao, valor, usuario_id, 
                venda_id, conta_pagar_id, conta_receber_id, observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tipo, categoria, descricao, valor, usuario_id, venda_id, conta_pagar_id, conta_receber_id, observacoes))
        
        conn.commit()
        return True, "Movimentação registrada com sucesso"
        
    except Exception as e:
        return False, f"Erro ao registrar movimentação: {str(e)}"
    finally:
        conn.close()

def obter_status_caixa():
    """Obtém o status atual do caixa"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, data_abertura, saldo_inicial, usuario_abertura, observacoes_abertura
        FROM caixa_sessoes 
        WHERE status = 'aberto'
        ORDER BY data_abertura DESC
        LIMIT 1
    ''')
    
    caixa_aberto = cursor.fetchone()
    
    if not caixa_aberto:
        conn.close()
        return None
    
    caixa_id, data_abertura, saldo_inicial, usuario_abertura, observacoes = caixa_aberto
    
    # Buscar nome do usuário
    cursor.execute("SELECT nome_completo, username FROM usuarios WHERE id = ?", (usuario_abertura,))
    usuario = cursor.fetchone()
    nome_usuario = usuario[0] if usuario and usuario[0] else usuario[1] if usuario else "Usuário desconhecido"
    
    # Calcular movimentações do dia
    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) as total_entradas,
            COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) as total_saidas,
            COUNT(*) as total_movimentacoes
        FROM caixa_movimentacoes 
        WHERE data_movimentacao >= ?
    ''', (data_abertura,))
    
    movimentacoes = cursor.fetchone()
    total_entradas = movimentacoes[0] if movimentacoes else 0
    total_saidas = movimentacoes[1] if movimentacoes else 0
    total_movimentacoes = movimentacoes[2] if movimentacoes else 0
    saldo_atual = saldo_inicial + total_entradas - total_saidas
    
    conn.close()
    
    return {
        'caixa_id': caixa_id,
        'data_abertura': data_abertura,
        'saldo_inicial': saldo_inicial,
        'saldo_atual': saldo_atual,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'total_movimentacoes': total_movimentacoes,
        'usuario_abertura': nome_usuario,
        'observacoes': observacoes
    }

def listar_movimentacoes_caixa(limit=50):
    """Lista as movimentações do caixa atual"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar data de abertura do caixa atual
    cursor.execute("SELECT data_abertura FROM caixa_sessoes WHERE status = 'aberto' ORDER BY data_abertura DESC LIMIT 1")
    caixa_aberto = cursor.fetchone()
    
    if not caixa_aberto:
        conn.close()
        return []
    
    data_abertura = caixa_aberto[0]
    
    cursor.execute('''
        SELECT cm.*, u.nome_completo, u.username
        FROM caixa_movimentacoes cm
        JOIN usuarios u ON cm.usuario_id = u.id
        WHERE cm.data_movimentacao >= ?
        ORDER BY cm.data_movimentacao DESC
        LIMIT ?
    ''', (data_abertura, limit))
    
    movimentacoes = []
    for row in cursor.fetchall():
        movimentacoes.append({
            'id': row[0],
            'tipo': row[1],
            'categoria': row[2],
            'descricao': row[3],
            'valor': row[4],
            'data_movimentacao': row[5],
            'usuario_id': row[6],
            'venda_id': row[7],
            'conta_pagar_id': row[8],
            'conta_receber_id': row[9],
            'observacoes': row[10],
            'usuario_nome': row[11] if row[11] else row[12]
        })
    
    conn.close()
    return movimentacoes

def criar_lancamento_financeiro(tipo, categoria, descricao, valor, data_lancamento, usuario_id, data_vencimento=None, fornecedor_cliente="", numero_documento="", observacoes="", auto_criar_conta=True):
    """Cria um lançamento financeiro (receita ou despesa) e automaticamente cria a conta correspondente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe lançamento similar para evitar duplicatas
        cursor.execute('''
            SELECT id FROM lancamentos_financeiros 
            WHERE tipo = ? AND descricao = ? AND valor = ? AND data_lancamento = ? AND status = 'pendente'
        ''', (tipo, descricao, valor, data_lancamento))
        
        lancamento_existente = cursor.fetchone()
        if lancamento_existente:
            return False, f"Já existe um lançamento similar pendente (ID: {lancamento_existente[0]})"
        
        # Criar o lançamento financeiro
        cursor.execute('''
            INSERT INTO lancamentos_financeiros (
                tipo, categoria, descricao, valor, data_lancamento, 
                data_vencimento, fornecedor_cliente, numero_documento, usuario_id, observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tipo, categoria, descricao, valor, data_lancamento, data_vencimento, fornecedor_cliente, numero_documento, usuario_id, observacoes))
        
        lancamento_id = cursor.lastrowid
        conn.commit()
        
        # Automaticamente criar conta correspondente se solicitado e há data de vencimento
        if auto_criar_conta and data_vencimento:
            try:
                if tipo == 'despesa':
                    # Buscar fornecedor pelo nome se informado
                    fornecedor_id = None
                    if fornecedor_cliente:
                        cursor.execute('SELECT id FROM fornecedores WHERE nome LIKE ? LIMIT 1', (f'%{fornecedor_cliente}%',))
                        fornecedor_result = cursor.fetchone()
                        if fornecedor_result:
                            fornecedor_id = fornecedor_result[0]
                    
                    # Criar conta a pagar
                    cursor.execute('''
                        INSERT INTO contas_pagar (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, lancamento_financeiro_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, lancamento_id))
                    
                    conta_id = cursor.lastrowid
                    
                    # Atualizar lançamento com referência à conta
                    cursor.execute('''
                        UPDATE lancamentos_financeiros 
                        SET conta_pagar_id = ?
                        WHERE id = ?
                    ''', (conta_id, lancamento_id))
                    
                    conn.commit()
                    return True, f"Lançamento criado (ID: {lancamento_id}) e conta a pagar criada automaticamente (ID: {conta_id})"
                
                elif tipo == 'receita':
                    # Buscar cliente pelo nome se informado
                    cliente_id = None
                    if fornecedor_cliente:
                        cursor.execute('SELECT id FROM clientes WHERE nome LIKE ? LIMIT 1', (f'%{fornecedor_cliente}%',))
                        cliente_result = cursor.fetchone()
                        if cliente_result:
                            cliente_id = cliente_result[0]
                    
                    # Criar conta a receber
                    cursor.execute('''
                        INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, observacoes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (descricao, valor, data_vencimento, cliente_id, observacoes))
                    
                    conta_id = cursor.lastrowid
                    
                    # Atualizar lançamento com referência à conta
                    cursor.execute('''
                        UPDATE lancamentos_financeiros 
                        SET conta_receber_id = ?
                        WHERE id = ?
                    ''', (conta_id, lancamento_id))
                    
                    conn.commit()
                    return True, f"Lançamento criado (ID: {lancamento_id}) e conta a receber criada automaticamente (ID: {conta_id})"
                
            except Exception as e_conta:
                # Se falhar na criação da conta, o lançamento ainda existe
                return True, f"Lançamento criado (ID: {lancamento_id}), mas erro ao criar conta: {str(e_conta)}"
        
        return True, f"Lançamento criado com sucesso (ID: {lancamento_id})"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao criar lançamento: {str(e)}"
    finally:
        conn.close()

def listar_lancamentos_financeiros(tipo=None, status='pendente'):
    """Lista lançamentos financeiros"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT lf.id, lf.tipo, lf.categoria, lf.descricao, lf.valor, 
               lf.data_lancamento, lf.data_vencimento, lf.data_pagamento, 
               lf.status, lf.forma_pagamento, lf.numero_documento, 
               lf.fornecedor_cliente, lf.usuario_id, lf.observacoes,
               lf.conta_pagar_id, lf.conta_receber_id,
               u.nome_completo, u.username
        FROM lancamentos_financeiros lf
        JOIN usuarios u ON lf.usuario_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if tipo:
        query += " AND lf.tipo = ?"
        params.append(tipo)
    
    if status:
        query += " AND lf.status = ?"
        params.append(status)
    
    query += " ORDER BY lf.data_vencimento, lf.data_lancamento"
    
    cursor.execute(query, params)
    
    lancamentos = []
    for row in cursor.fetchall():
        lancamentos.append({
            'id': row[0],
            'tipo': row[1],
            'categoria': row[2],
            'descricao': row[3],
            'valor': row[4],
            'data_lancamento': row[5],
            'data_vencimento': row[6],
            'data_pagamento': row[7],
            'status': row[8],
            'forma_pagamento': row[9],
            'numero_documento': row[10],
            'fornecedor_cliente': row[11],
            'usuario_id': row[12],
            'observacoes': row[13],
            'conta_pagar_id': row[14],
            'conta_receber_id': row[15],
            'usuario_nome': row[16] if row[16] else row[17]
        })
    
    conn.close()
    return lancamentos

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
        SELECT id, nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria, ativo, 
               codigo_fornecedor, preco_custo, margem_lucro, ncm, unidade, foto_url, marca
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
            'ativo': row[8],
            'codigo_fornecedor': row[9],
            'preco_custo': row[10] or 0,
            'margem_lucro': row[11] or 0,
            'ncm': row[12],
            'unidade': row[13] or 'UN',
            'foto_url': row[14],
            'marca': row[15]
        })
    
    conn.close()
    return produtos

def buscar_produto(termo_busca):
    """Busca produto por nome, código de barras, código do fornecedor, marca ou ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, preco, estoque, codigo_barras, codigo_fornecedor, preco_custo, margem_lucro, categoria, marca
        FROM produtos
        WHERE ativo = 1 AND (
            nome LIKE ? OR 
            codigo_barras = ? OR 
            codigo_fornecedor LIKE ? OR
            marca LIKE ? OR
            CAST(id AS TEXT) = ?
        )
        LIMIT 10
    ''', (f'%{termo_busca}%', termo_busca, f'%{termo_busca}%', f'%{termo_busca}%', termo_busca))
    
    produtos = []
    for row in cursor.fetchall():
        produtos.append({
            'id': row[0],
            'nome': row[1],
            'preco': row[2],
            'estoque': row[3],
            'codigo_barras': row[4],
            'codigo_fornecedor': row[5],
            'preco_custo': row[6] or 0,
            'margem_lucro': row[7] or 0,
            'categoria': row[8],
            'marca': row[9]
        })
    
    conn.close()
    return produtos

def obter_produto_por_id(produto_id):
    """Obtém um produto específico pelo ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria, ativo, 
               codigo_fornecedor, preco_custo, margem_lucro, ncm, unidade, foto_url, marca
        FROM produtos
        WHERE id = ? AND ativo = 1
    ''', (produto_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'nome': row[1],
            'preco': row[2],
            'estoque': row[3],
            'estoque_minimo': row[4],
            'codigo_barras': row[5],
            'descricao': row[6],
            'categoria': row[7],
            'ativo': row[8],
            'codigo_fornecedor': row[9],
            'preco_custo': row[10] or 0,
            'margem_lucro': row[11] or 0,
            'ncm': row[12],
            'unidade': row[13] or 'UN',
            'foto_url': row[14],
            'marca': row[15]
        }
    return None

def adicionar_produto(nome, preco, estoque=0, estoque_minimo=5, codigo_barras=None, descricao=None, categoria=None, 
                     codigo_fornecedor=None, preco_custo=0, margem_lucro=0, foto_url=None, marca=None):
    """Adiciona um novo produto"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calcular preço de venda baseado no custo e margem se fornecidos
    # Fórmula: Preço = Custo + (Custo * Margem/100)
    # Exemplo: R$ 20 + (R$ 20 * 100%) = R$ 20 + R$ 20 = R$ 40
    if preco_custo > 0 and margem_lucro > 0:
        preco = preco_custo + (preco_custo * margem_lucro / 100)
    
    cursor.execute('''
        INSERT INTO produtos (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
                            codigo_fornecedor, preco_custo, margem_lucro, foto_url, marca)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
          codigo_fornecedor, preco_custo, margem_lucro, foto_url, marca))
    
    produto_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return produto_id

def editar_produto(id, nome, preco, estoque, estoque_minimo=5, codigo_barras=None, descricao=None, categoria=None,
                  codigo_fornecedor=None, preco_custo=0, margem_lucro=0, foto_url=None, marca=None):
    """Edita um produto existente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calcular preço de venda baseado no custo e margem se fornecidos
    # Fórmula: Preço = Custo + (Custo * Margem/100)
    if preco_custo > 0 and margem_lucro > 0:
        preco = preco_custo + (preco_custo * margem_lucro / 100)
    
    cursor.execute('''
        UPDATE produtos 
        SET nome = ?, preco = ?, estoque = ?, estoque_minimo = ?, 
            codigo_barras = ?, descricao = ?, categoria = ?,
            codigo_fornecedor = ?, preco_custo = ?, margem_lucro = ?, foto_url = ?, marca = ?
        WHERE id = ?
    ''', (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
          codigo_fornecedor, preco_custo, margem_lucro, foto_url, marca, id))
    
    conn.commit()
    conn.close()

def deletar_produto(id):
    """Marca um produto como inativo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def deletar_todos_os_produtos():
    """Marca todos os produtos como inativos - FUNÇÃO DE TESTE"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Marcar todos os produtos como inativos
        cursor.execute("UPDATE produtos SET ativo = 0")
        
        # Contar quantos produtos foram marcados como inativos
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 0")
        total_deletados = cursor.fetchone()[0]
        
        conn.commit()
        print(f"✓ {total_deletados} produtos marcados como inativos")
        return total_deletados
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Erro ao deletar produtos: {e}")
        raise e
    finally:
        conn.close()

def limpar_completamente_produtos():
    """Remove completamente todos os produtos do banco - CUIDADO!"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Deletar primeiro os itens de venda relacionados
        cursor.execute("DELETE FROM itens_venda")
        
        # Deletar todos os produtos
        cursor.execute("DELETE FROM produtos")
        
        # Reset do auto increment
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='produtos'")
        
        conn.commit()
        print("✓ Todos os produtos removidos completamente do banco")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Erro ao limpar produtos: {e}")
        raise e
    finally:
        conn.close()

def atualizar_estoque(produto_id, quantidade):
    """Atualiza o estoque de um produto (diminui)"""
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar estoque antes de processar a venda
        for item in itens:
            cursor.execute('SELECT nome, estoque FROM produtos WHERE id = ?', (item['produto_id'],))
            produto = cursor.fetchone()
            
            if not produto:
                raise Exception(f"Produto com ID {item['produto_id']} não encontrado")
            
            nome_produto, estoque_atual = produto
            if estoque_atual < item['quantidade']:
                raise Exception(f"Estoque insuficiente para {nome_produto}. Disponível: {estoque_atual}, solicitado: {item['quantidade']}")
        
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
            
            # Atualiza o estoque diretamente na mesma transação
            cursor.execute('''
                UPDATE produtos 
                SET estoque = estoque - ? 
                WHERE id = ?
            ''', (item['quantidade'], item['produto_id']))
        
        # Se for venda a prazo, cria conta a receber
        if forma_pagamento == 'prazo':
            cursor.execute('''
                INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, venda_id)
                VALUES (?, ?, DATE('now', '+30 days'), ?, ?)
            ''', (f'Venda #{venda_id}', total, cliente_id, venda_id))
        else:
            # Se não for a prazo, registrar entrada no caixa (se houver caixa aberto)
            try:
                # Verificar se há caixa aberto
                cursor.execute("SELECT COUNT(*) FROM caixa_sessoes WHERE status = 'aberto'")
                if cursor.fetchone()[0] > 0:
                    # Registrar movimentação de entrada no caixa
                    cliente_nome = "Cliente Avulso"
                    if cliente_id:
                        cursor.execute("SELECT nome FROM clientes WHERE id = ?", (cliente_id,))
                        cliente_result = cursor.fetchone()
                        if cliente_result:
                            cliente_nome = cliente_result[0]
                    
                    cursor.execute('''
                        INSERT INTO caixa_movimentacoes (
                            tipo, categoria, descricao, valor, usuario_id, venda_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', ('entrada', 'venda', f'Venda #{venda_id} - {cliente_nome}', total, usuario_id, venda_id))
            except Exception as e:
                # Se der erro no caixa, não afeta a venda
                print(f"Aviso: Não foi possível registrar no caixa: {e}")
        
        conn.commit()
        return venda_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

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

def obter_venda_por_id(venda_id):
    """Obtém os detalhes completos de uma venda específica"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Buscar dados da venda
        cursor.execute('''
            SELECT v.id, v.cliente_id, c.nome as cliente_nome, c.telefone as cliente_telefone,
                   v.total, v.forma_pagamento, v.desconto, v.observacoes, 
                   v.data_venda as created_at, v.usuario_id,
                   u.nome_completo as vendedor_nome
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE v.id = ?
        ''', (venda_id,))
        
        venda_data = cursor.fetchone()
        if not venda_data:
            print(f"Venda {venda_id} não encontrada")
            return None
        
        print(f"Dados da venda {venda_id}: {venda_data}")
        
        # Buscar itens da venda
        cursor.execute('''
            SELECT iv.produto_id, p.nome as produto_nome, p.codigo_fornecedor, 
                   p.codigo_barras, iv.quantidade, iv.preco_unitario, iv.subtotal
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            WHERE iv.venda_id = ?
        ''', (venda_id,))
        
        itens = []
        for item_row in cursor.fetchall():
            itens.append({
                'produto_id': item_row[0],
                'produto_nome': item_row[1],
                'codigo_fornecedor': item_row[2] or '',
                'codigo_barras': item_row[3] or '',
                'quantidade': item_row[4],
                'preco_unitario': float(item_row[5]),
                'subtotal': float(item_row[6])
            })
        
        print(f"Itens da venda {venda_id}: {len(itens)} itens")
        
        # Montar resultado
        venda = {
            'id': venda_data[0],
            'cliente_id': venda_data[1],
            'cliente_nome': venda_data[2] or 'Cliente Avulso',
            'cliente_telefone': venda_data[3] or '',
            'total': float(venda_data[4]),
            'forma_pagamento': venda_data[5] or 'dinheiro',
            'desconto': float(venda_data[6] or 0),
            'observacoes': venda_data[7] or '',
            'created_at': venda_data[8],
            'usuario_id': venda_data[9],
            'valor_pago': float(venda_data[4]),  # Para compatibilidade, usar o total
            'troco': 0,  # Para compatibilidade 
            'vendedor_nome': venda_data[10] or 'Sistema',
            'itens': itens
        }
        
        print(f"Venda {venda_id} processada com sucesso: {venda['total']} reais, {len(venda['itens'])} itens")
        return venda
        
    except Exception as e:
        print(f"Erro ao buscar venda {venda_id}: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()

def limpar_sincronizacoes_incorretas():
    """Remove movimentações de caixa de vendas que não são do dia atual"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        from datetime import date
        hoje = date.today().strftime('%Y-%m-%d')
        
        # Buscar movimentações de vendas que não são de hoje
        cursor.execute('''
            SELECT cm.id, cm.venda_id, v.data_venda, cm.valor
            FROM caixa_movimentacoes cm
            JOIN vendas v ON cm.venda_id = v.id
            WHERE cm.categoria = 'venda'
            AND SUBSTR(v.data_venda, 1, 10) != ?
            AND DATE(cm.data_movimentacao) = ?
        ''', (hoje, hoje))
        
        movimentacoes_incorretas = cursor.fetchall()
        
        print(f"DEBUG LIMPEZA: Encontradas {len(movimentacoes_incorretas)} movimentações incorretas")
        
        # Remover movimentações incorretas
        for mov in movimentacoes_incorretas:
            mov_id, venda_id, data_venda, valor = mov
            data_venda_formatada = data_venda[:10] if data_venda else ''
            print(f"DEBUG LIMPEZA: Removendo mov #{mov_id} - Venda #{venda_id} de {data_venda_formatada} (R$ {valor})")
            
            cursor.execute('DELETE FROM caixa_movimentacoes WHERE id = ?', (mov_id,))
        
        conn.commit()
        return True, f"Removidas {len(movimentacoes_incorretas)} sincronizações incorretas"
        
    except Exception as e:
        print(f"DEBUG LIMPEZA: Erro: {str(e)}")
        return False, f"Erro ao limpar sincronizações: {str(e)}"
    finally:
        conn.close()

def sincronizar_vendas_com_caixa():
    """Sincroniza vendas existentes do dia atual com o caixa (caso não tenham sido registradas)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se há caixa aberto
        cursor.execute("SELECT COUNT(*) FROM caixa_sessoes WHERE status = 'aberto'")
        if cursor.fetchone()[0] == 0:
            conn.close()
            return False, "Não há caixa aberto"
        
        # Usar data específica do dia atual
        from datetime import date
        hoje = date.today().strftime('%Y-%m-%d')
        
        # Buscar vendas especificamente do dia atual que não estão no caixa
        cursor.execute('''
            SELECT v.id, v.cliente_id, v.total, v.forma_pagamento, v.usuario_id, v.data_venda
            FROM vendas v
            WHERE SUBSTR(v.data_venda, 1, 10) = ?
            AND v.forma_pagamento != 'prazo'
            AND NOT EXISTS (
                SELECT 1 FROM caixa_movimentacoes cm 
                WHERE cm.venda_id = v.id
            )
        ''', (hoje,))
        
        vendas_nao_sincronizadas = cursor.fetchall()
        
        print(f"DEBUG SYNC: Sincronizando vendas do dia {hoje}")
        print(f"DEBUG SYNC: Encontradas {len(vendas_nao_sincronizadas)} vendas para sincronizar")
        
        vendas_sincronizadas = 0
        
        for venda in vendas_nao_sincronizadas:
            venda_id, cliente_id, total, forma_pagamento, usuario_id, data_venda = venda
            
            # Verificar novamente se a venda é realmente de hoje
            data_venda_formatada = data_venda[:10] if data_venda else ''
            if data_venda_formatada != hoje:
                print(f"DEBUG SYNC: Venda #{venda_id} ignorada - Data: {data_venda_formatada} ≠ {hoje}")
                continue
            
            # Buscar nome do cliente
            cliente_nome = "Cliente Avulso"
            if cliente_id:
                cursor.execute("SELECT nome FROM clientes WHERE id = ?", (cliente_id,))
                cliente_result = cursor.fetchone()
                if cliente_result:
                    cliente_nome = cliente_result[0]
            
            # Registrar no caixa
            cursor.execute('''
                INSERT INTO caixa_movimentacoes (
                    tipo, categoria, descricao, valor, usuario_id, venda_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('entrada', 'venda', f'Venda #{venda_id} - {cliente_nome}', total, usuario_id, venda_id))
            
            vendas_sincronizadas += 1
            print(f"DEBUG SYNC: ✓ Venda #{venda_id} sincronizada - R$ {total}")
        
        conn.commit()
        print(f"DEBUG SYNC: Total sincronizado: {vendas_sincronizadas} vendas de {hoje}")
        return True, f"Sincronizadas {vendas_sincronizadas} vendas do dia atual"
        
    except Exception as e:
        print(f"DEBUG SYNC: Erro ao sincronizar: {str(e)}")
        return False, f"Erro ao sincronizar: {str(e)}"
    finally:
        conn.close()

def obter_vendas_do_dia():
    """Obtém as vendas do dia atual"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Limpar sincronizações incorretas primeiro
    limpar_sincronizacoes_incorretas()
    
    # Sincronizar vendas do dia atual com o caixa
    sincronizar_vendas_com_caixa()
    
    # Usar data específica do dia atual
    from datetime import date
    hoje = date.today().strftime('%Y-%m-%d')
    
    print(f"DEBUG VENDAS: Buscando vendas para {hoje}")
    
    # Buscar vendas especificamente do dia atual usando SUBSTR para garantir precisão
    cursor.execute('''
        SELECT v.id, c.nome, v.total, v.forma_pagamento, v.data_venda,
               COALESCE(SUM(iv.quantidade), 0) as total_itens,
               u.nome_completo as funcionario_nome, u.username as funcionario_username,
               v.usuario_id
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        LEFT JOIN itens_venda iv ON v.id = iv.venda_id
        LEFT JOIN usuarios u ON v.usuario_id = u.id
        WHERE SUBSTR(v.data_venda, 1, 10) = ?
        GROUP BY v.id, c.nome, v.total, v.forma_pagamento, v.data_venda, u.nome_completo, u.username, v.usuario_id
        ORDER BY v.data_venda DESC
    ''', (hoje,))
    
    vendas_encontradas = cursor.fetchall()
    
    vendas = []
    total_valor = 0
    total_itens = 0
    
    print(f"DEBUG VENDAS: Vendas encontradas para {hoje}:")
    for row in vendas_encontradas:
        # Verificar se a data da venda realmente corresponde ao dia atual
        data_venda = row[4][:10] if row[4] else ''
        
        if data_venda == hoje:
            venda = {
                'id': row[0],
                'cliente': row[1] or 'Cliente Avulso',
                'total': row[2],
                'forma_pagamento': row[3],
                'data_venda': row[4],
                'total_itens': row[5] or 0,
                'funcionario_nome': row[6] or 'Sem funcionário',
                'funcionario_username': row[7] or '',
                'usuario_id': row[8]
            }
            vendas.append(venda)
            total_valor += row[2]
            total_itens += row[5] or 0
            print(f"  ✓ Venda #{row[0]}: R$ {row[2]}, Data: {row[4]}, Itens: {row[5]}, Funcionário: {row[6] or 'N/A'}")
        else:
            print(f"  ✗ Venda #{row[0]} ignorada - Data: {data_venda} ≠ {hoje}")
    
    resultado = {
        'vendas': vendas,
        'total_vendas': len(vendas),
        'valor_total': total_valor,
        'itens_vendidos': total_itens
    }
    
    print(f"DEBUG VENDAS: Resultado final para {hoje}: {resultado}")
    
    conn.close()
    return resultado

# FUNÇÕES DE CONTAS A PAGAR
def listar_contas_pagar_hoje():
    """Lista contas a pagar com vencimento hoje"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT cp.id, cp.descricao, cp.valor, cp.data_vencimento, cp.status, cp.categoria, cp.observacoes,
               f.nome as fornecedor_nome
        FROM contas_pagar cp
        LEFT JOIN fornecedores f ON cp.fornecedor_id = f.id
        WHERE date(cp.data_vencimento) = date('now') AND cp.status = 'pendente'
        ORDER BY cp.valor DESC
    ''')
    
    contas = []
    for row in cursor.fetchall():
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': row[3],
            'status': row[4],
            'categoria': row[5],
            'observacoes': row[6],
            'fornecedor_nome': row[7] or 'Sem fornecedor'
        })
    
    conn.close()
    return contas

def listar_contas_pagar_por_periodo(filtro='todos', data_inicio=None, data_fim=None, status='pendente'):
    """Lista contas a pagar com filtros de período"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    base_query = '''
        SELECT cp.id, cp.descricao, cp.valor, cp.data_vencimento, cp.status, cp.categoria, cp.observacoes,
               f.nome as fornecedor_nome,
               julianday(cp.data_vencimento) - julianday('now') as dias_restantes,
               cp.data_pagamento
        FROM contas_pagar cp
        LEFT JOIN fornecedores f ON cp.fornecedor_id = f.id
        WHERE cp.status = ?
    '''
    
    params = [status]
    
    if filtro == 'hoje':
        base_query += " AND date(cp.data_vencimento) = date('now')"
    elif filtro == 'atrasadas':
        base_query += " AND date(cp.data_vencimento) < date('now')"
    elif filtro == 'futuras':
        base_query += " AND date(cp.data_vencimento) > date('now')"
    elif filtro == 'proximos_7_dias':
        base_query += " AND date(cp.data_vencimento) BETWEEN date('now') AND date('now', '+7 days')"
    elif filtro == 'proximos_30_dias':
        base_query += " AND date(cp.data_vencimento) BETWEEN date('now') AND date('now', '+30 days')"
    elif filtro == 'personalizado' and data_inicio and data_fim:
        base_query += " AND date(cp.data_vencimento) BETWEEN ? AND ?"
        params.extend([data_inicio, data_fim])
    
    base_query += " ORDER BY cp.data_vencimento"
    
    cursor.execute(base_query, params)
    
    contas = []
    for row in cursor.fetchall():
        dias_restantes = int(row[8]) if row[8] else 0
        status_visual = 'danger' if dias_restantes < 0 else ('warning' if dias_restantes <= 7 else 'success')
        
        # Para contas pagas, usar visual de sucesso
        if row[4] == 'pago':
            status_visual = 'success'
        
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': row[3],
            'status': row[4],
            'categoria': row[5],
            'observacoes': row[6],
            'fornecedor_nome': row[7] or 'Sem fornecedor',
            'dias_restantes': dias_restantes,
            'status_visual': status_visual,
            'texto_prazo': f"{abs(dias_restantes)} dias {'em atraso' if dias_restantes < 0 else ('restantes' if dias_restantes > 0 else 'vence hoje')}" if row[4] == 'pendente' else 'Pago',
            'data_pagamento': row[9]
        })
    
    conn.close()
    return contas

def adicionar_conta_pagar(descricao, valor, data_vencimento, categoria=None, observacoes=None, fornecedor_id=None, auto_sincronizar=True):
    """Adiciona uma nova conta a pagar"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe conta similar para evitar duplicatas
        cursor.execute('''
            SELECT id FROM contas_pagar 
            WHERE descricao = ? AND valor = ? AND data_vencimento = ? AND status = 'pendente'
        ''', (descricao, valor, data_vencimento))
        
        conta_existente = cursor.fetchone()
        if conta_existente:
            conn.close()
            return False, f"Já existe uma conta similar pendente (ID: {conta_existente[0]})"
        
        cursor.execute('''
            INSERT INTO contas_pagar (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id))
        
        conta_id = cursor.lastrowid
        conn.commit()
        
        
        conn.close()
        return True, f"Conta a pagar criada com sucesso (ID: {conta_id})"
            
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao criar conta: {str(e)}"

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

def listar_contas_receber_por_periodo(filtro='todos', data_inicio=None, data_fim=None, status='pendente'):
    """Lista contas a receber com filtros de período"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    base_query = '''
        SELECT cr.id, cr.descricao, cr.valor, cr.data_vencimento, cr.status, c.nome,
               julianday(cr.data_vencimento) - julianday('now') as dias_restantes,
               cr.data_recebimento
        FROM contas_receber cr
        LEFT JOIN clientes c ON cr.cliente_id = c.id
        WHERE cr.status = ?
    '''
    
    params = [status]
    
    if filtro == 'hoje':
        base_query += " AND date(cr.data_vencimento) = date('now')"
    elif filtro == 'atrasadas':
        base_query += " AND date(cr.data_vencimento) < date('now')"
    elif filtro == 'futuras':
        base_query += " AND date(cr.data_vencimento) > date('now')"
    elif filtro == 'proximos_7_dias':
        base_query += " AND date(cr.data_vencimento) BETWEEN date('now') AND date('now', '+7 days')"
    elif filtro == 'proximos_30_dias':
        base_query += " AND date(cr.data_vencimento) BETWEEN date('now') AND date('now', '+30 days')"
    elif filtro == 'personalizado' and data_inicio and data_fim:
        base_query += " AND date(cr.data_vencimento) BETWEEN ? AND ?"
        params.extend([data_inicio, data_fim])
    
    base_query += " ORDER BY cr.data_vencimento"
    
    cursor.execute(base_query, params)
    
    contas = []
    for row in cursor.fetchall():
        dias_restantes = int(row[6]) if row[6] else 0
        status_visual = 'danger' if dias_restantes < 0 else ('warning' if dias_restantes <= 7 else 'success')
        
        # Para contas recebidas, usar visual de sucesso
        if row[4] == 'recebido':
            status_visual = 'success'
        
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': row[3],
            'status': row[4],
            'cliente_nome': row[5] or 'Cliente não informado',
            'dias_restantes': dias_restantes,
            'status_visual': status_visual,
            'texto_prazo': f"{abs(dias_restantes)} dias {'em atraso' if dias_restantes < 0 else ('restantes' if dias_restantes > 0 else 'vence hoje')}" if row[4] == 'pendente' else 'Recebido',
            'data_recebimento': row[7]
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

def adicionar_conta_receber(descricao, valor, data_vencimento, cliente_id=None, observacoes=None, auto_sincronizar=True):
    """Adiciona uma nova conta a receber"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe conta similar para evitar duplicatas
        cursor.execute('''
            SELECT id FROM contas_receber 
            WHERE descricao = ? AND valor = ? AND data_vencimento = ? AND status = 'pendente'
        ''', (descricao, valor, data_vencimento))
        
        conta_existente = cursor.fetchone()
        if conta_existente:
            conn.close()
            return False, f"Já existe uma conta similar pendente (ID: {conta_existente[0]})"
        
        cursor.execute('''
            INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, observacoes)
            VALUES (?, ?, ?, ?, ?)
        ''', (descricao, valor, data_vencimento, cliente_id, observacoes))
        
        conta_id = cursor.lastrowid
        conn.commit()
        
        
        conn.close()
        return True, f"Conta a receber criada com sucesso (ID: {conta_id})"
            
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao criar conta: {str(e)}"

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
    
    # Total de fornecedores
    cursor.execute("SELECT COUNT(*) FROM fornecedores WHERE ativo = 1")
    total_fornecedores = cursor.fetchone()[0]
    
    # Valor do estoque
    cursor.execute("SELECT SUM(preco * estoque) FROM produtos WHERE ativo = 1")
    valor_estoque = cursor.fetchone()[0] or 0
    
    # Produtos com estoque baixo
    cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1 AND estoque <= estoque_minimo")
    produtos_estoque_baixo = cursor.fetchone()[0]
    
    # Produtos sem estoque
    cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1 AND estoque <= 0")
    produtos_sem_estoque = cursor.fetchone()[0]
    
    # Vendas do mês
    cursor.execute('''
        SELECT COUNT(*), SUM(total) 
        FROM vendas 
        WHERE strftime('%Y-%m', data_venda) = strftime('%Y-%m', 'now')
    ''')
    vendas_mes = cursor.fetchone()
    
    # Vendas do dia
    cursor.execute('''
        SELECT COUNT(*), SUM(total) 
        FROM vendas 
        WHERE date(data_venda) = date('now')
    ''')
    vendas_dia = cursor.fetchone()
    
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
        'total_fornecedores': total_fornecedores,
        'valor_estoque': valor_estoque,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'produtos_sem_estoque': produtos_sem_estoque,
        'vendas_mes_quantidade': vendas_mes[0] or 0,
        'vendas_mes_valor': vendas_mes[1] or 0,
        'vendas_dia_quantidade': vendas_dia[0] or 0,
        'vendas_dia_valor': vendas_dia[1] or 0,
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

# FUNÇÕES DE ORÇAMENTOS
def gerar_numero_orcamento():
    """Gera um número único para o orçamento"""
    from datetime import datetime
    import random
    agora = datetime.now()
    numero = f"ORC{agora.strftime('%Y%m%d')}{random.randint(1000, 9999)}"
    return numero

def criar_orcamento(itens, cliente_id=None, desconto=0, observacoes="", usuario_id=None):
    """Cria um novo orçamento"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Gerar número do orçamento
        numero_orcamento = gerar_numero_orcamento()
        
        # Calcular total sem desconto
        total_sem_desconto = sum(item['quantidade'] * item['preco_unitario'] for item in itens)
        
        # Calcular desconto em valor (porcentagem sobre o total)
        valor_desconto = total_sem_desconto * (desconto / 100)
        total_com_desconto = total_sem_desconto - valor_desconto
        
        # Inserir orçamento (salvar o total final e a porcentagem de desconto)
        cursor.execute('''
            INSERT INTO orcamentos (numero_orcamento, cliente_id, total, desconto, observacoes, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (numero_orcamento, cliente_id, total_com_desconto, desconto, observacoes, usuario_id))
        
        orcamento_id = cursor.lastrowid
        
        # Inserir itens do orçamento
        for item in itens:
            subtotal = item['quantidade'] * item['preco_unitario']
            cursor.execute('''
                INSERT INTO itens_orcamento (orcamento_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (orcamento_id, item['produto_id'], item['quantidade'], item['preco_unitario'], subtotal))
        
        conn.commit()
        return orcamento_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def listar_orcamentos():
    """Lista todos os orçamentos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT o.id, o.numero_orcamento, o.total, o.status, o.created_at,
               c.nome as cliente_nome
        FROM orcamentos o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        ORDER BY o.created_at DESC
    ''')
    
    orcamentos = []
    for row in cursor.fetchall():
        orcamentos.append({
            'id': row[0],
            'numero_orcamento': row[1],
            'total': row[2],
            'status': row[3],
            'created_at': row[4],
            'cliente_nome': row[5] or 'Cliente não informado'
        })
    
    conn.close()
    return orcamentos

def obter_orcamento(orcamento_id):
    """Obtém um orçamento específico com seus itens"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar orçamento
    cursor.execute('''
        SELECT o.*, c.nome as cliente_nome, c.telefone as cliente_telefone,
               c.email as cliente_email
        FROM orcamentos o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE o.id = ?
    ''', (orcamento_id,))
    
    orcamento_data = cursor.fetchone()
    if not orcamento_data:
        conn.close()
        return None
    
    # Buscar itens do orçamento
    cursor.execute('''
        SELECT io.*, p.nome as produto_nome
        FROM itens_orcamento io
        JOIN produtos p ON io.produto_id = p.id
        WHERE io.orcamento_id = ?
    ''', (orcamento_id,))
    
    itens = []
    for row in cursor.fetchall():
        itens.append({
            'id': row[0],
            'produto_id': row[2],
            'produto_nome': row[6],
            'quantidade': row[3],
            'preco_unitario': row[4],
            'subtotal': row[5]
        })
    
    # Calcular totais para exibição
    subtotal = sum(item['subtotal'] for item in itens)
    desconto_percentual = orcamento_data[4]  # Desconto em porcentagem
    valor_desconto = subtotal * (desconto_percentual / 100) if desconto_percentual > 0 else 0
    
    orcamento = {
        'id': orcamento_data[0],
        'numero_orcamento': orcamento_data[1],
        'cliente_id': orcamento_data[2],
        'total': orcamento_data[3],
        'desconto': orcamento_data[4],  # Porcentagem
        'desconto_valor': valor_desconto,  # Valor calculado
        'subtotal': subtotal,  # Subtotal sem desconto
        'observacoes': orcamento_data[5],
        'status': orcamento_data[6],
        'data_validade': orcamento_data[7],
        'created_at': orcamento_data[8],
        'usuario_id': orcamento_data[9],
        'cliente_nome': orcamento_data[10] or 'Cliente não informado',
        'cliente_telefone': orcamento_data[11] or '',
        'cliente_email': orcamento_data[12] or '',
        'itens': itens
    }
    
    conn.close()
    return orcamento

def atualizar_orcamento(orcamento_id, itens, cliente_id=None, desconto=0, observacoes=""):
    """Atualiza um orçamento existente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se o orçamento existe e está pendente
        cursor.execute('SELECT status FROM orcamentos WHERE id = ?', (orcamento_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            raise Exception("Orçamento não encontrado")
        
        if resultado[0] != 'pendente':
            raise Exception("Apenas orçamentos pendentes podem ser editados")
        
        # Calcular novo total sem desconto
        total_sem_desconto = sum(item['quantidade'] * item['preco_unitario'] for item in itens)
        
        # Calcular desconto em valor (porcentagem sobre o total)
        valor_desconto = total_sem_desconto * (desconto / 100)
        total_com_desconto = total_sem_desconto - valor_desconto
        
        # Atualizar dados principais do orçamento
        cursor.execute('''
            UPDATE orcamentos 
            SET cliente_id = ?, total = ?, desconto = ?, observacoes = ?
            WHERE id = ?
        ''', (cliente_id, total_com_desconto, desconto, observacoes, orcamento_id))
        
        # Remover itens antigos
        cursor.execute('DELETE FROM itens_orcamento WHERE orcamento_id = ?', (orcamento_id,))
        
        # Inserir novos itens
        for item in itens:
            cursor.execute('''
                INSERT INTO itens_orcamento (orcamento_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (orcamento_id, item['produto_id'], item['quantidade'], 
                  item['preco_unitario'], item['quantidade'] * item['preco_unitario']))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def excluir_orcamento(orcamento_id):
    """Exclui um orçamento e seus itens"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se o orçamento existe
        cursor.execute('SELECT status FROM orcamentos WHERE id = ?', (orcamento_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            raise Exception("Orçamento não encontrado")
        
        # Verificar se o orçamento pode ser excluído (apenas pendentes e rejeitados)
        if resultado[0] not in ['pendente', 'rejeitado']:
            raise Exception("Apenas orçamentos pendentes ou rejeitados podem ser excluídos")
        
        # Excluir itens do orçamento primeiro (devido à foreign key)
        cursor.execute('DELETE FROM itens_orcamento WHERE orcamento_id = ?', (orcamento_id,))
        
        # Excluir o orçamento
        cursor.execute('DELETE FROM orcamentos WHERE id = ?', (orcamento_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def converter_orcamento_em_venda(orcamento_id, forma_pagamento):
    """Converte um orçamento aprovado em venda"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Buscar orçamento
        orcamento = obter_orcamento(orcamento_id)
        if not orcamento:
            raise ValueError("Orçamento não encontrado")
        
        # Criar venda
        cursor.execute('''
            INSERT INTO vendas (cliente_id, total, forma_pagamento, desconto, observacoes, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (orcamento['cliente_id'], orcamento['total'], forma_pagamento, 
              orcamento['desconto'], orcamento['observacoes'], orcamento['usuario_id']))
        
        venda_id = cursor.lastrowid
        
        # Copiar itens para venda
        for item in orcamento['itens']:
            cursor.execute('''
                INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (venda_id, item['produto_id'], item['quantidade'], 
                  item['preco_unitario'], item['subtotal']))
            
            # Atualizar estoque
            cursor.execute('''
                UPDATE produtos 
                SET estoque = estoque - ? 
                WHERE id = ?
            ''', (item['quantidade'], item['produto_id']))
        
        # Atualizar status do orçamento
        cursor.execute('''
            UPDATE orcamentos 
            SET status = 'convertido' 
            WHERE id = ?
        ''', (orcamento_id,))
        
        conn.commit()
        return venda_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def mapear_ncm_para_categoria(ncm):
    """Mapeia códigos NCM para categorias de autopeças"""
    if not ncm:
        return "Geral"
    
    # Mapeamento baseado em códigos NCM comuns de autopeças
    mapeamentos = {
        "2710": "Óleos e Lubrificantes",  # Óleos de petróleo
        "3819": "Fluidos de Freio",       # Fluidos para freios hidráulicos
        "4009": "Borrachas",              # Tubos e mangueiras de borracha
        "7318": "Parafusos e Fixadores",  # Parafusos, porcas, rebites
        "8307": "Tubos Flexíveis",        # Tubos flexíveis de metais comuns
        "8409": "Motor",                  # Partes de motores de pistão
        "8411": "Turbo e Compressores",   # Turbojatos, turbopropulsores
        "8412": "Sistema Hidráulico",     # Outros motores e máquinas
        "8413": "Bombas",                 # Bombas para líquidos
        "8414": "Compressores de Ar",     # Bombas de ar, compressores
        "8421": "Filtros",                # Centrifugadoras, filtros
        "8483": "Transmissão",            # Árvores de transmissão
        "8507": "Bateria",                # Acumuladores elétricos
        "8511": "Sistema Elétrico",       # Aparelhos e dispositivos elétricos
        "8708": "Peças Automotivas",      # Partes e acessórios de veículos
        "9401": "Assentos",               # Assentos e suas partes
    }
    
    # Verificar pelos primeiros 4 dígitos do NCM
    ncm_clean = ncm.replace(".", "").replace("-", "")[:4]
    
    for codigo, categoria in mapeamentos.items():
        if ncm_clean.startswith(codigo):
            return categoria
    
    # Categorias por faixa de NCM
    if ncm_clean.startswith("27"):
        return "Combustíveis e Óleos"
    elif ncm_clean.startswith("38"):
        return "Produtos Químicos"
    elif ncm_clean.startswith("40"):
        return "Borrachas e Vedações"
    elif ncm_clean.startswith("73") or ncm_clean.startswith("76"):
        return "Peças Metálicas"
    elif ncm_clean.startswith("84") or ncm_clean.startswith("85"):
        return "Componentes Mecânicos"
    elif ncm_clean.startswith("87"):
        return "Peças Automotivas"
    else:
        return "Geral"

def importar_produtos_de_xml_avancado(conteudo_xml, margem_padrao=100, estoque_minimo=5, usar_preco_nfe=True, acao_existente='atualizar_estoque'):
    """
    Importa produtos de um arquivo XML de NFe com configurações avançadas
    
    Args:
        conteudo_xml: Conteúdo do arquivo XML como string
        margem_padrao: Margem de lucro padrão (%)
        estoque_minimo: Estoque mínimo padrão
        usar_preco_nfe: Se deve usar preço da NFe como custo
        acao_existente: 'atualizar_estoque', 'substituir_dados' ou 'ignorar'
    """
    import xml.etree.ElementTree as ET
    
    produtos_importados = 0
    produtos_atualizados = 0
    produtos_ignorados = 0
    erros = []
    
    try:
        # Parse do XML
        root = ET.fromstring(conteudo_xml)
        
        # Namespace da NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Buscar todos os produtos (det)
        produtos_xml = root.findall('.//nfe:det', ns)
        
        if not produtos_xml:
            raise ValueError("Nenhum produto encontrado no XML")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for det in produtos_xml:
            try:
                # Extrair dados do produto
                prod = det.find('nfe:prod', ns)
                if prod is None:
                    continue
                
                # Dados básicos do produto
                codigo_produto = prod.find('nfe:cProd', ns)
                codigo_produto = codigo_produto.text if codigo_produto is not None else ''
                
                codigo_ean = prod.find('nfe:cEAN', ns)
                codigo_ean = codigo_ean.text if codigo_ean is not None else ''
                if codigo_ean in ['SEM GTIN', '']:
                    codigo_ean = ''
                
                nome_produto = prod.find('nfe:xProd', ns)
                nome_produto = nome_produto.text if nome_produto is not None else ''
                
                valor_unitario = prod.find('nfe:vUnCom', ns)
                valor_unitario = float(valor_unitario.text) if valor_unitario is not None else 0.0
                
                quantidade = prod.find('nfe:qCom', ns)
                quantidade = int(float(quantidade.text)) if quantidade is not None else 0
                
                ncm = prod.find('nfe:NCM', ns)
                ncm = ncm.text if ncm is not None else ''
                
                unidade = prod.find('nfe:uCom', ns)
                unidade = unidade.text if unidade is not None else 'UN'
                
                if not nome_produto:
                    erros.append(f"Produto sem nome encontrado (código: {codigo_produto})")
                    continue
                
                # Calcular preços
                preco_custo = valor_unitario if usar_preco_nfe else 0.0
                preco_venda = preco_custo + (preco_custo * margem_padrao / 100) if preco_custo > 0 else 0.0
                
                # Determinar categoria baseada no NCM
                categoria = obter_categoria_por_ncm_avancado(ncm) if ncm else "Geral"
                
                # Verificar se produto já existe (por código de barras ou código do produto)
                produto_existente = None
                if codigo_ean:
                    cursor.execute('''
                        SELECT id, nome, preco, estoque 
                        FROM produtos 
                        WHERE codigo_barras = ?
                    ''', (codigo_ean,))
                    produto_existente = cursor.fetchone()
                
                if not produto_existente and codigo_produto:
                    cursor.execute('''
                        SELECT id, nome, preco, estoque 
                        FROM produtos 
                        WHERE codigo_fornecedor = ? OR nome LIKE ?
                    ''', (codigo_produto, f'%{codigo_produto}%'))
                    produto_existente = cursor.fetchone()
                
                if produto_existente:
                    if acao_existente == 'ignorar':
                        produtos_ignorados += 1
                        continue
                    elif acao_existente == 'atualizar_estoque':
                        # Atualizar apenas estoque
                        produto_id = produto_existente[0]
                        novo_estoque = produto_existente[3] + quantidade
                        cursor.execute('''
                            UPDATE produtos 
                            SET estoque = ?
                            WHERE id = ?
                        ''', (novo_estoque, produto_id))
                        produtos_atualizados += 1
                        continue
                    elif acao_existente == 'substituir_dados':
                        # Substituir todos os dados
                        produto_id = produto_existente[0]
                        cursor.execute('''
                            UPDATE produtos 
                            SET nome = ?, codigo_fornecedor = ?, codigo_barras = ?, categoria = ?, 
                                preco_custo = ?, preco = ?, estoque = ?, estoque_minimo = ?,
                                unidade = ?, ncm = ?
                            WHERE id = ?
                        ''', (nome_produto, codigo_produto, codigo_ean, categoria, 
                             preco_custo, preco_venda, quantidade, estoque_minimo, 
                             unidade, ncm, produto_id))
                        produtos_atualizados += 1
                        continue
                
                # Inserir novo produto
                cursor.execute('''
                    INSERT INTO produtos (nome, codigo_fornecedor, codigo_barras, categoria, descricao,
                                        preco_custo, preco, estoque, estoque_minimo, unidade, ncm, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nome_produto, codigo_produto, codigo_ean, categoria, 
                     "Importado via NFe XML", preco_custo, preco_venda, 
                     quantidade, estoque_minimo, unidade, ncm, 1))
                
                produtos_importados += 1
                
            except Exception as e:
                erros.append(f"Erro ao processar produto {codigo_produto}: {str(e)}")
                continue
        
        conn.commit()
        conn.close()
        
        return {
            'sucesso': True,
            'produtos_importados': produtos_importados,
            'produtos_atualizados': produtos_atualizados,
            'produtos_ignorados': produtos_ignorados,
            'total_processados': produtos_importados + produtos_atualizados + produtos_ignorados,
            'erros': erros
        }
        
    except ET.ParseError as e:
        return {
            'sucesso': False,
            'erro': f'Erro ao analisar XML: {str(e)}',
            'produtos_importados': 0,
            'produtos_atualizados': 0,
            'produtos_ignorados': 0,
            'erros': [f'XML inválido: {str(e)}']
        }
    except Exception as e:
        return {
            'sucesso': False,
            'erro': f'Erro geral: {str(e)}',
            'produtos_importados': 0,
            'produtos_atualizados': 0,
            'produtos_ignorados': 0,
            'erros': [str(e)]
        }

def obter_categoria_por_ncm_avancado(ncm):
    """
    Determina a categoria do produto baseada no código NCM (versão avançada)
    """
    if not ncm or len(ncm) < 4:
        return "Geral"
    
    # Mapeamento mais abrangente de prefixos NCM para categorias
    categorias_ncm = {
        "8708": "Autopeças",
        "8409": "Motor",
        "8716": "Reboque/Carretinha", 
        "4016": "Borracha",
        "7318": "Parafusos/Fixadores",
        "8536": "Elétrica/Eletrônica",
        "3926": "Plásticos",
        "8544": "Cabos Elétricos",
        "7326": "Metalúrgica",
        "3917": "Tubos/Conexões",
        "8481": "Válvulas",
        "8421": "Filtros",
        "7308": "Estruturas Metálicas",
        "4009": "Mangueiras",
        "8483": "Transmissão",
        "8511": "Sistema Elétrico",
        "8412": "Hidráulica",
        "3403": "Lubrificantes",
        "2710": "Combustíveis",
        "9401": "Assentos",
        "7309": "Reservatórios",
        "8414": "Compressores",
        "8482": "Rolamentos",
        "7616": "Alumínio",
        "8418": "Refrigeração",
        "8525": "Telecomunicações",
        "8703": "Automóveis",
        "8704": "Veículos de Carga"
    }
    
    # Buscar por prefixo de 4 dígitos
    prefixo = ncm[:4]
    categoria = categorias_ncm.get(prefixo)
    
    if categoria:
        return categoria
    
    # Se não encontrou, tentar com 2 dígitos (capítulos mais gerais)
    prefixo_2 = ncm[:2]
    categorias_gerais = {
        "84": "Máquinas/Equipamentos",
        "87": "Veículos",
        "73": "Ferro/Aço", 
        "39": "Plásticos",
        "40": "Borracha",
        "76": "Alumínio",
        "94": "Móveis"
    }
    
    return categorias_gerais.get(prefixo_2, "Geral")

def importar_produtos_de_xml(conteudo_xml):
    """
    Importa produtos de um arquivo XML de NFe (função original mantida para compatibilidade)
    """
    import xml.etree.ElementTree as ET
    
    produtos_importados = []
    produtos_atualizados = []
    erros = []
    
    try:
        # Parse do XML
        root = ET.fromstring(conteudo_xml)
        
        # Namespace da NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Buscar todos os produtos (det)
        produtos_xml = root.findall('.//nfe:det', ns)
        
        if not produtos_xml:
            raise ValueError("Nenhum produto encontrado no XML")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for det in produtos_xml:
            try:
                # Extrair dados do produto
                prod = det.find('nfe:prod', ns)
                if prod is None:
                    continue
                
                # Dados básicos do produto
                codigo_produto = prod.find('nfe:cProd', ns)
                codigo_produto = codigo_produto.text if codigo_produto is not None else ''
                
                codigo_ean = prod.find('nfe:cEAN', ns)
                codigo_ean = codigo_ean.text if codigo_ean is not None else ''
                if codigo_ean in ['SEM GTIN', '']:
                    codigo_ean = ''
                
                nome_produto = prod.find('nfe:xProd', ns)
                nome_produto = nome_produto.text if nome_produto is not None else ''
                
                valor_unitario = prod.find('nfe:vUnCom', ns)
                valor_unitario = float(valor_unitario.text) if valor_unitario is not None else 0.0
                
                quantidade = prod.find('nfe:qCom', ns)
                quantidade = int(float(quantidade.text)) if quantidade is not None else 0
                
                ncm = prod.find('nfe:NCM', ns)
                ncm = ncm.text if ncm is not None else ''
                
                unidade = prod.find('nfe:uCom', ns)
                unidade = unidade.text if unidade is not None else 'UN'
                
                if not nome_produto:
                    erros.append(f"Produto sem nome encontrado (código: {codigo_produto})")
                    continue
                
                # Verificar se produto já existe (por código de barras ou código do produto)
                produto_existente = None
                if codigo_ean:
                    cursor.execute('''
                        SELECT id, nome, preco, estoque 
                        FROM produtos 
                        WHERE codigo_barras = ?
                    ''', (codigo_ean,))
                    produto_existente = cursor.fetchone()
                
                if not produto_existente and codigo_produto:
                    cursor.execute('''
                        SELECT id, nome, preco, estoque 
                        FROM produtos 
                        WHERE codigo_fornecedor = ? OR nome LIKE ?
                    ''', (codigo_produto, f'%{codigo_produto}%'))
                    produto_existente = cursor.fetchone()
                
                if produto_existente:
                    # Atualizar produto existente incluindo categoria
                    produto_id = produto_existente[0]
                    novo_estoque = produto_existente[3] + quantidade
                    categoria = mapear_ncm_para_categoria(ncm)
                    
                    cursor.execute('''
                        UPDATE produtos 
                        SET estoque = ?, preco = ?, ncm = ?, unidade = ?, categoria = ?
                        WHERE id = ?
                    ''', (novo_estoque, valor_unitario, ncm, unidade, categoria, produto_id))
                    
                    produtos_atualizados.append({
                        'id': produto_id,
                        'nome': produto_existente[1],
                        'quantidade_adicionada': quantidade,
                        'novo_estoque': novo_estoque,
                        'preco_atualizado': valor_unitario
                    })
                else:
                    # Criar novo produto com categoria baseada no NCM
                    categoria = mapear_ncm_para_categoria(ncm)
                    
                    cursor.execute('''
                        INSERT INTO produtos (nome, preco, estoque, codigo_barras, ncm, unidade, codigo_fornecedor, categoria)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (nome_produto, valor_unitario, quantidade, codigo_ean, ncm, unidade, codigo_produto, categoria))
                    
                    produto_id = cursor.lastrowid
                    produtos_importados.append({
                        'id': produto_id,
                        'nome': nome_produto,
                        'preco': valor_unitario,
                        'estoque': quantidade,
                        'codigo_barras': codigo_ean,
                        'codigo_fornecedor': codigo_produto,
                        'categoria': categoria
                    })
                
            except Exception as e:
                erros.append(f"Erro ao processar produto {codigo_produto}: {str(e)}")
                continue
        
        conn.commit()
        conn.close()
        
        return {
            'sucesso': True,
            'produtos_importados': produtos_importados,
            'produtos_atualizados': produtos_atualizados,
            'erros': erros,
            'total_processados': len(produtos_xml)
        }
        
    except ET.ParseError as e:
        return {
            'sucesso': False,
            'erro': f'Erro ao analisar XML: {str(e)}',
            'produtos_importados': [],
            'produtos_atualizados': [],
            'erros': [f'XML inválido: {str(e)}']
        }
    except Exception as e:
        return {
            'sucesso': False,
            'erro': f'Erro geral: {str(e)}',
            'produtos_importados': [],
            'produtos_atualizados': [],
            'erros': [str(e)]
        }

# FUNÇÕES DE RELATÓRIOS

def gerar_relatorio_vendas(data_inicio=None, data_fim=None, cliente_id=None):
    """Gera relatório de vendas por período e/ou cliente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Query base
        query = '''
            SELECT 
                v.id,
                v.data_venda,
                c.nome as cliente_nome,
                v.total,
                v.forma_pagamento,
                u.username as vendedor,
                COUNT(vi.id) as quantidade_itens
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            LEFT JOIN itens_venda vi ON v.id = vi.venda_id
            WHERE 1=1
        '''
        
        params = []
        
        # Filtros por data
        if data_inicio:
            query += " AND DATE(v.data_venda) >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND DATE(v.data_venda) <= ?"
            params.append(data_fim)
        if cliente_id:
            query += " AND v.cliente_id = ?"
            params.append(cliente_id)
        
        query += '''
            GROUP BY v.id
            ORDER BY v.data_venda DESC
        '''
        
        cursor.execute(query, params)
        vendas = []
        total_geral = 0
        
        for row in cursor.fetchall():
            venda = {
                'id': row[0],
                'data_venda': row[1],
                'cliente': row[2] or 'Cliente Avulso',
                'total': row[3],
                'forma_pagamento': row[4],
                'vendedor': row[5],
                'quantidade_itens': row[6]
            }
            vendas.append(venda)
            total_geral += row[3]
        
        # Estatísticas resumidas
        cursor.execute('''
            SELECT 
                COUNT(*) as total_vendas,
                SUM(total) as valor_total,
                AVG(total) as ticket_medio,
                forma_pagamento,
                COUNT(*) as quantidade_por_forma
            FROM vendas v
            WHERE 1=1
        ''' + (" AND DATE(v.data_venda) >= ?" if data_inicio else "") +
              (" AND DATE(v.data_venda) <= ?" if data_fim else "") +
              (" AND v.cliente_id = ?" if cliente_id else "") +
              " GROUP BY forma_pagamento", params)
        
        formas_pagamento = cursor.fetchall()
        
        conn.close()
        
        return {
            'vendas': vendas,
            'total_geral': total_geral,
            'quantidade_vendas': len(vendas),
            'ticket_medio': total_geral / len(vendas) if vendas else 0,
            'formas_pagamento': formas_pagamento
        }
        
    except Exception as e:
        conn.close()
        return {'erro': str(e)}

def gerar_relatorio_produtos_mais_vendidos(data_inicio=None, data_fim=None, limit=10):
    """Gera relatório dos produtos mais vendidos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT 
                p.nome,
                p.codigo_barras,
                SUM(vi.quantidade) as total_vendido,
                SUM(vi.subtotal) as valor_total,
                AVG(vi.preco_unitario) as preco_medio,
                COUNT(DISTINCT vi.venda_id) as numero_vendas
            FROM itens_venda vi
            JOIN produtos p ON vi.produto_id = p.id
            JOIN vendas v ON vi.venda_id = v.id
            WHERE 1=1
        '''
        
        params = []
        
        if data_inicio:
            query += " AND DATE(v.data_venda) >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND DATE(v.data_venda) <= ?"
            params.append(data_fim)
        
        query += '''
            GROUP BY p.id, p.nome, p.codigo_barras
            ORDER BY total_vendido DESC
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        produtos = []
        
        for row in cursor.fetchall():
            produto = {
                'nome': row[0],
                'codigo': row[1],
                'quantidade_vendida': row[2],
                'valor_total': row[3],
                'preco_medio': row[4],
                'numero_vendas': row[5]
            }
            produtos.append(produto)
        
        conn.close()
        return {'produtos': produtos}
        
    except Exception as e:
        conn.close()
        return {'erro': str(e)}

def gerar_relatorio_estoque():
    """Gera relatório completo do estoque"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Produtos em estoque
        cursor.execute('''
            SELECT 
                p.nome,
                p.codigo_barras,
                p.estoque,
                p.estoque_minimo,
                p.preco,
                (p.estoque * p.preco) as valor_estoque,
                p.categoria,
                CASE 
                    WHEN p.estoque <= 0 THEN 'Sem Estoque'
                    WHEN p.estoque <= p.estoque_minimo THEN 'Estoque Baixo'
                    ELSE 'Estoque OK'
                END as status_estoque
            FROM produtos p
            WHERE p.ativo = 1
            ORDER BY p.categoria, p.nome
        ''')
        
        produtos = []
        valor_total_estoque = 0
        produtos_sem_estoque = 0
        produtos_estoque_baixo = 0
        
        for row in cursor.fetchall():
            produto = {
                'nome': row[0],
                'codigo': row[1],
                'estoque': row[2],
                'estoque_minimo': row[3],
                'preco': row[4],
                'valor_estoque': row[5],
                'categoria': row[6],
                'status': row[7]
            }
            produtos.append(produto)
            valor_total_estoque += row[5]
            
            if row[2] <= 0:
                produtos_sem_estoque += 1
            elif row[2] <= row[3]:
                produtos_estoque_baixo += 1
        
        # Estatísticas por categoria
        cursor.execute('''
            SELECT 
                categoria,
                COUNT(*) as quantidade_produtos,
                SUM(estoque) as total_estoque,
                SUM(estoque * preco) as valor_categoria
            FROM produtos 
            WHERE ativo = 1
            GROUP BY categoria
            ORDER BY valor_categoria DESC
        ''')
        
        categorias = []
        for row in cursor.fetchall():
            categoria = {
                'nome': row[0],
                'quantidade_produtos': row[1],
                'total_estoque': row[2],
                'valor_categoria': row[3]
            }
            categorias.append(categoria)
        
        conn.close()
        
        return {
            'produtos': produtos,
            'categorias': categorias,
            'resumo': {
                'valor_total_estoque': valor_total_estoque,
                'total_produtos': len(produtos),
                'produtos_sem_estoque': produtos_sem_estoque,
                'produtos_estoque_baixo': produtos_estoque_baixo
            }
        }
        
    except Exception as e:
        conn.close()
        return {'erro': str(e)}

def gerar_relatorio_financeiro(data_inicio=None, data_fim=None):
    """Gera relatório financeiro completo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Vendas por forma de pagamento
        query_vendas = '''
            SELECT 
                forma_pagamento,
                COUNT(*) as quantidade,
                SUM(total) as valor_total
            FROM vendas
            WHERE 1=1
        '''
        
        params = []
        
        if data_inicio:
            query_vendas += " AND DATE(data_venda) >= ?"
            params.append(data_inicio)
        if data_fim:
            query_vendas += " AND DATE(data_venda) <= ?"
            params.append(data_fim)
        
        query_vendas += " GROUP BY forma_pagamento"
        
        cursor.execute(query_vendas, params)
        vendas_forma_pagamento = []
        total_vendas = 0
        
        for row in cursor.fetchall():
            forma = {
                'forma_pagamento': row[0],
                'quantidade': row[1],
                'valor': row[2]
            }
            vendas_forma_pagamento.append(forma)
            total_vendas += row[2]
        
        # Contas a receber
        query_receber = '''
            SELECT 
                status,
                COUNT(*) as quantidade,
                SUM(valor) as valor_total
            FROM contas_receber
            WHERE 1=1
        '''
        
        if data_inicio:
            query_receber += " AND DATE(data_vencimento) >= ?"
        if data_fim:
            query_receber += " AND DATE(data_vencimento) <= ?"
        
        query_receber += " GROUP BY status"
        
        cursor.execute(query_receber, params)
        contas_receber = []
        total_a_receber = 0
        
        for row in cursor.fetchall():
            conta = {
                'status': row[0],
                'quantidade': row[1],
                'valor': row[2]
            }
            contas_receber.append(conta)
            if row[0] == 'pendente':
                total_a_receber += row[2]
        
        # Contas a pagar
        cursor.execute(query_receber.replace('contas_receber', 'contas_pagar'), params)
        contas_pagar = []
        total_a_pagar = 0
        
        for row in cursor.fetchall():
            conta = {
                'status': row[0],
                'quantidade': row[1],
                'valor': row[2]
            }
            contas_pagar.append(conta)
            if row[0] == 'pendente':
                total_a_pagar += row[2]
        
        # Movimentações do caixa
        query_caixa = '''
            SELECT 
                tipo,
                COUNT(*) as quantidade,
                SUM(valor) as valor_total
            FROM caixa_movimentacoes cm
            WHERE 1=1
        '''
        
        if data_inicio:
            query_caixa += " AND DATE(cm.data_movimentacao) >= ?"
        if data_fim:
            query_caixa += " AND DATE(cm.data_movimentacao) <= ?"
        
        query_caixa += " GROUP BY tipo"
        
        cursor.execute(query_caixa, params)
        movimentacoes_caixa = []
        
        for row in cursor.fetchall():
            movimento = {
                'tipo': row[0],
                'quantidade': row[1],
                'valor': row[2]
            }
            movimentacoes_caixa.append(movimento)
        
        conn.close()
        
        return {
            'vendas_forma_pagamento': vendas_forma_pagamento,
            'contas_receber': contas_receber,
            'contas_pagar': contas_pagar,
            'movimentacoes_caixa': movimentacoes_caixa,
            'resumo': {
                'total_vendas': total_vendas,
                'total_a_receber': total_a_receber,
                'total_a_pagar': total_a_pagar,
                'saldo_liquido': total_vendas + total_a_receber - total_a_pagar
            }
        }
        
    except Exception as e:
        conn.close()
        return {'erro': str(e)}

# ========================
# FUNÇÕES DE FORNECEDORES
# ========================

def listar_fornecedores():
    """Lista todos os fornecedores ativos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, nome, cnpj, telefone, email, endereco, cidade, estado, 
                   cep, contato_pessoa, observacoes, ativo, created_at
            FROM fornecedores 
            WHERE ativo = 1
            ORDER BY nome
        ''')
        
        fornecedores = []
        for row in cursor.fetchall():
            fornecedor = {
                'id': row[0],
                'nome': row[1],
                'cnpj': row[2],
                'telefone': row[3],
                'email': row[4],
                'endereco': row[5],
                'cidade': row[6],
                'estado': row[7],
                'cep': row[8],
                'contato_pessoa': row[9],
                'observacoes': row[10],
                'ativo': row[11],
                'created_at': row[12]
            }
            fornecedores.append(fornecedor)
        
        return fornecedores
    except Exception as e:
        print(f"Erro ao listar fornecedores: {e}")
        return []
    finally:
        conn.close()

def buscar_fornecedor(fornecedor_id):
    """Busca um fornecedor específico pelo ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, nome, cnpj, telefone, email, endereco, cidade, estado, 
                   cep, contato_pessoa, observacoes, ativo, created_at
            FROM fornecedores 
            WHERE id = ?
        ''', (fornecedor_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'nome': row[1],
                'cnpj': row[2],
                'telefone': row[3],
                'email': row[4],
                'endereco': row[5],
                'cidade': row[6],
                'estado': row[7],
                'cep': row[8],
                'contato_pessoa': row[9],
                'observacoes': row[10],
                'ativo': row[11],
                'created_at': row[12]
            }
        return None
    except Exception as e:
        print(f"Erro ao buscar fornecedor: {e}")
        return None
    finally:
        conn.close()

def adicionar_fornecedor(nome, cnpj=None, telefone=None, email=None, endereco=None, 
                        cidade=None, estado=None, cep=None, contato_pessoa=None, observacoes=None):
    """Adiciona um novo fornecedor"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO fornecedores (nome, cnpj, telefone, email, endereco, cidade, 
                                    estado, cep, contato_pessoa, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, cnpj, telefone, email, endereco, cidade, estado, cep, contato_pessoa, observacoes))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar fornecedor: {e}")
        return None
    finally:
        conn.close()

def editar_fornecedor(fornecedor_id, nome, cnpj=None, telefone=None, email=None, endereco=None, 
                     cidade=None, estado=None, cep=None, contato_pessoa=None, observacoes=None):
    """Edita um fornecedor existente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE fornecedores 
            SET nome = ?, cnpj = ?, telefone = ?, email = ?, endereco = ?, 
                cidade = ?, estado = ?, cep = ?, contato_pessoa = ?, observacoes = ?
            WHERE id = ?
        ''', (nome, cnpj, telefone, email, endereco, cidade, estado, cep, 
              contato_pessoa, observacoes, fornecedor_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao editar fornecedor: {e}")
        return False
    finally:
        conn.close()

def deletar_fornecedor(fornecedor_id):
    """Deleta (desativa) um fornecedor"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se há produtos vinculados a este fornecedor
        cursor.execute('SELECT COUNT(*) FROM produtos WHERE fornecedor_id = ? AND ativo = 1', (fornecedor_id,))
        produtos_vinculados = cursor.fetchone()[0]
        
        if produtos_vinculados > 0:
            # Se há produtos vinculados, apenas desativar
            cursor.execute('UPDATE fornecedores SET ativo = 0 WHERE id = ?', (fornecedor_id,))
        else:
            # Se não há produtos vinculados, pode deletar fisicamente
            cursor.execute('DELETE FROM fornecedores WHERE id = ?', (fornecedor_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao deletar fornecedor: {e}")
        return False
    finally:
        conn.close()

def obter_fornecedores_para_select():
    """Retorna lista de fornecedores para uso em dropdowns"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, nome 
            FROM fornecedores 
            WHERE ativo = 1 
            ORDER BY nome
        ''')
        
        fornecedores = []
        for row in cursor.fetchall():
            fornecedores.append({
                'id': row[0],
                'nome': row[1]
            })
        
        return fornecedores
    except Exception as e:
        print(f"Erro ao obter fornecedores para select: {e}")
        return []
    finally:
        conn.close()

def contar_fornecedores():
    """Conta o total de fornecedores ativos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM fornecedores WHERE ativo = 1')
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"Erro ao contar fornecedores: {e}")
        return 0
    finally:
        conn.close()

def listar_produtos_por_fornecedor(fornecedor_id):
    """Lista todos os produtos de um fornecedor específico"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT p.id, p.nome, p.preco, p.estoque, p.preco_custo, p.codigo_barras
            FROM produtos p
            WHERE p.fornecedor_id = ? AND p.ativo = 1
            ORDER BY p.nome
        ''', (fornecedor_id,))
        
        produtos = []
        for row in cursor.fetchall():
            produtos.append({
                'id': row[0],
                'nome': row[1],
                'preco': row[2],
                'estoque': row[3],
                'preco_custo': row[4],
                'codigo_barras': row[5]
            })
        
        return produtos
    
    except Exception as e:
        print(f"Erro ao listar produtos por fornecedor: {e}")
        return []
    finally:
        conn.close()

def sincronizar_lancamentos_com_contas(usuario_id):
    """Sincroniza lançamentos financeiros existentes criando as contas correspondentes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    resultado = {"despesas": 0, "receitas": 0, "erros": []}
    
    try:
        # Buscar lançamentos de despesa sem conta a pagar correspondente
        cursor.execute('''
            SELECT id, categoria, descricao, valor, data_vencimento, fornecedor_cliente, observacoes
            FROM lancamentos_financeiros 
            WHERE tipo = 'despesa' AND conta_pagar_id IS NULL AND data_vencimento IS NOT NULL AND status = 'pendente'
        ''')
        
        despesas = cursor.fetchall()
        
        for despesa in despesas:
            lancamento_id, categoria, descricao, valor, data_vencimento, fornecedor_cliente, observacoes = despesa
            
            try:
                # Buscar fornecedor pelo nome se informado
                fornecedor_id = None
                if fornecedor_cliente:
                    cursor.execute('SELECT id FROM fornecedores WHERE nome LIKE ? LIMIT 1', (f'%{fornecedor_cliente}%',))
                    fornecedor_result = cursor.fetchone()
                    if fornecedor_result:
                        fornecedor_id = fornecedor_result[0]
                
                # Criar conta a pagar
                cursor.execute('''
                    INSERT INTO contas_pagar (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, lancamento_financeiro_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, lancamento_id))
                
                conta_id = cursor.lastrowid
                
                # Atualizar lançamento com referência à conta
                cursor.execute('''
                    UPDATE lancamentos_financeiros 
                    SET conta_pagar_id = ?
                    WHERE id = ?
                ''', (conta_id, lancamento_id))
                
                resultado["despesas"] += 1
                
            except Exception as e:
                resultado["erros"].append(f"Erro ao criar conta para lançamento {lancamento_id}: {str(e)}")
        
        # Buscar lançamentos de receita sem conta a receber correspondente
        cursor.execute('''
            SELECT id, categoria, descricao, valor, data_vencimento, fornecedor_cliente, observacoes
            FROM lancamentos_financeiros 
            WHERE tipo = 'receita' AND conta_receber_id IS NULL AND data_vencimento IS NOT NULL AND status = 'pendente'
        ''')
        
        receitas = cursor.fetchall()
        
        for receita in receitas:
            lancamento_id, categoria, descricao, valor, data_vencimento, fornecedor_cliente, observacoes = receita
            
            try:
                # Buscar cliente pelo nome se informado
                cliente_id = None
                if fornecedor_cliente:
                    cursor.execute('SELECT id FROM clientes WHERE nome LIKE ? LIMIT 1', (f'%{fornecedor_cliente}%',))
                    cliente_result = cursor.fetchone()
                    if cliente_result:
                        cliente_id = cliente_result[0]
                
                # Criar conta a receber
                cursor.execute('''
                    INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, observacoes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (descricao, valor, data_vencimento, cliente_id, observacoes))
                
                conta_id = cursor.lastrowid
                
                # Atualizar lançamento com referência à conta
                cursor.execute('''
                    UPDATE lancamentos_financeiros 
                    SET conta_receber_id = ?
                    WHERE id = ?
                ''', (conta_id, lancamento_id))
                
                resultado["receitas"] += 1
                
            except Exception as e:
                resultado["erros"].append(f"Erro ao criar conta para lançamento {lancamento_id}: {str(e)}")
        
        conn.commit()
        return True, resultado
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro geral na sincronização: {str(e)}"
    finally:
        conn.close()

# FUNÇÕES DE CONFIGURAÇÕES DA EMPRESA
def obter_configuracoes_empresa():
    """Obtém as configurações da empresa"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Primeiro, verificar se a tabela existe
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='configuracoes_empresa'
        ''')
        
        if not cursor.fetchone():
            print("Tabela configuracoes_empresa não existe, retornando configurações padrão")
            return obter_configuracoes_padrao()
        
        cursor.execute('''
            SELECT nome_empresa, cnpj, endereco, cidade, estado, cep, 
                   telefone, email, website, logo_path, observacoes
            FROM configuracoes_empresa 
            ORDER BY id DESC 
            LIMIT 1
        ''')
        
        resultado = cursor.fetchone()
        if resultado:
            config = {
                'nome_empresa': resultado[0] or 'FG AUTO PEÇAS',
                'cnpj': resultado[1] or '',
                'endereco': resultado[2] or 'Rua Exemplo, 123 - Centro',
                'cidade': resultado[3] or '',
                'estado': resultado[4] or '',
                'cep': resultado[5] or '',
                'telefone': resultado[6] or '(00) 0000-0000',
                'email': resultado[7] or 'contato@fgautopecas.com.br',
                'website': resultado[8] or '',
                'logo_path': resultado[9] or '',
                'observacoes': resultado[10] or ''
            }
            print(f"Configurações da empresa carregadas: {config['nome_empresa']}")
            return config
        else:
            print("Nenhuma configuração encontrada, retornando configurações padrão")
            return obter_configuracoes_padrao()
            
    except Exception as e:
        print(f"Erro ao buscar configurações da empresa: {e}")
        import traceback
        traceback.print_exc()
        return obter_configuracoes_padrao()
    finally:
        conn.close()

def obter_configuracoes_padrao():
    """Retorna configurações padrão da empresa"""
    return {
        'nome_empresa': 'FG AUTO PEÇAS',
        'cnpj': '',
        'endereco': 'Rua Exemplo, 123 - Centro',
        'cidade': '',
        'estado': '',
        'cep': '',
        'telefone': '(00) 0000-0000',
        'email': 'contato@fgautopecas.com.br',
        'website': '',
        'logo_path': '',
        'observacoes': ''
    }

def atualizar_configuracoes_empresa(dados):
    """Atualiza as configurações da empresa"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe configuração
        cursor.execute("SELECT COUNT(*) FROM configuracoes_empresa")
        existe = cursor.fetchone()[0] > 0
        
        if existe:
            # Atualizar existente
            cursor.execute('''
                UPDATE configuracoes_empresa SET
                    nome_empresa = ?, cnpj = ?, endereco = ?, cidade = ?, 
                    estado = ?, cep = ?, telefone = ?, email = ?, 
                    website = ?, observacoes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM configuracoes_empresa ORDER BY id DESC LIMIT 1)
            ''', (
                dados['nome_empresa'], dados['cnpj'], dados['endereco'],
                dados['cidade'], dados['estado'], dados['cep'],
                dados['telefone'], dados['email'], dados['website'],
                dados['observacoes']
            ))
        else:
            # Inserir nova
            cursor.execute('''
                INSERT INTO configuracoes_empresa (
                    nome_empresa, cnpj, endereco, cidade, estado, cep,
                    telefone, email, website, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados['nome_empresa'], dados['cnpj'], dados['endereco'],
                dados['cidade'], dados['estado'], dados['cep'],
                dados['telefone'], dados['email'], dados['website'],
                dados['observacoes']
            ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Erro ao atualizar configurações da empresa: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Inicialização automática
def editar_lancamento_financeiro_db(lancamento_id, categoria, descricao, valor, data_vencimento=None, fornecedor_cliente="", numero_documento="", observacoes=""):
    """Edita um lançamento financeiro existente"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se o lançamento existe e está pendente
        cursor.execute('SELECT id, status FROM lancamentos_financeiros WHERE id = ?', (lancamento_id,))
        lancamento = cursor.fetchone()
        
        if not lancamento:
            return False, "Lançamento não encontrado"
        
        if lancamento[1] != 'pendente':
            return False, "Só é possível editar lançamentos pendentes"
        
        # Atualizar o lançamento
        cursor.execute('''
            UPDATE lancamentos_financeiros 
            SET categoria = ?, descricao = ?, valor = ?, data_vencimento = ?,
                fornecedor_cliente = ?, numero_documento = ?, observacoes = ?
            WHERE id = ?
        ''', (categoria, descricao, valor, data_vencimento, fornecedor_cliente, numero_documento, observacoes, lancamento_id))
        
        conn.commit()
        return True, f"Lançamento {lancamento_id} editado com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao editar lançamento: {str(e)}"
    finally:
        conn.close()

def alterar_status_lancamento_financeiro(lancamento_id, novo_status, forma_pagamento="", data_pagamento=None):
    """Altera o status de um lançamento financeiro (pago/recebido/cancelado)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se o lançamento existe
        cursor.execute('SELECT id, tipo, status FROM lancamentos_financeiros WHERE id = ?', (lancamento_id,))
        lancamento = cursor.fetchone()
        
        if not lancamento:
            return False, "Lançamento não encontrado"
        
        if lancamento[2] == novo_status:
            return False, f"Lançamento já está com status '{novo_status}'"
        
        # Se não foi fornecida data de pagamento, usar data atual
        if novo_status == 'pago' and not data_pagamento:
            data_pagamento = date.today().isoformat()
        
        # Atualizar o status do lançamento
        cursor.execute('''
            UPDATE lancamentos_financeiros 
            SET status = ?, forma_pagamento = ?, data_pagamento = ?
            WHERE id = ?
        ''', (novo_status, forma_pagamento, data_pagamento, lancamento_id))
        
        conn.commit()
        
        tipo_texto = "receita" if lancamento[1] == 'receita' else "despesa"
        status_texto = "recebida" if lancamento[1] == 'receita' and novo_status == 'pago' else ("paga" if novo_status == 'pago' else novo_status)
        
        return True, f"{tipo_texto.capitalize()} {status_texto} com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao alterar status do lançamento: {str(e)}"
    finally:
        conn.close()

def listar_vendas_por_periodo(data_inicio, data_fim):
    """Lista vendas por período específico com estatísticas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Ajustar datas para incluir o dia completo
        data_inicio_completa = f"{data_inicio} 00:00:00"
        data_fim_completa = f"{data_fim} 23:59:59"
        
        # Buscar vendas do período
        cursor.execute('''
            SELECT v.id, c.nome, v.total, v.forma_pagamento, v.data_venda, v.desconto,
                   (SELECT COUNT(*) FROM itens_venda iv WHERE iv.venda_id = v.id) as total_itens
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            WHERE v.data_venda BETWEEN ? AND ?
            ORDER BY v.data_venda DESC
        ''', (data_inicio_completa, data_fim_completa))
        
        vendas = []
        for row in cursor.fetchall():
            vendas.append({
                'id': row[0],
                'cliente': row[1] or 'Cliente Avulso',
                'total': float(row[2]),
                'forma_pagamento': row[3],
                'data_venda': row[4],
                'desconto': float(row[5]) if row[5] else 0,
                'total_itens': row[6] or 0
            })
        
        return vendas
        
    except Exception as e:
        print(f"Erro ao listar vendas por período: {str(e)}")
        return []
    finally:
        conn.close()

def deletar_lancamento_financeiro_db(lancamento_id):
    """Deleta um lançamento financeiro e suas contas associadas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se o lançamento existe
        cursor.execute('''
            SELECT id, tipo, status, conta_pagar_id, conta_receber_id 
            FROM lancamentos_financeiros 
            WHERE id = ?
        ''', (lancamento_id,))
        lancamento = cursor.fetchone()
        
        if not lancamento:
            return False, "Lançamento não encontrado"
        
        # Não permitir deletar lançamentos já pagos/recebidos
        if lancamento[2] == 'pago':
            return False, "Não é possível deletar lançamentos já pagos/recebidos"
        
        # Deletar contas associadas se existirem
        if lancamento[3]:  # conta_pagar_id
            cursor.execute('DELETE FROM contas_pagar WHERE id = ?', (lancamento[3],))
        
        if lancamento[4]:  # conta_receber_id
            cursor.execute('DELETE FROM contas_receber WHERE id = ?', (lancamento[4],))
        
        # Deletar o lançamento
        cursor.execute('DELETE FROM lancamentos_financeiros WHERE id = ?', (lancamento_id,))
        
        conn.commit()
        tipo_texto = "receita" if lancamento[1] == 'receita' else "despesa"
        return True, f"{tipo_texto.capitalize()} deletada com sucesso"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao deletar lançamento: {str(e)}"
    finally:
        conn.close()

def deletar_venda(venda_id, restaurar_estoque=True):
    """
    Deleta uma venda específica do sistema
    
    Args:
        venda_id (int): ID da venda a ser deletada
        restaurar_estoque (bool): Se True, restaura o estoque dos produtos vendidos
    
    Returns:
        dict: Informações sobre a operação realizada
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        resultado = {
            'success': False,
            'venda_deletada': False,
            'itens_deletados': 0,
            'movimentacoes_caixa_deletadas': 0,
            'contas_receber_deletadas': 0,
            'estoque_restaurado': {},
            'erro': None
        }
        
        # Verificar se a venda existe
        cursor.execute('SELECT id, total, forma_pagamento FROM vendas WHERE id = ?', (venda_id,))
        venda = cursor.fetchone()
        
        if not venda:
            resultado['erro'] = f'Venda #{venda_id} não encontrada'
            return resultado
        
        # Se deve restaurar estoque, primeiro obter todos os itens da venda
        if restaurar_estoque:
            cursor.execute('''
                SELECT iv.produto_id, p.nome, iv.quantidade
                FROM itens_venda iv
                JOIN produtos p ON iv.produto_id = p.id
                WHERE iv.venda_id = ?
            ''', (venda_id,))
            itens_venda = cursor.fetchall()
            
            # Restaurar estoque de cada produto
            for produto_id, nome_produto, quantidade in itens_venda:
                cursor.execute('''
                    UPDATE produtos 
                    SET estoque = estoque + ?
                    WHERE id = ?
                ''', (quantidade, produto_id))
                
                resultado['estoque_restaurado'][nome_produto] = quantidade
        
        # Contar e deletar itens da venda
        cursor.execute('SELECT COUNT(*) FROM itens_venda WHERE venda_id = ?', (venda_id,))
        resultado['itens_deletados'] = cursor.fetchone()[0]
        cursor.execute('DELETE FROM itens_venda WHERE venda_id = ?', (venda_id,))
        
        # Contar e deletar movimentações de caixa relacionadas à venda
        cursor.execute('SELECT COUNT(*) FROM caixa_movimentacoes WHERE venda_id = ?', (venda_id,))
        resultado['movimentacoes_caixa_deletadas'] = cursor.fetchone()[0]
        cursor.execute('DELETE FROM caixa_movimentacoes WHERE venda_id = ?', (venda_id,))
        
        # Contar e deletar contas a receber relacionadas à venda
        cursor.execute('SELECT COUNT(*) FROM contas_receber WHERE venda_id = ?', (venda_id,))
        resultado['contas_receber_deletadas'] = cursor.fetchone()[0]
        cursor.execute('DELETE FROM contas_receber WHERE venda_id = ?', (venda_id,))
        
        # Deletar a venda
        cursor.execute('DELETE FROM vendas WHERE id = ?', (venda_id,))
        
        if cursor.rowcount > 0:
            resultado['venda_deletada'] = True
            resultado['success'] = True
        
        conn.commit()
        return resultado
        
    except Exception as e:
        conn.rollback()
        resultado['erro'] = str(e)
        return resultado
    finally:
        conn.close()

def deletar_todas_vendas(restaurar_estoque=True):
    """
    Deleta todas as vendas do sistema
    
    Args:
        restaurar_estoque (bool): Se True, restaura o estoque dos produtos vendidos
    
    Returns:
        dict: Informações sobre a operação realizada
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        resultado = {
            'vendas_deletadas': 0,
            'itens_deletados': 0,
            'movimentacoes_caixa_deletadas': 0,
            'estoque_restaurado': {},
            'erro': None
        }
        
        # Se deve restaurar estoque, primeiro obter todos os itens vendidos
        if restaurar_estoque:
            cursor.execute('''
                SELECT iv.produto_id, p.nome, SUM(iv.quantidade) as total_vendido
                FROM itens_venda iv
                JOIN produtos p ON iv.produto_id = p.id
                GROUP BY iv.produto_id, p.nome
            ''')
            produtos_vendidos = cursor.fetchall()
            
            # Restaurar estoque
            for produto_id, nome_produto, quantidade_vendida in produtos_vendidos:
                cursor.execute('''
                    UPDATE produtos 
                    SET estoque = estoque + ?
                    WHERE id = ?
                ''', (quantidade_vendida, produto_id))
                
                resultado['estoque_restaurado'][nome_produto] = quantidade_vendida
        
        # Contar registros antes de deletar
        cursor.execute('SELECT COUNT(*) FROM vendas')
        resultado['vendas_deletadas'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM itens_venda')
        resultado['itens_deletados'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM caixa_movimentacoes WHERE venda_id IS NOT NULL')
        resultado['movimentacoes_caixa_deletadas'] = cursor.fetchone()[0]
        
        # Deletar movimentações de caixa relacionadas às vendas
        cursor.execute('DELETE FROM caixa_movimentacoes WHERE venda_id IS NOT NULL')
        
        # Deletar contas a receber relacionadas às vendas
        cursor.execute('DELETE FROM contas_receber WHERE venda_id IS NOT NULL')
        
        # Deletar itens de venda
        cursor.execute('DELETE FROM itens_venda')
        
        # Deletar vendas
        cursor.execute('DELETE FROM vendas')
        
        # Reset dos IDs auto-increment
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('vendas', 'itens_venda')")
        
        conn.commit()
        return resultado
        
    except Exception as e:
        conn.rollback()
        return {
            'vendas_deletadas': 0,
            'itens_deletados': 0,
            'movimentacoes_caixa_deletadas': 0,
            'estoque_restaurado': {},
            'erro': str(e)
        }
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    criar_usuario_admin()
    popular_dados_exemplo()
    print("Banco de dados inicializado com sucesso!")