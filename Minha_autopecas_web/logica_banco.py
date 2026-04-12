# LOGICA DE BANCO DE DADOS - SISTEMA DE AUTOPEÇAS FAMÍLIA
# POSTGRESQL COM NEON
import psycopg2
import psycopg2.extras
import psycopg2.errors
import os
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from math import ceil
import pytz

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# URL de conexão do PostgreSQL Neon
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada! Configure o arquivo .env com suas credenciais do Neon.")

# Configuração do fuso horário brasileiro
TIMEZONE_BR = pytz.timezone('America/Sao_Paulo')
_fiscal_schema_checked = False
_clientes_schema_checked = False
_contas_receber_schema_checked = False

def agora_br():
    """Retorna o datetime atual no horário de Brasília"""
    return datetime.now(TIMEZONE_BR)

def hoje_br():
    """Retorna a data atual no horário de Brasília"""
    return agora_br().date()

def converter_utc_para_br(dt_utc):
    """Converte um datetime em UTC para o timezone de Brasília"""
    if dt_utc is None:
        return None
    
    # Se for um objeto date (sem hora), apenas retornar como string
    if isinstance(dt_utc, date) and not isinstance(dt_utc, datetime):
        return dt_utc
    
    # Se o datetime não tem timezone, assumir que é UTC
    if hasattr(dt_utc, 'tzinfo') and dt_utc.tzinfo is None:
        dt_utc = pytz.utc.localize(dt_utc)
    
    # Converter para timezone de Brasília
    if hasattr(dt_utc, 'astimezone'):
        return dt_utc.astimezone(TIMEZONE_BR)
    
    return dt_utc

def normalizar_cnpj(cnpj):
    """Remove todos os caracteres não numéricos do CNPJ para comparação"""
    if not cnpj:
        return None
    # Remove pontos, barras, hífens e espaços
    import re
    return re.sub(r'[^0-9]', '', str(cnpj))

def get_db_connection():
    """Cria uma conexão com o banco PostgreSQL Neon"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        # PostgreSQL usa autocommit=False por padrão, o que é bom para transações
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

def add_column_if_not_exists(cursor, conn, table_name, column_definition):
    """Adiciona uma coluna em uma tabela se ela não existir"""
    try:
        # Extrair o nome da coluna da definição
        column_name = column_definition.split()[0]
        
        # Verificar se a coluna já existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name=%s AND column_name=%s
        """, (table_name, column_name))
        
        if cursor.fetchone() is None:
            # Coluna não existe, adicionar
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar coluna {column_definition} na tabela {table_name}: {e}")


def garantir_colunas_clientes():
    """Garante colunas opcionais da tabela clientes para compatibilidade com bancos antigos."""
    global _clientes_schema_checked

    if _clientes_schema_checked:
        return True

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        add_column_if_not_exists(cursor, conn, 'clientes', "tipo_pessoa VARCHAR(1) DEFAULT 'F'")
        add_column_if_not_exists(cursor, conn, 'clientes', "razao_social TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "inscricao_estadual TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "rua TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "numero TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "complemento TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "bairro TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "cidade TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "estado VARCHAR(2)")
        add_column_if_not_exists(cursor, conn, 'clientes', "cep TEXT")
        _clientes_schema_checked = True
        return True
    except Exception as e:
        print(f"Erro ao garantir colunas da tabela clientes: {e}")
        return False
    finally:
        conn.close()


def garantir_colunas_contas_receber():
    """Garante colunas da tabela contas_receber usadas nas telas financeiras."""
    global _contas_receber_schema_checked

    if _contas_receber_schema_checked:
        return True

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        add_column_if_not_exists(cursor, conn, 'contas_receber', "status TEXT DEFAULT 'pendente'")
        add_column_if_not_exists(cursor, conn, 'contas_receber', "data_recebimento DATE")
        add_column_if_not_exists(cursor, conn, 'contas_receber', "cliente_id INTEGER")
        add_column_if_not_exists(cursor, conn, 'contas_receber', "observacoes TEXT")
        _contas_receber_schema_checked = True
        return True
    except Exception as e:
        print(f"Erro ao garantir colunas da tabela contas_receber: {e}")
        return False
    finally:
        conn.close()

def init_db():
    """Inicializa o banco de dados criando todas as tabelas necessárias"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de usuários com permissões
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            email TEXT NOT NULL,
            ativo BOOLEAN DEFAULT TRUE,
            permissao_vendas BOOLEAN DEFAULT TRUE,
            permissao_estoque BOOLEAN DEFAULT TRUE,
            permissao_clientes BOOLEAN DEFAULT TRUE,
            permissao_financeiro BOOLEAN DEFAULT FALSE,
            permissao_caixa BOOLEAN DEFAULT FALSE,
            permissao_relatorios BOOLEAN DEFAULT FALSE,
            permissao_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES usuarios (id)
        )
    ''')
    conn.commit()  # Commit da tabela de usuários
    
    # Verificar e adicionar colunas se não existirem (para compatibilidade com DB existente)
    add_column_if_not_exists(cursor, conn, 'usuarios', "nome_completo TEXT DEFAULT ''")
    add_column_if_not_exists(cursor, conn, 'usuarios', "ativo BOOLEAN DEFAULT TRUE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_vendas BOOLEAN DEFAULT TRUE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_estoque BOOLEAN DEFAULT TRUE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_clientes BOOLEAN DEFAULT TRUE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_financeiro BOOLEAN DEFAULT FALSE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_caixa BOOLEAN DEFAULT FALSE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_relatorios BOOLEAN DEFAULT FALSE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_admin BOOLEAN DEFAULT FALSE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "created_by INTEGER")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_contas_pagar BOOLEAN DEFAULT FALSE")
    add_column_if_not_exists(cursor, conn, 'usuarios', "permissao_contas_receber BOOLEAN DEFAULT FALSE")
    
    # Tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            cpf_cnpj TEXT,
            endereco TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()  # Commit da tabela de clientes
    
    # Adicionar colunas para dados de NF-e
    add_column_if_not_exists(cursor, conn, 'clientes', "tipo_pessoa VARCHAR(1) DEFAULT 'F'")
    add_column_if_not_exists(cursor, conn, 'clientes', "razao_social TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "inscricao_estadual TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "rua TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "numero TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "complemento TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "bairro TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "cidade TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "estado VARCHAR(2)")
    add_column_if_not_exists(cursor, conn, 'clientes', "cep TEXT")

    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            preco DECIMAL(10,2) NOT NULL,
            estoque INTEGER DEFAULT 0,
            estoque_minimo INTEGER DEFAULT 1,
            codigo_barras TEXT UNIQUE,
            descricao TEXT,
            categoria TEXT,
            ativo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()  # Commit da tabela de produtos
    
    # Adicionar colunas para dados da NFe e gestão comercial se não existirem
    add_column_if_not_exists(cursor, conn, 'produtos', "ncm TEXT")
    add_column_if_not_exists(cursor, conn, 'produtos', "unidade TEXT DEFAULT 'UN'")
    add_column_if_not_exists(cursor, conn, 'produtos', "codigo_fornecedor TEXT")
    add_column_if_not_exists(cursor, conn, 'produtos', "preco_custo DECIMAL(10,2) DEFAULT 0")
    add_column_if_not_exists(cursor, conn, 'produtos', "margem_lucro DECIMAL(10,2) DEFAULT 0")
    add_column_if_not_exists(cursor, conn, 'produtos', "fornecedor_id INTEGER")
    add_column_if_not_exists(cursor, conn, 'produtos', "foto_url TEXT")
    add_column_if_not_exists(cursor, conn, 'produtos', "marca TEXT")
    
    # Tabela de vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER,
            total DECIMAL(10,2) NOT NULL,
            forma_pagamento TEXT NOT NULL,
            desconto DECIMAL(10,2) DEFAULT 0,
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
            id SERIAL PRIMARY KEY,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario DECIMAL(10,2) NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    # Tabela de contas a pagar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas_pagar (
            id SERIAL PRIMARY KEY,
            descricao TEXT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            data_vencimento DATE NOT NULL,
            data_pagamento DATE,
            status TEXT DEFAULT 'pendente',
            categoria TEXT,
            observacoes TEXT,
            fornecedor_id INTEGER,
            lancamento_financeiro_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de contas a receber
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contas_receber (
            id SERIAL PRIMARY KEY,
            descricao TEXT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
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
            id SERIAL PRIMARY KEY,
            numero_orcamento TEXT UNIQUE NOT NULL,
            cliente_id INTEGER,
            total DECIMAL(10,2) NOT NULL DEFAULT 0,
            desconto DECIMAL(10,2) DEFAULT 0,
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
            id SERIAL PRIMARY KEY,
            orcamento_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario DECIMAL(10,2) NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (orcamento_id) REFERENCES orcamentos (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    # Tabela de caixa - movimentações financeiras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caixa_movimentacoes (
            id SERIAL PRIMARY KEY,
            tipo TEXT NOT NULL, -- 'entrada', 'saida'
            categoria TEXT NOT NULL, -- 'venda', 'conta_paga', 'conta_recebida', 'despesa', 'receita'
            descricao TEXT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER NOT NULL,
            venda_id INTEGER, -- Link com venda se aplicável
            conta_pagar_id INTEGER, -- Link com conta a pagar se aplicável
            conta_receber_id INTEGER, -- Link com conta a receber se aplicável
            observacoes TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (venda_id) REFERENCES vendas (id)
        )
    ''')
    
    # Tabela de abertura/fechamento de caixa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caixa_sessoes (
            id SERIAL PRIMARY KEY,
            data_abertura TIMESTAMP NOT NULL,
            data_fechamento TIMESTAMP,
            saldo_inicial DECIMAL(10,2) NOT NULL DEFAULT 0,
            saldo_final DECIMAL(10,2),
            total_entradas DECIMAL(10,2) DEFAULT 0,
            total_saidas DECIMAL(10,2) DEFAULT 0,
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
            id SERIAL PRIMARY KEY,
            tipo TEXT NOT NULL, -- 'receita', 'despesa'
            categoria TEXT NOT NULL, -- 'combustivel', 'energia', 'telefone', 'aluguel', etc
            descricao TEXT NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
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
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabela de fornecedores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fornecedores (
            id SERIAL PRIMARY KEY,
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
            ativo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de configurações da empresa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes_empresa (
            id SERIAL PRIMARY KEY,
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
            VALUES (%s, %s, %s, %s)
        ''', ('FG AUTO PEÇAS', 'Rua Exemplo, 123 - Centro', '(00) 0000-0000', 'contato@fgautopecas.com.br'))
    
    # Tabela de movimentações de produtos (para aprovação antes de ir ao estoque)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id SERIAL PRIMARY KEY,
            tipo_movimentacao TEXT NOT NULL DEFAULT 'entrada', -- 'entrada', 'saida', 'ajuste'
            origem TEXT NOT NULL DEFAULT 'manual', -- 'manual', 'xml_nfe', 'xml_nfce'
            status TEXT NOT NULL DEFAULT 'pendente', -- 'pendente', 'aprovada', 'cancelada'
            
            -- Dados do produto
            nome TEXT NOT NULL,
            codigo_barras TEXT,
            codigo_fornecedor TEXT,
            descricao TEXT,
            categoria TEXT,
            marca TEXT,
            ncm TEXT,
            unidade TEXT DEFAULT 'UN',
            
            -- Dados financeiros
            quantidade INTEGER NOT NULL DEFAULT 0,
            preco_custo DECIMAL(10,2) DEFAULT 0,
            margem_lucro DECIMAL(10,2) DEFAULT 0,
            preco_venda DECIMAL(10,2) NOT NULL,
            
            -- Estoque
            estoque_minimo INTEGER DEFAULT 1,
            
            -- Relacionamentos
            fornecedor_id INTEGER,
            produto_id INTEGER, -- Referência ao produto caso já exista
            foto_url TEXT,
            
            -- Dados do XML (quando aplicável)
            xml_nfe_chave TEXT,
            xml_nfe_numero TEXT,
            xml_nfe_data DATE,
            xml_produto_codigo TEXT,
            xml_conteudo TEXT, -- Armazenar XML completo se necessário
            
            -- Auditoria
            usuario_criacao INTEGER NOT NULL,
            usuario_aprovacao INTEGER,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_aprovacao TIMESTAMP,
            observacoes TEXT,
            motivo_rejeicao TEXT,
            
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (usuario_criacao) REFERENCES usuarios (id),
            FOREIGN KEY (usuario_aprovacao) REFERENCES usuarios (id)
        )
    ''')
    
    # Adicionar colunas para sincronização financeira se não existirem
    add_column_if_not_exists(cursor, conn, 'contas_pagar', "fornecedor_id INTEGER")
    add_column_if_not_exists(cursor, conn, 'contas_pagar', "lancamento_financeiro_id INTEGER")
    add_column_if_not_exists(cursor, conn, 'lancamentos_financeiros', "conta_pagar_id INTEGER")
    add_column_if_not_exists(cursor, conn, 'lancamentos_financeiros', "conta_receber_id INTEGER")

    # Colunas fiscais para NF-e
    add_column_if_not_exists(cursor, conn, 'clientes', "ie TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "indicador_ie TEXT DEFAULT '9'")
    add_column_if_not_exists(cursor, conn, 'clientes', "tipo_pessoa TEXT DEFAULT 'FISICA'")
    add_column_if_not_exists(cursor, conn, 'clientes', "bairro TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "numero TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "complemento TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "codigo_municipio_ibge TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "estado TEXT")
    add_column_if_not_exists(cursor, conn, 'clientes', "cep TEXT")

    add_column_if_not_exists(cursor, conn, 'produtos', "cest TEXT")
    add_column_if_not_exists(cursor, conn, 'produtos', "cfop TEXT DEFAULT '5102'")
    add_column_if_not_exists(cursor, conn, 'produtos', "origem_mercadoria TEXT DEFAULT '0'")
    add_column_if_not_exists(cursor, conn, 'produtos', "csosn TEXT DEFAULT '102'")
    add_column_if_not_exists(cursor, conn, 'produtos', "cst_icms TEXT")
    add_column_if_not_exists(cursor, conn, 'produtos', "cst_pis TEXT DEFAULT '01'")
    add_column_if_not_exists(cursor, conn, 'produtos', "cst_cofins TEXT DEFAULT '01'")
    add_column_if_not_exists(cursor, conn, 'produtos', "aliquota_icms DECIMAL(5,2) DEFAULT 0")
    add_column_if_not_exists(cursor, conn, 'produtos', "aliquota_pis DECIMAL(5,2) DEFAULT 0")
    add_column_if_not_exists(cursor, conn, 'produtos', "aliquota_cofins DECIMAL(5,2) DEFAULT 0")

    add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "ie TEXT")
    add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "crt TEXT DEFAULT '1'")
    add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "cnae TEXT")
    add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "codigo_municipio_ibge TEXT")
    add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "ambiente_fiscal TEXT DEFAULT 'homologacao'")
    add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "serie_nfe INTEGER DEFAULT 1")

    # Tabelas fiscais de emissao NF-e
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_nfe_numeracao (
            id SERIAL PRIMARY KEY,
            ano INTEGER NOT NULL,
            serie INTEGER NOT NULL DEFAULT 1,
            ultimo_numero INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (ano, serie)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_nfe (
            id SERIAL PRIMARY KEY,
            venda_id INTEGER NOT NULL UNIQUE,
            numero INTEGER NOT NULL,
            serie INTEGER NOT NULL DEFAULT 1,
            modelo TEXT NOT NULL DEFAULT '55',
            ambiente TEXT NOT NULL DEFAULT 'homologacao',
            status TEXT NOT NULL DEFAULT 'rascunho',
            chave_acesso TEXT,
            protocolo_autorizacao TEXT,
            motivo_status TEXT,
            xml_enviado TEXT,
            xml_autorizado TEXT,
            danfe_url TEXT,
            payload_json JSONB,
            response_json JSONB,
            emitida_por INTEGER,
            data_emissao TIMESTAMP,
            data_autorizacao TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (venda_id) REFERENCES vendas (id) ON DELETE CASCADE,
            FOREIGN KEY (emitida_por) REFERENCES usuarios (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_nfe_itens (
            id SERIAL PRIMARY KEY,
            nfe_id INTEGER NOT NULL,
            venda_item_id INTEGER,
            produto_id INTEGER,
            descricao TEXT NOT NULL,
            ncm TEXT,
            cest TEXT,
            cfop TEXT,
            unidade TEXT,
            origem_mercadoria TEXT,
            csosn TEXT,
            cst_icms TEXT,
            cst_pis TEXT,
            cst_cofins TEXT,
            aliquota_icms DECIMAL(5,2) DEFAULT 0,
            aliquota_pis DECIMAL(5,2) DEFAULT 0,
            aliquota_cofins DECIMAL(5,2) DEFAULT 0,
            quantidade DECIMAL(12,4) NOT NULL,
            valor_unitario DECIMAL(12,4) NOT NULL,
            valor_total DECIMAL(12,4) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nfe_id) REFERENCES fiscal_nfe (id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_nfe_eventos (
            id SERIAL PRIMARY KEY,
            nfe_id INTEGER NOT NULL,
            tipo_evento TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'registrado',
            protocolo TEXT,
            justificativa TEXT,
            request_json JSONB,
            response_json JSONB,
            usuario_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nfe_id) REFERENCES fiscal_nfe (id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fiscal_nfe_status ON fiscal_nfe(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fiscal_nfe_venda_id ON fiscal_nfe(venda_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fiscal_nfe_eventos_nfe_id ON fiscal_nfe_eventos(nfe_id)")
    
    conn.commit()
    conn.close()

def criar_usuario_admin():
    """Cria um usuário administrador padrão se não existir"""
    conn = get_db_connection()
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', ('admin', password_hash, 'Administrador do Sistema', 'admin@autopecas.com',
              True, True, True, True, True, True, True))  # Admin tem todas as permissões
        conn.commit()
    else:
        # Atualizar usuário admin existente para ter todas as permissões
        cursor.execute('''
            UPDATE usuarios SET 
                nome_completo = COALESCE(nome_completo, 'Administrador do Sistema'),
                permissao_vendas = TRUE,
                permissao_estoque = TRUE,
                permissao_clientes = TRUE,
                permissao_financeiro = TRUE,
                permissao_caixa = TRUE,
                permissao_relatorios = TRUE,
                permissao_admin = TRUE
            WHERE username = 'admin'
        ''')
        conn.commit()
    
    conn.close()

def popular_dados_exemplo():
    """Popula o banco com dados de exemplo se estiver vazio"""
    conn = get_db_connection()
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
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                VALUES (%s, %s, %s, %s, %s)
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', fornecedor)
        
        # Verificar se há usuário para as vendas
        cursor.execute("SELECT id FROM usuarios WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            admin_id = admin_user[0]
            
            # Adicionar algumas vendas de exemplo
            from datetime import timedelta
            import random
            
            # Vendas dos últimos 30 dias
            for i in range(20):
                data_venda = agora_br() - timedelta(days=random.randint(0, 30))
                cliente_id = random.randint(1, 3)
                forma_pagamento = random.choice(['dinheiro', 'cartao_credito', 'cartao_debito', 'pix'])
                
                # Criar venda
                cursor.execute('''
                    INSERT INTO vendas (cliente_id, total, forma_pagamento, data_venda, usuario_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (cliente_id, 0, forma_pagamento, data_venda, admin_id))
                
                venda_id = cursor.fetchone()[0]
                total_venda = 0
                
                # Adicionar 1-3 itens por venda
                num_itens = random.randint(1, 3)
                for j in range(num_itens):
                    produto_id = random.randint(1, 10)
                    quantidade = random.randint(1, 3)
                    
                    # Buscar preço do produto
                    cursor.execute("SELECT preco FROM produtos WHERE id = %s", (produto_id,))
                    preco_result = cursor.fetchone()
                    if preco_result:
                        preco = preco_result[0]
                        subtotal = preco * quantidade
                        
                        cursor.execute('''
                            INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (venda_id, produto_id, quantidade, preco, subtotal))
                        
                        total_venda += subtotal
                
                # Atualizar total da venda
                cursor.execute("UPDATE vendas SET total = %s WHERE id = %s", (total_venda, venda_id))
        
        conn.commit()
        print("Dados de exemplo adicionados com sucesso!")
    
    conn.close()

# FUNÇÕES DE USUÁRIOS
def verificar_usuario(username, password):
    """Verifica se o usuário e senha estão corretos e se o usuário está ativo"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash, ativo FROM usuarios WHERE username = %s", (username,))
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, nome_completo, ativo,
               permissao_vendas, permissao_estoque, permissao_clientes,
               permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin,
               permissao_contas_pagar, permissao_contas_receber
        FROM usuarios WHERE id = %s
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, nome_completo, ativo,
               permissao_vendas, permissao_estoque, permissao_clientes,
               permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin
        FROM usuarios WHERE email = %s AND ativo = TRUE
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

def validar_senha_segura(senha):
    """
    Valida se a senha atende aos requisitos de segurança:
    - Pelo menos 6 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos um caractere especial
    """
    import re
    
    if len(senha) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres"
    
    if not re.search(r'[A-Z]', senha):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\\/;`~]', senha):
        return False, r"A senha deve conter pelo menos um caractere especial (!@#$%^&*(),.?\":{}|<>_-+=[]\\\/;`~)"
    
    return True, "Senha válida"

def atualizar_senha_usuario(user_id, nova_senha, senha_atual=None):
    """
    Atualiza a senha de um usuário
    Se senha_atual for fornecida, valida antes de atualizar
    """
    # Validar requisitos de segurança da nova senha
    valida, mensagem = validar_senha_segura(nova_senha)
    if not valida:
        return False, mensagem
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Se senha_atual foi fornecida, validar
        if senha_atual is not None:
            cursor.execute('SELECT password_hash FROM usuarios WHERE id = %s', (user_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Usuário não encontrado"
            
            if not check_password_hash(result[0], senha_atual):
                return False, "Senha atual incorreta"
        
        # Atualizar senha
        password_hash = generate_password_hash(nova_senha)
        cursor.execute('''
            UPDATE usuarios SET password_hash = %s WHERE id = %s
        ''', (password_hash, user_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        
        if success:
            return True, "Senha atualizada com sucesso"
        else:
            return False, "Erro ao atualizar senha"
            
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao atualizar senha: {str(e)}"
    finally:
        conn.close()

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
    
    # Validar requisitos de segurança da senha
    valida, mensagem = validar_senha_segura(password)
    if not valida:
        return False, mensagem
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se username já existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s", (username,))
        if cursor.fetchone()[0] > 0:
            return False, "Nome de usuário já existe"
        
        # Verificar se email já existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (email,))
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        conn.rollback()
        return False, f"Erro ao criar usuário: {str(e)}"
    finally:
        conn.close()

def listar_usuarios():
    """Lista todos os usuários do sistema"""
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Construir query de update dinamicamente
        updates = []
        params = []
        
        if nome_completo is not None:
            updates.append("nome_completo = %s")
            params.append(nome_completo)
        
        if email is not None:
            # Verificar se email já existe em outro usuário
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s AND id != %s", (email, user_id))
            if cursor.fetchone()[0] > 0:
                return False, "Email já está em uso por outro usuário"
            updates.append("email = %s")
            params.append(email)
        
        if ativo is not None:
            updates.append("ativo = %s")
            params.append(ativo)
        
        if permissoes:
            for perm, value in permissoes.items():
                updates.append(f"permissao_{perm} = %s")
                params.append(value)
        
        if not updates:
            return False, "Nenhuma alteração especificada"
        
        params.append(user_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
        
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE usuarios SET ativo = FALSE WHERE id = %s", (user_id,))
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT permissao_{permissao}, permissao_admin FROM usuarios WHERE id = %s AND ativo = TRUE", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Admin tem todas as permissões
        return result[1] or result[0]
    return False

# FUNÇÕES DE CAIXA
def abrir_caixa(usuario_id, saldo_inicial=0, observacoes=""):
    """Abre uma nova sessão de caixa"""
    conn = get_db_connection()
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
            VALUES (%s, %s, %s, %s)
            RETURNING id
        ''', (agora_br(), saldo_inicial, usuario_id, observacoes))
        
        sessao_id = cursor.fetchone()[0]
        conn.commit()
        return True, f"Caixa aberto com sucesso. Sessão: {sessao_id}"
        
    except Exception as e:
        return False, f"Erro ao abrir caixa: {str(e)}"
    finally:
        conn.close()

def fechar_caixa(usuario_id, observacoes=""):
    """Fecha a sessão de caixa atual"""
    conn = get_db_connection()
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
                SELECT data_abertura FROM caixa_sessoes WHERE id = %s
            )
        ''', (caixa_id,))
        
        totais = cursor.fetchone()
        total_entradas = totais[0] if totais else 0
        total_saidas = totais[1] if totais else 0
        saldo_final = saldo_inicial + total_entradas - total_saidas
        
        # Fechar caixa
        cursor.execute('''
            UPDATE caixa_sessoes SET 
                data_fechamento = %s, 
                saldo_final = %s, 
                total_entradas = %s, 
                total_saidas = %s, 
                usuario_fechamento = %s,
                observacoes_fechamento = %s,
                status = 'fechado'
            WHERE id = %s
        ''', (agora_br(), saldo_final, total_entradas, total_saidas, usuario_id, observacoes, caixa_id))
        
        conn.commit()
        return True, f"Caixa fechado com sucesso. Saldo final: R$ {saldo_final:,.2f}"
        
    except Exception as e:
        return False, f"Erro ao fechar caixa: {str(e)}"
    finally:
        conn.close()

def registrar_movimentacao_caixa(tipo, categoria, descricao, valor, usuario_id, venda_id=None, conta_pagar_id=None, conta_receber_id=None, observacoes=""):
    """Registra uma movimentação no caixa"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se há caixa aberto
        cursor.execute("SELECT COUNT(*) FROM caixa_sessoes WHERE status = 'aberto'")
        if cursor.fetchone()[0] == 0:
            return False, "Não há caixa aberto. Abra o caixa antes de registrar movimentações."
        
        cursor.execute('''
            INSERT INTO caixa_movimentacoes (
                tipo, categoria, descricao, valor, usuario_id, 
                venda_id, conta_pagar_id, conta_receber_id, observacoes, data_movimentacao
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (tipo, categoria, descricao, valor, usuario_id, venda_id, conta_pagar_id, conta_receber_id, observacoes, agora_br()))
        
        conn.commit()
        return True, "Movimentação registrada com sucesso"
        
    except Exception as e:
        return False, f"Erro ao registrar movimentação: {str(e)}"
    finally:
        conn.close()

def obter_status_caixa():
    """Obtém o status atual do caixa"""
    conn = get_db_connection()
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
    
    # Converter data_abertura de UTC para Brasil
    data_abertura = converter_utc_para_br(data_abertura)
    
    # Buscar nome do usuário
    cursor.execute("SELECT nome_completo, username FROM usuarios WHERE id = %s", (usuario_abertura,))
    usuario = cursor.fetchone()
    nome_usuario = usuario[0] if usuario and usuario[0] else usuario[1] if usuario else "Usuário desconhecido"
    
    # Calcular movimentações do dia
    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) as total_entradas,
            COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) as total_saidas,
            COUNT(*) as total_movimentacoes
        FROM caixa_movimentacoes 
        WHERE data_movimentacao >= %s
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

def caixa_esta_aberto():
    """Verifica se há um caixa aberto no momento"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM caixa_sessoes WHERE status = 'aberto'")
        resultado = cursor.fetchone()
        return resultado[0] > 0 if resultado else False
    finally:
        conn.close()

def listar_movimentacoes_caixa(limit=50):
    """Lista as movimentações do caixa atual"""
    conn = get_db_connection()
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
        WHERE cm.data_movimentacao >= %s
        ORDER BY cm.data_movimentacao DESC
        LIMIT %s
    ''', (data_abertura, limit))
    
    movimentacoes = []
    for row in cursor.fetchall():
        movimentacoes.append({
            'id': row[0],
            'tipo': row[1],
            'categoria': row[2],
            'descricao': row[3],
            'valor': row[4],
            'data_movimentacao': converter_utc_para_br(row[5]),
            'usuario_id': row[6],
            'venda_id': row[7],
            'conta_pagar_id': row[8],
            'conta_receber_id': row[9],
            'observacoes': row[10],
            'usuario_nome': row[11] if row[11] else row[12]
        })
    
    conn.close()
    return movimentacoes

def obter_movimentacoes_caixa(data):
    """Obtém as movimentações do caixa para uma data específica"""
    from datetime import datetime, timedelta
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Converter string de data para objeto datetime
        if isinstance(data, str):
            data_obj = datetime.strptime(data, '%Y-%m-%d')
        else:
            data_obj = data
        
        # Definir início e fim do dia
        data_inicio = data_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        data_fim = data_inicio + timedelta(days=1)
        
        cursor.execute('''
            SELECT cm.*, u.nome_completo, u.username
            FROM caixa_movimentacoes cm
            JOIN usuarios u ON cm.usuario_id = u.id
            WHERE cm.data_movimentacao >= %s AND cm.data_movimentacao < %s
            ORDER BY cm.data_movimentacao DESC
        ''', (data_inicio, data_fim))
        
        movimentacoes = []
        for row in cursor.fetchall():
            movimentacoes.append({
                'id': row[0],
                'tipo': row[1],
                'categoria': row[2],
                'descricao': row[3],
                'valor': row[4],
                'data_movimentacao': converter_utc_para_br(row[5]),
                'usuario_id': row[6],
                'venda_id': row[7],
                'conta_pagar_id': row[8],
                'conta_receber_id': row[9],
                'observacoes': row[10],
                'usuario_nome': row[11] if row[11] else row[12]
            })
        
        return movimentacoes
    except Exception as e:
        print(f"Erro ao obter movimentações do caixa: {e}")
        return []
    finally:
        conn.close()

def criar_lancamento_financeiro(tipo, categoria, descricao, valor, data_lancamento, usuario_id, data_vencimento=None, fornecedor_cliente="", numero_documento="", observacoes="", auto_criar_conta=True):
    """Cria um lançamento financeiro (receita ou despesa) e automaticamente cria a conta correspondente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe lançamento similar para evitar duplicatas
        cursor.execute('''
            SELECT id FROM lancamentos_financeiros 
            WHERE tipo = %s AND descricao = %s AND valor = %s AND data_lancamento = %s AND status = 'pendente'
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (tipo, categoria, descricao, valor, data_lancamento, data_vencimento, fornecedor_cliente, numero_documento, usuario_id, observacoes))
        
        lancamento_id = cursor.fetchone()[0]
        conn.commit()
        
        # Automaticamente criar conta correspondente se solicitado e há data de vencimento
        if auto_criar_conta and data_vencimento:
            try:
                if tipo == 'despesa':
                    # Buscar fornecedor pelo nome se informado
                    fornecedor_id = None
                    if fornecedor_cliente:
                        cursor.execute('SELECT id FROM fornecedores WHERE nome LIKE %s LIMIT 1', (f'%{fornecedor_cliente}%',))
                        fornecedor_result = cursor.fetchone()
                        if fornecedor_result:
                            fornecedor_id = fornecedor_result[0]
                    
                    # Criar conta a pagar
                    cursor.execute('''
                        INSERT INTO contas_pagar (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, lancamento_financeiro_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    ''', (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, lancamento_id))
                    
                    conta_id = cursor.fetchone()[0]
                    
                    # Atualizar lançamento com referência à conta
                    cursor.execute('''
                        UPDATE lancamentos_financeiros 
                        SET conta_pagar_id = %s
                        WHERE id = %s
                    ''', (conta_id, lancamento_id))
                    
                    conn.commit()
                    return True, f"Lançamento criado (ID: {lancamento_id}) e conta a pagar criada automaticamente (ID: {conta_id})"
                
                elif tipo == 'receita':
                    # Buscar cliente pelo nome se informado
                    cliente_id = None
                    if fornecedor_cliente:
                        cursor.execute('SELECT id FROM clientes WHERE nome LIKE %s LIMIT 1', (f'%{fornecedor_cliente}%',))
                        cliente_result = cursor.fetchone()
                        if cliente_result:
                            cliente_id = cliente_result[0]
                    
                    # Criar conta a receber
                    cursor.execute('''
                        INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, observacoes)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    ''', (descricao, valor, data_vencimento, cliente_id, observacoes))
                    
                    conta_id = cursor.fetchone()[0]
                    
                    # Atualizar lançamento com referência à conta
                    cursor.execute('''
                        UPDATE lancamentos_financeiros 
                        SET conta_receber_id = %s
                        WHERE id = %s
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
    conn = get_db_connection()
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
        query += " AND lf.tipo = %s"
        params.append(tipo)
    
    if status:
        query += " AND lf.status = %s"
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
            'data_lancamento': converter_utc_para_br(row[5]),
            'data_vencimento': converter_utc_para_br(row[6]),
            'data_pagamento': converter_utc_para_br(row[7]),
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
    garantir_colunas_clientes()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, telefone, email, cpf_cnpj, endereco,
               COALESCE(tipo_pessoa, 'F') as tipo_pessoa, 
               COALESCE(razao_social, '') as razao_social, 
               COALESCE(inscricao_estadual, '') as inscricao_estadual,
               COALESCE(rua, '') as rua, 
               COALESCE(numero, '') as numero, 
               COALESCE(complemento, '') as complemento,
               COALESCE(bairro, '') as bairro, 
               COALESCE(cidade, '') as cidade, 
               COALESCE(estado, '') as estado, 
               COALESCE(cep, '') as cep
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
            'endereco': row[5],
            'tipo_pessoa': row[6],
            'razao_social': row[7],
            'inscricao_estadual': row[8],
            'rua': row[9],
            'numero': row[10],
            'complemento': row[11],
            'bairro': row[12],
            'cidade': row[13],
            'estado': row[14],
            'cep': row[15]
        })
    
    conn.close()
    return clientes

def adicionar_cliente(nome, telefone=None, email=None, cpf_cnpj=None, endereco=None, 
                     tipo_pessoa='F', razao_social=None, inscricao_estadual=None, 
                     rua=None, numero=None, complemento=None, bairro=None, 
                     cidade=None, estado=None, cep=None):
    """Adiciona um novo cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tentar inserir com todas as colunas
        cursor.execute('''
            INSERT INTO clientes (nome, telefone, email, cpf_cnpj, endereco, tipo_pessoa, 
                                 razao_social, inscricao_estadual, rua, numero, complemento, 
                                 bairro, cidade, estado, cep)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (nome, telefone, email, cpf_cnpj, endereco, tipo_pessoa, razao_social, 
               inscricao_estadual, rua, numero, complemento, bairro, cidade, estado, cep))
    except Exception as e:
        # Se falhar, tentar com apenas as colunas básicas (fallback)
        print(f"Insert com colunas novaspfalhou: {e}")
        cursor.execute('''
            INSERT INTO clientes (nome, telefone, email, cpf_cnpj, endereco)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        ''', (nome, telefone, email, cpf_cnpj, endereco))
    
    cliente_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return cliente_id

def editar_cliente(id, nome, telefone=None, email=None, cpf_cnpj=None, endereco=None, 
                   tipo_pessoa='F', razao_social=None, inscricao_estadual=None, 
                   rua=None, numero=None, complemento=None, bairro=None, 
                   cidade=None, estado=None, cep=None):
    """Edita um cliente existente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tentar atualizar com todas as colunas
        cursor.execute('''
            UPDATE clientes 
            SET nome = %s, telefone = %s, email = %s, cpf_cnpj = %s, endereco = %s, 
                tipo_pessoa = %s, razao_social = %s, inscricao_estadual = %s, 
                rua = %s, numero = %s, complemento = %s, bairro = %s, 
                cidade = %s, estado = %s, cep = %s
            WHERE id = %s
        ''', (nome, telefone, email, cpf_cnpj, endereco, tipo_pessoa, razao_social, 
               inscricao_estadual, rua, numero, complemento, bairro, cidade, estado, cep, id))
    except Exception as e:
        # Se falhar, tentar com apenas as colunas básicas (fallback)
        print(f"Update com colunas novas falhou: {e}")
        cursor.execute('''
            UPDATE clientes 
            SET nome = %s, telefone = %s, email = %s, cpf_cnpj = %s, endereco = %s
            WHERE id = %s
        ''', (nome, telefone, email, cpf_cnpj, endereco, id))
    
    conn.commit()
    conn.close()
    return True

def deletar_cliente(id):
    """Deleta um cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
    conn.commit()
    conn.close()

# FUNÇÕES DE PRODUTOS
def listar_produtos(page=1, per_page=10):
    """Lista produtos ativos com paginação"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Contar o número total de produtos ativos
    cursor.execute('SELECT COUNT(*) FROM produtos WHERE ativo = TRUE')
    total_produtos = cursor.fetchone()[0]
    
    # Calcular o total de páginas
    total_pages = ceil(total_produtos / per_page)
    
    # Calcular o offset
    offset = (page - 1) * per_page
    
    cursor.execute('''
        SELECT id, nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria, ativo, 
               codigo_fornecedor, preco_custo, margem_lucro, ncm, unidade, foto_url, marca, fornecedor_id
        FROM produtos
        WHERE ativo = TRUE
        ORDER BY nome
        LIMIT %s OFFSET %s
    ''', (per_page, offset))
    
    produtos = []
    for row in cursor.fetchall():
        produtos.append({
            'id': row[0],
            'nome': row[1],
            'preco': row[2] if row[2] is not None else 0,
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
            'marca': row[15],
            'fornecedor_id': row[16]
        })
    
    conn.close()
    
    return {'produtos': produtos, 'total_pages': total_pages, 'current_page': page}

def buscar_produto(termo_busca):
    """Busca produto por nome, código de barras, código do fornecedor, marca ou ID
    Suporta busca com múltiplos termos separados por % ou espaço
    Exemplo: 'PIVO%GOL' ou 'PIVO GOL' retorna produtos que contenham ambos os termos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Dividir o termo de busca em múltiplas palavras
    # Substituir % por espaço e dividir
    termo_limpo = termo_busca.replace('%', ' ').strip()
    termos = [t.strip() for t in termo_limpo.split() if t.strip()]
    
    # Se não houver termos, retornar vazio
    if not termos:
        conn.close()
        return []
    
    # Se houver apenas um termo, usar busca simples
    if len(termos) == 1:
        termo = termos[0]
        cursor.execute('''
            SELECT id, nome, preco, estoque, codigo_barras, codigo_fornecedor, preco_custo, margem_lucro, categoria, marca
            FROM produtos
            WHERE ativo = TRUE AND (
                nome ILIKE %s OR 
                codigo_barras = %s OR 
                codigo_fornecedor ILIKE %s OR
                marca ILIKE %s OR
                categoria ILIKE %s OR
                CAST(id AS TEXT) = %s
            )
            ORDER BY 
                CASE 
                    WHEN nome ILIKE %s THEN 1
                    WHEN marca ILIKE %s THEN 2
                    WHEN codigo_barras = %s THEN 3
                    ELSE 4
                END
            LIMIT 50
        ''', (f'%{termo}%', termo, f'%{termo}%', f'%{termo}%', f'%{termo}%', termo,
              f'{termo}%', f'{termo}%', termo))
    else:
        # Busca com múltiplos termos - todos devem estar presentes
        conditions = []
        params = []
        
        for termo in termos:
            # Para cada termo, verificar se está presente em qualquer campo
            conditions.append('''(
                nome ILIKE %s OR 
                codigo_barras ILIKE %s OR 
                codigo_fornecedor ILIKE %s OR
                marca ILIKE %s OR
                categoria ILIKE %s
            )''')
            params.extend([f'%{termo}%', f'%{termo}%', f'%{termo}%', f'%{termo}%', f'%{termo}%'])
        
        # Juntar todas as condições com AND (todos os termos devem estar presentes)
        where_clause = ' AND '.join(conditions)
        
        query = f'''
            SELECT id, nome, preco, estoque, codigo_barras, codigo_fornecedor, preco_custo, margem_lucro, categoria, marca
            FROM produtos
            WHERE ativo = TRUE AND ({where_clause})
            ORDER BY nome
            LIMIT 50
        '''
        
        cursor.execute(query, params)
    
    produtos = []
    for row in cursor.fetchall():
        produtos.append({
            'id': row[0],
            'nome': row[1],
            'preco': row[2] if row[2] is not None else 0,
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria, ativo, 
               codigo_fornecedor, preco_custo, margem_lucro, ncm, unidade, foto_url, marca
        FROM produtos
        WHERE id = %s AND ativo = TRUE
    ''', (produto_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'nome': row[1],
            'preco': row[2] if row[2] is not None else 0,
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

def adicionar_produto(nome, preco, estoque=0, estoque_minimo=1, codigo_barras=None, descricao=None, categoria=None, 
                     codigo_fornecedor=None, preco_custo=0, margem_lucro=0, foto_url=None, marca=None, fornecedor_id=None):
    """Adiciona um novo produto"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calcular preço de venda baseado no custo e margem se fornecidos
    # Fórmula: Preço = Custo + (Custo * Margem/100)
    # Exemplo: R$ 20 + (R$ 20 * 100%) = R$ 20 + R$ 20 = R$ 40
    if preco_custo > 0 and margem_lucro > 0:
        preco = preco_custo + (preco_custo * margem_lucro / 100)
    
    cursor.execute('''
        INSERT INTO produtos (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
                            codigo_fornecedor, preco_custo, margem_lucro, foto_url, marca, fornecedor_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
          codigo_fornecedor, preco_custo, margem_lucro, foto_url, marca, fornecedor_id))
    
    produto_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return produto_id

def editar_produto(id, nome, preco, estoque, estoque_minimo=1, codigo_barras=None, descricao=None, categoria=None,
                  codigo_fornecedor=None, preco_custo=0, margem_lucro=0, foto_url=None, marca=None, fornecedor_id=None):
    """Edita um produto existente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calcular preço de venda baseado no custo e margem se fornecidos
    # Fórmula: Preço = Custo + (Custo * Margem/100)
    if preco_custo > 0 and margem_lucro > 0:
        preco = preco_custo + (preco_custo * margem_lucro / 100)
    
    cursor.execute('''
        UPDATE produtos 
        SET nome = %s, preco = %s, estoque = %s, estoque_minimo = %s, 
            codigo_barras = %s, descricao = %s, categoria = %s,
            codigo_fornecedor = %s, preco_custo = %s, margem_lucro = %s, foto_url = %s, marca = %s,
            fornecedor_id = %s
        WHERE id = %s
    ''', (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
          codigo_fornecedor, preco_custo, margem_lucro, foto_url, marca, fornecedor_id, id))
    
    conn.commit()
    conn.close()
    return True

def deletar_produto(id):
    """Marca um produto como inativo"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE produtos SET ativo = FALSE WHERE id = %s", (id,))
    conn.commit()
    conn.close()

def deletar_todos_os_produtos():
    """Marca todos os produtos como inativos - FUNÇÃO DE TESTE"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Marcar todos os produtos como inativos
        cursor.execute("UPDATE produtos SET ativo = FALSE")
        
        # Contar quantos produtos foram marcados como inativos
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE ativo = FALSE")
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
    conn = get_db_connection()
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
        SET estoque = estoque - %s 
        WHERE id = %s
    ''', (quantidade, produto_id))
    
    conn.commit()
    conn.close()

# FUNÇÕES DE MOVIMENTAÇÕES DE PRODUTOS
def adicionar_movimentacao(nome, preco_venda, quantidade=0, tipo_movimentacao='entrada', origem='manual',
                          estoque_minimo=1, codigo_barras=None, descricao=None, categoria=None,
                          codigo_fornecedor=None, preco_custo=0, margem_lucro=0, foto_url=None,
                          marca=None, fornecedor_id=None, ncm=None, unidade='UN',
                          xml_nfe_chave=None, xml_nfe_numero=None, xml_nfe_data=None,
                          xml_produto_codigo=None, xml_conteudo=None, usuario_id=None, observacoes=None):
    """Adiciona uma nova movimentação e a aprova automaticamente se o produto já existir."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Verificar se o produto já existe (PRIORIDADE: Código do Fornecedor)
        produto_existente_id = None
        if codigo_fornecedor:
            cursor.execute("SELECT id FROM produtos WHERE codigo_fornecedor = %s AND ativo = TRUE", (codigo_fornecedor,))
            result = cursor.fetchone()
            if result:
                produto_existente_id = result[0]

        if not produto_existente_id and codigo_barras:
            cursor.execute("SELECT id FROM produtos WHERE codigo_barras = %s AND ativo = TRUE", (codigo_barras,))
            result = cursor.fetchone()
            if result:
                produto_existente_id = result[0]

        # Determinar o status inicial
        status_inicial = 'aprovada' if produto_existente_id else 'pendente'

        # 2. Calcular a margem de lucro
        if preco_custo and preco_custo > 0 and preco_venda > preco_custo:
            margem_lucro = ((preco_venda - preco_custo) / preco_custo) * 100
        else:
            margem_lucro = 0

        # 3. Inserir a movimentação
        cursor.execute('''
            INSERT INTO movimentacoes (
                tipo_movimentacao, origem, status, nome, codigo_barras, codigo_fornecedor,
                descricao, categoria, marca, ncm, unidade, quantidade, preco_custo,
                margem_lucro, preco_venda, estoque_minimo, fornecedor_id, foto_url,
                xml_nfe_chave, xml_nfe_numero, xml_nfe_data, xml_produto_codigo, xml_conteudo,
                usuario_criacao, observacoes, produto_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (tipo_movimentacao, origem, status_inicial, nome, codigo_barras, codigo_fornecedor,
              descricao, categoria, marca, ncm, unidade, quantidade, preco_custo,
              margem_lucro, preco_venda, estoque_minimo, fornecedor_id, foto_url,
              xml_nfe_chave, xml_nfe_numero, xml_nfe_data, xml_produto_codigo, xml_conteudo,
              usuario_id, observacoes, produto_existente_id))
        
        movimentacao_id = cursor.fetchone()[0]

        # 4. Se o produto já existe, aprovar a movimentação imediatamente
        if status_inicial == 'aprovada':
            print(f"[AUTO-APROVACAO] Movimentação {movimentacao_id} para produto existente ID {produto_existente_id}. Aprovando...")
            # Chamar a lógica de aprovação diretamente
            aprovar_movimentacao(movimentacao_id, usuario_id, conn, cursor)

        conn.commit()
        return movimentacao_id

    except Exception as e:
        conn.rollback()
        print(f"Erro em adicionar_movimentacao: {e}")
        raise
    finally:
        conn.close()

def listar_movimentacoes(status=None, tipo_movimentacao=None):
    """Lista todas as movimentações, opcionalmente filtrando por status e tipo"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    query = '''
        SELECT m.*, 
               f.nome as fornecedor_nome,
               u.nome_completo as usuario_nome,
               ua.nome_completo as usuario_aprovacao_nome
        FROM movimentacoes m
        LEFT JOIN fornecedores f ON m.fornecedor_id = f.id
        LEFT JOIN usuarios u ON m.usuario_criacao = u.id
        LEFT JOIN usuarios ua ON m.usuario_aprovacao = ua.id
        WHERE 1=1
    '''
    params = []
    
    if status:
        query += " AND m.status = %s"
        params.append(status)
    
    if tipo_movimentacao:
        query += " AND m.tipo_movimentacao = %s"
        params.append(tipo_movimentacao)
    
    query += " ORDER BY m.data_criacao DESC"
    
    cursor.execute(query, params)
    movimentacoes = cursor.fetchall()
    conn.close()
    return movimentacoes

def obter_movimentacao_por_id(movimentacao_id):
    """Busca uma movimentação específica por ID"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute('''
        SELECT m.*, 
               f.nome as fornecedor_nome,
               u.nome_completo as usuario_nome
        FROM movimentacoes m
        LEFT JOIN fornecedores f ON m.fornecedor_id = f.id
        LEFT JOIN usuarios u ON m.usuario_criacao = u.id
        WHERE m.id = %s
    ''', (movimentacao_id,))
    
    movimentacao = cursor.fetchone()
    conn.close()
    return movimentacao

def editar_movimentacao(movimentacao_id, nome, preco_venda, quantidade, estoque_minimo=1,
                       codigo_barras=None, descricao=None, categoria=None, codigo_fornecedor=None,
                       preco_custo=0, margem_lucro=0, foto_url=None, marca=None, fornecedor_id=None):
    """Edita uma movimentação pendente"""
    print(f"[DEBUG] Iniciando edição da movimentação ID: {movimentacao_id}")
    print(f"[DEBUG] Dados recebidos: nome={nome}, preco_venda={preco_venda}, preco_custo={preco_custo}, quantidade={quantidade}")
    print(f"[DEBUG] Foto URL recebida: {foto_url}")
    
    # Converter para float para evitar problemas com Decimal
    preco_venda = float(preco_venda) if preco_venda else 0
    preco_custo = float(preco_custo) if preco_custo else 0
    
    # Calcular margem de lucro com base no preço de venda e custo
    if preco_custo and preco_custo > 0 and preco_venda > preco_custo:
        margem_lucro = ((preco_venda - preco_custo) / preco_custo) * 100
        print(f"[DEBUG] Margem calculada automaticamente: {margem_lucro:.2f}%")
    else:
        margem_lucro = 0
        print(f"[DEBUG] Margem definida como 0 (custo inválido ou venda <= custo)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificar se a movimentação está pendente
    cursor.execute('SELECT status, foto_url FROM movimentacoes WHERE id = %s', (movimentacao_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        raise ValueError("Movimentação não encontrada")
    
    if result[0] != 'pendente':
        conn.close()
        raise ValueError("Apenas movimentações pendentes podem ser editadas")
    
    # Se não foi enviada nova foto, manter a existente
    if foto_url is None:
        foto_url = result[1]
        print(f"[DEBUG] Mantendo foto existente: {foto_url}")
    else:
        print(f"[DEBUG] Atualizando para nova foto: {foto_url}")
    
    print(f"[DEBUG] Executando UPDATE na movimentação {movimentacao_id}")
    
    cursor.execute('''
        UPDATE movimentacoes 
        SET nome = %s, preco_venda = %s, quantidade = %s, estoque_minimo = %s,
            codigo_barras = %s, descricao = %s, categoria = %s, codigo_fornecedor = %s,
            preco_custo = %s, margem_lucro = %s, foto_url = %s, marca = %s, fornecedor_id = %s
        WHERE id = %s AND status = 'pendente'
    ''', (nome, preco_venda, quantidade, estoque_minimo, codigo_barras, descricao, categoria,
          codigo_fornecedor, preco_custo, margem_lucro, foto_url, marca, fornecedor_id, movimentacao_id))
    
    linhas_afetadas = cursor.rowcount
    print(f"[DEBUG] Linhas afetadas pelo UPDATE: {linhas_afetadas}")
    
    conn.commit()
    conn.close()
    
    print(f"[DEBUG] Edição concluída com sucesso! Foto final: {foto_url}, Margem final: {margem_lucro:.2f}%")
    return True

def aprovar_movimentacao(movimentacao_id, usuario_id, conn=None, cursor=None):
    """Aprova uma movimentação e cria/atualiza o produto no estoque."""
    # Gerenciar conexão e cursor
    local_conn = False
    if conn is None or cursor is None:
        conn = get_db_connection()
        cursor = conn.cursor()
        local_conn = True

    try:
        # Buscar dados da movimentação
        cursor.execute('SELECT * FROM movimentacoes WHERE id = %s', (movimentacao_id,))
        mov = cursor.fetchone()
        
        if not mov:
            raise ValueError("Movimentação não encontrada")

        # Extrair dados da movimentação (usando índices de coluna)
        mov_id, tipo_mov, origem, status, nome, cod_barras, cod_forn, desc, cat, marca, ncm, unid, qtd, p_custo, m_lucro, p_venda, est_min, forn_id, produto_id_mov, foto, xml_chave, xml_num, xml_data, xml_prod_cod, xml_cont, user_c, user_a, data_c, data_a, obs, motivo_r = mov

        if status != 'pendente' and status != 'aprovada': # Permitir re-aprovação
            raise ValueError(f"Apenas movimentações pendentes ou já aprovadas podem ser processadas. Status atual: {status}")

        # Verificar se produto já existe (PRIORIDADE: Código do Fornecedor)
        produto_id = produto_id_mov
        if not produto_id:
            if cod_forn:
                cursor.execute('SELECT id FROM produtos WHERE codigo_fornecedor = %s AND ativo = TRUE', (cod_forn,))
                res = cursor.fetchone()
                if res: produto_id = res[0]
            if not produto_id and cod_barras:
                cursor.execute('SELECT id FROM produtos WHERE codigo_barras = %s AND ativo = TRUE', (cod_barras,))
                res = cursor.fetchone()
                if res: produto_id = res[0]

        # Atualizar ou criar produto
        if produto_id:
            # Produto existe - ATUALIZAR
            print(f"[APROVACAO] Produto {produto_id} existe. Atualizando...")
            update_fields = []
            params = []

            # Adicionar campos para atualização se tiverem valor
            if nome: update_fields.append("nome = %s"); params.append(nome)
            if p_venda: update_fields.append("preco = %s"); params.append(p_venda)
            if p_custo: update_fields.append("preco_custo = %s"); params.append(p_custo)
            if m_lucro: update_fields.append("margem_lucro = %s"); params.append(m_lucro)
            if desc: update_fields.append("descricao = %s"); params.append(desc)
            if cat: update_fields.append("categoria = %s"); params.append(cat)
            if marca: update_fields.append("marca = %s"); params.append(marca)
            if forn_id: update_fields.append("fornecedor_id = %s"); params.append(forn_id)
            if est_min: update_fields.append("estoque_minimo = %s"); params.append(est_min)
            if ncm: update_fields.append("ncm = %s"); params.append(ncm)
            if unid: update_fields.append("unidade = %s"); params.append(unid)
            if foto: update_fields.append("foto_url = %s"); params.append(foto)

            if update_fields:
                query = f"UPDATE produtos SET estoque = estoque + %s, { ', '.join(update_fields) } WHERE id = %s"
                params.insert(0, qtd)
                params.append(produto_id)
                cursor.execute(query, tuple(params))
            else:
                # Se nenhum campo for atualizado, apenas o estoque
                cursor.execute("UPDATE produtos SET estoque = estoque + %s WHERE id = %s", (qtd, produto_id))
        else:
            # Produto não existe - CRIAR
            print(f"[APROVACAO] Criando novo produto.")
            cursor.execute('''
                INSERT INTO produtos (nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
                                    codigo_fornecedor, preco_custo, margem_lucro, foto_url, marca, fornecedor_id,
                                    ncm, unidade, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id
            ''', (nome, p_venda, qtd, est_min, cod_barras, desc, cat, cod_forn, p_custo, m_lucro, foto, marca, forn_id, ncm, unid))
            produto_id = cursor.fetchone()[0]

        # Atualizar status da movimentação
        cursor.execute('''
            UPDATE movimentacoes 
            SET status = 'aprovada', usuario_aprovacao = %s, data_aprovacao = %s, produto_id = %s
            WHERE id = %s
        ''', (usuario_id, agora_br(), produto_id, movimentacao_id))

        if local_conn:
            conn.commit()
        
        return produto_id

    except Exception as e:
        if local_conn:
            conn.rollback()
        print(f"Erro em aprovar_movimentacao: {e}")
        raise
    finally:
        if local_conn:
            conn.close()

def cancelar_movimentacao(movimentacao_id, usuario_id, motivo_cancelamento):
    """Cancela uma movimentação (permite deletar depois)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE movimentacoes 
        SET status = 'cancelada', usuario_aprovacao = %s, data_aprovacao = %s,
            motivo_rejeicao = %s
        WHERE id = %s AND status = 'pendente'
    ''', (usuario_id, agora_br(), motivo_cancelamento, movimentacao_id))
    
    conn.commit()
    conn.close()
    return True

# Mantém compatibilidade com código antigo
def rejeitar_movimentacao(movimentacao_id, usuario_id, motivo_rejeicao):
    """DEPRECATED: Use cancelar_movimentacao()"""
    return cancelar_movimentacao(movimentacao_id, usuario_id, motivo_rejeicao)

def deletar_movimentacao(movimentacao_id):
    """Deleta uma movimentação pendente ou cancelada"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificar se está pendente ou cancelada antes de deletar
    cursor.execute('SELECT status FROM movimentacoes WHERE id = %s', (movimentacao_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        raise ValueError("Movimentação não encontrada")
    
    if result[0] not in ['pendente', 'cancelada']:
        conn.close()
        raise ValueError("Apenas movimentações pendentes ou canceladas podem ser deletadas")
    
    conn.close()
    return True

def vincular_produto_nfe(movimentacao_id, produto_id, usuario_id):
    """
    Vincula uma movimentação pendente a um produto existente no estoque.
    Atualiza os dados da movimentação com os dados do produto existente,
    exceto o preço de venda, custo e quantidade.
    """
    conn = get_db_connection()
    # Use RealDictCursor to fetch product data as a dictionary
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # 1. Verificar se a movimentação existe e está pendente
        cursor.execute("SELECT status FROM movimentacoes WHERE id = %s", (movimentacao_id,))
        movimentacao = cursor.fetchone()
        
        if not movimentacao:
            return False, "Movimentação não encontrada."
        
        if movimentacao['status'] != 'pendente':
            return False, "Apenas movimentações pendentes podem ser vinculadas."
            
        # 2. Buscar os dados do produto de destino
        # Usando a função já existente para consistência
        produto_existente = obter_produto_por_id(produto_id)

        if not produto_existente:
            return False, "Produto de destino não encontrado ou está inativo."
            
        # 3. Atualizar a movimentação com os dados do produto, exceto preços e quantidade
        # ACAO: Atualiza os dados da movimentação com os dados do produto vinculado
        # Manter o preco_venda, preco_custo e quantidade da NFe original
        cursor.execute("""
            UPDATE movimentacoes 
            SET 
                produto_id = %(produto_id)s,
                nome = %(nome)s,
                codigo_barras = %(codigo_barras)s,
                codigo_fornecedor = %(codigo_fornecedor)s,
                descricao = %(descricao)s,
                categoria = %(categoria)s,
                marca = %(marca)s,
                ncm = %(ncm)s,
                unidade = %(unidade)s,
                estoque_minimo = %(estoque_minimo)s,
                fornecedor_id = %(fornecedor_id)s,
                foto_url = %(foto_url)s,
                observacoes = COALESCE(observacoes, '') || %(observacao)s
            WHERE id = %(movimentacao_id)s
        """, {
            'produto_id': produto_id,
            'nome': produto_existente.get('nome'),
            'codigo_barras': produto_existente.get('codigo_barras'),
            'codigo_fornecedor': produto_existente.get('codigo_fornecedor'),
            'descricao': produto_existente.get('descricao'),
            'categoria': produto_existente.get('categoria'),
            'marca': produto_existente.get('marca'),
            'ncm': produto_existente.get('ncm'),
            'unidade': produto_existente.get('unidade'),
            'estoque_minimo': produto_existente.get('estoque_minimo'),
            'fornecedor_id': produto_existente.get('fornecedor_id'),
            'foto_url': produto_existente.get('foto_url'),
            'observacao': f'\n[Vinculado ao produto ID {produto_id} por usuário {usuario_id} em {agora_br().strftime("%Y-%m-%d %H:%M:%S")}]',
            'movimentacao_id': movimentacao_id
        })
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, f"Movimentação ID {movimentacao_id} vinculada e atualizada com sucesso com os dados do Produto ID {produto_id}."
        else:
            # Isso pode acontecer se a movimentação não for encontrada no WHERE
            return False, "Não foi possível vincular e atualizar a movimentação."
            
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False, f"Erro ao vincular produto: {str(e)}"
    finally:
        conn.close()

def reverter_e_deletar_movimentacao_aprovada(movimentacao_id, usuario_id):
    """Reverte o estoque de uma movimentação aprovada e a deleta."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Buscar dados da movimentação
        cursor.execute('SELECT produto_id, quantidade, status FROM movimentacoes WHERE id = %s', (movimentacao_id,))
        mov = cursor.fetchone()

        if not mov:
            raise ValueError(f"Movimentação com ID {movimentacao_id} não encontrada.")

        produto_id, quantidade, status = mov

        if status != 'aprovada':
            raise ValueError(f"Esta função só pode ser usada para movimentações aprovadas. Status atual: {status}")

        if not produto_id:
            # Se não há produto_id, a movimentação, embora aprovada, não afetou o estoque.
            # Apenas deletar a movimentação.
            print(f"[REVERSAO] Movimentação {movimentacao_id} não tem produto associado. Apenas deletando.")
            cursor.execute("DELETE FROM movimentacoes WHERE id = %s", (movimentacao_id,))
            conn.commit()
            return True, f"Movimentação {movimentacao_id} deletada (não havia estoque para reverter)."

        # Reverter o estoque do produto
        print(f"[REVERSAO] Revertendo {quantidade} unidade(s) do produto ID {produto_id}.")
        cursor.execute("UPDATE produtos SET estoque = estoque - %s WHERE id = %s", (quantidade, produto_id))

        # Deletar a movimentação
        cursor.execute("DELETE FROM movimentacoes WHERE id = %s", (movimentacao_id,))
        print(f"[REVERSAO] Movimentação {movimentacao_id} deletada.")

        conn.commit()
        return True, f"Movimentação {movimentacao_id} revertida e deletada com sucesso."

    except Exception as e:
        conn.rollback()
        print(f"Erro em reverter_e_deletar_movimentacao_aprovada: {e}")
        raise
    finally:
        conn.close()

def contar_movimentacoes_pendentes():
    """Conta o número de movimentações pendentes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM movimentacoes WHERE status = 'pendente'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def listar_nfes_agrupadas(status=None):
    """
    Lista as NFes com movimentações agrupadas
    Retorna informações resumidas de cada NFe com contagem de produtos
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    query = '''
        SELECT 
            COALESCE(m.xml_nfe_numero, 'MANUAL-' || m.id) as nfe_identificador,
            m.xml_nfe_numero,
            m.xml_nfe_chave,
            m.xml_nfe_data,
            m.origem,
            m.status,
            MIN(m.data_criacao) as data_criacao,
            MAX(m.data_aprovacao) as data_aprovacao,
            f.nome as fornecedor_nome,
            m.fornecedor_id,
            u.nome_completo as usuario_nome,
            COUNT(*) as total_produtos,
            SUM(m.quantidade) as total_quantidade,
            SUM(m.preco_custo * m.quantidade) as total_custo,
            SUM(m.preco_venda * m.quantidade) as total_venda,
            -- Status consolidado da NFe
            CASE 
                WHEN COUNT(*) FILTER (WHERE m.status = 'pendente') > 0 THEN 'pendente'
                WHEN COUNT(*) FILTER (WHERE m.status = 'cancelada') = COUNT(*) THEN 'cancelada'
                WHEN COUNT(*) FILTER (WHERE m.status = 'aprovada') = COUNT(*) THEN 'aprovada'
                ELSE 'parcial'
            END as status_nfe
        FROM movimentacoes m
        LEFT JOIN fornecedores f ON m.fornecedor_id = f.id
        LEFT JOIN usuarios u ON m.usuario_criacao = u.id
        WHERE 1=1
    '''
    
    params = []
    
    if status:
        # Filtrar pelo status dos itens
        query += " AND m.status = %s"
        params.append(status)
    
    query += '''
        GROUP BY 
            COALESCE(m.xml_nfe_numero, 'MANUAL-' || m.id),
            m.xml_nfe_numero, m.xml_nfe_chave, m.xml_nfe_data,
            m.origem, m.status, f.nome, m.fornecedor_id, u.nome_completo
        ORDER BY MIN(m.data_criacao) DESC
    '''
    
    cursor.execute(query, params)
    nfes = cursor.fetchall()
    conn.close()
    return nfes

def listar_produtos_por_nfe(nfe_numero=None, nfe_identificador=None):
    """
    Lista todos os produtos/movimentações de uma NFe específica
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    query = '''
        SELECT m.*, 
               f.nome as fornecedor_nome,
               u.nome_completo as usuario_nome,
               ua.nome_completo as usuario_aprovacao_nome
        FROM movimentacoes m
        LEFT JOIN fornecedores f ON m.fornecedor_id = f.id
        LEFT JOIN usuarios u ON m.usuario_criacao = u.id
        LEFT JOIN usuarios ua ON m.usuario_aprovacao = ua.id
        WHERE 1=1
    '''
    
    params = []
    
    if nfe_numero:
        query += " AND m.xml_nfe_numero = %s"
        params.append(nfe_numero)
    elif nfe_identificador and nfe_identificador.startswith('MANUAL-'):
        # Para movimentações manuais
        id_manual = nfe_identificador.replace('MANUAL-', '')
        query += " AND m.id = %s AND m.origem = 'manual'"
        params.append(int(id_manual))
    
    query += " ORDER BY m.id"
    
    cursor.execute(query, params)
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def aprovar_nfe_completa(nfe_numero, usuario_id):
    """
    Aprova todos os produtos pendentes de uma NFe de uma vez
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar todas as movimentações pendentes da NFe
        # Suporta tanto NFe importadas quanto movimentações manuais
        if nfe_numero.startswith('MANUAL-'):
            # Movimentação manual
            id_manual = nfe_numero.replace('MANUAL-', '')
            cursor.execute('''
                SELECT id FROM movimentacoes 
                WHERE id = %s AND status = 'pendente' AND origem = 'manual'
            ''', (int(id_manual),))
        else:
            # NFe importada
            cursor.execute('''
                SELECT id FROM movimentacoes 
                WHERE xml_nfe_numero = %s AND status = 'pendente'
            ''', (nfe_numero,))
        
        movimentacoes_pendentes = cursor.fetchall()
        produtos_aprovados = []
        
        for mov in movimentacoes_pendentes:
            try:
                produto_id = aprovar_movimentacao(mov[0], usuario_id)
                produtos_aprovados.append(produto_id)
            except Exception as e:
                # Se falhar em uma movimentação específica, continua com as outras
                print(f"[AVISO] Erro ao aprovar movimentação {mov[0]}: {str(e)}")
                continue
        
        return {
            'sucesso': True,
            'total_aprovados': len(produtos_aprovados),
            'produtos_ids': produtos_aprovados
        }
        
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e)
        }

def cancelar_nfe_completa(nfe_numero, usuario_id, motivo_cancelamento):
    """
    Cancela todos os produtos pendentes de uma NFe de uma vez (permite deletar depois)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Suporta tanto NFe importadas quanto movimentações manuais
        if nfe_numero.startswith('MANUAL-'):
            # Movimentação manual
            id_manual = nfe_numero.replace('MANUAL-', '')
            cursor.execute('''
                UPDATE movimentacoes 
                SET status = 'cancelada', 
                    usuario_aprovacao = %s, 
                    data_aprovacao = CURRENT_TIMESTAMP,
                    motivo_rejeicao = %s
                WHERE id = %s AND status = 'pendente' AND origem = 'manual'
            ''', (usuario_id, motivo_cancelamento, int(id_manual)))
        else:
            # NFe importada
            cursor.execute('''
                UPDATE movimentacoes 
                SET status = 'cancelada', 
                    usuario_aprovacao = %s, 
                    data_aprovacao = CURRENT_TIMESTAMP,
                    motivo_rejeicao = %s
                WHERE xml_nfe_numero = %s AND status = 'pendente'
            ''', (usuario_id, motivo_cancelamento, nfe_numero))
        
        total_cancelados = cursor.rowcount
        conn.commit()
        conn.close()
        
        return {
            'sucesso': True,
            'total_cancelados': total_cancelados
        }
    except Exception as e:
        conn.rollback()
        conn.close()
        return {
            'sucesso': False,
            'erro': str(e)
        }

# Mantém compatibilidade com código antigo
def rejeitar_nfe_completa(nfe_numero, usuario_id, motivo_rejeicao):
    """DEPRECATED: Use cancelar_nfe_completa()"""
    return cancelar_nfe_completa(nfe_numero, usuario_id, motivo_rejeicao)

# FUNÇÕES DE VENDAS
def registrar_venda(cliente_id, itens, forma_pagamento, desconto=0, observacoes=None, usuario_id=None):
    """Registra uma nova venda com seus itens
    
    Validações:
    - Se a forma de pagamento não for 'prazo', o caixa DEVE estar aberto
    - Verifica estoque disponível
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # IMPORTANTE: Validar se o caixa está aberto para vendas não-prazo
        if forma_pagamento != 'prazo':
            cursor.execute("SELECT COUNT(*) FROM caixa_sessoes WHERE status = 'aberto'")
            if cursor.fetchone()[0] == 0:
                raise Exception("❌ CAIXA FECHADO! O caixa deve estar aberto para registrar vendas. Por favor, abra o caixa antes de continuar.")
        
        # Verificar estoque antes de processar a venda
        for item in itens:
            cursor.execute('SELECT nome, estoque FROM produtos WHERE id = %s', (item['produto_id'],))
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
            INSERT INTO vendas (cliente_id, total, forma_pagamento, desconto, observacoes, usuario_id, data_venda)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (cliente_id, total, forma_pagamento, desconto, observacoes, usuario_id, agora_br()))
        
        venda_id = cursor.fetchone()[0]
        
        # Insere os itens da venda
        for item in itens:
            cursor.execute('''
                INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            ''', (venda_id, item['produto_id'], item['quantidade'], 
                  item['preco_unitario'], item['quantidade'] * item['preco_unitario']))
            
            # Atualiza o estoque diretamente na mesma transação
            cursor.execute('''
                UPDATE produtos 
                SET estoque = estoque - %s 
                WHERE id = %s
            ''', (item['quantidade'], item['produto_id']))
        
        # Se for venda a prazo, cria conta a receber
        if forma_pagamento == 'prazo':
            cursor.execute('''
                INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, venda_id)
                VALUES (%s, %s, (CURRENT_DATE + INTERVAL '30 days'), %s, %s)
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
                        cursor.execute("SELECT nome FROM clientes WHERE id = %s", (cliente_id,))
                        cliente_result = cursor.fetchone()
                        if cliente_result:
                            cliente_nome = cliente_result[0]
                    
                    cursor.execute('''
                        INSERT INTO caixa_movimentacoes (
                            tipo, categoria, descricao, valor, usuario_id, venda_id
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.id, c.nome, v.total, v.forma_pagamento, v.data_venda
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.data_venda DESC
        LIMIT %s
    ''', (limit,))
    
    vendas = []
    for row in cursor.fetchall():
        vendas.append({
            'id': row[0],
            'cliente': row[1] or 'Cliente Avulso',
            'total': row[2],
            'forma_pagamento': row[3],
            'data_venda': converter_utc_para_br(row[4])
        })
    
    conn.close()
    return vendas

def obter_venda_por_id(venda_id):
    """Obtem os detalhes completos de uma venda especifica"""
    try:
        garantir_estrutura_fiscal()
    except Exception as e:
        # Nao bloqueia a visualizacao da venda caso a estrutura fiscal esteja inconsistente.
        print(f"Aviso ao garantir estrutura fiscal para venda {venda_id}: {e}")

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # Consulta robusta: usa to_jsonb para tolerar ausencia de colunas fiscais legadas.
        cursor.execute(
            '''
            SELECT
                v.id,
                v.cliente_id,
                COALESCE(to_jsonb(c)->>'nome', 'Cliente Avulso') AS cliente_nome,
                COALESCE(to_jsonb(c)->>'telefone', '') AS cliente_telefone,
                COALESCE(to_jsonb(c)->>'email', '') AS cliente_email,
                COALESCE(to_jsonb(c)->>'cpf_cnpj', '') AS cliente_cpf_cnpj,
                COALESCE(to_jsonb(c)->>'endereco', '') AS cliente_endereco,
                COALESCE(to_jsonb(c)->>'ie', '') AS cliente_ie,
                COALESCE(to_jsonb(c)->>'indicador_ie', '') AS cliente_indicador_ie,
                COALESCE(to_jsonb(c)->>'tipo_pessoa', '') AS cliente_tipo_pessoa,
                COALESCE(to_jsonb(c)->>'cidade', '') AS cliente_cidade,
                COALESCE(to_jsonb(c)->>'estado', '') AS cliente_estado,
                COALESCE(to_jsonb(c)->>'cep', '') AS cliente_cep,
                COALESCE(to_jsonb(c)->>'bairro', '') AS cliente_bairro,
                COALESCE(to_jsonb(c)->>'numero', '') AS cliente_numero,
                COALESCE(to_jsonb(c)->>'complemento', '') AS cliente_complemento,
                COALESCE(to_jsonb(c)->>'codigo_municipio_ibge', '') AS cliente_codigo_municipio_ibge,
                v.total,
                v.forma_pagamento,
                v.desconto,
                v.observacoes,
                v.data_venda AS created_at,
                v.usuario_id,
                COALESCE(u.nome_completo, 'Sistema') AS vendedor_nome
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            WHERE v.id = %s
            ''',
            (venda_id,),
        )

        venda_data = cursor.fetchone()
        if not venda_data:
            print(f"Venda {venda_id} nao encontrada")
            return None

        # Buscar itens da venda
        cursor.execute(
            '''
            SELECT
                iv.produto_id,
                COALESCE(p.nome, 'Produto removido') AS produto_nome,
                COALESCE(p.codigo_fornecedor, '') AS codigo_fornecedor,
                COALESCE(p.codigo_barras, '') AS codigo_barras,
                iv.quantidade,
                iv.preco_unitario,
                iv.subtotal
            FROM itens_venda iv
            LEFT JOIN produtos p ON iv.produto_id = p.id
            WHERE iv.venda_id = %s
            ORDER BY iv.id
            ''',
            (venda_id,),
        )

        itens = []
        for item_row in cursor.fetchall():
            itens.append({
                'produto_id': item_row['produto_id'],
                'produto_nome': item_row['produto_nome'],
                'codigo_fornecedor': item_row['codigo_fornecedor'],
                'codigo_barras': item_row['codigo_barras'],
                'quantidade': item_row['quantidade'],
                'preco_unitario': float(item_row['preco_unitario']),
                'subtotal': float(item_row['subtotal']),
            })

        # Montar resultado
        venda = {
            'id': venda_data['id'],
            'cliente_id': venda_data['cliente_id'],
            'cliente_nome': venda_data['cliente_nome'] or 'Cliente Avulso',
            'cliente': venda_data['cliente_nome'] or 'Cliente Avulso',
            'cliente_telefone': venda_data['cliente_telefone'] or '',
            'cliente_email': venda_data['cliente_email'] or '',
            'cliente_cpf_cnpj': venda_data['cliente_cpf_cnpj'] or '',
            'cliente_endereco': venda_data['cliente_endereco'] or '',
            'cliente_ie': venda_data['cliente_ie'] or '',
            'cliente_indicador_ie': venda_data['cliente_indicador_ie'] or '',
            'cliente_tipo_pessoa': venda_data['cliente_tipo_pessoa'] or '',
            'cliente_cidade': venda_data['cliente_cidade'] or '',
            'cliente_estado': venda_data['cliente_estado'] or '',
            'cliente_cep': venda_data['cliente_cep'] or '',
            'cliente_bairro': venda_data['cliente_bairro'] or '',
            'cliente_numero': venda_data['cliente_numero'] or '',
            'cliente_complemento': venda_data['cliente_complemento'] or '',
            'cliente_codigo_municipio_ibge': venda_data['cliente_codigo_municipio_ibge'] or '',
            'total': float(venda_data['total']),
            'forma_pagamento': venda_data['forma_pagamento'] or 'dinheiro',
            'desconto': float(venda_data['desconto'] or 0),
            'observacoes': venda_data['observacoes'] or '',
            'created_at': converter_utc_para_br(venda_data['created_at']),
            'data_venda': converter_utc_para_br(venda_data['created_at']),
            'usuario_id': venda_data['usuario_id'],
            'valor_pago': float(venda_data['total']),  # Para compatibilidade, usar o total
            'troco': 0,  # Para compatibilidade
            'vendedor_nome': venda_data['vendedor_nome'] or 'Sistema',
            'funcionario_nome': venda_data['vendedor_nome'] or 'Sistema',
            'itens': itens,
        }

        return venda

    except Exception as e:
        print(f"Erro ao buscar venda {venda_id}: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

def limpar_sincronizacoes_incorretas():
    """Remove movimentações de caixa de vendas que não são do dia atual"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hoje = hoje_br().strftime('%Y-%m-%d')
        
        # Buscar movimentações de vendas que não são de hoje
        cursor.execute('''
            SELECT cm.id, cm.venda_id, v.data_venda, cm.valor
            FROM caixa_movimentacoes cm
            JOIN vendas v ON cm.venda_id = v.id
            WHERE cm.categoria = 'venda'
            AND v.data_venda::date::text != %s
            AND cm.data_movimentacao::date = %s
        ''', (hoje, hoje))
        
        movimentacoes_incorretas = cursor.fetchall()
        
        print(f"DEBUG LIMPEZA: Encontradas {len(movimentacoes_incorretas)} movimentações incorretas")
        
        # Remover movimentações incorretas
        for mov in movimentacoes_incorretas:
            mov_id, venda_id, data_venda, valor = mov
            data_venda_formatada = data_venda[:10] if data_venda else ''
            print(f"DEBUG LIMPEZA: Removendo mov #{mov_id} - Venda #{venda_id} de {data_venda_formatada} (R$ {valor})")
            
            cursor.execute('DELETE FROM caixa_movimentacoes WHERE id = %s', (mov_id,))
        
        conn.commit()
        return True, f"Removidas {len(movimentacoes_incorretas)} sincronizações incorretas"
        
    except Exception as e:
        print(f"DEBUG LIMPEZA: Erro: {str(e)}")
        return False, f"Erro ao limpar sincronizações: {str(e)}"
    finally:
        conn.close()

def sincronizar_vendas_com_caixa():
    """Sincroniza vendas existentes do dia atual com o caixa (caso não tenham sido registradas)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se há caixa aberto
        cursor.execute("SELECT COUNT(*) FROM caixa_sessoes WHERE status = 'aberto'")
        if cursor.fetchone()[0] == 0:
            conn.close()
            return False, "Não há caixa aberto"
        
        # Usar data específica do dia atual
        hoje = hoje_br().strftime('%Y-%m-%d')
        
        # Buscar vendas especificamente do dia atual que não estão no caixa
        cursor.execute('''
            SELECT v.id, v.cliente_id, v.total, v.forma_pagamento, v.usuario_id, v.data_venda
            FROM vendas v
            WHERE v.data_venda::date::text = %s
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
                cursor.execute("SELECT nome FROM clientes WHERE id = %s", (cliente_id,))
                cliente_result = cursor.fetchone()
                if cliente_result:
                    cliente_nome = cliente_result[0]
            
            # Registrar no caixa
            cursor.execute('''
                INSERT INTO caixa_movimentacoes (
                    tipo, categoria, descricao, valor, usuario_id, venda_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Limpar sincronizações incorretas primeiro
    limpar_sincronizacoes_incorretas()
    
    # Sincronizar vendas do dia atual com o caixa
    sincronizar_vendas_com_caixa()
    
    # Usar data específica do dia atual
    hoje = hoje_br().strftime('%Y-%m-%d')
    
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
        WHERE v.data_venda::date::text = %s
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
        # row[4] é um objeto datetime do PostgreSQL, converter para string
        data_venda_convertida = converter_utc_para_br(row[4])
        data_venda = data_venda_convertida.strftime('%Y-%m-%d') if data_venda_convertida else ''
        
        if data_venda == hoje:
            venda = {
                'id': row[0],
                'cliente': row[1] or 'Cliente Avulso',
                'total': row[2],
                'forma_pagamento': row[3],
                'data_venda': data_venda_convertida,
                'total_itens': row[5] or 0,
                'funcionario_nome': row[6] or 'Sem funcionário',
                'funcionario_username': row[7] or '',
                'usuario_id': row[8]
            }
            vendas.append(venda)
            total_valor += row[2]
            total_itens += row[5] or 0
            print(f"  ✓ Venda #{row[0]}: R$ {row[2]}, Data: {data_venda_convertida}, Itens: {row[5]}, Funcionário: {row[6] or 'N/A'}")
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hoje = hoje_br().strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT cp.id, cp.descricao, cp.valor, cp.data_vencimento, cp.status, cp.categoria, cp.observacoes,
               f.nome as fornecedor_nome
        FROM contas_pagar cp
        LEFT JOIN fornecedores f ON cp.fornecedor_id = f.id
        WHERE cp.data_vencimento::date = %s AND cp.status = 'pendente'
        ORDER BY cp.valor DESC
    ''', (hoje,))
    
    contas = []
    for row in cursor.fetchall():
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': converter_utc_para_br(row[3]),
            'status': row[4],
            'categoria': row[5],
            'observacoes': row[6],
            'fornecedor_nome': row[7] or 'Sem fornecedor'
        })
    
    conn.close()
    return contas

def listar_contas_pagar_por_periodo(filtro='todos', data_inicio=None, data_fim=None, status='pendente'):
    """Lista contas a pagar com filtros de período"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hoje = hoje_br().strftime('%Y-%m-%d')
    
    base_query = '''
        SELECT cp.id, cp.descricao, cp.valor, cp.data_vencimento, cp.status, cp.categoria, cp.observacoes,
               f.nome as fornecedor_nome,
               (cp.data_vencimento::date - %s::date) as dias_restantes,
               cp.data_pagamento
        FROM contas_pagar cp
        LEFT JOIN fornecedores f ON cp.fornecedor_id = f.id
        WHERE cp.status = %s
    '''
    
    params = [hoje, status]
    
    # Para contas pagas, usar data_pagamento; para pendentes, usar data_vencimento
    campo_data = 'cp.data_pagamento' if status == 'pago' else 'cp.data_vencimento'
    
    if filtro == 'hoje':
        base_query += f" AND {campo_data}::date = %s"
        params.append(hoje)
    elif filtro == 'atrasadas':
        base_query += f" AND {campo_data}::date < %s"
        params.append(hoje)
    elif filtro == 'futuras':
        base_query += f" AND {campo_data}::date > %s"
        params.append(hoje)
    elif filtro == 'proximos_7_dias':
        proximos_7 = (datetime.now(TIMEZONE_BR) + timedelta(days=7)).strftime('%Y-%m-%d')
        base_query += f" AND {campo_data}::date BETWEEN %s AND %s"
        params.extend([hoje, proximos_7])
    elif filtro == 'proximos_30_dias':
        proximos_30 = (datetime.now(TIMEZONE_BR) + timedelta(days=30)).strftime('%Y-%m-%d')
        base_query += f" AND {campo_data}::date BETWEEN %s AND %s"
        params.extend([hoje, proximos_30])
    elif filtro == 'personalizado' and data_inicio and data_fim:
        base_query += f" AND {campo_data}::date BETWEEN %s AND %s"
        params.extend([data_inicio, data_fim])
    
    # Ordenar por data_pagamento se estiver consultando contas pagas (DESC para mostrar mais recentes primeiro)
    # Para contas pendentes, ordenar por vencimento (ASC) com atrasadas primeiro
    if status == 'pago':
        base_query += " ORDER BY cp.data_pagamento DESC"
    else:
        # Ordenar: atrasadas primeiro (por data ASC), depois futuras (por data ASC)
        base_query += f" ORDER BY CASE WHEN cp.data_vencimento::date < %s::date THEN 0 ELSE 1 END, cp.data_vencimento ASC"
        params.append(hoje)
    
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
            'data_vencimento': converter_utc_para_br(row[3]),
            'status': row[4],
            'categoria': row[5],
            'observacoes': row[6],
            'fornecedor_nome': row[7] or 'Sem fornecedor',
            'dias_restantes': dias_restantes,
            'status_visual': status_visual,
            'texto_prazo': f"{abs(dias_restantes)} dias {'em atraso' if dias_restantes < 0 else ('restantes' if dias_restantes > 0 else 'vence hoje')}" if row[4] == 'pendente' else 'Pago',
            'data_pagamento': converter_utc_para_br(row[9])
        })
    
    conn.close()
    return contas

def adicionar_conta_pagar(descricao, valor, data_vencimento, categoria=None, observacoes=None, fornecedor_id=None, auto_sincronizar=True):
    """Adiciona uma nova conta a pagar"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe conta similar para evitar duplicatas
        cursor.execute('''
            SELECT id FROM contas_pagar 
            WHERE descricao = %s AND valor = %s AND data_vencimento = %s AND status = 'pendente'
        ''', (descricao, valor, data_vencimento))
        
        conta_existente = cursor.fetchone()
        if conta_existente:
            conn.close()
            return False, f"Já existe uma conta similar pendente (ID: {conta_existente[0]})"
        
        cursor.execute('''
            INSERT INTO contas_pagar (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id))
        
        conta_id = cursor.fetchone()[0]
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
        data_pagamento = hoje_br().isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE contas_pagar 
        SET status = 'pago', data_pagamento = %s
        WHERE id = %s
    ''', (data_pagamento, conta_id))
    
    conn.commit()
    conn.close()

def duplicar_conta_pagar(conta_id):
    """Duplica uma conta a pagar existente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar dados da conta original
        cursor.execute('''
            SELECT descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id
            FROM contas_pagar
            WHERE id = %s
        ''', (conta_id,))
        
        conta = cursor.fetchone()
        if not conta:
            conn.close()
            return False, "Conta não encontrada"
        
        descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id = conta
        
        # Adicionar " - Cópia" na descrição
        descricao = f"{descricao} - Cópia"
        
        # Inserir nova conta
        cursor.execute('''
            INSERT INTO contas_pagar (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pendente')
            RETURNING id
        ''', (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id))
        
        nova_conta_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        return True, f"Conta duplicada com sucesso (Nova ID: {nova_conta_id})"
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao duplicar conta: {str(e)}"

def excluir_conta_pagar(conta_id):
    """Exclui uma conta a pagar"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se a conta existe
        cursor.execute('SELECT id FROM contas_pagar WHERE id = %s', (conta_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Conta não encontrada"
        
        # Excluir a conta
        cursor.execute('DELETE FROM contas_pagar WHERE id = %s', (conta_id,))
        conn.commit()
        conn.close()
        
        return True, "Conta excluída com sucesso"
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao excluir conta: {str(e)}"

def obter_conta_pagar(conta_id):
    """Obtém os dados de uma conta a pagar"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT cp.id, cp.descricao, cp.valor, cp.data_vencimento, cp.categoria, 
                   cp.observacoes, cp.fornecedor_id, cp.status, cp.data_pagamento,
                   f.nome as fornecedor_nome
            FROM contas_pagar cp
            LEFT JOIN fornecedores f ON cp.fornecedor_id = f.id
            WHERE cp.id = %s
        ''', (conta_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False, "Conta não encontrada"
        
        data_vencimento_convertida = converter_utc_para_br(row[3])
        data_pagamento_convertida = converter_utc_para_br(row[8])
        
        conta = {
            'id': row[0],
            'descricao': row[1],
            'valor': float(row[2]),
            'data_vencimento': data_vencimento_convertida.strftime('%Y-%m-%d') if data_vencimento_convertida else None,
            'categoria': row[4],
            'observacoes': row[5],
            'fornecedor_id': row[6],
            'status': row[7],
            'data_pagamento': data_pagamento_convertida.strftime('%Y-%m-%d') if data_pagamento_convertida else None,
            'fornecedor_nome': row[9]
        }
        
        return True, conta
    
    except Exception as e:
        conn.close()
        return False, f"Erro ao obter conta: {str(e)}"

def editar_conta_pagar(conta_id, descricao, valor, data_vencimento, categoria=None, observacoes=None, fornecedor_id=None):
    """Edita uma conta a pagar existente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se a conta existe
        cursor.execute('SELECT id FROM contas_pagar WHERE id = %s', (conta_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Conta não encontrada"
        
        # Atualizar a conta
        cursor.execute('''
            UPDATE contas_pagar
            SET descricao = %s, valor = %s, data_vencimento = %s, 
                categoria = %s, observacoes = %s, fornecedor_id = %s
            WHERE id = %s
        ''', (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, conta_id))
        
        conn.commit()
        conn.close()
        
        return True, "Conta atualizada com sucesso"
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao editar conta: {str(e)}"

# FUNÇÕES DE CONTAS A RECEBER
def listar_contas_receber_hoje():
    """Lista contas a receber com vencimento hoje"""
    garantir_colunas_contas_receber()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hoje = hoje_br().strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT cr.id, cr.descricao, cr.valor, cr.data_vencimento, cr.status, c.nome
        FROM contas_receber cr
        LEFT JOIN clientes c ON cr.cliente_id = c.id
        WHERE cr.data_vencimento::date = %s AND cr.status = 'pendente'
        ORDER BY cr.valor DESC
    ''', (hoje,))
    
    contas = []
    for row in cursor.fetchall():
        contas.append({
            'id': row[0],
            'descricao': row[1],
            'valor': row[2],
            'data_vencimento': converter_utc_para_br(row[3]),
            'status': row[4],
            'cliente': row[5]
        })
    
    conn.close()
    return contas

def listar_contas_receber_por_periodo(filtro='todos', data_inicio=None, data_fim=None, status='pendente'):
    """Lista contas a receber com filtros de período"""
    garantir_colunas_contas_receber()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hoje = hoje_br().strftime('%Y-%m-%d')
    
    base_query = '''
        SELECT cr.id, cr.descricao, cr.valor, cr.data_vencimento, cr.status, c.nome,
               (cr.data_vencimento::date - %s::date) as dias_restantes,
               cr.data_recebimento
        FROM contas_receber cr
        LEFT JOIN clientes c ON cr.cliente_id = c.id
        WHERE cr.status = %s
    '''
    
    params = [hoje, status]
    
    # Para contas recebidas, usar data_recebimento; para pendentes, usar data_vencimento
    campo_data = 'cr.data_recebimento' if status == 'recebido' else 'cr.data_vencimento'
    
    if filtro == 'hoje':
        base_query += f" AND {campo_data}::date = %s"
        params.append(hoje)
    elif filtro == 'atrasadas':
        base_query += f" AND {campo_data}::date < %s"
        params.append(hoje)
    elif filtro == 'futuras':
        base_query += f" AND {campo_data}::date > %s"
        params.append(hoje)
    elif filtro == 'proximos_7_dias':
        proximos_7 = (datetime.now(TIMEZONE_BR) + timedelta(days=7)).strftime('%Y-%m-%d')
        base_query += f" AND {campo_data}::date BETWEEN %s AND %s"
        params.extend([hoje, proximos_7])
    elif filtro == 'proximos_30_dias':
        proximos_30 = (datetime.now(TIMEZONE_BR) + timedelta(days=30)).strftime('%Y-%m-%d')
        base_query += f" AND {campo_data}::date BETWEEN %s AND %s"
        params.extend([hoje, proximos_30])
    elif filtro == 'personalizado' and data_inicio and data_fim:
        base_query += f" AND {campo_data}::date BETWEEN %s AND %s"
        params.extend([data_inicio, data_fim])
    
    # Ordenar por data_recebimento se estiver consultando contas recebidas (DESC para mostrar mais recentes primeiro)
    campo_ordenacao = 'cr.data_recebimento' if status == 'recebido' else 'cr.data_vencimento'
    base_query += f" ORDER BY {campo_ordenacao} DESC"
    
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
            'data_vencimento': converter_utc_para_br(row[3]),
            'status': row[4],
            'cliente_nome': row[5] or 'Cliente não informado',
            'dias_restantes': dias_restantes,
            'status_visual': status_visual,
            'texto_prazo': f"{abs(dias_restantes)} dias {'em atraso' if dias_restantes < 0 else ('restantes' if dias_restantes > 0 else 'vence hoje')}" if row[4] == 'pendente' else 'Recebido',
            'data_recebimento': converter_utc_para_br(row[7])
        })
    
    conn.close()
    return contas

def receber_conta(conta_id, data_recebimento=None):
    """Marca uma conta como recebida"""
    if not data_recebimento:
        data_recebimento = hoje_br().isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE contas_receber 
        SET status = 'recebido', data_recebimento = %s
        WHERE id = %s
    ''', (data_recebimento, conta_id))
    
    conn.commit()
    conn.close()

def adicionar_conta_receber(descricao, valor, data_vencimento, cliente_id=None, observacoes=None, auto_sincronizar=True):
    """Adiciona uma nova conta a receber"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe conta similar para evitar duplicatas
        cursor.execute('''
            SELECT id FROM contas_receber 
            WHERE descricao = %s AND valor = %s AND data_vencimento = %s AND status = 'pendente'
        ''', (descricao, valor, data_vencimento))
        
        conta_existente = cursor.fetchone()
        if conta_existente:
            conn.close()
            return False, f"Já existe uma conta similar pendente (ID: {conta_existente[0]})"
        
        cursor.execute('''
            INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, observacoes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        ''', (descricao, valor, data_vencimento, cliente_id, observacoes))
        
        conta_id = cursor.fetchone()[0]
        conn.commit()
        
        
        conn.close()
        return True, f"Conta a receber criada com sucesso (ID: {conta_id})"
            
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao criar conta: {str(e)}"

def duplicar_conta_receber(conta_id):
    """Duplica uma conta a receber existente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar dados da conta original
        cursor.execute('''
            SELECT descricao, valor, data_vencimento, cliente_id, observacoes
            FROM contas_receber
            WHERE id = %s
        ''', (conta_id,))
        
        conta = cursor.fetchone()
        if not conta:
            conn.close()
            return False, "Conta não encontrada"
        
        descricao, valor, data_vencimento, cliente_id, observacoes = conta
        
        # Adicionar " - Cópia" na descrição
        descricao = f"{descricao} - Cópia"
        
        # Inserir nova conta
        cursor.execute('''
            INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, observacoes, status)
            VALUES (%s, %s, %s, %s, %s, 'pendente')
            RETURNING id
        ''', (descricao, valor, data_vencimento, cliente_id, observacoes))
        
        nova_conta_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        return True, f"Conta duplicada com sucesso (Nova ID: {nova_conta_id})"
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao duplicar conta: {str(e)}"

def excluir_conta_receber(conta_id):
    """Exclui uma conta a receber"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se a conta existe
        cursor.execute('SELECT id FROM contas_receber WHERE id = %s', (conta_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Conta não encontrada"
        
        # Excluir a conta
        cursor.execute('DELETE FROM contas_receber WHERE id = %s', (conta_id,))
        conn.commit()
        conn.close()
        
        return True, "Conta excluída com sucesso"
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao excluir conta: {str(e)}"

def obter_conta_receber(conta_id):
    """Obtém os dados de uma conta a receber"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT cr.id, cr.descricao, cr.valor, cr.data_vencimento, 
                   cr.observacoes, cr.cliente_id, cr.status, cr.data_recebimento,
                   c.nome as cliente_nome
            FROM contas_receber cr
            LEFT JOIN clientes c ON cr.cliente_id = c.id
            WHERE cr.id = %s
        ''', (conta_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False, "Conta não encontrada"
        
        data_vencimento_convertida = converter_utc_para_br(row[3])
        data_recebimento_convertida = converter_utc_para_br(row[7])
        
        conta = {
            'id': row[0],
            'descricao': row[1],
            'valor': float(row[2]),
            'data_vencimento': data_vencimento_convertida.strftime('%Y-%m-%d') if data_vencimento_convertida else None,
            'observacoes': row[4],
            'cliente_id': row[5],
            'status': row[6],
            'data_recebimento': data_recebimento_convertida.strftime('%Y-%m-%d') if data_recebimento_convertida else None,
            'cliente_nome': row[8]
        }
        
        return True, conta
    
    except Exception as e:
        conn.close()
        return False, f"Erro ao obter conta: {str(e)}"

def editar_conta_receber(conta_id, descricao, valor, data_vencimento, cliente_id=None, observacoes=None):
    """Edita uma conta a receber existente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se a conta existe
        cursor.execute('SELECT id FROM contas_receber WHERE id = %s', (conta_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Conta não encontrada"
        
        # Atualizar a conta
        cursor.execute('''
            UPDATE contas_receber
            SET descricao = %s, valor = %s, data_vencimento = %s, 
                cliente_id = %s, observacoes = %s
            WHERE id = %s
        ''', (descricao, valor, data_vencimento, cliente_id, observacoes, conta_id))
        
        conn.commit()
        conn.close()
        
        return True, "Conta atualizada com sucesso"
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao editar conta: {str(e)}"

def listar_contas_atrasadas():
    """Lista contas a pagar e a receber que estão em atraso (vencimento anterior ao dia de hoje)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    contas_atrasadas = []
    
    # Contas a pagar atrasadas
    cursor.execute('''
        SELECT 'pagar' as tipo, cp.id, cp.descricao, cp.valor, cp.data_vencimento, 
               f.nome as entidade, (CURRENT_DATE - cp.data_vencimento::date) as dias_atraso
        FROM contas_pagar cp
        LEFT JOIN fornecedores f ON cp.fornecedor_id = f.id
        WHERE cp.data_vencimento::date < CURRENT_DATE AND cp.status = 'pendente'
        ORDER BY cp.data_vencimento ASC
    ''')
    
    for row in cursor.fetchall():
        contas_atrasadas.append({
            'tipo': 'pagar',
            'tipo_label': 'A Pagar',
            'id': row[1],
            'descricao': row[2],
            'valor': float(row[3]) if row[3] else 0,
            'data_vencimento': row[4],
            'entidade': row[5] or 'Sem fornecedor',
            'dias_atraso': int(row[6]) if row[6] else 0
        })
    
    # Contas a receber atrasadas
    cursor.execute('''
        SELECT 'receber' as tipo, cr.id, cr.descricao, cr.valor, cr.data_vencimento, 
               c.nome as entidade, (CURRENT_DATE - cr.data_vencimento::date) as dias_atraso
        FROM contas_receber cr
        LEFT JOIN clientes c ON cr.cliente_id = c.id
        WHERE cr.data_vencimento::date < CURRENT_DATE AND cr.status = 'pendente'
        ORDER BY cr.data_vencimento ASC
    ''')
    
    for row in cursor.fetchall():
        contas_atrasadas.append({
            'tipo': 'receber',
            'tipo_label': 'A Receber',
            'id': row[1],
            'descricao': row[2],
            'valor': float(row[3]) if row[3] else 0,
            'data_vencimento': row[4],
            'entidade': row[5] or 'Sem cliente',
            'dias_atraso': int(row[6]) if row[6] else 0
        })
    
    conn.close()
    
    # Ordenar por dias de atraso (maiores primeiro)
    contas_atrasadas.sort(key=lambda x: x['dias_atraso'], reverse=True)
    
    return contas_atrasadas

def contar_contas_atrasadas():
    """Conta o total de contas em atraso (pagar + receber)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*)
        FROM (
            SELECT 1 FROM contas_pagar 
            WHERE data_vencimento::date < CURRENT_DATE AND status = 'pendente'
            UNION ALL
            SELECT 1 FROM contas_receber 
            WHERE data_vencimento::date < CURRENT_DATE AND status = 'pendente'
        ) as contas
    ''')
    
    total = cursor.fetchone()[0] or 0
    conn.close()
    
    return total

# FUNÇÕES DE ESTATÍSTICAS
def obter_estatisticas_dashboard():
    """Obtém estatísticas para o dashboard"""
    
    # Usar conexões separadas para evitar conflitos de transação
    def executar_consulta_segura(query, default=0):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()[0] or default
            conn.close()
            return resultado
        except Exception as e:
            return default
    
    # Total de produtos
    total_produtos = executar_consulta_segura("SELECT COUNT(*) FROM produtos WHERE ativo = TRUE")
    
    # Total de clientes
    total_clientes = executar_consulta_segura("SELECT COUNT(*) FROM clientes")
    
    # Total de fornecedores
    total_fornecedores = executar_consulta_segura("SELECT COUNT(*) FROM fornecedores WHERE ativo = TRUE")
    
    # Valor do estoque
    valor_estoque = executar_consulta_segura("SELECT SUM(preco * estoque) FROM produtos WHERE ativo = TRUE")
    
    # Produtos com estoque baixo
    produtos_estoque_baixo = executar_consulta_segura("SELECT COUNT(*) FROM produtos WHERE ativo = TRUE AND estoque > 0 AND estoque <= estoque_minimo")

    # Produtos sem estoque
    produtos_sem_estoque = executar_consulta_segura("SELECT COUNT(*) FROM produtos WHERE ativo = TRUE AND estoque = 0")
    
    # Vendas do mês e do dia - usando uma conexão para ambas
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vendas do mês
        cursor.execute('''
            SELECT COUNT(*), SUM(total) 
            FROM vendas 
            WHERE to_char(data_venda, 'YYYY-MM') = to_char(CURRENT_DATE, 'YYYY-MM')
        ''')
        vendas_mes = cursor.fetchone()
        
        # Vendas do dia
        cursor.execute('''
            SELECT COUNT(*), SUM(total) 
            FROM vendas 
            WHERE data_venda::date = CURRENT_DATE
        ''')
        vendas_dia = cursor.fetchone()
        
        conn.close()
    except:
        vendas_mes = (0, 0)
        vendas_dia = (0, 0)
    
    # Contas em atraso
    valor_atraso_receber = executar_consulta_segura('''
        SELECT SUM(valor) 
        FROM contas_receber 
        WHERE data_vencimento::date < CURRENT_DATE AND status = 'pendente'
    ''')
    
    valor_atraso_pagar = executar_consulta_segura('''
        SELECT SUM(valor) 
        FROM contas_pagar 
        WHERE data_vencimento::date < CURRENT_DATE AND status = 'pendente'
    ''')
    
    # Movimentações pendentes (verificar se a tabela existe)
    movimentacoes_pendentes = executar_consulta_segura('''
        SELECT COUNT(*) 
        FROM movimentacoes_produtos 
        WHERE status = 'pendente'
    ''')
    
    # Orçamentos pendentes
    orcamentos_pendentes = executar_consulta_segura('''
        SELECT COUNT(*) 
        FROM orcamentos 
        WHERE status = 'pendente'
    ''')
    
    # Contas a pagar hoje
    contas_pagar_hoje = executar_consulta_segura('''
        SELECT COUNT(*) 
        FROM contas_pagar 
        WHERE data_vencimento::date = CURRENT_DATE AND status = 'pendente'
    ''')
    
    # Contas a receber hoje
    contas_receber_hoje = executar_consulta_segura('''
        SELECT COUNT(*) 
        FROM contas_receber 
        WHERE data_vencimento::date = CURRENT_DATE AND status = 'pendente'
    ''')
    
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
        'valor_atraso_pagar': valor_atraso_pagar,
        'movimentacoes_pendentes': movimentacoes_pendentes,
        'orcamentos_pendentes': orcamentos_pendentes,
        'contas_pagar_hoje': contas_pagar_hoje,
        'contas_receber_hoje': contas_receber_hoje
    }

def produtos_estoque_baixo():
    """Lista produtos com estoque baixo"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, estoque, estoque_minimo
        FROM produtos
        WHERE ativo = TRUE AND estoque > 0 AND estoque <= estoque_minimo
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
    import random
    agora_orc = agora_br()
    numero = f"ORC{agora_orc.strftime('%Y%m%d')}{random.randint(1000, 9999)}"
    return numero

def criar_orcamento(itens, cliente_id=None, desconto=0, observacoes="", usuario_id=None):
    """Cria um novo orçamento"""
    conn = get_db_connection()
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
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (numero_orcamento, cliente_id, total_com_desconto, desconto, observacoes, usuario_id))
        
        orcamento_id = cursor.fetchone()[0]
        
        # Inserir itens do orçamento
        for item in itens:
            subtotal = item['quantidade'] * item['preco_unitario']
            cursor.execute('''
                INSERT INTO itens_orcamento (orcamento_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
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
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar orçamento
    cursor.execute('''
        SELECT o.*, c.nome as cliente_nome, c.telefone as cliente_telefone,
               c.email as cliente_email
        FROM orcamentos o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE o.id = %s
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
        WHERE io.orcamento_id = %s
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o orçamento existe e está pendente
        cursor.execute('SELECT status FROM orcamentos WHERE id = %s', (orcamento_id,))
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
            SET cliente_id = %s, total = %s, desconto = %s, observacoes = %s
            WHERE id = %s
        ''', (cliente_id, total_com_desconto, desconto, observacoes, orcamento_id))
        
        # Remover itens antigos
        cursor.execute('DELETE FROM itens_orcamento WHERE orcamento_id = %s', (orcamento_id,))
        
        # Inserir novos itens
        for item in itens:
            cursor.execute('''
                INSERT INTO itens_orcamento (orcamento_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o orçamento existe
        cursor.execute('SELECT status FROM orcamentos WHERE id = %s', (orcamento_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            raise Exception("Orçamento não encontrado")
        
        # Verificar se o orçamento pode ser excluído (apenas pendentes e rejeitados)
        if resultado[0] not in ['pendente', 'rejeitado']:
            raise Exception("Apenas orçamentos pendentes ou rejeitados podem ser excluídos")
        
        # Excluir itens do orçamento primeiro (devido à foreign key)
        cursor.execute('DELETE FROM itens_orcamento WHERE orcamento_id = %s', (orcamento_id,))
        
        # Excluir o orçamento
        cursor.execute('DELETE FROM orcamentos WHERE id = %s', (orcamento_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def converter_orcamento_em_venda(orcamento_id, forma_pagamento):
    """Converte um orçamento aprovado em venda"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar orçamento
        orcamento = obter_orcamento(orcamento_id)
        if not orcamento:
            raise ValueError("Orçamento não encontrado")
        
        # Criar venda
        cursor.execute('''
            INSERT INTO vendas (cliente_id, total, forma_pagamento, desconto, observacoes, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (orcamento['cliente_id'], orcamento['total'], forma_pagamento, 
              orcamento['desconto'], orcamento['observacoes'], orcamento['usuario_id']))
        
        venda_id = cursor.fetchone()[0]
        
        # Copiar itens para venda
        for item in orcamento['itens']:
            cursor.execute('''
                INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            ''', (venda_id, item['produto_id'], item['quantidade'], 
                  item['preco_unitario'], item['subtotal']))
            
            # Atualizar estoque
            cursor.execute('''
                UPDATE produtos 
                SET estoque = estoque - %s 
                WHERE id = %s
            ''', (item['quantidade'], item['produto_id']))
        
        # Atualizar status do orçamento
        cursor.execute('''
            UPDATE orcamentos 
            SET status = 'convertido' 
            WHERE id = %s
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

def importar_produtos_de_xml_avancado(conteudo_xml, margem_padrao=100, estoque_minimo=1, usar_preco_nfe=True, acao_existente='atualizar_estoque'):
    """
    Importa produtos de um arquivo XML de NFe com configurações avançadas
    Também extrai e cadastra/atualiza automaticamente o fornecedor baseado nos dados do emitente da NF-e
    
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
    fornecedor_id = None
    
    try:
        # Parse do XML
        root = ET.fromstring(conteudo_xml)
        
        # Namespace da NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # ===== EXTRAIR E CADASTRAR/ATUALIZAR FORNECEDOR =====
        emit = root.find('.//nfe:emit', ns)
        if emit is not None:
            try:
                # Extrair dados do emitente (fornecedor)
                cnpj_fornecedor = emit.find('nfe:CNPJ', ns)
                cnpj_fornecedor = cnpj_fornecedor.text if cnpj_fornecedor is not None else None
                
                nome_fornecedor = emit.find('nfe:xNome', ns)
                nome_fornecedor = nome_fornecedor.text if nome_fornecedor is not None else None
                
                nome_fantasia = emit.find('nfe:xFant', ns)
                nome_fantasia = nome_fantasia.text if nome_fantasia is not None else None
                
                # Dados de endereço
                enderEmit = emit.find('nfe:enderEmit', ns)
                endereco_completo = None
                cidade = None
                estado = None
                cep = None
                telefone = None
                
                if enderEmit is not None:
                    xLgr = enderEmit.find('nfe:xLgr', ns)
                    nro = enderEmit.find('nfe:nro', ns)
                    xBairro = enderEmit.find('nfe:xBairro', ns)
                    xCpl = enderEmit.find('nfe:xCpl', ns)
                    
                    cidade_elem = enderEmit.find('nfe:xMun', ns)
                    cidade = cidade_elem.text if cidade_elem is not None else None
                    
                    estado_elem = enderEmit.find('nfe:UF', ns)
                    estado = estado_elem.text if estado_elem is not None else None
                    
                    cep_elem = enderEmit.find('nfe:CEP', ns)
                    cep = cep_elem.text if cep_elem is not None else None
                    
                    fone_elem = enderEmit.find('nfe:fone', ns)
                    telefone = fone_elem.text if fone_elem is not None else None
                    
                    # Montar endereço completo
                    partes_endereco = []
                    if xLgr is not None:
                        partes_endereco.append(xLgr.text)
                    if nro is not None:
                        partes_endereco.append(f"nº {nro.text}")
                    if xCpl is not None and xCpl.text:
                        partes_endereco.append(xCpl.text)
                    if xBairro is not None:
                        partes_endereco.append(xBairro.text)
                    
                    endereco_completo = ', '.join(partes_endereco) if partes_endereco else None
                
                # Buscar ou criar fornecedor
                if cnpj_fornecedor and nome_fornecedor:
                    # Buscar fornecedor existente pelo CNPJ normalizado
                    fornecedor_existente = buscar_fornecedor_por_cnpj(cnpj_fornecedor)
                    
                    if fornecedor_existente:
                        # Atualizar fornecedor existente
                        fornecedor_id = fornecedor_existente['id']
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE fornecedores 
                            SET nome = %s, telefone = %s, endereco = %s, cidade = %s, estado = %s, cep = %s
                            WHERE id = %s
                        ''', (nome_fornecedor, telefone, endereco_completo, cidade, estado, cep, fornecedor_id))
                        conn.commit()
                        conn.close()
                    else:
                        # Criar novo fornecedor
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO fornecedores (nome, cnpj, telefone, endereco, cidade, estado, cep, observacoes)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        ''', (nome_fornecedor, cnpj_fornecedor, telefone, endereco_completo, cidade, estado, cep, 
                              f"Importado de NF-e. Nome Fantasia: {nome_fantasia}" if nome_fantasia else "Importado de NF-e"))
                        fornecedor_id = cursor.fetchone()[0]
                        conn.commit()
                        conn.close()
                    
            except Exception as e:
                erros.append(f"Erro ao processar fornecedor: {str(e)}")
        
        # ===== BUSCAR PRODUTOS DO XML =====
        # Buscar todos os produtos (det)
        produtos_xml = root.findall('.//nfe:det', ns)
        
        if not produtos_xml:
            raise ValueError("Nenhum produto encontrado no XML")
        
        conn = get_db_connection()
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
                codigo_ean = codigo_ean.text if codigo_ean is not None else None
                if codigo_ean in ['SEM GTIN', '', None]:
                    codigo_ean = None  # NULL para produtos sem código de barras
                
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
                        WHERE codigo_barras = %s
                    ''', (codigo_ean,))
                    produto_existente = cursor.fetchone()
                
                if not produto_existente and codigo_produto:
                    cursor.execute('''
                        SELECT id, nome, preco, estoque 
                        FROM produtos 
                        WHERE codigo_fornecedor = %s OR nome LIKE %s
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
                            SET estoque = %s
                            WHERE id = %s
                        ''', (novo_estoque, produto_id))
                        produtos_atualizados += 1
                        continue
                    elif acao_existente == 'substituir_dados':
                        # Substituir todos os dados (incluindo fornecedor)
                        produto_id = produto_existente[0]
                        cursor.execute('''
                            UPDATE produtos 
                            SET nome = %s, codigo_fornecedor = %s, codigo_barras = %s, categoria = %s, 
                                preco_custo = %s, preco = %s, estoque = %s, estoque_minimo = %s,
                                unidade = %s, ncm = %s, fornecedor_id = %s
                            WHERE id = %s
                        ''', (nome_produto, codigo_produto, codigo_ean, categoria, 
                             preco_custo, preco_venda, quantidade, estoque_minimo, 
                             unidade, ncm, fornecedor_id, produto_id))
                        produtos_atualizados += 1
                        continue
                
                # Inserir novo produto (vinculando ao fornecedor)
                cursor.execute('''
                    INSERT INTO produtos (nome, codigo_fornecedor, codigo_barras, categoria, descricao,
                                        preco_custo, preco, estoque, estoque_minimo, unidade, ncm, ativo, fornecedor_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (nome_produto, codigo_produto, codigo_ean, categoria, 
                     "Importado via NFe XML", preco_custo, preco_venda, 
                     quantidade, estoque_minimo, unidade, ncm, True, fornecedor_id))
                
                produtos_importados += 1
                
            except Exception as e:
                conn.rollback()  # Fazer rollback para poder continuar processando
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
        
        conn = get_db_connection()
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
                codigo_ean = codigo_ean.text if codigo_ean is not None else None
                if codigo_ean in ['SEM GTIN', '', None]:
                    codigo_ean = None  # NULL para produtos sem código de barras
                
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
                        WHERE codigo_barras = %s
                    ''', (codigo_ean,))
                    produto_existente = cursor.fetchone()
                
                if not produto_existente and codigo_produto:
                    cursor.execute('''
                        SELECT id, nome, preco, estoque 
                        FROM produtos 
                        WHERE codigo_fornecedor = %s OR nome LIKE %s
                    ''', (codigo_produto, f'%{codigo_produto}%'))
                    produto_existente = cursor.fetchone()
                
                if produto_existente:
                    # Atualizar produto existente incluindo categoria
                    produto_id = produto_existente[0]
                    novo_estoque = produto_existente[3] + quantidade
                    categoria = mapear_ncm_para_categoria(ncm)
                    
                    cursor.execute('''
                        UPDATE produtos 
                        SET estoque = %s, preco = %s, ncm = %s, unidade = %s, categoria = %s
                        WHERE id = %s
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
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (nome_produto, valor_unitario, quantidade, codigo_ean, ncm, unidade, codigo_produto, categoria))
                    
                    produto_id = cursor.fetchone()[0]
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
                conn.rollback()  # Fazer rollback para poder continuar processando
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

def importar_xml_para_movimentacoes(conteudo_xml, margem_padrao=100, estoque_minimo=1, usuario_id=None):
    """
    Importa produtos de um arquivo XML de NFe criando movimentações pendentes de aprovação
    ao invés de adicionar diretamente ao estoque
    
    Args:
        conteudo_xml: Conteúdo do arquivo XML como string
        margem_padrao: Margem de lucro padrão (%)
        estoque_minimo: Estoque mínimo padrão
        usuario_id: ID do usuário que está importando
    
    Returns:
        Dict com informações sobre a importação
    """
    import xml.etree.ElementTree as ET
    
    movimentacoes_criadas = 0
    erros = []
    fornecedor_id = None
    
    try:
        # Parse do XML
        root = ET.fromstring(conteudo_xml)
        
        # Namespace da NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Extrair dados da NFe (chave, número, data)
        inf_nfe = root.find('.//nfe:infNFe', ns)
        nfe_chave = inf_nfe.get('Id').replace('NFe', '') if inf_nfe is not None and inf_nfe.get('Id') else None
        
        ide = root.find('.//nfe:ide', ns)
        nfe_numero = ide.find('nfe:nNF', ns).text if ide is not None and ide.find('nfe:nNF', ns) is not None else None
        
        dhEmi = ide.find('nfe:dhEmi', ns) if ide is not None else None
        nfe_data = None
        if dhEmi is not None and dhEmi.text:
            try:
                from datetime import datetime
                nfe_data = datetime.fromisoformat(dhEmi.text.replace('Z', '+00:00')).date()
            except:
                nfe_data = None
        
        # ===== EXTRAIR E CADASTRAR/ATUALIZAR FORNECEDOR =====
        emit = root.find('.//nfe:emit', ns)
        if emit is not None:
            try:
                # Extrair dados do emitente (fornecedor)
                cnpj_fornecedor = emit.find('nfe:CNPJ', ns)
                cnpj_fornecedor = cnpj_fornecedor.text if cnpj_fornecedor is not None else None
                
                nome_fornecedor = emit.find('nfe:xNome', ns)
                nome_fornecedor = nome_fornecedor.text if nome_fornecedor is not None else None
                
                nome_fantasia = emit.find('nfe:xFant', ns)
                nome_fantasia = nome_fantasia.text if nome_fantasia is not None else None
                
                # Dados de endereço
                enderEmit = emit.find('nfe:enderEmit', ns)
                endereco_completo = None
                cidade = None
                estado = None
                cep = None
                telefone = None
                
                if enderEmit is not None:
                    xLgr = enderEmit.find('nfe:xLgr', ns)
                    nro = enderEmit.find('nfe:nro', ns)
                    xBairro = enderEmit.find('nfe:xBairro', ns)
                    xCpl = enderEmit.find('nfe:xCpl', ns)
                    
                    cidade_elem = enderEmit.find('nfe:xMun', ns)
                    cidade = cidade_elem.text if cidade_elem is not None else None
                    
                    estado_elem = enderEmit.find('nfe:UF', ns)
                    estado = estado_elem.text if estado_elem is not None else None
                    
                    cep_elem = enderEmit.find('nfe:CEP', ns)
                    cep = cep_elem.text if cep_elem is not None else None
                    
                    fone_elem = enderEmit.find('nfe:fone', ns)
                    telefone = fone_elem.text if fone_elem is not None else None
                    
                    # Montar endereço completo
                    partes_endereco = []
                    if xLgr is not None:
                        partes_endereco.append(xLgr.text)
                    if nro is not None:
                        partes_endereco.append(f"nº {nro.text}")
                    if xCpl is not None and xCpl.text:
                        partes_endereco.append(xCpl.text)
                    if xBairro is not None:
                        partes_endereco.append(xBairro.text)
                    
                    endereco_completo = ', '.join(partes_endereco) if partes_endereco else None
                
                # Buscar ou criar fornecedor usando validação robusta
                if cnpj_fornecedor and nome_fornecedor:
                    # Usar função robusta que evita duplicações
                    resultado_fornecedor = adicionar_ou_atualizar_fornecedor_automatico(
                        nome=nome_fornecedor,
                        cnpj=cnpj_fornecedor,
                        telefone=telefone,
                        endereco=endereco_completo,
                        cidade=cidade,
                        estado=estado,
                        cep=cep,
                        observacoes=f"Importado de NF-e {nfe_numero}. Nome Fantasia: {nome_fantasia}" if nome_fantasia else f"Importado de NF-e {nfe_numero}"
                    )
                    
                    if resultado_fornecedor['sucesso']:
                        fornecedor_id = resultado_fornecedor['fornecedor_id']
                        if resultado_fornecedor['criado']:
                            print(f"DEBUG XML: Novo fornecedor criado: {nome_fornecedor} (ID: {fornecedor_id})")
                        else:
                            print(f"DEBUG XML: Fornecedor já existia: {nome_fornecedor} (ID: {fornecedor_id})")
                    else:
                        erros.append(f"Erro ao processar fornecedor {nome_fornecedor}: {resultado_fornecedor['mensagem']}")
                        fornecedor_id = None
                    
            except Exception as e:
                erros.append(f"Erro ao processar fornecedor: {str(e)}")
        
        # ===== BUSCAR PRODUTOS DO XML E CRIAR MOVIMENTAÇÕES =====
        produtos_xml = root.findall('.//nfe:det', ns)
        
        if not produtos_xml:
            raise ValueError("Nenhum produto encontrado no XML")
        
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
                codigo_ean = codigo_ean.text if codigo_ean is not None else None
                if codigo_ean in ['SEM GTIN', '', None]:
                    codigo_ean = None
                
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
                preco_custo = valor_unitario
                preco_venda = preco_custo + (preco_custo * margem_padrao / 100) if preco_custo > 0 else 0.0
                
                # Determinar categoria baseada no NCM
                categoria = obter_categoria_por_ncm_avancado(ncm) if ncm else "Geral"
                
                # Criar movimentação pendente (margem será calculada automaticamente)
                adicionar_movimentacao(
                    nome=nome_produto,
                    preco_venda=preco_venda,
                    quantidade=quantidade,
                    tipo_movimentacao='entrada',
                    origem='xml_nfe',
                    estoque_minimo=estoque_minimo,
                    codigo_barras=codigo_ean,
                    descricao=f"Importado da NFe {nfe_numero}",
                    categoria=categoria,
                    codigo_fornecedor=codigo_produto,
                    preco_custo=preco_custo,
                    margem_lucro=0,  # Será calculado automaticamente pela função
                    marca=None,
                    fornecedor_id=fornecedor_id,
                    ncm=ncm,
                    unidade=unidade,
                    xml_nfe_chave=nfe_chave,
                    xml_nfe_numero=nfe_numero,
                    xml_nfe_data=nfe_data,
                    xml_produto_codigo=codigo_produto,
                    usuario_id=usuario_id,
                    observacoes=f"Importado automaticamente de NFe {nfe_numero}"
                )
                
                movimentacoes_criadas += 1
                
            except Exception as e:
                erros.append(f"Erro ao criar movimentação para produto {codigo_produto}: {str(e)}")
                continue
        
        return {
            'sucesso': True,
            'movimentacoes_criadas': movimentacoes_criadas,
            'fornecedor_id': fornecedor_id,
            'nfe_numero': nfe_numero,
            'erros': erros,
            'total_produtos_xml': len(produtos_xml)
        }
        
    except ET.ParseError as e:
        return {
            'sucesso': False,
            'erro': f'Erro ao analisar XML: {str(e)}',
            'movimentacoes_criadas': 0,
            'erros': [f'XML inválido: {str(e)}']
        }
    except Exception as e:
        return {
            'sucesso': False,
            'erro': f'Erro geral: {str(e)}',
            'movimentacoes_criadas': 0,
            'erros': [str(e)]
        }

# FUNÇÕES DE RELATÓRIOS

def gerar_relatorio_vendas(data_inicio=None, data_fim=None, cliente_id=None):
    """Gera relatório de vendas por período e/ou cliente"""
    conn = get_db_connection()
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
            query += " AND v.data_venda::date >= %s"
            params.append(data_inicio)
        if data_fim:
            query += " AND v.data_venda::date <= %s"
            params.append(data_fim)
        if cliente_id:
            query += " AND v.cliente_id = %s"
            params.append(cliente_id)
        
        query += '''
            GROUP BY v.id, v.data_venda, c.nome, v.total, v.forma_pagamento, u.username
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
        ''' + (" AND v.data_venda::date >= %s" if data_inicio else "") +
              (" AND v.data_venda::date <= %s" if data_fim else "") +
              (" AND v.cliente_id = %s" if cliente_id else "") +
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
    conn = get_db_connection()
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
            query += " AND v.data_venda::date >= %s"
            params.append(data_inicio)
        if data_fim:
            query += " AND v.data_venda::date <= %s"
            params.append(data_fim)
        
        query += '''
            GROUP BY p.id, p.nome, p.codigo_barras
            ORDER BY total_vendido DESC
            LIMIT %s
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
    conn = get_db_connection()
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
            WHERE p.ativo = TRUE
            ORDER BY p.categoria, p.nome
        ''')
        
        produtos = []
        valor_total_estoque = 0
        valor_total_estoque_custo = 0
        produtos_sem_estoque = 0
        produtos_estoque_baixo = 0
        
        for row in cursor.fetchall():
            preco_venda = row[4] if row[4] is not None else 0
            preco_custo = preco_venda / 2  # Margem de 100%
            valor_estoque_custo = row[2] * preco_custo  # estoque * preço de custo
            
            produto = {
                'nome': row[0],
                'codigo': row[1],
                'estoque': row[2],
                'estoque_minimo': row[3],
                'preco': preco_venda,
                'preco_custo': preco_custo,
                'valor_estoque': row[5],
                'valor_estoque_custo': valor_estoque_custo,
                'categoria': row[6],
                'status': row[7]
            }
            produtos.append(produto)
            valor_total_estoque += row[5] if row[5] else 0
            valor_total_estoque_custo += valor_estoque_custo
            
            if row[2] == 0:
                produtos_sem_estoque += 1
            elif row[2] <= 1:
                produtos_estoque_baixo += 1
        
        # Estatísticas por categoria
        cursor.execute('''
            SELECT 
                categoria,
                COUNT(*) as quantidade_produtos,
                SUM(estoque) as total_estoque,
                SUM(estoque * preco) as valor_categoria
            FROM produtos 
            WHERE ativo = TRUE
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
                'valor_total_estoque_custo': valor_total_estoque_custo,
                'total_produtos': len(produtos),
                'produtos_sem_estoque': produtos_sem_estoque,
                'produtos_estoque_baixo': produtos_estoque_baixo
            }
        }
        
    except Exception as e:
        conn.close()
        return {'erro': str(e)}

def gerar_relatorio_financeiro(data_inicio=None, data_fim=None):
    """Gera relatório financeiro completo com detalhes de todas as movimentações"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Lista de parâmetros para filtros de data (usada para data_venda e data_vencimento)
        params_venda_vencimento = []
        
        if data_inicio:
            params_venda_vencimento.append(data_inicio)
        if data_fim:
            params_venda_vencimento.append(data_fim)
        
        # --- 1. Vendas por forma de pagamento ---
        query_vendas = '''
            SELECT 
                forma_pagamento,
                COUNT(*) as quantidade,
                SUM(total) as valor_total
            FROM vendas
            WHERE 1=1
        '''
        if data_inicio:
            query_vendas += " AND DATE(data_venda) >= %s"
        if data_fim:
            query_vendas += " AND DATE(data_venda) <= %s"
        
        query_vendas += " GROUP BY forma_pagamento"
        
        # Determina quantos placeholders são necessários para a query de Vendas
        num_vendas_params = 0
        if data_inicio: num_vendas_params += 1
        if data_fim: num_vendas_params += 1
        
        cursor.execute(query_vendas, params_venda_vencimento[:num_vendas_params])
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
            
        # --- 2. CÁLCULO EXATO DE VALORES PAGOS E RECEBIDOS NO PERÍODO ---
        
        # Parâmetros para filtros que usam data_pagamento/recebimento
        params_pago_recebido = []
        
        # 2.1. Total RECEBIDO (status='recebido', filtrado por data_recebimento)
        query_total_recebido = '''
            SELECT COALESCE(SUM(valor), 0)
            FROM contas_receber 
            WHERE status = 'recebido'
        '''
        if data_inicio:
            query_total_recebido += " AND DATE(data_recebimento) >= %s"
            params_pago_recebido.append(data_inicio)
        if data_fim:
            query_total_recebido += " AND DATE(data_recebimento) <= %s"
            params_pago_recebido.append(data_fim)
            
        cursor.execute(query_total_recebido, params_pago_recebido)
        total_recebido = cursor.fetchone()[0] or 0
        
        # 2.2. Total PAGO (status='pago', filtrado por data_pagamento)
        query_total_pago = '''
            SELECT COALESCE(SUM(valor), 0)
            FROM contas_pagar 
            WHERE status = 'pago'
        '''
        if data_inicio:
            query_total_pago += " AND DATE(data_pagamento) >= %s"
        if data_fim:
            query_total_pago += " AND DATE(data_pagamento) <= %s"
            
        cursor.execute(query_total_pago, params_pago_recebido)
        total_pago = cursor.fetchone()[0] or 0

        # 2.3. Total A RECEBER (status='pendente', filtrado por data_vencimento)
        query_total_a_receber = '''
            SELECT COALESCE(SUM(valor), 0)
            FROM contas_receber 
            WHERE status = 'pendente'
        '''
        if data_inicio:
            query_total_a_receber += " AND DATE(data_vencimento) >= %s"
        if data_fim:
            query_total_a_receber += " AND DATE(data_vencimento) <= %s"
        
        cursor.execute(query_total_a_receber, params_venda_vencimento)
        total_a_receber = cursor.fetchone()[0] or 0
        
        # 2.4. Total A PAGAR (status='pendente', filtrado por data_vencimento)
        query_total_a_pagar = query_total_a_receber.replace('contas_receber', 'contas_pagar')
        
        cursor.execute(query_total_a_pagar, params_venda_vencimento)
        total_a_pagar = cursor.fetchone()[0] or 0
        
        # --- 3. RESUMO E DETALHES (LISTAGEM) ---
        
        # Lista de parâmetros com filtro combinado (vencimento ou pagamento/recebimento)
        params_vencimento_recebimento = []
        if data_inicio:
            params_vencimento_recebimento.extend([data_inicio, data_inicio])
        if data_fim:
            params_vencimento_recebimento.extend([data_fim, data_fim])

        # Contas a receber RESUMO (listagem resumida)
        query_receber_resumo = '''
            SELECT 
                status,
                COUNT(*) as quantidade,
                SUM(valor) as valor_total
            FROM contas_receber
            WHERE 1=1
        '''
        if data_inicio:
            query_receber_resumo += " AND (DATE(data_vencimento) >= %s OR DATE(data_recebimento) >= %s)"
        if data_fim:
            query_receber_resumo += " AND (DATE(data_vencimento) <= %s OR DATE(data_recebimento) <= %s)"
        
        query_receber_resumo += " GROUP BY status"
        
        cursor.execute(query_receber_resumo, params_vencimento_recebimento)
        contas_receber_resumo = []
        for row in cursor.fetchall():
            contas_receber_resumo.append({'status': row[0], 'quantidade': row[1], 'valor': row[2]})

        # Contas a pagar RESUMO (listagem resumida)
        query_pagar_resumo = '''
            SELECT 
                status,
                COUNT(*) as quantidade,
                SUM(valor) as valor_total
            FROM contas_pagar
            WHERE 1=1
        '''
        if data_inicio:
            query_pagar_resumo += " AND (DATE(data_vencimento) >= %s OR DATE(data_pagamento) >= %s)"
        if data_fim:
            query_pagar_resumo += " AND (DATE(data_vencimento) <= %s OR DATE(data_pagamento) <= %s)"
        
        query_pagar_resumo += " GROUP BY status"
        
        cursor.execute(query_pagar_resumo, params_vencimento_recebimento)
        contas_pagar_resumo = []
        for row in cursor.fetchall():
            contas_pagar_resumo.append({'status': row[0], 'quantidade': row[1], 'valor': row[2]})
        
        # Contas a receber DETALHADAS (listagem detalhada)
        query_receber_detalhado = '''
            SELECT 
                cr.id, cr.descricao, cr.valor, cr.data_vencimento, cr.data_recebimento, 
                cr.status, c.nome as cliente
            FROM contas_receber cr
            LEFT JOIN clientes c ON cr.cliente_id = c.id
            WHERE 1=1
        '''
        if data_inicio:
            query_receber_detalhado += " AND (DATE(cr.data_vencimento) >= %s OR DATE(cr.data_recebimento) >= %s)"
        if data_fim:
            query_receber_detalhado += " AND (DATE(cr.data_vencimento) <= %s OR DATE(cr.data_recebimento) <= %s)"
        
        query_receber_detalhado += " ORDER BY cr.data_vencimento DESC"
        
        cursor.execute(query_receber_detalhado, params_vencimento_recebimento)
        contas_receber_detalhadas = []
        
        for row in cursor.fetchall():
            contas_receber_detalhadas.append({
                'id': row[0], 'descricao': row[1], 'valor': row[2], 'data_vencimento': row[3], 
                'data_recebimento': row[4], 'status': row[5], 'cliente': row[6] or 'Cliente Avulso'
            })
        
        # Contas a pagar DETALHADAS (listagem detalhada)
        query_pagar_detalhado = '''
            SELECT 
                cp.id, cp.descricao, cp.valor, cp.data_vencimento, cp.data_pagamento, 
                cp.status, f.nome as fornecedor
            FROM contas_pagar cp
            LEFT JOIN fornecedores f ON cp.fornecedor_id = f.id
            WHERE 1=1
        '''
        if data_inicio:
            query_pagar_detalhado += " AND (DATE(cp.data_vencimento) >= %s OR DATE(cp.data_pagamento) >= %s)"
        if data_fim:
            query_pagar_detalhado += " AND (DATE(cp.data_vencimento) <= %s OR DATE(cp.data_pagamento) <= %s)"
        
        query_pagar_detalhado += " ORDER BY cp.data_vencimento DESC"
        
        cursor.execute(query_pagar_detalhado, params_vencimento_recebimento)
        contas_pagar_detalhadas = []
        
        for row in cursor.fetchall():
            contas_pagar_detalhadas.append({
                'id': row[0], 'descricao': row[1], 'valor': row[2], 'data_vencimento': row[3], 
                'data_pagamento': row[4], 'status': row[5], 'fornecedor': row[6] or 'Sem Fornecedor'
            })
        
        # Movimentações do caixa RESUMO e DETALHADAS
        query_caixa = '''
            SELECT 
                tipo, COUNT(*) as quantidade, SUM(valor) as valor_total
            FROM caixa_movimentacoes cm
            WHERE 1=1
        '''
        
        if data_inicio:
            query_caixa += " AND cm.data_movimentacao::date >= %s"
        if data_fim:
            query_caixa += " AND cm.data_movimentacao::date <= %s"
        
        query_caixa += " GROUP BY tipo"
        
        params_caixa = []
        if data_inicio: params_caixa.append(data_inicio)
        if data_fim: params_caixa.append(data_fim)
        
        cursor.execute(query_caixa, params_caixa)
        movimentacoes_caixa_resumo = []
        
        for row in cursor.fetchall():
            movimentacoes_caixa_resumo.append({'tipo': row[0], 'quantidade': row[1], 'valor': row[2]})
        
        query_caixa_detalhado = '''
            SELECT 
                cm.id, cm.tipo, cm.categoria, cm.descricao, cm.valor, cm.data_movimentacao, 
                cm.observacoes, cm.venda_id, cm.conta_pagar_id, cm.conta_receber_id,
                u.nome_completo, u.username
            FROM caixa_movimentacoes cm
            JOIN usuarios u ON cm.usuario_id = u.id
            WHERE 1=1
        '''
        if data_inicio:
            query_caixa_detalhado += " AND cm.data_movimentacao::date >= %s"
        if data_fim:
            query_caixa_detalhado += " AND cm.data_movimentacao::date <= %s"
        
        query_caixa_detalhado += " ORDER BY cm.data_movimentacao DESC"
        
        cursor.execute(query_caixa_detalhado, params_caixa)
        movimentacoes_caixa_detalhadas = []
        
        for row in cursor.fetchall():
            movimentacoes_caixa_detalhadas.append({
                'id': row[0], 'tipo': row[1], 'categoria': row[2], 'descricao': row[3], 
                'valor': row[4], 'data_movimentacao': row[5], 'observacoes': row[6], 
                'venda_id': row[7], 'conta_pagar_id': row[8], 'conta_receber_id': row[9], 
                'usuario_nome': row[10] if row[10] else row[11]
            })
        
        # --- 4. CÁLCULO FINAL DO RESUMO ---
        # Saldo Líquido = Total Recebido (no período) - Total Pago (no período)
        saldo_liquido = total_recebido - total_pago

        conn.close()
        
        return {
            'vendas_forma_pagamento': vendas_forma_pagamento,
            'contas_receber': contas_receber_resumo,
            'contas_receber_detalhadas': contas_receber_detalhadas,
            'contas_pagar': contas_pagar_resumo,
            'contas_pagar_detalhadas': contas_pagar_detalhadas,
            'movimentacoes_caixa': movimentacoes_caixa_resumo,
            'movimentacoes_caixa_detalhadas': movimentacoes_caixa_detalhadas,
            'resumo': {
                'total_vendas': total_vendas,
                'total_a_receber': total_a_receber,
                'total_recebido': total_recebido,
                'total_a_pagar': total_a_pagar,
                'total_pago': total_pago,
                'saldo_liquido': saldo_liquido
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
            WHERE ativo = TRUE
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
            WHERE id = %s
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

def buscar_fornecedor_por_cnpj(cnpj):
    """
    Busca um fornecedor pelo CNPJ (normalizado).
    Agora usa a validação robusta de fornecedor.
    
    Args:
        cnpj: CNPJ do fornecedor (pode ser com ou sem formatação)
    
    Returns:
        Dict com dados do fornecedor ou None
    """
    if not cnpj:
        return None
    
    # Usar a função robusta de busca
    return buscar_fornecedor_melhorado(cnpj=cnpj)

def adicionar_fornecedor(nome, cnpj=None, telefone=None, email=None, endereco=None, 
                        cidade=None, estado=None, cep=None, contato_pessoa=None, observacoes=None):
    """
    Adiciona um novo fornecedor com validação robusta de duplicação.
    
    Raises:
        ValueError: Se o fornecedor já existe (detectado por CNPJ, email ou nome similar)
    
    Returns:
        int: ID do fornecedor criado ou None em caso de erro
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Validar duplicação usando a função robusta
        validacao = validar_fornecedor_duplicado(
            nome=nome,
            cnpj=cnpj,
            email=email,
            telefone=telefone
        )
        
        if validacao['duplicado']:
            raise ValueError(f"{validacao['mensagem']} (Critério: {validacao['critério']})")
        
        cursor.execute('''
            INSERT INTO fornecedores (nome, cnpj, telefone, email, endereco, cidade, 
                                    estado, cep, contato_pessoa, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (nome, cnpj, telefone, email, endereco, cidade, estado, cep, contato_pessoa, observacoes))
        
        fornecedor_id = cursor.fetchone()[0]
        conn.commit()
        return fornecedor_id
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar fornecedor: {e}")
        return None
    finally:
        conn.close()

def editar_fornecedor(fornecedor_id, nome, cnpj=None, telefone=None, email=None, endereco=None, 
                     cidade=None, estado=None, cep=None, contato_pessoa=None, observacoes=None):
    """
    Edita um fornecedor existente com validação robusta de duplicação.
    
    Raises:
        ValueError: Se já existe outro fornecedor com os mesmos dados
    
    Returns:
        bool: True se atualizado com sucesso, False caso contrário
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Validar duplicação usando a função robusta (excluindo este fornecedor)
        validacao = validar_fornecedor_duplicado(
            nome=nome,
            cnpj=cnpj,
            email=email,
            telefone=telefone,
            fornecedor_id_excluir=fornecedor_id
        )
        
        if validacao['duplicado']:
            raise ValueError(f"{validacao['mensagem']} (Critério: {validacao['critério']})")
        
        cursor.execute('''
            UPDATE fornecedores 
            SET nome = %s, cnpj = %s, telefone = %s, email = %s, endereco = %s, 
                cidade = %s, estado = %s, cep = %s, contato_pessoa = %s, observacoes = %s
            WHERE id = %s
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
        cursor.execute('SELECT COUNT(*) FROM produtos WHERE fornecedor_id = %s AND ativo = TRUE', (fornecedor_id,))
        produtos_vinculados = cursor.fetchone()[0]
        
        if produtos_vinculados > 0:
            # Se há produtos vinculados, apenas desativar
            cursor.execute('UPDATE fornecedores SET ativo = FALSE WHERE id = %s', (fornecedor_id,))
        else:
            # Se não há produtos vinculados, pode deletar fisicamente
            cursor.execute('DELETE FROM fornecedores WHERE id = %s', (fornecedor_id,))
        
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
            WHERE ativo = TRUE 
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
        cursor.execute('SELECT COUNT(*) FROM fornecedores WHERE ativo = TRUE')
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
            WHERE p.fornecedor_id = %s AND p.ativo = TRUE
            ORDER BY p.nome
        ''', (fornecedor_id,))
        
        produtos = []
        for row in cursor.fetchall():
            produtos.append({
                'id': row[0],
                'nome': row[1],
                'preco': row[2] if row[2] is not None else 0,
                'estoque': row[3],
                'preco_custo': row[4] or 0,
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
    conn = get_db_connection()
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
                    cursor.execute('SELECT id FROM fornecedores WHERE nome LIKE %s LIMIT 1', (f'%{fornecedor_cliente}%',))
                    fornecedor_result = cursor.fetchone()
                    if fornecedor_result:
                        fornecedor_id = fornecedor_result[0]
                
                # Criar conta a pagar
                cursor.execute('''
                    INSERT INTO contas_pagar (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, lancamento_financeiro_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id, lancamento_id))
                
                conta_id = cursor.fetchone()[0]
                
                # Atualizar lançamento com referência à conta
                cursor.execute('''
                    UPDATE lancamentos_financeiros 
                    SET conta_pagar_id = %s
                    WHERE id = %s
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
                    cursor.execute('SELECT id FROM clientes WHERE nome LIKE %s LIMIT 1', (f'%{fornecedor_cliente}%',))
                    cliente_result = cursor.fetchone()
                    if cliente_result:
                        cliente_id = cliente_result[0]
                
                # Criar conta a receber
                cursor.execute('''
                    INSERT INTO contas_receber (descricao, valor, data_vencimento, cliente_id, observacoes)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (descricao, valor, data_vencimento, cliente_id, observacoes))
                
                conta_id = cursor.fetchone()[0]
                
                # Atualizar lançamento com referência à conta
                cursor.execute('''
                    UPDATE lancamentos_financeiros 
                    SET conta_receber_id = %s
                    WHERE id = %s
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
    garantir_estrutura_fiscal()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Primeiro, verificar se a tabela existe (PostgreSQL)
        cursor.execute('''
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'configuracoes_empresa'
        ''')
        
        if not cursor.fetchone():
            print("Tabela configuracoes_empresa não existe, retornando configurações padrão")
            return obter_configuracoes_padrao()
        
        cursor.execute('''
            SELECT nome_empresa, cnpj, ie, crt, cnae, codigo_municipio_ibge,
                   ambiente_fiscal, serie_nfe,
                   endereco, cidade, estado, cep, telefone, email, website, logo_path, observacoes
            FROM configuracoes_empresa 
            ORDER BY id DESC 
            LIMIT 1
        ''')
        
        resultado = cursor.fetchone()
        if resultado:
            config = {
                'nome_empresa': resultado[0] or 'FG AUTO PEÇAS',
                'cnpj': resultado[1] or '',
                'ie': resultado[2] or '',
                'crt': resultado[3] or '1',
                'cnae': resultado[4] or '',
                'codigo_municipio_ibge': resultado[5] or '',
                'ambiente_fiscal': resultado[6] or 'homologacao',
                'serie_nfe': resultado[7] or 1,
                'endereco': resultado[8] or 'Rua Exemplo, 123 - Centro',
                'cidade': resultado[9] or '',
                'estado': resultado[10] or '',
                'cep': resultado[11] or '',
                'telefone': resultado[12] or '(00) 0000-0000',
                'email': resultado[13] or 'contato@fgautopecas.com.br',
                'website': resultado[14] or '',
                'logo_path': resultado[15] or '',
                'observacoes': resultado[16] or ''
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
        'ie': '',
        'crt': '1',
        'cnae': '',
        'codigo_municipio_ibge': '',
        'ambiente_fiscal': 'homologacao',
        'serie_nfe': 1,
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
    garantir_estrutura_fiscal()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe configuração
        cursor.execute("SELECT COUNT(*) FROM configuracoes_empresa")
        existe = cursor.fetchone()[0] > 0
        
        if existe:
            # Atualizar existente
            cursor.execute('''
                UPDATE configuracoes_empresa SET
                    nome_empresa = %s, cnpj = %s, ie = %s, crt = %s, cnae = %s, codigo_municipio_ibge = %s,
                    ambiente_fiscal = %s, serie_nfe = %s,
                    endereco = %s, cidade = %s, estado = %s, cep = %s, telefone = %s, email = %s, 
                    website = %s, observacoes = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM configuracoes_empresa ORDER BY id DESC LIMIT 1)
            ''', (
                dados.get('nome_empresa', ''), dados.get('cnpj', ''), dados.get('ie', ''), dados.get('crt', '1'),
                dados.get('cnae', ''), dados.get('codigo_municipio_ibge', ''),
                dados.get('ambiente_fiscal', 'homologacao'), int(dados.get('serie_nfe', 1) or 1),
                dados.get('endereco', ''), dados.get('cidade', ''), dados.get('estado', ''), dados.get('cep', ''),
                dados.get('telefone', ''), dados.get('email', ''), dados.get('website', ''),
                dados.get('observacoes', '')
            ))
        else:
            # Inserir nova
            cursor.execute('''
                INSERT INTO configuracoes_empresa (
                    nome_empresa, cnpj, ie, crt, cnae, codigo_municipio_ibge, ambiente_fiscal, serie_nfe,
                    endereco, cidade, estado, cep, telefone, email, website, observacoes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                dados.get('nome_empresa', ''), dados.get('cnpj', ''), dados.get('ie', ''), dados.get('crt', '1'),
                dados.get('cnae', ''), dados.get('codigo_municipio_ibge', ''),
                dados.get('ambiente_fiscal', 'homologacao'), int(dados.get('serie_nfe', 1) or 1),
                dados.get('endereco', ''), dados.get('cidade', ''), dados.get('estado', ''), dados.get('cep', ''),
                dados.get('telefone', ''), dados.get('email', ''), dados.get('website', ''),
                dados.get('observacoes', '')
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o lançamento existe e está pendente
        cursor.execute('SELECT id, status FROM lancamentos_financeiros WHERE id = %s', (lancamento_id,))
        lancamento = cursor.fetchone()
        
        if not lancamento:
            return False, "Lançamento não encontrado"
        
        if lancamento[1] != 'pendente':
            return False, "Só é possível editar lançamentos pendentes"
        
        # Atualizar o lançamento
        cursor.execute('''
            UPDATE lancamentos_financeiros 
            SET categoria = %s, descricao = %s, valor = %s, data_vencimento = %s,
                fornecedor_cliente = %s, numero_documento = %s, observacoes = %s
            WHERE id = %s
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o lançamento existe
        cursor.execute('SELECT id, tipo, status FROM lancamentos_financeiros WHERE id = %s', (lancamento_id,))
        lancamento = cursor.fetchone()
        
        if not lancamento:
            return False, "Lançamento não encontrado"
        
        if lancamento[2] == novo_status:
            return False, f"Lançamento já está com status '{novo_status}'"
        
        # Se não foi fornecida data de pagamento, usar data atual
        if novo_status == 'pago' and not data_pagamento:
            data_pagamento = hoje_br().isoformat()
        
        # Atualizar o status do lançamento
        cursor.execute('''
            UPDATE lancamentos_financeiros 
            SET status = %s, forma_pagamento = %s, data_pagamento = %s
            WHERE id = %s
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
    conn = get_db_connection()
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
            WHERE v.data_venda BETWEEN %s AND %s
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o lançamento existe
        cursor.execute('''
            SELECT id, tipo, status, conta_pagar_id, conta_receber_id 
            FROM lancamentos_financeiros 
            WHERE id = %s
        ''', (lancamento_id,))
        lancamento = cursor.fetchone()
        
        if not lancamento:
            return False, "Lançamento não encontrado"
        
        # Não permitir deletar lançamentos já pagos/recebidos
        if lancamento[2] == 'pago':
            return False, "Não é possível deletar lançamentos já pagos/recebidos"
        
        # Deletar contas associadas se existirem
        if lancamento[3]:  # conta_pagar_id
            cursor.execute('DELETE FROM contas_pagar WHERE id = %s', (lancamento[3],))
        
        if lancamento[4]:  # conta_receber_id
            cursor.execute('DELETE FROM contas_receber WHERE id = %s', (lancamento[4],))
        
        # Deletar o lançamento
        cursor.execute('DELETE FROM lancamentos_financeiros WHERE id = %s', (lancamento_id,))
        
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
        cursor.execute('SELECT id, total, forma_pagamento FROM vendas WHERE id = %s', (venda_id,))
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
                WHERE iv.venda_id = %s
            ''', (venda_id,))
            itens_venda = cursor.fetchall()
            
            # Restaurar estoque de cada produto
            for produto_id, nome_produto, quantidade in itens_venda:
                cursor.execute('''
                    UPDATE produtos 
                    SET estoque = estoque + %s
                    WHERE id = %s
                ''', (quantidade, produto_id))
                
                resultado['estoque_restaurado'][nome_produto] = quantidade
        
        # Contar e deletar itens da venda
        cursor.execute('SELECT COUNT(*) FROM itens_venda WHERE venda_id = %s', (venda_id,))
        resultado['itens_deletados'] = cursor.fetchone()[0]
        cursor.execute('DELETE FROM itens_venda WHERE venda_id = %s', (venda_id,))
        
        # Contar e deletar movimentações de caixa relacionadas à venda
        cursor.execute('SELECT COUNT(*) FROM caixa_movimentacoes WHERE venda_id = %s', (venda_id,))
        resultado['movimentacoes_caixa_deletadas'] = cursor.fetchone()[0]
        cursor.execute('DELETE FROM caixa_movimentacoes WHERE venda_id = %s', (venda_id,))
        
        # Contar e deletar contas a receber relacionadas à venda
        cursor.execute('SELECT COUNT(*) FROM contas_receber WHERE venda_id = %s', (venda_id,))
        resultado['contas_receber_deletadas'] = cursor.fetchone()[0]
        cursor.execute('DELETE FROM contas_receber WHERE venda_id = %s', (venda_id,))
        
        # Deletar a venda
        cursor.execute('DELETE FROM vendas WHERE id = %s', (venda_id,))
        
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
                    SET estoque = estoque + %s
                    WHERE id = %s
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

def obter_marcas_cadastradas():
    """Retorna lista de todas as marcas únicas cadastradas no sistema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar marcas únicas de produtos
        cursor.execute('''
            SELECT DISTINCT marca
            FROM produtos
            WHERE marca IS NOT NULL AND marca != ''
            ORDER BY marca
        ''')
        marcas_produtos = [row[0] for row in cursor.fetchall()]
        
        # Buscar marcas únicas de movimentações
        cursor.execute('''
            SELECT DISTINCT marca
            FROM movimentacoes
            WHERE marca IS NOT NULL AND marca != ''
            ORDER BY marca
        ''')
        marcas_movimentacoes = [row[0] for row in cursor.fetchall()]
        
        # Combinar e eliminar duplicatas
        marcas = sorted(list(set(marcas_produtos + marcas_movimentacoes)))
        
        conn.close()
        return marcas
        
    except Exception as e:
        print(f"Erro ao obter marcas: {e}")
        conn.close()
        return []

def obter_categorias_cadastradas():
    """Retorna lista de todas as categorias únicas cadastradas no sistema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar categorias únicas de produtos
        cursor.execute('''
            SELECT DISTINCT categoria
            FROM produtos
            WHERE categoria IS NOT NULL AND categoria != ''
            ORDER BY categoria
        ''')
        categorias_produtos = [row[0] for row in cursor.fetchall()]
        
        # Buscar categorias únicas de movimentações
        cursor.execute('''
            SELECT DISTINCT categoria
            FROM movimentacoes
            WHERE categoria IS NOT NULL AND categoria != ''
            ORDER BY categoria
        ''')
        categorias_movimentacoes = [row[0] for row in cursor.fetchall()]
        
        # Combinar e eliminar duplicatas
        categorias = sorted(list(set(categorias_produtos + categorias_movimentacoes)))
        
        conn.close()
        return categorias
        
    except Exception as e:
        print(f"Erro ao obter categorias: {e}")
        conn.close()
        return []


# ========================================
# FUNÇÕES ROBUSTAS DE VALIDAÇÃO DE FORNECEDORES
# ========================================

def validar_fornecedor_duplicado(nome=None, cnpj=None, email=None, telefone=None, fornecedor_id_excluir=None):
    """
    Valida se um fornecedor já está cadastrado no sistema usando múltiplos critérios.
    
    Busca por:
    - CNPJ (com e sem formatação)
    - Nome (comparação com fuzzy matching para variações)
    - Email
    - Combinação de critérios
    
    Args:
        nome: Nome do fornecedor
        cnpj: CNPJ (formatado ou não)
        email: Email do fornecedor
        telefone: Telefone do fornecedor
        fornecedor_id_excluir: ID do fornecedor a excluir da busca (para edição)
    
    Returns:
        Dict com resultado: {
            'duplicado': bool,
            'fornecedor_existente': dict or None,
            'critério': str (qual critério detectou a duplicação),
            'mensagem': str
        }
    """
    import re
    from difflib import SequenceMatcher
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar todos os fornecedores (exceto o que está sendo editado)
        query = 'SELECT id, nome, cnpj, email, telefone FROM fornecedores WHERE ativo = TRUE'
        params = []
        
        if fornecedor_id_excluir:
            query += ' AND id != %s'
            params.append(fornecedor_id_excluir)
        
        cursor.execute(query, params)
        fornecedores_existentes = cursor.fetchall()
        
        # 1. Verificar CNPJ (com normalização)
        if cnpj:
            cnpj_normalizado = normalizar_cnpj(cnpj)
            if cnpj_normalizado:
                for forn in fornecedores_existentes:
                    if forn[2]:  # Se fornecedor existente tem CNPJ
                        if normalizar_cnpj(forn[2]) == cnpj_normalizado:
                            return {
                                'duplicado': True,
                                'fornecedor_existente': {
                                    'id': forn[0],
                                    'nome': forn[1],
                                    'cnpj': forn[2],
                                    'email': forn[3],
                                    'telefone': forn[4]
                                },
                                'critério': 'CNPJ',
                                'mensagem': f"Fornecedor '{forn[1]}' já cadastrado com CNPJ {forn[2]}"
                            }
        
        # 2. Verificar Email (idêntico)
        if email and email.strip():
            email_lower = email.lower().strip()
            for forn in fornecedores_existentes:
                if forn[3]:  # Se fornecedor existente tem email
                    if forn[3].lower().strip() == email_lower:
                        return {
                            'duplicado': True,
                            'fornecedor_existente': {
                                'id': forn[0],
                                'nome': forn[1],
                                'cnpj': forn[2],
                                'email': forn[3],
                                'telefone': forn[4]
                            },
                            'critério': 'Email',
                            'mensagem': f"Fornecedor '{forn[1]}' já cadastrado com email {forn[3]}"
                        }
        
        # 3. Verificar Nome (com fuzzy matching para variações)
        if nome:
            nome_limpo = re.sub(r'[^a-záéíóúâêô\s]', '', nome.lower().strip())
            
            for forn in fornecedores_existentes:
                forn_nome_limpo = re.sub(r'[^a-záéíóúâêô\s]', '', forn[1].lower().strip())
                
                # Comparação exata após limpeza
                if nome_limpo == forn_nome_limpo:
                    return {
                        'duplicado': True,
                        'fornecedor_existente': {
                            'id': forn[0],
                            'nome': forn[1],
                            'cnpj': forn[2],
                            'email': forn[3],
                            'telefone': forn[4]
                        },
                        'critério': 'Nome (exato)',
                        'mensagem': f"Fornecedor '{forn[1]}' já cadastrado no sistema"
                    }
                
                # Comparação com fuzzy matching (89% de similitude)
                similaridade = SequenceMatcher(None, nome_limpo, forn_nome_limpo).ratio()
                if similaridade >= 0.89:
                    return {
                        'duplicado': True,
                        'fornecedor_existente': {
                            'id': forn[0],
                            'nome': forn[1],
                            'cnpj': forn[2],
                            'email': forn[3],
                            'telefone': forn[4]
                        },
                        'critério': 'Nome (similar)',
                        'mensagem': f"Possível duplicação: já existe fornecedor '{forn[1]}' similar (89% de similaridade)"
                    }
        
        # 4. Verificar Telefone (se fornecido e nenhuma duplicação anterior)
        if telefone and telefone.strip():
            telefone_normalizado = re.sub(r'\D', '', telefone)
            
            if telefone_normalizado:
                for forn in fornecedores_existentes:
                    if forn[4]:  # Se fornecedor existente tem telefone
                        if re.sub(r'\D', '', forn[4]) == telefone_normalizado:
                            return {
                                'duplicado': True,
                                'fornecedor_existente': {
                                    'id': forn[0],
                                    'nome': forn[1],
                                    'cnpj': forn[2],
                                    'email': forn[3],
                                    'telefone': forn[4]
                                },
                                'critério': 'Telefone',
                                'mensagem': f"Fornecedor '{forn[1]}' já cadastrado com telefone {forn[4]}"
                            }
        
        # Nenhuma duplicação encontrada
        return {
            'duplicado': False,
            'fornecedor_existente': None,
            'critério': None,
            'mensagem': 'Fornecedor não encontrado no sistema'
        }
        
    except Exception as e:
        print(f"Erro ao validar fornecedor: {e}")
        return {
            'duplicado': False,
            'fornecedor_existente': None,
            'critério': 'erro',
            'mensagem': f'Erro ao validar: {str(e)}'
        }
    finally:
        conn.close()


def buscar_fornecedor_melhorado(nome=None, cnpj=None, email=None):
    """
    Busca um fornecedor usando múltiplos critérios com precedência.
    
    Precedência:
    1. CNPJ (normalizado)
    2. Email
    3. Nome (com fuzzy matching)
    
    Returns:
        Dict com dados do fornecedor ou None
    """
    validacao = validar_fornecedor_duplicado(
        nome=nome, 
        cnpj=cnpj, 
        email=email
    )
    
    if validacao['duplicado']:
        return validacao['fornecedor_existente']
    
    return None


def adicionar_ou_atualizar_fornecedor_automatico(nome, cnpj=None, email=None, telefone=None, 
                                                  endereco=None, cidade=None, estado=None, 
                                                  cep=None, observacoes=None):
    """
    Adiciona um novo fornecedor ou retorna o existente se já cadastrado.
    Evita duplicações usando validação robusta.
    
    Returns:
        Dict: {
            'sucesso': bool,
            'fornecedor_id': int,
            'criado': bool (True se foi criado, False se já existia),
            'fornecedor': dict,
            'mensagem': str
        }
    """
    try:
        # Validar se já existe
        validacao = validar_fornecedor_duplicado(
            nome=nome,
            cnpj=cnpj,
            email=email,
            telefone=telefone
        )
        
        if validacao['duplicado']:
            return {
                'sucesso': True,
                'fornecedor_id': validacao['fornecedor_existente']['id'],
                'criado': False,
                'fornecedor': validacao['fornecedor_existente'],
                'mensagem': f"Fornecedor já cadastrado: {validacao['fornecedor_existente']['nome']}"
            }
        
        # Criar novo fornecedor
        fornecedor_id = adicionar_fornecedor(
            nome=nome,
            cnpj=cnpj,
            email=email,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            cep=cep,
            observacoes=observacoes
        )
        
        if fornecedor_id:
            fornecedor = buscar_fornecedor(fornecedor_id)
            return {
                'sucesso': True,
                'fornecedor_id': fornecedor_id,
                'criado': True,
                'fornecedor': fornecedor,
                'mensagem': f"Novo fornecedor '{nome}' cadastrado com sucesso"
            }
        else:
            return {
                'sucesso': False,
                'fornecedor_id': None,
                'criado': False,
                'fornecedor': None,
                'mensagem': 'Erro ao cadastrar fornecedor'
            }
    
    except Exception as e:
        print(f"Erro ao adicionar/atualizar fornecedor: {e}")
        return {
            'sucesso': False,
            'fornecedor_id': None,
            'criado': False,
            'fornecedor': None,
            'mensagem': f'Erro: {str(e)}'
        }


# =========================
# FUNCOES FISCAIS (NF-e)
# =========================
def garantir_estrutura_fiscal():
    """Garante que tabelas e colunas fiscais existam no banco."""
    global _fiscal_schema_checked

    if _fiscal_schema_checked:
        return True

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        add_column_if_not_exists(cursor, conn, 'clientes', "ie TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "indicador_ie TEXT DEFAULT '9'")
        add_column_if_not_exists(cursor, conn, 'clientes', "tipo_pessoa TEXT DEFAULT 'FISICA'")
        add_column_if_not_exists(cursor, conn, 'clientes', "bairro TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "numero TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "complemento TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "codigo_municipio_ibge TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "estado TEXT")
        add_column_if_not_exists(cursor, conn, 'clientes', "cep TEXT")

        add_column_if_not_exists(cursor, conn, 'produtos', "cest TEXT")
        add_column_if_not_exists(cursor, conn, 'produtos', "cfop TEXT DEFAULT '5102'")
        add_column_if_not_exists(cursor, conn, 'produtos', "origem_mercadoria TEXT DEFAULT '0'")
        add_column_if_not_exists(cursor, conn, 'produtos', "csosn TEXT DEFAULT '102'")
        add_column_if_not_exists(cursor, conn, 'produtos', "cst_icms TEXT")
        add_column_if_not_exists(cursor, conn, 'produtos', "cst_pis TEXT DEFAULT '01'")
        add_column_if_not_exists(cursor, conn, 'produtos', "cst_cofins TEXT DEFAULT '01'")
        add_column_if_not_exists(cursor, conn, 'produtos', "aliquota_icms DECIMAL(5,2) DEFAULT 0")
        add_column_if_not_exists(cursor, conn, 'produtos', "aliquota_pis DECIMAL(5,2) DEFAULT 0")
        add_column_if_not_exists(cursor, conn, 'produtos', "aliquota_cofins DECIMAL(5,2) DEFAULT 0")

        add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "ie TEXT")
        add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "crt TEXT DEFAULT '1'")
        add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "cnae TEXT")
        add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "codigo_municipio_ibge TEXT")
        add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "ambiente_fiscal TEXT DEFAULT 'homologacao'")
        add_column_if_not_exists(cursor, conn, 'configuracoes_empresa', "serie_nfe INTEGER DEFAULT 1")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fiscal_nfe_numeracao (
                id SERIAL PRIMARY KEY,
                ano INTEGER NOT NULL,
                serie INTEGER NOT NULL DEFAULT 1,
                ultimo_numero INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (ano, serie)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fiscal_nfe (
                id SERIAL PRIMARY KEY,
                venda_id INTEGER NOT NULL UNIQUE,
                numero INTEGER NOT NULL,
                serie INTEGER NOT NULL DEFAULT 1,
                modelo TEXT NOT NULL DEFAULT '55',
                ambiente TEXT NOT NULL DEFAULT 'homologacao',
                status TEXT NOT NULL DEFAULT 'rascunho',
                chave_acesso TEXT,
                protocolo_autorizacao TEXT,
                motivo_status TEXT,
                xml_enviado TEXT,
                xml_autorizado TEXT,
                danfe_url TEXT,
                payload_json JSONB,
                response_json JSONB,
                emitida_por INTEGER,
                data_emissao TIMESTAMP,
                data_autorizacao TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (venda_id) REFERENCES vendas (id) ON DELETE CASCADE,
                FOREIGN KEY (emitida_por) REFERENCES usuarios (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fiscal_nfe_itens (
                id SERIAL PRIMARY KEY,
                nfe_id INTEGER NOT NULL,
                venda_item_id INTEGER,
                produto_id INTEGER,
                descricao TEXT NOT NULL,
                ncm TEXT,
                cest TEXT,
                cfop TEXT,
                unidade TEXT,
                origem_mercadoria TEXT,
                csosn TEXT,
                cst_icms TEXT,
                cst_pis TEXT,
                cst_cofins TEXT,
                aliquota_icms DECIMAL(5,2) DEFAULT 0,
                aliquota_pis DECIMAL(5,2) DEFAULT 0,
                aliquota_cofins DECIMAL(5,2) DEFAULT 0,
                quantidade DECIMAL(12,4) NOT NULL,
                valor_unitario DECIMAL(12,4) NOT NULL,
                valor_total DECIMAL(12,4) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (nfe_id) REFERENCES fiscal_nfe (id) ON DELETE CASCADE,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fiscal_nfe_eventos (
                id SERIAL PRIMARY KEY,
                nfe_id INTEGER NOT NULL,
                tipo_evento TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'registrado',
                protocolo TEXT,
                justificativa TEXT,
                request_json JSONB,
                response_json JSONB,
                usuario_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (nfe_id) REFERENCES fiscal_nfe (id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fiscal_nfe_status ON fiscal_nfe(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fiscal_nfe_venda_id ON fiscal_nfe(venda_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fiscal_nfe_eventos_nfe_id ON fiscal_nfe_eventos(nfe_id)")

        conn.commit()
        _fiscal_schema_checked = True
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao garantir estrutura fiscal: {e}")
        return False
    finally:
        conn.close()


def reservar_proximo_numero_nfe(serie=1, ano=None, conn=None, cursor=None):
    """
    Reserva o proximo numero de NF-e de forma transacional.
    Se conn/cursor forem passados, usa a mesma transacao.
    """
    garantir_estrutura_fiscal()
    ano = ano or hoje_br().year
    close_conn = False

    if conn is None or cursor is None:
        conn = get_db_connection()
        cursor = conn.cursor()
        close_conn = True

    try:
        cursor.execute(
            '''
            SELECT id, ultimo_numero
            FROM fiscal_nfe_numeracao
            WHERE ano = %s AND serie = %s
            FOR UPDATE
            ''',
            (ano, serie)
        )
        row = cursor.fetchone()

        if row:
            numeracao_id, ultimo_numero = row
            proximo = int(ultimo_numero) + 1
            cursor.execute(
                '''
                UPDATE fiscal_nfe_numeracao
                SET ultimo_numero = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                ''',
                (proximo, numeracao_id)
            )
        else:
            proximo = 1
            cursor.execute(
                '''
                INSERT INTO fiscal_nfe_numeracao (ano, serie, ultimo_numero)
                VALUES (%s, %s, %s)
                ''',
                (ano, serie, proximo)
            )

        if close_conn:
            conn.commit()

        return proximo
    except Exception:
        if close_conn:
            conn.rollback()
        raise
    finally:
        if close_conn:
            conn.close()


def _registrar_snapshot_itens_nfe(cursor, nfe_id, venda_id):
    """Registra snapshot fiscal dos itens da venda na NF-e."""
    cursor.execute(
        '''
        SELECT iv.id, iv.produto_id, p.nome, p.ncm, p.cest, p.cfop, p.unidade,
               p.origem_mercadoria, p.csosn, p.cst_icms, p.cst_pis, p.cst_cofins,
               p.aliquota_icms, p.aliquota_pis, p.aliquota_cofins,
               iv.quantidade, iv.preco_unitario, iv.subtotal
        FROM itens_venda iv
        JOIN produtos p ON p.id = iv.produto_id
        WHERE iv.venda_id = %s
        ORDER BY iv.id
        ''',
        (venda_id,)
    )
    itens = cursor.fetchall()

    cursor.execute("DELETE FROM fiscal_nfe_itens WHERE nfe_id = %s", (nfe_id,))

    for item in itens:
        cursor.execute(
            '''
            INSERT INTO fiscal_nfe_itens (
                nfe_id, venda_item_id, produto_id, descricao, ncm, cest, cfop, unidade,
                origem_mercadoria, csosn, cst_icms, cst_pis, cst_cofins,
                aliquota_icms, aliquota_pis, aliquota_cofins,
                quantidade, valor_unitario, valor_total
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
            ''',
            (
                nfe_id, item[0], item[1], item[2], item[3], item[4], item[5], item[6] or 'UN',
                item[7], item[8], item[9], item[10], item[11],
                item[12] or 0, item[13] or 0, item[14] or 0,
                item[15], item[16], item[17]
            )
        )


def criar_rascunho_nfe_para_venda(venda_id, usuario_id=None, ambiente='homologacao', serie=1):
    """Cria rascunho fiscal para uma venda e retorna os dados da NF-e."""
    if not garantir_estrutura_fiscal():
        return {'sucesso': False, 'erro': 'Nao foi possivel inicializar a estrutura fiscal.'}

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("SELECT id FROM vendas WHERE id = %s", (venda_id,))
        venda = cursor.fetchone()
        if not venda:
            return {'sucesso': False, 'erro': f'Venda {venda_id} nao encontrada.'}

        cursor.execute(
            '''
            SELECT *
            FROM fiscal_nfe
            WHERE venda_id = %s
            LIMIT 1
            ''',
            (venda_id,)
        )
        existente = cursor.fetchone()
        if existente:
            _registrar_snapshot_itens_nfe(cursor, existente['id'], venda_id)
            conn.commit()
            return {'sucesso': True, 'criada': False, 'nfe': dict(existente)}

        numero_nfe = reservar_proximo_numero_nfe(serie=serie, conn=conn, cursor=cursor)
        cursor.execute(
            '''
            INSERT INTO fiscal_nfe (
                venda_id, numero, serie, ambiente, status, emitida_por, data_emissao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            ''',
            (venda_id, numero_nfe, serie, ambiente, 'rascunho', usuario_id, agora_br())
        )
        nfe = cursor.fetchone()
        _registrar_snapshot_itens_nfe(cursor, nfe['id'], venda_id)
        conn.commit()
        return {'sucesso': True, 'criada': True, 'nfe': dict(nfe)}
    except Exception as e:
        conn.rollback()
        return {'sucesso': False, 'erro': f'Erro ao criar rascunho NF-e: {str(e)}'}
    finally:
        conn.close()


def obter_nfe_por_venda(venda_id):
    """Retorna os dados da NF-e vinculada a venda."""
    if not garantir_estrutura_fiscal():
        return None

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute(
            '''
            SELECT *
            FROM fiscal_nfe
            WHERE venda_id = %s
            LIMIT 1
            ''',
            (venda_id,)
        )
        nfe = cursor.fetchone()
        if not nfe:
            return None
        return dict(nfe)
    except Exception as e:
        print(f"Erro ao obter NF-e da venda {venda_id}: {e}")
        return None
    finally:
        conn.close()


def obter_nfe_por_id(nfe_id):
    """Retorna os dados da NF-e por ID."""
    if not garantir_estrutura_fiscal():
        return None

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("SELECT * FROM fiscal_nfe WHERE id = %s", (nfe_id,))
        nfe = cursor.fetchone()
        return dict(nfe) if nfe else None
    except Exception as e:
        print(f"Erro ao obter NF-e #{nfe_id}: {e}")
        return None
    finally:
        conn.close()


def atualizar_dados_nfe(nfe_id, **campos):
    """Atualiza campos da fiscal_nfe dinamicamente."""
    if not campos:
        return True

    if not garantir_estrutura_fiscal():
        return False

    campos_permitidos = {
        'status', 'chave_acesso', 'protocolo_autorizacao', 'motivo_status',
        'xml_enviado', 'xml_autorizado', 'danfe_url', 'payload_json',
        'response_json', 'data_emissao', 'data_autorizacao', 'ambiente'
    }

    updates = []
    params = []

    for chave, valor in campos.items():
        if chave not in campos_permitidos:
            continue

        if chave in ('payload_json', 'response_json') and valor is not None:
            updates.append(f"{chave} = %s")
            params.append(psycopg2.extras.Json(valor))
        else:
            updates.append(f"{chave} = %s")
            params.append(valor)

    if not updates:
        return True

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(nfe_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"UPDATE fiscal_nfe SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar NF-e #{nfe_id}: {e}")
        return False
    finally:
        conn.close()


def registrar_evento_nfe(nfe_id, tipo_evento, status='registrado', protocolo=None, justificativa=None,
                         request_json=None, response_json=None, usuario_id=None):
    """Registra um evento fiscal da NF-e."""
    if not garantir_estrutura_fiscal():
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''
            INSERT INTO fiscal_nfe_eventos (
                nfe_id, tipo_evento, status, protocolo, justificativa,
                request_json, response_json, usuario_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                nfe_id, tipo_evento, status, protocolo, justificativa,
                psycopg2.extras.Json(request_json) if request_json is not None else None,
                psycopg2.extras.Json(response_json) if response_json is not None else None,
                usuario_id
            )
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao registrar evento da NF-e #{nfe_id}: {e}")
        return False
    finally:
        conn.close()


def obter_itens_nfe(nfe_id):
    """Retorna os itens fiscais de uma NF-e."""
    if not garantir_estrutura_fiscal():
        return []

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute(
            '''
            SELECT *
            FROM fiscal_nfe_itens
            WHERE nfe_id = %s
            ORDER BY id
            ''',
            (nfe_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter itens da NF-e #{nfe_id}: {e}")
        return []
    finally:
        conn.close()


def obter_dados_venda_para_nfe(venda_id):
    """Carrega dados fiscais completos da venda, emitente, destinatario e itens."""
    if not garantir_estrutura_fiscal():
        return {'sucesso': False, 'erro': 'Estrutura fiscal indisponivel.'}

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute(
            '''
            SELECT
                v.id, v.cliente_id, v.total, v.forma_pagamento, v.desconto, v.observacoes,
                v.data_venda, v.usuario_id,
                COALESCE(to_jsonb(c)->>'nome', 'Cliente Avulso') AS cliente_nome,
                COALESCE(to_jsonb(c)->>'telefone', '') AS cliente_telefone,
                COALESCE(to_jsonb(c)->>'email', '') AS cliente_email,
                COALESCE(to_jsonb(c)->>'cpf_cnpj', '') AS cliente_cpf_cnpj,
                COALESCE(to_jsonb(c)->>'ie', '') AS cliente_ie,
                COALESCE(to_jsonb(c)->>'indicador_ie', '') AS cliente_indicador_ie,
                COALESCE(to_jsonb(c)->>'tipo_pessoa', '') AS cliente_tipo_pessoa,
                COALESCE(to_jsonb(c)->>'endereco', '') AS cliente_endereco,
                COALESCE(to_jsonb(c)->>'bairro', '') AS cliente_bairro,
                COALESCE(to_jsonb(c)->>'numero', '') AS cliente_numero,
                COALESCE(to_jsonb(c)->>'complemento', '') AS cliente_complemento,
                COALESCE(to_jsonb(c)->>'cidade', '') AS cliente_cidade,
                COALESCE(to_jsonb(c)->>'estado', '') AS cliente_estado,
                COALESCE(to_jsonb(c)->>'cep', '') AS cliente_cep,
                COALESCE(to_jsonb(c)->>'codigo_municipio_ibge', '') AS cliente_codigo_municipio_ibge
            FROM vendas v
            LEFT JOIN clientes c ON c.id = v.cliente_id
            WHERE v.id = %s
            ''',
            (venda_id,)
        )
        venda = cursor.fetchone()
        if not venda:
            return {'sucesso': False, 'erro': f'Venda {venda_id} nao encontrada.'}

        cursor.execute(
            '''
            SELECT
                COALESCE(to_jsonb(cfg)->>'nome_empresa', '') AS nome_empresa,
                COALESCE(to_jsonb(cfg)->>'cnpj', '') AS cnpj,
                COALESCE(to_jsonb(cfg)->>'ie', '') AS ie,
                COALESCE(to_jsonb(cfg)->>'crt', '1') AS crt,
                COALESCE(to_jsonb(cfg)->>'cnae', '') AS cnae,
                COALESCE(to_jsonb(cfg)->>'endereco', '') AS endereco,
                COALESCE(to_jsonb(cfg)->>'cidade', '') AS cidade,
                COALESCE(to_jsonb(cfg)->>'estado', '') AS estado,
                COALESCE(to_jsonb(cfg)->>'cep', '') AS cep,
                COALESCE(to_jsonb(cfg)->>'telefone', '') AS telefone,
                COALESCE(to_jsonb(cfg)->>'email', '') AS email,
                COALESCE(to_jsonb(cfg)->>'codigo_municipio_ibge', '') AS codigo_municipio_ibge,
                COALESCE(to_jsonb(cfg)->>'ambiente_fiscal', 'homologacao') AS ambiente_fiscal,
                CASE
                    WHEN COALESCE(to_jsonb(cfg)->>'serie_nfe', '') ~ '^[0-9]+$'
                    THEN (to_jsonb(cfg)->>'serie_nfe')::INTEGER
                    ELSE 1
                END AS serie_nfe
            FROM configuracoes_empresa cfg
            ORDER BY cfg.id DESC
            LIMIT 1
            '''
        )
        empresa = cursor.fetchone()
        if not empresa:
            return {'sucesso': False, 'erro': 'Configuracoes da empresa nao encontradas.'}

        cursor.execute(
            '''
            SELECT
                iv.id AS venda_item_id, iv.produto_id, iv.quantidade, iv.preco_unitario, iv.subtotal,
                COALESCE(p.nome, 'Produto removido') AS produto_nome,
                COALESCE(to_jsonb(p)->>'ncm', '') AS ncm,
                COALESCE(to_jsonb(p)->>'cest', '') AS cest,
                COALESCE(to_jsonb(p)->>'cfop', '') AS cfop,
                COALESCE(to_jsonb(p)->>'unidade', '') AS unidade,
                COALESCE(to_jsonb(p)->>'origem_mercadoria', '') AS origem_mercadoria,
                COALESCE(to_jsonb(p)->>'csosn', '') AS csosn,
                COALESCE(to_jsonb(p)->>'cst_icms', '') AS cst_icms,
                COALESCE(to_jsonb(p)->>'cst_pis', '') AS cst_pis,
                COALESCE(to_jsonb(p)->>'cst_cofins', '') AS cst_cofins,
                COALESCE(to_jsonb(p)->>'aliquota_icms', '0')::DECIMAL AS aliquota_icms,
                COALESCE(to_jsonb(p)->>'aliquota_pis', '0')::DECIMAL AS aliquota_pis,
                COALESCE(to_jsonb(p)->>'aliquota_cofins', '0')::DECIMAL AS aliquota_cofins
            FROM itens_venda iv
            LEFT JOIN produtos p ON p.id = iv.produto_id
            WHERE iv.venda_id = %s
            ORDER BY iv.id
            ''',
            (venda_id,)
        )
        itens = cursor.fetchall()

        return {
            'sucesso': True,
            'venda': dict(venda),
            'empresa': dict(empresa),
            'itens': [dict(item) for item in itens]
        }
    except Exception as e:
        return {'sucesso': False, 'erro': f'Erro ao montar dados da NF-e: {str(e)}'}
    finally:
        conn.close()


def atualizar_nfe_por_webhook(nfe_id=None, venda_id=None, status=None, payload=None):
    """
    Atualiza NF-e por webhook de provedor externo.
    Permite buscar por nfe_id ou venda_id.
    """
    if not garantir_estrutura_fiscal():
        return {'sucesso': False, 'erro': 'Estrutura fiscal indisponivel.'}

    if not nfe_id and not venda_id:
        return {'sucesso': False, 'erro': 'Informe nfe_id ou venda_id.'}

    nfe = None
    if nfe_id:
        nfe = obter_nfe_por_id(nfe_id)
    elif venda_id:
        nfe = obter_nfe_por_venda(venda_id)

    if not nfe:
        return {'sucesso': False, 'erro': 'NF-e nao encontrada.'}

    campos = {'response_json': payload or {}}
    if status:
        campos['status'] = status

    chave = None
    protocolo = None
    motivo = None
    danfe_url = None
    xml = None

    if payload:
        chave = payload.get('chave_acesso') or payload.get('chave') or payload.get('access_key')
        protocolo = payload.get('protocolo') or payload.get('protocolo_autorizacao') or payload.get('protocol')
        motivo = payload.get('motivo') or payload.get('mensagem') or payload.get('status_motivo')
        danfe_url = payload.get('danfe_url') or payload.get('url_danfe')
        xml = payload.get('xml') or payload.get('xml_autorizado')

    if chave:
        campos['chave_acesso'] = chave
    if protocolo:
        campos['protocolo_autorizacao'] = protocolo
    if motivo:
        campos['motivo_status'] = motivo
    if danfe_url:
        campos['danfe_url'] = danfe_url
    if xml:
        campos['xml_autorizado'] = xml
    if status == 'autorizada':
        campos['data_autorizacao'] = agora_br()

    sucesso = atualizar_dados_nfe(nfe['id'], **campos)
    if not sucesso:
        return {'sucesso': False, 'erro': 'Falha ao atualizar dados da NF-e.'}

    registrar_evento_nfe(
        nfe['id'],
        tipo_evento='webhook_retorno',
        status=status or 'processado',
        protocolo=protocolo,
        justificativa=motivo,
        response_json=payload or {}
    )

    return {'sucesso': True, 'nfe_id': nfe['id']}


if __name__ == "__main__":
    init_db()
    criar_usuario_admin()
    popular_dados_exemplo()
    print("Banco de dados inicializado com sucesso!")
