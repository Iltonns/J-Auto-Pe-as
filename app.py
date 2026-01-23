# SISTEMA DE AUTOPEÇAS - FAMÍLIA
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, date
import json
import os
import uuid
from werkzeug.utils import secure_filename
from functools import wraps
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from dotenv import load_dotenv
import pytz

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do fuso horário brasileiro
TIMEZONE_BR = pytz.timezone('America/Sao_Paulo')

def agora_br():
    """Retorna o datetime atual no horário de Brasília"""
    return datetime.now(TIMEZONE_BR)

def hoje_br():
    """Retorna a data atual no horário de Brasília"""
    return agora_br().date()

# Importar funções do banco de dados
from Minha_autopecas_web.logica_banco import (
    init_db, criar_usuario_admin, verificar_usuario, buscar_usuario_por_id,
    buscar_usuario_por_email, atualizar_senha_usuario, validar_senha_segura,
    criar_usuario, listar_usuarios, editar_usuario, deletar_usuario, verificar_permissao,
    listar_clientes, adicionar_cliente, editar_cliente, deletar_cliente,
    listar_produtos, buscar_produto, adicionar_produto, editar_produto, deletar_produto, obter_produto_por_id,
    deletar_todos_os_produtos, limpar_completamente_produtos,
    registrar_venda, listar_vendas, obter_vendas_do_dia, sincronizar_vendas_com_caixa, obter_venda_por_id, deletar_venda,
    obter_configuracoes_empresa, atualizar_configuracoes_empresa,
    listar_contas_pagar_hoje, adicionar_conta_pagar, pagar_conta, duplicar_conta_pagar, excluir_conta_pagar, obter_conta_pagar, editar_conta_pagar,
    listar_contas_receber_hoje, receber_conta, adicionar_conta_receber, duplicar_conta_receber, excluir_conta_receber, obter_conta_receber, editar_conta_receber,
    listar_contas_pagar_por_periodo, listar_contas_receber_por_periodo,
    obter_estatisticas_dashboard, produtos_estoque_baixo,
    criar_orcamento, listar_orcamentos, obter_orcamento, converter_orcamento_em_venda, atualizar_orcamento, excluir_orcamento,
    popular_dados_exemplo,
    # Novas funções do caixa
    abrir_caixa, fechar_caixa, registrar_movimentacao_caixa, obter_status_caixa, caixa_esta_aberto,
    listar_movimentacoes_caixa, obter_movimentacoes_caixa, criar_lancamento_financeiro, listar_lancamentos_financeiros,
    # Função de importação XML
    importar_produtos_de_xml,
    # Funções de relatórios
    gerar_relatorio_vendas, gerar_relatorio_produtos_mais_vendidos,
    gerar_relatorio_estoque, gerar_relatorio_financeiro,
    # Funções de fornecedores
    listar_fornecedores, buscar_fornecedor, adicionar_fornecedor, editar_fornecedor, 
    deletar_fornecedor, obter_fornecedores_para_select, contar_fornecedores, listar_produtos_por_fornecedor,
    # Funções de sincronização financeira
    sincronizar_lancamentos_com_contas,
    # Novas funções para edição e controle de lançamentos financeiros
    editar_lancamento_financeiro_db, alterar_status_lancamento_financeiro, deletar_lancamento_financeiro_db,
    # Nova função para vendas por período
    listar_vendas_por_periodo,
    # Função para limpar sincronizações incorretas
    limpar_sincronizacoes_incorretas,
    # Funções de movimentações de produtos
    adicionar_movimentacao, listar_movimentacoes, obter_movimentacao_por_id,
    editar_movimentacao, aprovar_movimentacao, rejeitar_movimentacao, cancelar_movimentacao,
    deletar_movimentacao, contar_movimentacoes_pendentes, importar_xml_para_movimentacoes,
    listar_nfes_agrupadas, listar_produtos_por_nfe, aprovar_nfe_completa, rejeitar_nfe_completa, cancelar_nfe_completa,
    vincular_produto_nfe,
    # Funções para autocomplete de marcas e categorias
    obter_marcas_cadastradas, obter_categorias_cadastradas
)

app = Flask(__name__)
# Usar SECRET_KEY do .env ou gerar uma aleatória
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())

# Dicionário para controlar sessões únicas por usuário
# Formato: {user_id: session_id}
active_sessions = {}

# Configuração para upload de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'produtos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB máximo

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para salvar foto do produto
def salvar_foto_produto(file):
    if file and allowed_file(file.filename):
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + '_' + filename
        
        # Criar diretório se não existir
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Salvar arquivo
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Retornar URL relativa para armazenar no banco
        return f'/static/images/produtos/{unique_filename}'
    return None

# Função para remover foto do produto
def remover_foto_produto(foto_url):
    if foto_url:
        try:
            # Converter URL relativa para caminho absoluto
            filename = os.path.basename(foto_url)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Erro ao remover foto: {e}")

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Você precisa fazer login para acessar esta página.'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['id'])
        self.username = user_data['username']
        self.email = user_data.get('email', '')

# Middleware para verificar sessão única
@app.before_request
def check_session_validity():
    """Verifica se a sessão do usuário ainda é válida (não foi substituída por outro login)"""
    if current_user.is_authenticated:
        user_id = current_user.id
        current_session_id = session.get('session_id')
        
        # Verificar se existe uma sessão ativa para este usuário
        if user_id in active_sessions:
            # Se o session_id não corresponde, significa que houve um novo login
            if active_sessions[user_id] != current_session_id:
                # Derrubar esta sessão antiga
                logout_user()
                session.clear()
                flash('Sua sessão foi encerrada porque você fez login em outro dispositivo/navegador.', 'warning')
                return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    user_data = buscar_usuario_por_id(int(user_id))
    if user_data and user_data.get('ativo', False):
        return User(user_data)
    return None

# Decorator para verificar permissões
def required_permission(permission):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not verificar_permissao(current_user.id, permission):
                flash(f'Acesso negado. Você não tem permissão para acessar esta área.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Filtros do Jinja2
@app.template_filter('format_currency')
def format_currency(value):
    """Formata valores como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

@app.template_filter('format_date')
def format_date(value):
    """Formata datas"""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except:
            return value
    if isinstance(value, date):
        return value.strftime('%d/%m/%Y')
    return value

# Função helper para templates
@app.context_processor
def utility_processor():
    def has_permission(permission):
        if current_user.is_authenticated:
            return verificar_permissao(current_user.id, permission)
        return False
    return dict(has_permission=has_permission)

# Verificação de usuário ativo antes de cada requisição
@app.before_request
def check_user_active():
    """Verifica se o usuário logado ainda está ativo antes de cada requisição"""
    # Lista de rotas que não precisam dessa verificação
    excluded_routes = ['login', 'logout', 'static']
    
    # Se não for uma rota excluída e o usuário estiver autenticado
    if request.endpoint not in excluded_routes and current_user.is_authenticated:
        # Verificar se o usuário ainda existe e está ativo
        user_data = buscar_usuario_por_id(int(current_user.id))
        if not user_data or not user_data.get('ativo', False):
            # Usuário foi inativado, fazer logout automaticamente
            logout_user()
            flash('Sua conta foi inativada. Entre em contato com o administrador.', 'error')
            return redirect(url_for('login'))

# ROTAS DE AUTENTICAÇÃO
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = verificar_usuario(username, password)
        if user_data:
            user = User(user_data)
            login_user(user)
            
            # Gerar um ID único para esta sessão
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            
            # Armazenar esta sessão como a sessão ativa do usuário
            # Isso automaticamente invalida qualquer sessão anterior
            active_sessions[user.id] = session_id
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        elif user_data is False:
            # Usuário existe mas está inativo
            flash('Sua conta está inativa. Entre em contato com o administrador.', 'error')
        else:
            # Usuário ou senha incorretos
            flash('Usuário ou senha incorretos!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Remover a sessão ativa do usuário
    user_id = current_user.id
    if user_id in active_sessions:
        del active_sessions[user_id]
    
    logout_user()
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if not email or not nova_senha or not confirmar_senha:
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template('recuperar_senha.html')
        
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem!', 'error')
            return render_template('recuperar_senha.html')
        
        if len(nova_senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres!', 'error')
            return render_template('recuperar_senha.html')
        
        # Buscar usuário por email
        usuario = buscar_usuario_por_email(email)
        if not usuario:
            flash('Email não encontrado em nosso sistema!', 'error')
            return render_template('recuperar_senha.html')
        
        # Atualizar senha
        if atualizar_senha_usuario(usuario['id'], nova_senha):
            flash('Senha atualizada com sucesso! Você já pode fazer login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Erro ao atualizar senha. Tente novamente.', 'error')
    
    return render_template('recuperar_senha.html')

# ROTAS DE CRIAÇÃO DE USUÁRIO (apenas para admins logados)
@app.route('/criar-usuario', methods=['POST'])
@login_required
@required_permission('admin')
def criar_usuario_route():
    try:
        username = request.form['username']
        password = request.form['password']
        nome_completo = request.form['nome_completo']
        email = request.form['email']
        
        # Configurar permissões baseadas no formulário
        permissoes = {
            'vendas': request.form.get('permissao_vendas') == 'on',
            'estoque': request.form.get('permissao_estoque') == 'on',
            'clientes': request.form.get('permissao_clientes') == 'on',
            'financeiro': request.form.get('permissao_financeiro') == 'on',
            'caixa': request.form.get('permissao_caixa') == 'on',
            'relatorios': request.form.get('permissao_relatorios') == 'on',
            'admin': request.form.get('permissao_admin') == 'on',
            'contas_pagar': request.form.get('permissao_contas_pagar') == 'on',
            'contas_receber': request.form.get('permissao_contas_receber') == 'on'
        }
        
        # Usar o ID do usuário atual como created_by
        created_by = current_user.id
        
        success, message = criar_usuario(username, password, nome_completo, email, permissoes, created_by)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        flash(f'Erro ao criar usuário: {str(e)}', 'error')
    
    return redirect(url_for('usuarios'))

# GERENCIAMENTO DE USUÁRIOS (apenas para admins)
@app.route('/usuarios')
@login_required
def usuarios():
    # Verificar se o usuário tem permissão de admin
    if not verificar_permissao(current_user.id, 'admin'):
        flash('Acesso negado. Você não tem permissão para gerenciar usuários.', 'error')
        return redirect(url_for('dashboard'))
    
    usuarios_lista = listar_usuarios()
    return render_template('usuarios.html', usuarios=usuarios_lista)

@app.route('/usuarios/editar/<int:user_id>', methods=['POST'])
@login_required
def editar_usuario_route(user_id):
    # Verificar se o usuário tem permissão de admin
    if not verificar_permissao(current_user.id, 'admin'):
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        nome_completo = request.form.get('nome_completo')
        email = request.form.get('email')
        ativo = request.form.get('ativo') == '1'
        
        permissoes = {
            'vendas': request.form.get('permissao_vendas') == 'on',
            'estoque': request.form.get('permissao_estoque') == 'on',
            'clientes': request.form.get('permissao_clientes') == 'on',
            'financeiro': request.form.get('permissao_financeiro') == 'on',
            'caixa': request.form.get('permissao_caixa') == 'on',
            'relatorios': request.form.get('permissao_relatorios') == 'on',
            'admin': request.form.get('permissao_admin') == 'on',
            'contas_pagar': request.form.get('permissao_contas_pagar') == 'on',
            'contas_receber': request.form.get('permissao_contas_receber') == 'on'
        }
        
        success, message = editar_usuario(user_id, nome_completo, email, permissoes, ativo)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        flash(f'Erro ao editar usuário: {str(e)}', 'error')
    
    return redirect(url_for('usuarios'))

@app.route('/usuarios/deletar/<int:user_id>', methods=['POST'])
@login_required
def deletar_usuario_route(user_id):
    # Verificar se o usuário tem permissão de admin
    if not verificar_permissao(current_user.id, 'admin'):
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    # Não permitir que o usuário delete a si mesmo
    if user_id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'error')
        return redirect(url_for('usuarios'))
    
    try:
        success, message = deletar_usuario(user_id)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        flash(f'Erro ao desativar usuário: {str(e)}', 'error')
    
    return redirect(url_for('usuarios'))

@app.route('/usuarios/trocar-senha/<int:user_id>', methods=['POST'])
@login_required
def trocar_senha_usuario_route(user_id):
    """Rota para trocar senha de um usuário"""
    try:
        # Apenas admins podem trocar senha de outros usuários
        # Usuários podem trocar sua própria senha
        if user_id != current_user.id and not verificar_permissao(current_user.id, 'admin'):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        senha_atual = request.form.get('senha_atual')
        
        # Validações
        if not nova_senha or not confirmar_senha:
            return jsonify({'success': False, 'message': 'Por favor, preencha todos os campos'}), 400
        
        if nova_senha != confirmar_senha:
            return jsonify({'success': False, 'message': 'As senhas não coincidem'}), 400
        
        # Se o usuário está trocando sua própria senha, exigir senha atual
        # Admins podem trocar senha de outros sem senha atual
        if user_id == current_user.id:
            if not senha_atual:
                return jsonify({'success': False, 'message': 'Senha atual é obrigatória'}), 400
            success, message = atualizar_senha_usuario(user_id, nova_senha, senha_atual)
        else:
            # Admin trocando senha de outro usuário
            success, message = atualizar_senha_usuario(user_id, nova_senha)
        
        if success:
            flash(message, 'success')
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao trocar senha: {str(e)}'}), 500

# CONFIGURAÇÕES DA EMPRESA
@app.route('/configuracoes-empresa')
@required_permission('admin')
def configuracoes_empresa():
    config = obter_configuracoes_empresa()
    return render_template('configuracoes_empresa.html', config=config)

@app.route('/configuracoes-empresa/atualizar', methods=['POST'])
@required_permission('admin')
def atualizar_configuracoes_empresa_route():
    try:
        dados = {
            'nome_empresa': request.form['nome_empresa'],
            'cnpj': request.form['cnpj'],
            'endereco': request.form['endereco'],
            'cidade': request.form['cidade'],
            'estado': request.form['estado'],
            'cep': request.form['cep'],
            'telefone': request.form['telefone'],
            'email': request.form['email'],
            'website': request.form['website'],
            'observacoes': request.form['observacoes']
        }
        
        if atualizar_configuracoes_empresa(dados):
            flash('Configurações da empresa atualizadas com sucesso!', 'success')
        else:
            flash('Erro ao atualizar configurações da empresa!', 'error')
            
    except Exception as e:
        flash(f'Erro ao atualizar configurações: {str(e)}', 'error')
    
    return redirect(url_for('configuracoes_empresa'))

# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    estatisticas = obter_estatisticas_dashboard()
    produtos_baixo_estoque = produtos_estoque_baixo()
    vendas_recentes = listar_vendas(limit=10)
    contas_pagar_hoje = listar_contas_pagar_hoje()
    contas_receber_hoje = listar_contas_receber_hoje()
    
    return render_template('dashboard.html',
                         estatisticas=estatisticas,
                         produtos_baixo_estoque=produtos_baixo_estoque,
                         vendas_recentes=vendas_recentes,
                         contas_pagar_hoje=contas_pagar_hoje,
                         contas_receber_hoje=contas_receber_hoje)

# DEMONSTRAÇÃO DO TEMA
@app.route('/demo-theme')
@login_required
def demo_theme():
    return render_template('demo-theme.html')

# =====================================================
# ROTAS DO CAIXA FINANCEIRO
# =====================================================

@app.route('/caixa')
@login_required
@required_permission('caixa')
def caixa():
    """Página principal do caixa"""
    status_caixa = obter_status_caixa()
    movimentacoes = listar_movimentacoes_caixa(20)
    
    # Usar a função específica para buscar vendas do dia
    dados_vendas = obter_vendas_do_dia()
    
    # Debug: Imprimir dados das vendas
    print(f"DEBUG CAIXA: dados_vendas = {dados_vendas}")
    
    resumo_vendas = {
        'total_vendas': dados_vendas['total_vendas'],
        'valor_vendas': dados_vendas['valor_total'],
        'itens_vendidos': dados_vendas['itens_vendidos']
    }
    
    print(f"DEBUG CAIXA: resumo_vendas = {resumo_vendas}")
    
    return render_template('caixa.html', 
                         status_caixa=status_caixa, 
                         movimentacoes=movimentacoes,
                         resumo_vendas=resumo_vendas)

@app.route('/caixa/abrir', methods=['POST'])
@login_required
@required_permission('caixa')
def abrir_caixa_route():
    """Abrir nova sessão de caixa"""
    saldo_inicial = float(request.form.get('saldo_inicial', 0))
    observacoes = request.form.get('observacoes', '')
    
    sucesso, mensagem = abrir_caixa(current_user.id, saldo_inicial, observacoes)
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('caixa'))

@app.route('/caixa/fechar', methods=['POST'])
@login_required
@required_permission('caixa')
def fechar_caixa_route():
    """Fechar sessão de caixa atual"""
    observacoes = request.form.get('observacoes', '')
    
    sucesso, mensagem = fechar_caixa(current_user.id, observacoes)
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('caixa'))

@app.route('/caixa/movimentacao', methods=['POST'])
@login_required
@required_permission('caixa')
def nova_movimentacao_caixa():
    """Registrar nova movimentação no caixa"""
    tipo = request.form.get('tipo')
    categoria = request.form.get('categoria')
    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor'))
    observacoes = request.form.get('observacoes', '')
    
    sucesso, mensagem = registrar_movimentacao_caixa(
        tipo, categoria, descricao, valor, current_user.id, observacoes=observacoes
    )
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('caixa'))

@app.route('/financeiro')
@login_required
@required_permission('caixa')
def financeiro():
    """Página do módulo financeiro"""
    receitas_pendentes = listar_lancamentos_financeiros('receita', 'pendente')
    despesas_pendentes = listar_lancamentos_financeiros('despesa', 'pendente')
    return render_template('financeiro.html', receitas=receitas_pendentes, despesas=despesas_pendentes)

@app.route('/financeiro/lancamento', methods=['POST'])
@login_required
@required_permission('caixa')
def novo_lancamento_financeiro():
    """Criar novo lançamento financeiro"""
    tipo = request.form.get('tipo')
    categoria = request.form.get('categoria')
    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor'))
    data_lancamento = request.form.get('data_lancamento')
    data_vencimento = request.form.get('data_vencimento')
    fornecedor_cliente = request.form.get('fornecedor_cliente', '')
    numero_documento = request.form.get('numero_documento', '')
    observacoes = request.form.get('observacoes', '')
    
    sucesso, mensagem = criar_lancamento_financeiro(
        tipo, categoria, descricao, valor, data_lancamento, current_user.id,
        data_vencimento, fornecedor_cliente, numero_documento, observacoes
    )
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('financeiro'))

@app.route('/financeiro/lancamento/<int:lancamento_id>/editar', methods=['POST'])
@login_required
@required_permission('caixa')
def editar_lancamento_financeiro(lancamento_id):
    """Editar um lançamento financeiro existente"""
    categoria = request.form.get('categoria')
    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor'))
    data_vencimento = request.form.get('data_vencimento')
    fornecedor_cliente = request.form.get('fornecedor_cliente', '')
    numero_documento = request.form.get('numero_documento', '')
    observacoes = request.form.get('observacoes', '')
    
    sucesso, mensagem = editar_lancamento_financeiro_db(
        lancamento_id, categoria, descricao, valor, data_vencimento,
        fornecedor_cliente, numero_documento, observacoes
    )
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('financeiro'))

@app.route('/financeiro/lancamento/<int:lancamento_id>/status', methods=['POST'])
@login_required
@required_permission('caixa')
def alterar_status_lancamento(lancamento_id):
    """Marcar lançamento como pago/recebido ou cancelado"""
    novo_status = request.form.get('status')
    forma_pagamento = request.form.get('forma_pagamento', '')
    data_pagamento = request.form.get('data_pagamento')
    
    sucesso, mensagem = alterar_status_lancamento_financeiro(
        lancamento_id, novo_status, forma_pagamento, data_pagamento
    )
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('financeiro'))

@app.route('/financeiro/lancamento/<int:lancamento_id>/deletar', methods=['POST'])
@login_required
@required_permission('caixa')
def deletar_lancamento_financeiro(lancamento_id):
    """Deletar um lançamento financeiro"""
    sucesso, mensagem = deletar_lancamento_financeiro_db(lancamento_id)
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('financeiro'))

@app.route('/financeiro/sincronizar-lancamentos-com-contas', methods=['POST'])
@login_required
@required_permission('financeiro')
def sincronizar_lancamentos_com_contas_route():
    """Sincroniza lançamentos financeiros criando as contas correspondentes"""
    try:
        sucesso, resultado = sincronizar_lancamentos_com_contas(current_user.id)
        
        if sucesso:
            flash(f'Sincronização concluída! {resultado["despesas"]} contas a pagar e {resultado["receitas"]} contas a receber criadas a partir dos lançamentos.', 'success')
            if resultado["erros"]:
                for erro in resultado["erros"]:
                    flash(erro, 'warning')
        else:
            flash(f'Erro na sincronização: {resultado}', 'error')
    except Exception as e:
        flash(f'Erro ao sincronizar lançamentos: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('financeiro'))

@app.route('/caixa/sincronizar-vendas', methods=['POST'])
@login_required
@required_permission('caixa')
def sincronizar_vendas_caixa():
    """Sincronizar vendas do dia com o caixa"""
    sucesso, mensagem = sincronizar_vendas_com_caixa()
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('caixa'))

@app.route('/caixa/limpar-sincronizacoes', methods=['POST'])
@login_required
@required_permission('admin')
def limpar_sincronizacoes_caixa():
    """Limpar sincronizações incorretas do caixa (apenas admin)"""
    sucesso, mensagem = limpar_sincronizacoes_incorretas()
    
    if sucesso:
        flash(f"✅ {mensagem}", 'success')
    else:
        flash(f"❌ {mensagem}", 'error')
    
    return redirect(url_for('caixa'))

@app.route('/api/caixa/status')
@login_required
def api_status_caixa():
    """Retorna o status atual do caixa para o frontend"""
    try:
        caixa_aberto = caixa_esta_aberto()
        status_caixa = obter_status_caixa()
        
        return jsonify({
            'aberto': caixa_aberto,
            'status': status_caixa
        })
    except Exception as e:
        return jsonify({
            'aberto': False,
            'error': str(e)
        }), 400

@app.route('/api/caixa/exportar/pdf')
@login_required
def exportar_caixa_pdf():
    """Exportar relatório do caixa em PDF"""
    try:
        data = request.args.get('data')
        if not data:
            data = hoje_br().strftime('%Y-%m-%d')
        
        # Obter dados do caixa
        status_caixa = obter_status_caixa()
        movimentacoes = obter_movimentacoes_caixa(data)
        resumo_vendas = obter_vendas_do_dia()
        
        # Criar PDF
        pdf_buffer = criar_pdf_caixa(status_caixa, movimentacoes, resumo_vendas, data)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio_caixa_{data}.pdf'
        
        return response
    except Exception as e:
        flash(f'Erro ao exportar PDF do caixa: {str(e)}', 'error')
        return redirect(url_for('caixa'))

@app.route('/debug-vendas')
@login_required
def debug_vendas():
    """Rota para debugar dados de vendas"""
    hoje = hoje_br().strftime('%Y-%m-%d')
    
    dados = obter_vendas_do_dia()
    
    html = f"""
    <h1>Debug - Vendas do Dia {hoje}</h1>
    <h2>Dados Retornados:</h2>
    <ul>
        <li>Total de Vendas: {dados['total_vendas']}</li>
        <li>Valor Total: R$ {dados['valor_total']:.2f}</li>
        <li>Itens Vendidos: {dados['itens_vendidos']}</li>
    </ul>
    
    <h2>Vendas Individuais:</h2>
    <ul>
    """
    
    for venda in dados['vendas']:
        html += f"<li>Venda #{venda['id']}: {venda['cliente']} - R$ {venda['total']:.2f} em {venda['data_venda']}</li>"
    
    html += """
    </ul>
    <a href="/caixa">Voltar ao Caixa</a>
    """
    
    return html

# =====================================================
# CLIENTES
# =====================================================
@app.route('/clientes')
@login_required
def clientes():
    clientes_lista = listar_clientes()
    return render_template('clientes.html', clientes=clientes_lista)

@app.route('/clientes/adicionar', methods=['POST'], endpoint='adicionar_cliente')
@login_required
def adicionar_cliente_route():
    nome = request.form['nome']
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    cpf_cnpj = request.form.get('cpf_cnpj')
    endereco = request.form.get('endereco')
    
    try:
        adicionar_cliente(nome, telefone, email, cpf_cnpj, endereco)
        flash('Cliente adicionado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar cliente: {str(e)}', 'error')
    
    return redirect(url_for('clientes'))

@app.route('/clientes/editar/<int:id>', methods=['POST'], endpoint='atualizar_cliente')
@login_required
def editar_cliente_route(id):
    nome = request.form['nome']
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    cpf_cnpj = request.form.get('cpf_cnpj')
    endereco = request.form.get('endereco')
    
    try:
        editar_cliente(id, nome, telefone, email, cpf_cnpj, endereco)
        flash('Cliente editado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao editar cliente: {str(e)}', 'error')
    
    return redirect(url_for('clientes'))

@app.route('/clientes/deletar/<int:id>', methods=['POST'], endpoint='excluir_cliente')
@login_required
def deletar_cliente_route(id):
    try:
        deletar_cliente(id)
        flash('Cliente excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir cliente: {str(e)}', 'error')
    
    return redirect(url_for('clientes'))

# FORNECEDORES
@app.route('/fornecedores')
@login_required
def fornecedores():
    fornecedores_lista = listar_fornecedores()
    return render_template('fornecedores.html', fornecedores=fornecedores_lista)

@app.route('/fornecedores/adicionar', methods=['POST'], endpoint='adicionar_fornecedor')
@login_required
def adicionar_fornecedor_route():
    try:
        nome = request.form['nome']
        cnpj = request.form.get('cnpj', '').strip() or None
        telefone = request.form.get('telefone', '').strip() or None
        email = request.form.get('email', '').strip() or None
        endereco = request.form.get('endereco', '').strip() or None
        cidade = request.form.get('cidade', '').strip() or None
        estado = request.form.get('estado', '').strip() or None
        cep = request.form.get('cep', '').strip() or None
        contato_pessoa = request.form.get('contato_pessoa', '').strip() or None
        observacoes = request.form.get('observacoes', '').strip() or None
        
        adicionar_fornecedor(nome, cnpj, telefone, email, endereco, cidade, estado, cep, contato_pessoa, observacoes)
        flash('Fornecedor adicionado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar fornecedor: {str(e)}', 'error')
    
    return redirect(url_for('fornecedores'))

@app.route('/fornecedores/adicionar-ajax', methods=['POST'])
@login_required
def adicionar_fornecedor_ajax():
    """Adiciona um fornecedor via AJAX e retorna JSON"""
    try:
        nome = request.form['nome']
        cnpj = request.form.get('cnpj', '').strip() or None
        telefone = request.form.get('telefone', '').strip() or None
        email = request.form.get('email', '').strip() or None
        endereco = request.form.get('endereco', '').strip() or None
        cidade = request.form.get('cidade', '').strip() or None
        estado = request.form.get('estado', '').strip() or None
        cep = request.form.get('cep', '').strip() or None
        contato_pessoa = request.form.get('contato_pessoa', '').strip() or None
        observacoes = request.form.get('observacoes', '').strip() or None
        
        fornecedor_id = adicionar_fornecedor(nome, cnpj, telefone, email, endereco, cidade, estado, cep, contato_pessoa, observacoes)
        
        if fornecedor_id:
            return jsonify({
                'sucesso': True,
                'fornecedor_id': fornecedor_id,
                'fornecedor_nome': nome
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Erro ao cadastrar fornecedor'
            })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        })

@app.route('/fornecedores/editar/<int:id>', methods=['POST'], endpoint='atualizar_fornecedor')
@login_required
def editar_fornecedor_route(id):
    try:
        nome = request.form['nome']
        cnpj = request.form.get('cnpj', '').strip() or None
        telefone = request.form.get('telefone', '').strip() or None
        email = request.form.get('email', '').strip() or None
        endereco = request.form.get('endereco', '').strip() or None
        cidade = request.form.get('cidade', '').strip() or None
        estado = request.form.get('estado', '').strip() or None
        cep = request.form.get('cep', '').strip() or None
        contato_pessoa = request.form.get('contato_pessoa', '').strip() or None
        observacoes = request.form.get('observacoes', '').strip() or None
        
        editar_fornecedor(id, nome, cnpj, telefone, email, endereco, cidade, estado, cep, contato_pessoa, observacoes)
        flash('Fornecedor atualizado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar fornecedor: {str(e)}', 'error')
    
    return redirect(url_for('fornecedores'))

@app.route('/fornecedores/deletar/<int:id>', methods=['POST'], endpoint='excluir_fornecedor')
@login_required
def deletar_fornecedor_route(id):
    try:
        deletar_fornecedor(id)
        flash('Fornecedor excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir fornecedor: {str(e)}', 'error')
    
    return redirect(url_for('fornecedores'))

@app.route('/fornecedores/<int:id>/produtos')
@login_required
def produtos_fornecedor(id):
    fornecedor = buscar_fornecedor(id)
    if not fornecedor:
        flash('Fornecedor não encontrado!', 'error')
        return redirect(url_for('fornecedores'))
    
    produtos_lista = listar_produtos_por_fornecedor(id)
    return render_template('produtos_fornecedor.html', fornecedor=fornecedor, produtos=produtos_lista)

# PRODUTOS
# === ROTAS DE PRODUTOS ===

# app.py

# ... (Linha 603)
@app.route('/produtos')
@login_required
def produtos():
    """Exibe a página de gerenciamento de produtos"""
    try:
        # Carregar TODOS os produtos para paginação JavaScript
        # Remover paginação server-side para usar paginação client-side
        produtos_data = listar_produtos(page=1, per_page=999999)  # Carregar todos
        
        fornecedores_lista = obter_fornecedores_para_select()
        estatisticas = obter_estatisticas_dashboard()
        
        return render_template('produtos.html', 
                             produtos=produtos_data['produtos'], 
                             fornecedores=fornecedores_lista, 
                             estatisticas=estatisticas)
    except Exception as e:
        flash(f'Erro ao carregar produtos: {str(e)}', 'error')
        return render_template('produtos.html', 
                             produtos=[], 
                             fornecedores=[], 
                             estatisticas={'produtos_estoque_baixo': 0, 'produtos_sem_estoque': 0})
    
    
@app.route('/produtos/buscar')
@login_required
def buscar_produto_route():
    """API para buscar produtos para vinculação"""
    try:
        termo = request.args.get('termo', '').strip()
        if len(termo) < 2:
            return jsonify([])
        
        # Usar a função buscar_produto que é mais flexível
        produtos = buscar_produto(termo)
        
        # Renomear 'preco' para 'preco_venda' e converter tipos
        for produto in produtos:
            produto['preco_venda'] = float(produto.pop('preco', 0) or 0)
            if 'preco_custo' in produto and produto['preco_custo'] is not None:
                produto['preco_custo'] = float(produto['preco_custo'])
            if 'quantidade' in produto and produto['quantidade'] is not None:
                produto['quantidade'] = int(produto['quantidade'])

        return jsonify(produtos)
    except Exception as e:
        print(f"[ERRO] na busca de produtos para vincular: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/movimentacoes/vincular/<int:movimentacao_id>/<int:produto_id>', methods=['POST'])
@login_required
@required_permission('estoque')
def vincular_movimentacao_route(movimentacao_id, produto_id):
    """Vincula uma movimentação pendente a um produto existente"""
    try:
        # Importar a função aqui para evitar dependência circular
        from Minha_autopecas_web.logica_banco import vincular_produto_nfe
        
        sucesso, mensagem = vincular_produto_nfe(movimentacao_id, produto_id, current_user.id)
        
        if sucesso:
            return jsonify({'success': True, 'message': mensagem})
        else:
            return jsonify({'success': False, 'message': mensagem}), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Erro interno no servidor: {str(e)}'}), 500

@app.route('/api/produtos/buscar')
@login_required
def api_buscar_produtos():
    """API avançada para buscar produtos com filtros
    Suporta busca com múltiplos termos separados por % ou espaço
    Exemplo: 'PIVO%GOL' ou 'PIVO GOL' retorna produtos que contenham ambos os termos
    """
    try:
        termo = request.args.get('q', '').strip()
        categoria = request.args.get('categoria', '')
        
        # Se não houver termo, retornar lista completa
        if not termo:
            produtos_data = listar_produtos(page=1, per_page=999999)
            produtos = produtos_data['produtos']
        else:
            # Usar a função buscar_produto que já tem a lógica inteligente
            produtos = buscar_produto(termo)
        
        # Filtrar por categoria se especificada
        if categoria and categoria != 'todas':
            produtos = [p for p in produtos if p.get('categoria') == categoria]
        
        # Converter Decimals para float
        for produto in produtos:
            if 'preco' in produto and produto['preco'] is not None:
                produto['preco'] = float(produto['preco'])
            if 'preco_custo' in produto and produto['preco_custo'] is not None:
                produto['preco_custo'] = float(produto['preco_custo'])
            if 'margem_lucro' in produto and produto['margem_lucro'] is not None:
                produto['margem_lucro'] = float(produto['margem_lucro'])
        
        return jsonify(produtos[:50])  # Limitar a 50 resultados
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/produto/<termo>')
@login_required
def api_buscar_produto_unico(termo):
    """Busca um produto específico pelo termo"""
    try:
        # Carregar todos os produtos
        produtos_data = listar_produtos(page=1, per_page=999999)
        produtos = produtos_data['produtos']
        
        def converter_decimals(produto):
            """Converte campos Decimal para float"""
            if 'preco' in produto and produto['preco'] is not None:
                produto['preco'] = float(produto['preco'])
            if 'preco_custo' in produto and produto['preco_custo'] is not None:
                produto['preco_custo'] = float(produto['preco_custo'])
            if 'margem_lucro' in produto and produto['margem_lucro'] is not None:
                produto['margem_lucro'] = float(produto['margem_lucro'])
            return produto
        
        # Primeiro tenta encontrar por ID exato
        try:
            produto_id = int(termo)
            for produto in produtos:
                if produto['id'] == produto_id:
                    return jsonify(converter_decimals(produto))
        except ValueError:
            pass
        
        # Depois busca por código de barras exato
        for produto in produtos:
            if produto.get('codigo_barras') and produto['codigo_barras'].lower() == termo.lower():
                return jsonify(converter_decimals(produto))
        
        # Depois busca por código de fornecedor exato
        for produto in produtos:
            if produto.get('codigo_fornecedor') and produto['codigo_fornecedor'].lower() == termo.lower():
                return jsonify(converter_decimals(produto))
        
        # Por último, busca por nome (primeiro que contenha o termo)
        termo_lower = termo.lower()
        for produto in produtos:
            if termo_lower in produto['nome'].lower():
                return jsonify(converter_decimals(produto))
        
        return jsonify({'error': 'Produto não encontrado'}), 404
    except Exception as e:
        print(f"Erro ao buscar produto: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/produtos/adicionar', methods=['POST'])
@login_required
def adicionar_produto_route():
    """Adiciona um novo produto"""
    try:
        # Função auxiliar para conversão segura
        def safe_float(value, default=0.0):
            try:
                return float(value) if value and str(value).strip() else default
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=0):
            try:
                return int(float(value)) if value and str(value).strip() else default
            except (ValueError, TypeError):
                return default

        # Coletar dados do formulário
        nome = request.form.get('nome', '').strip()
        if not nome:
            flash('Nome do produto é obrigatório!', 'error')
            return redirect(url_for('produtos'))

        codigo_barras = request.form.get('codigo_barras', '').strip()
        codigo_fornecedor = request.form.get('codigo_fornecedor', '').strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', '').strip()
        marca = request.form.get('marca', '').strip()
        fornecedor_id = safe_int(request.form.get('fornecedor_id', 0)) or None
        
        # Campos numéricos
        estoque = safe_int(request.form.get('estoque', 0))
        estoque_minimo = safe_int(request.form.get('estoque_minimo', 1), 1)
        preco_custo = safe_float(request.form.get('preco_custo', 0))
        margem_lucro = safe_float(request.form.get('margem_lucro', 0))
        
        # Calcular preço de venda
        if preco_custo > 0 and margem_lucro >= 0:
            preco = preco_custo + (preco_custo * margem_lucro / 100)
        else:
            preco = safe_float(request.form.get('preco', 0))
        
        if preco <= 0:
            flash('Preço do produto deve ser maior que zero!', 'error')
            return redirect(url_for('produtos'))

        # Processar upload de foto
        foto_url = None
        if 'foto_produto' in request.files:
            file = request.files['foto_produto']
            if file.filename:
                foto_url = salvar_foto_produto(file)
                if not foto_url:
                    flash('Erro ao fazer upload da foto. Verifique se o formato é válido (PNG, JPG, JPEG, GIF) e o tamanho é menor que 5MB.', 'warning')

        # Adicionar produto ao banco
        produto_id = adicionar_produto(
            nome=nome,
            preco=preco,
            estoque=estoque,
            estoque_minimo=estoque_minimo,
            codigo_barras=codigo_barras if codigo_barras else None,
            descricao=descricao if descricao else None,
            categoria=categoria if categoria else None,
            codigo_fornecedor=codigo_fornecedor if codigo_fornecedor else None,
            preco_custo=preco_custo,
            margem_lucro=margem_lucro,
            foto_url=foto_url,
            marca=marca if marca else None,
            fornecedor_id=fornecedor_id
        )
        
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('produtos'))
        
    except Exception as e:
        # Se houve erro e foto foi salva, remove a foto
        if 'foto_url' in locals() and foto_url:
            remover_foto_produto(foto_url)
        flash(f'Erro ao adicionar produto: {str(e)}', 'error')
        return redirect(url_for('produtos'))

@app.route('/produtos/editar/<int:id>', methods=['POST'])
@login_required
def editar_produto_route(id):
    """Edita um produto existente"""
    try:
        # Função auxiliar para conversão segura
        def safe_float(value, default=0.0):
            try:
                return float(value) if value and str(value).strip() else default
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=0):
            try:
                return int(float(value)) if value and str(value).strip() else default
            except (ValueError, TypeError):
                return default

        # Verificar se produto existe
        produto_atual = obter_produto_por_id(id)
        if not produto_atual:
            flash('Produto não encontrado!', 'error')
            return redirect(url_for('produtos'))

        # Coletar dados do formulário
        nome = request.form.get('nome', '').strip()
        if not nome:
            flash('Nome do produto é obrigatório!', 'error')
            return redirect(url_for('produtos'))

        codigo_barras = request.form.get('codigo_barras', '').strip()
        codigo_fornecedor = request.form.get('codigo_fornecedor', '').strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', '').strip()
        marca = request.form.get('marca', '').strip()
        fornecedor_id = safe_int(request.form.get('fornecedor_id', 0)) or None
        
        # Campos numéricos
        estoque = safe_int(request.form.get('estoque', 0))
        estoque_minimo = safe_int(request.form.get('estoque_minimo', 1), 1)
        preco_custo = safe_float(request.form.get('preco_custo', 0))
        margem_lucro = safe_float(request.form.get('margem_lucro', 0))
        
        # Calcular preço de venda
        if preco_custo > 0 and margem_lucro >= 0:
            preco = preco_custo + (preco_custo * margem_lucro / 100)
        else:
            preco = safe_float(request.form.get('preco', 0))
        
        if preco <= 0:
            flash('Preço do produto deve ser maior que zero!', 'error')
            return redirect(url_for('produtos'))

        # Processar foto
        foto_url = produto_atual.get('foto_url')  # Manter foto atual por padrão
        remover_foto = request.form.get('remover_foto') == '1'
        
        if remover_foto:
            # Remover foto existente
            if foto_url:
                remover_foto_produto(foto_url)
            foto_url = None
        elif 'foto_produto' in request.files:
            file = request.files['foto_produto']
            if file.filename:
                # Nova foto foi enviada
                nova_foto_url = salvar_foto_produto(file)
                if nova_foto_url:
                    # Remover foto anterior se existir
                    if foto_url:
                        remover_foto_produto(foto_url)
                    foto_url = nova_foto_url
                else:
                    flash('Erro ao fazer upload da foto. Verifique se o formato é válido (PNG, JPG, JPEG, GIF) e o tamanho é menor que 5MB.', 'warning')

        # Atualizar produto no banco
        editar_produto(
            id=id,
            nome=nome,
            preco=preco,
            estoque=estoque,
            estoque_minimo=estoque_minimo,
            codigo_barras=codigo_barras if codigo_barras else None,
            descricao=descricao if descricao else None,
            categoria=categoria if categoria else None,
            codigo_fornecedor=codigo_fornecedor if codigo_fornecedor else None,
            preco_custo=preco_custo,
            margem_lucro=margem_lucro,
            foto_url=foto_url,
            marca=marca if marca else None,
            fornecedor_id=fornecedor_id
        )
        
        flash('Produto editado com sucesso!', 'success')
        return redirect(url_for('produtos'))
        
    except Exception as e:
        flash(f'Erro ao editar produto: {str(e)}', 'error')
        return redirect(url_for('produtos'))

@app.route('/produtos/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_produto_route(id):
    """Deleta um produto (marca como inativo)"""
    try:
        produto = obter_produto_por_id(id)
        if not produto:
            flash('Produto não encontrado!', 'error')
            return redirect(url_for('produtos'))
        
        deletar_produto(id)
        flash('Produto excluído com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao excluir produto: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

@app.route('/produtos/deletar-todos', methods=['POST'])
@login_required
def deletar_todos_produtos_route():
    """Deleta todos os produtos (função de teste)"""
    try:
        total_deletados = deletar_todos_os_produtos()
        flash(f'Todos os produtos foram removidos com sucesso! ({total_deletados} produtos)', 'success')
    except Exception as e:
        flash(f'Erro ao deletar todos os produtos: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

@app.route('/produtos/limpar-completamente', methods=['POST'])
@login_required
def limpar_produtos_completamente_route():
    """Remove completamente todos os produtos do banco (cuidado!)"""
    try:
        limpar_completamente_produtos()
        flash('Todos os produtos foram removidos completamente do banco de dados!', 'success')
    except Exception as e:
        flash(f'Erro ao limpar produtos: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

# === FIM DAS ROTAS DE PRODUTOS ===





# Rota de teste para desconto
@app.route('/teste-desconto')
@login_required
def teste_desconto():
    return render_template('teste_desconto.html')

# Rota de teste para busca
@app.route('/teste-busca')
@login_required
def teste_busca():
    return render_template('teste_busca.html')

# Rota de teste para debug de vendas
@app.route('/teste-vendas-debug')
@login_required
def teste_vendas_debug():
    return render_template('teste_vendas_debug.html')

# Rota de teste simples para vendas
@app.route('/teste-vendas-simples')
@login_required
def teste_vendas_simples():
    return render_template('teste_vendas_simples.html')

# Rota de teste direto
@app.route('/teste-direto')
@login_required
def teste_direto():
    return render_template('teste_direto.html')

@app.route('/api/test')
def api_test():
    return jsonify({"status": "ok", "message": "API funcionando"})














@app.route('/produtos/importar-xml', methods=['POST'], endpoint='importar_produtos_xml')
@login_required
def importar_produtos_xml_route():
    """Rota para importar produtos via arquivo XML de NFe com configurações avançadas"""
    from Minha_autopecas_web.logica_banco import importar_produtos_de_xml_avancado
    
    try:
        # Verificar se arquivo foi enviado
        if 'arquivo_xml' not in request.files:
            flash('Nenhum arquivo foi selecionado!', 'error')
            return redirect(url_for('produtos'))
        
        arquivo = request.files['arquivo_xml']
        
        if arquivo.filename == '':
            flash('Nenhum arquivo foi selecionado!', 'error')
            return redirect(url_for('produtos'))
        
        if arquivo and arquivo.filename.lower().endswith('.xml'):
            try:
                # Obter configurações do formulário
                margem_padrao = float(request.form.get('margem_padrao', 100))
                estoque_minimo_padrao = int(request.form.get('estoque_minimo_padrao', 1))
                usar_preco_nfe = request.form.get('usar_preco_nfe') == 'on'
                acao_existente = request.form.get('acao_existente', 'atualizar_estoque')
                
                # Ler conteúdo do arquivo
                conteudo_xml = arquivo.read().decode('utf-8')
                
                # Processar XML com configurações avançadas
                resultado = importar_produtos_de_xml_avancado(
                    conteudo_xml=conteudo_xml,
                    margem_padrao=margem_padrao,
                    estoque_minimo=estoque_minimo_padrao,
                    usar_preco_nfe=usar_preco_nfe,
                    acao_existente=acao_existente
                )
                
                if resultado['sucesso']:
                    # Montar mensagem de sucesso detalhada
                    mensagem_partes = []
                    
                    if resultado['produtos_importados'] > 0:
                        mensagem_partes.append(f"{resultado['produtos_importados']} novo(s) produto(s) importado(s)")
                    
                    if resultado['produtos_atualizados'] > 0:
                        mensagem_partes.append(f"{resultado['produtos_atualizados']} produto(s) atualizado(s)")
                    
                    if resultado['produtos_ignorados'] > 0:
                        mensagem_partes.append(f"{resultado['produtos_ignorados']} produto(s) ignorado(s)")
                    
                    if mensagem_partes:
                        flash(f"Importação concluída! {', '.join(mensagem_partes)}.", 'success')
                    else:
                        flash('Nenhum produto foi processado.', 'warning')
                    
                    # Mostrar configurações utilizadas
                    flash(f"Configurações: Margem {margem_padrao}%, Estoque mín. {estoque_minimo_padrao}, Ação: {acao_existente}", 'info')
                    
                    # Mostrar erros se houver
                    if resultado['erros']:
                        for erro in resultado['erros'][:5]:  # Mostrar apenas os 5 primeiros erros
                            flash(f"Aviso: {erro}", 'warning')
                        
                        if len(resultado['erros']) > 5:
                            flash(f"... e mais {len(resultado['erros']) - 5} erro(s)", 'warning')
                
                else:
                    flash(f"Erro ao processar XML: {resultado['erro']}", 'error')
                    
            except UnicodeDecodeError:
                flash('Erro: Arquivo XML com codificação inválida. Certifique-se de que o arquivo está em UTF-8.', 'error')
            except Exception as e:
                flash(f'Erro ao processar arquivo XML: {str(e)}', 'error')
        else:
            flash('Arquivo deve ser um XML válido!', 'error')
            
    except Exception as e:
        flash(f'Erro ao processar arquivo XML: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

# MOVIMENTAÇÕES DE PRODUTOS
@app.route('/movimentacoes')
@login_required
@required_permission('estoque')
def movimentacoes():
    """Tela de gerenciamento de movimentações de produtos - Agrupadas por NFe"""
    # Listar NFes agrupadas
    todas_nfes = listar_nfes_agrupadas()
    pendentes = [nfe for nfe in todas_nfes if nfe['status_nfe'] == 'pendente']
    aprovadas = [nfe for nfe in todas_nfes if nfe['status_nfe'] == 'aprovada']
    rejeitadas = [nfe for nfe in todas_nfes if nfe['status_nfe'] in ['cancelada', 'rejeitada']]  # Compatibilidade
    
    # Listar fornecedores para o formulário
    fornecedores_lista = listar_fornecedores()
    
    return render_template('movimentacoes.html',
                         nfes=todas_nfes,
                         pendentes=pendentes,
                         aprovadas=aprovadas,
                         rejeitadas=rejeitadas,
                         fornecedores=fornecedores_lista)

@app.route('/movimentacoes/nfe/<nfe_numero>')
@login_required
@required_permission('estoque')
def visualizar_nfe(nfe_numero):
    """Visualiza os produtos de uma NFe específica"""
    produtos = listar_produtos_por_nfe(nfe_numero=nfe_numero)
    fornecedores_lista = listar_fornecedores()
    
    # Pegar informações da primeira movimentação para exibir dados da NFe
    nfe_info = produtos[0] if produtos else None
    
    # Identificador da NFe (pode ser número ou identificador manual)
    nfe_identificador = nfe_numero
    
    return render_template('produtos_nfe.html',
                         nfe_numero=nfe_numero,
                         nfe_identificador=nfe_identificador,
                         nfe_info=nfe_info,
                         produtos=produtos,
                         fornecedores=fornecedores_lista)

@app.route('/movimentacoes/nfe/<nfe_numero>/aprovar-tudo', methods=['POST'])
@login_required
@required_permission('estoque')
def aprovar_nfe_route(nfe_numero):
    """Aprova todos os produtos de uma NFe"""
    try:
        resultado = aprovar_nfe_completa(nfe_numero, current_user.id)
        if resultado['sucesso']:
            flash(f"NFe aprovada com sucesso! {resultado['total_aprovados']} produtos adicionados ao estoque.", 'success')
        else:
            flash(f"Erro ao aprovar NFe: {resultado['erro']}", 'error')
    except Exception as e:
        flash(f'Erro ao aprovar NFe: {str(e)}', 'error')
    
    return redirect(url_for('movimentacoes'))

@app.route('/movimentacoes/nfe/<nfe_numero>/cancelar-tudo', methods=['POST'])
@login_required
@required_permission('estoque')
def cancelar_nfe_route(nfe_numero):
    """Cancela todos os produtos de uma NFe (permite deletar depois)"""
    try:
        motivo = request.form.get('motivo_cancelamento', 'Não especificado')
        resultado = cancelar_nfe_completa(nfe_numero, current_user.id, motivo)
        if resultado['sucesso']:
            flash(f"NFe cancelada com sucesso! {resultado['total_cancelados']} produtos cancelados. Você pode deletá-los agora.", 'warning')
        else:
            flash(f"Erro ao cancelar NFe: {resultado['erro']}", 'error')
    except Exception as e:
        flash(f'Erro ao cancelar NFe: {str(e)}', 'error')
    
    return redirect(url_for('movimentacoes'))

@app.route('/movimentacoes/nfe/<nfe_numero>/deletar-tudo', methods=['POST'])
@login_required
@required_permission('estoque')
def deletar_nfe_route(nfe_numero):
    """Deleta todos os produtos cancelados de uma NFe"""
    try:
        from Minha_autopecas_web.logica_banco import listar_produtos_por_nfe, deletar_movimentacao
        
        # Buscar produtos da NFe
        produtos = listar_produtos_por_nfe(nfe_numero=nfe_numero if not nfe_numero.startswith('MANUAL-') else None,
                                          nfe_identificador=nfe_numero if nfe_numero.startswith('MANUAL-') else None)
        
        total_deletados = 0
        erros = 0
        
        for produto in produtos:
            if produto['status'] == 'cancelada':
                try:
                    deletar_movimentacao(produto['id'])
                    total_deletados += 1
                except Exception as e:
                    print(f"[ERRO] Falha ao deletar movimentação {produto['id']}: {str(e)}")
                    erros += 1
        
        if total_deletados > 0:
            flash(f"NFe deletada com sucesso! {total_deletados} produto(s) cancelado(s) removido(s).", 'success')
        elif erros > 0:
            flash(f"Erro ao deletar NFe. {erros} erro(s) encontrado(s).", 'error')
        else:
            flash("Nenhum produto cancelado encontrado para deletar.", 'info')
            
    except Exception as e:
        flash(f'Erro ao deletar NFe: {str(e)}', 'error')
    
    return redirect(url_for('movimentacoes'))

# Mantém rota antiga para compatibilidade (redireciona para cancelar)
@app.route('/movimentacoes/nfe/<nfe_numero>/rejeitar-tudo', methods=['POST'])
@login_required
@required_permission('estoque')
def rejeitar_nfe_route(nfe_numero):
    """DEPRECATED: Use /movimentacoes/nfe/<nfe_numero>/cancelar-tudo"""
    return cancelar_nfe_route(nfe_numero)

@app.route('/movimentacoes/adicionar', methods=['POST'])
@login_required
@required_permission('estoque')
def adicionar_movimentacao_route():
    """Adiciona uma nova movimentação manual"""
    try:
        # Função auxiliar para conversão segura
        def safe_float(value, default=0.0):
            try:
                return float(value) if value and str(value).strip() else default
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=0):
            try:
                return int(float(value)) if value and str(value).strip() else default
            except (ValueError, TypeError):
                return default

        # Coletar dados do formulário
        nome = request.form.get('nome', '').strip()
        if not nome:
            flash('Nome do produto é obrigatório!', 'error')
            return redirect(url_for('movimentacoes'))

        codigo_barras = request.form.get('codigo_barras', '').strip()
        codigo_fornecedor = request.form.get('codigo_fornecedor', '').strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', '').strip()
        marca = request.form.get('marca', '').strip()
        fornecedor_id = safe_int(request.form.get('fornecedor_id', 0)) or None
        
        # Campos numéricos
        quantidade = safe_int(request.form.get('quantidade', 0))
        estoque_minimo = safe_int(request.form.get('estoque_minimo', 1), 1)
        preco_custo = safe_float(request.form.get('preco_custo', 0))
        preco_venda = safe_float(request.form.get('preco_venda', 0))
        
        # Se o usuário usou o botão "Aplicar Margem", pegue o preço calculado
        # Mas sempre priorizamos o preço de venda final digitado pelo usuário
        if preco_venda <= 0:
            margem_digitada = safe_float(request.form.get('margem_lucro', 0))
            if preco_custo > 0 and margem_digitada > 0:
                preco_venda = preco_custo + (preco_custo * margem_digitada / 100)
        
        if preco_venda <= 0:
            flash('Preço de venda deve ser maior que zero!', 'error')
            return redirect(url_for('movimentacoes'))

        # Processar upload de foto
        foto_url = None
        if 'foto_produto' in request.files:
            file = request.files['foto_produto']
            if file.filename:
                foto_url = salvar_foto_produto(file)
                if not foto_url:
                    flash('Erro ao fazer upload da foto. Verifique o formato e tamanho.', 'warning')

        # Adicionar movimentação (margem será calculada automaticamente pela função)
        movimentacao_id = adicionar_movimentacao(
            nome=nome,
            preco_venda=preco_venda,
            quantidade=quantidade,
            tipo_movimentacao='entrada',
            origem='manual',
            estoque_minimo=estoque_minimo,
            codigo_barras=codigo_barras if codigo_barras else None,
            descricao=descricao if descricao else None,
            categoria=categoria if categoria else None,
            codigo_fornecedor=codigo_fornecedor if codigo_fornecedor else None,
            preco_custo=preco_custo,
            margem_lucro=0,  # Será calculado automaticamente pela função
            foto_url=foto_url,
            marca=marca if marca else None,
            fornecedor_id=fornecedor_id,
            usuario_id=current_user.id,
            observacoes=request.form.get('observacoes', '')
        )
        
        flash('Movimentação criada com sucesso! Aguardando aprovação.', 'success')
        return redirect(url_for('movimentacoes'))
        
    except Exception as e:
        if 'foto_url' in locals() and foto_url:
            remover_foto_produto(foto_url)
        flash(f'Erro ao adicionar movimentação: {str(e)}', 'error')
        return redirect(url_for('movimentacoes'))

@app.route('/movimentacoes/editar/<int:id>/dados')
@login_required
@required_permission('estoque')
def obter_dados_movimentacao(id):
    """Retorna os dados de uma movimentação em formato JSON para edição via AJAX"""
    try:
        print(f"[DEBUG] Buscando movimentação ID: {id}")  # Log de debug
        movimentacao = obter_movimentacao_por_id(id)
        
        if not movimentacao:
            print(f"[DEBUG] Movimentação {id} não encontrada")
            return jsonify({'erro': 'Movimentação não encontrada'}), 404
        
        print(f"[DEBUG] Movimentação encontrada: {movimentacao.get('nome', 'SEM NOME')}")
        
        # Converter para dicionário serializável
        dados = {
            'id': movimentacao.get('id'),
            'nome': movimentacao.get('nome', ''),
            'quantidade': movimentacao.get('quantidade', 0),
            'codigo_barras': movimentacao.get('codigo_barras', ''),
            'codigo_fornecedor': movimentacao.get('codigo_fornecedor', ''),
            'marca': movimentacao.get('marca', ''),
            'categoria': movimentacao.get('categoria', ''),
            'preco_custo': float(movimentacao['preco_custo']) if movimentacao.get('preco_custo') else 0,
            'margem_lucro': float(movimentacao['margem_lucro']) if movimentacao.get('margem_lucro') else 0,
            'preco_venda': float(movimentacao['preco_venda']) if movimentacao.get('preco_venda') else 0,
            'descricao': movimentacao.get('descricao', '')
        }
        
        print(f"[DEBUG] Dados preparados para envio: {dados}")
        return jsonify(dados)
        
    except Exception as e:
        print(f"[ERRO] Erro ao buscar movimentação {id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@app.route('/movimentacoes/editar/<int:id>', methods=['POST'])
@login_required
@required_permission('estoque')
def editar_movimentacao_route(id):
    """Edita uma movimentação pendente"""
    try:
        def safe_float(value, default=0.0):
            try:
                return float(value) if value and str(value).strip() else default
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=0):
            try:
                return int(float(value)) if value and str(value).strip() else default
            except (ValueError, TypeError):
                return default

        # Verificar se movimentação existe
        movimentacao_atual = obter_movimentacao_por_id(id)
        if not movimentacao_atual:
            flash('Movimentação não encontrada!', 'error')
            return redirect(url_for('movimentacoes'))
        
        if movimentacao_atual['status'] != 'pendente':
            flash('Apenas movimentações pendentes podem ser editadas!', 'error')
            return redirect(url_for('movimentacoes'))

        # Coletar dados do formulário
        nome = request.form.get('nome', '').strip()
        if not nome:
            flash('Nome do produto é obrigatório!', 'error')
            return redirect(url_for('movimentacoes'))

        codigo_barras = request.form.get('codigo_barras', '').strip()
        codigo_fornecedor = request.form.get('codigo_fornecedor', '').strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', '').strip()
        marca = request.form.get('marca', '').strip()
        fornecedor_id = safe_int(request.form.get('fornecedor_id', 0)) or None
        
        quantidade = safe_int(request.form.get('quantidade', 0))
        estoque_minimo = safe_int(request.form.get('estoque_minimo', 1), 1)
        preco_custo = safe_float(request.form.get('preco_custo', 0))
        margem_lucro = safe_float(request.form.get('margem_lucro', 0))
        
        # Usar o preço de venda informado pelo usuário (controle total)
        preco_venda = safe_float(request.form.get('preco_venda', 0))
        
        if preco_venda <= 0:
            flash('Preço de venda deve ser maior que zero!', 'error')
            # Redirecionar de volta para a NFe
            nfe_numero = movimentacao_atual.get('xml_nfe_numero') or f"MANUAL-{movimentacao_atual.get('id')}"
            return redirect(url_for('visualizar_nfe', nfe_numero=nfe_numero))

        # Processar foto
        foto_url = movimentacao_atual.get('foto_url')
        if 'foto_produto' in request.files:
            file = request.files['foto_produto']
            if file.filename:
                nova_foto = salvar_foto_produto(file)
                if nova_foto:
                    if foto_url:
                        remover_foto_produto(foto_url)
                    foto_url = nova_foto

        # Editar movimentação
        sucesso = editar_movimentacao(
            movimentacao_id=id,
            nome=nome,
            preco_venda=preco_venda,
            quantidade=quantidade,
            estoque_minimo=estoque_minimo,
            codigo_barras=codigo_barras if codigo_barras else None,
            descricao=descricao if descricao else None,
            categoria=categoria if categoria else None,
            codigo_fornecedor=codigo_fornecedor if codigo_fornecedor else None,
            preco_custo=preco_custo,
            margem_lucro=margem_lucro,
            foto_url=foto_url,
            marca=marca if marca else None,
            fornecedor_id=fornecedor_id
        )
        
        if sucesso:
            flash('Produto editado com sucesso!', 'success')
        
        # Obter o número da NFe para redirecionar de volta para a página de produtos da NFe
        nfe_numero = movimentacao_atual.get('xml_nfe_numero') or f"MANUAL-{movimentacao_atual.get('id')}"
        return redirect(url_for('visualizar_nfe', nfe_numero=nfe_numero))
        
    except Exception as e:
        flash(f'Erro ao editar produto: {str(e)}', 'error')
        print(f"[ERRO] Erro ao editar movimentação {id}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Tentar redirecionar de volta para a NFe mesmo em caso de erro
        try:
            movimentacao_atual = obter_movimentacao_por_id(id)
            if movimentacao_atual:
                nfe_numero = movimentacao_atual.get('xml_nfe_numero') or f"MANUAL-{movimentacao_atual.get('id')}"
                return redirect(url_for('visualizar_nfe', nfe_numero=nfe_numero))
        except:
            pass
        
        return redirect(url_for('movimentacoes'))

@app.route('/movimentacoes/aprovar/<int:id>', methods=['POST'])
@login_required
@required_permission('estoque')
def aprovar_movimentacao_route(id):
    """Aprova uma movimentação e adiciona ao estoque"""
    try:
        # Obter dados da movimentação antes de aprovar (para pegar o número da NFe)
        movimentacao = obter_movimentacao_por_id(id)
        nfe_numero = movimentacao.get('xml_nfe_numero') or f"MANUAL-{movimentacao.get('id')}" if movimentacao else None
        
        produto_id = aprovar_movimentacao(id, current_user.id)
        flash(f'Produto aprovado com sucesso! Adicionado ao estoque (ID: #{produto_id}).', 'success')
        
        # Redirecionar de volta para a página da NFe
        if nfe_numero:
            return redirect(url_for('visualizar_nfe', nfe_numero=nfe_numero))
    except Exception as e:
        flash(f'Erro ao aprovar produto: {str(e)}', 'error')
        print(f"[ERRO] Erro ao aprovar movimentação {id}: {str(e)}")
    
    return redirect(url_for('movimentacoes'))

@app.route('/movimentacoes/cancelar/<int:id>', methods=['POST'])
@login_required
@required_permission('estoque')
def cancelar_movimentacao_route(id):
    """Cancela uma movimentação (permite deletar depois)"""
    try:
        # Obter dados da movimentação antes de cancelar (para pegar o número da NFe)
        movimentacao = obter_movimentacao_por_id(id)
        nfe_numero = movimentacao.get('xml_nfe_numero') or f"MANUAL-{movimentacao.get('id')}" if movimentacao else None
        
        motivo = request.form.get('motivo_cancelamento', 'Não especificado')
        cancelar_movimentacao(id, current_user.id, motivo)
        flash('Produto cancelado com sucesso! Você pode deletá-lo agora se desejar.', 'warning')
        
        # Redirecionar de volta para a página da NFe
        if nfe_numero:
            return redirect(url_for('visualizar_nfe', nfe_numero=nfe_numero))
    except Exception as e:
        flash(f'Erro ao cancelar produto: {str(e)}', 'error')
        print(f"[ERRO] Erro ao cancelar movimentação {id}: {str(e)}")
    
    return redirect(url_for('movimentacoes'))

# Mantém rota antiga para compatibilidade (redireciona para cancelar)
@app.route('/movimentacoes/rejeitar/<int:id>', methods=['POST'])
@login_required
@required_permission('estoque')
def rejeitar_movimentacao_route(id):
    """DEPRECATED: Use /movimentacoes/cancelar/<id>"""
    return cancelar_movimentacao_route(id)

@app.route('/movimentacoes/deletar/<int:id>', methods=['POST'])
@login_required
@required_permission('estoque')
def deletar_movimentacao_route(id):
    """Deleta uma movimentação pendente"""
    try:
        # Obter dados da movimentação antes de deletar (para pegar o número da NFe)
        movimentacao = obter_movimentacao_por_id(id)
        nfe_numero = movimentacao.get('xml_nfe_numero') or f"MANUAL-{movimentacao.get('id')}" if movimentacao else None
        
        deletar_movimentacao(id)
        flash('Produto deletado com sucesso!', 'success')
        
        # Redirecionar de volta para a página da NFe
        if nfe_numero:
            return redirect(url_for('visualizar_nfe', nfe_numero=nfe_numero))
    except Exception as e:
        flash(f'Erro ao deletar produto: {str(e)}', 'error')
        print(f"[ERRO] Erro ao deletar movimentação {id}: {str(e)}")
    
    return redirect(url_for('movimentacoes'))

@app.route('/movimentacoes/importar-xml', methods=['POST'])
@login_required
@required_permission('estoque')
def importar_xml_movimentacoes_route():
    """Importa produtos de XML criando movimentações pendentes"""
    try:
        # Verificar se arquivo foi enviado
        if 'arquivo_xml' not in request.files:
            flash('Nenhum arquivo foi selecionado!', 'error')
            return redirect(url_for('movimentacoes'))
        
        arquivo = request.files['arquivo_xml']
        
        if arquivo.filename == '':
            flash('Nenhum arquivo foi selecionado!', 'error')
            return redirect(url_for('movimentacoes'))
        
        if arquivo and arquivo.filename.lower().endswith('.xml'):
            try:
                # Obter configurações do formulário
                margem_padrao = float(request.form.get('margem_padrao', 100))
                estoque_minimo_padrao = int(request.form.get('estoque_minimo_padrao', 1))
                
                # Ler conteúdo do arquivo
                conteudo_xml = arquivo.read().decode('utf-8')
                
                # Processar XML criando movimentações
                resultado = importar_xml_para_movimentacoes(
                    conteudo_xml=conteudo_xml,
                    margem_padrao=margem_padrao,
                    estoque_minimo=estoque_minimo_padrao,
                    usuario_id=current_user.id
                )
                
                if resultado['sucesso']:
                    if resultado['movimentacoes_criadas'] > 0:
                        flash(f"Importação concluída! {resultado['movimentacoes_criadas']} movimentação(ões) criada(s) da NFe {resultado.get('nfe_numero', '')}.", 'success')
                        flash('As movimentações estão pendentes de aprovação. Revise e aprove cada uma.', 'info')
                    else:
                        flash('Nenhuma movimentação foi criada.', 'warning')
                    
                    # Mostrar erros se houver
                    if resultado['erros']:
                        for erro in resultado['erros'][:5]:
                            flash(f"Aviso: {erro}", 'warning')
                        
                        if len(resultado['erros']) > 5:
                            flash(f"... e mais {len(resultado['erros']) - 5} erro(s)", 'warning')
                else:
                    flash(f"Erro ao processar XML: {resultado.get('erro', 'Erro desconhecido')}", 'error')
                    
            except UnicodeDecodeError:
                flash('Erro: Arquivo XML com codificação inválida.', 'error')
            except Exception as e:
                flash(f'Erro ao processar arquivo XML: {str(e)}', 'error')
        else:
            flash('Arquivo deve ser um XML válido!', 'error')
            
    except Exception as e:
        flash(f'Erro ao processar arquivo XML: {str(e)}', 'error')
    
    return redirect(url_for('movimentacoes'))

# VENDAS
@app.route('/vendas')
@login_required
def vendas():
    clientes_lista = listar_clientes()
    # Buscar vendas do dia para exibir na lista
    vendas_dados = obter_vendas_do_dia()
    vendas_hoje = vendas_dados.get('vendas', [])
    produtos_data = listar_produtos(page=1, per_page=999999)
    produtos_lista = produtos_data['produtos']
    usuarios_lista = listar_usuarios()
    
    # Calcular estatísticas
    total_vendas_hoje = sum(venda.get('total', 0) for venda in vendas_hoje)
    total_itens_vendidos = sum(venda.get('total_itens', 0) for venda in vendas_hoje)
    ticket_medio = total_vendas_hoje / len(vendas_hoje) if vendas_hoje else 0
    
    # Data de hoje para filtros
    data_hoje = agora_br().strftime('%Y-%m-%d')
    
    return render_template('vendas.html', 
                         clientes=clientes_lista, 
                         vendas_hoje=vendas_hoje,
                         total_vendas_hoje=total_vendas_hoje,
                         total_itens_vendidos=total_itens_vendidos,
                         ticket_medio=ticket_medio,
                         data_hoje=data_hoje,
                         produtos=produtos_lista,
                         usuarios=usuarios_lista)

# API para filtros de vendas por período
@app.route('/api/vendas/periodo')
@login_required  
def api_vendas_periodo():
    """API para buscar vendas por período com estatísticas"""
    try:
        data_inicio = request.args.get('inicio')
        data_fim = request.args.get('fim')
        
        if not data_inicio or not data_fim:
            return jsonify({'error': 'Parâmetros de data são obrigatórios'}), 400
        
        # Buscar vendas do período usando a nova função
        vendas = listar_vendas_por_periodo(data_inicio, data_fim)
        
        # Calcular estatísticas
        total_vendas = len(vendas)
        faturamento = sum(venda.get('total', 0) for venda in vendas)
        total_itens = sum(venda.get('total_itens', 0) for venda in vendas)
        ticket_medio = faturamento / total_vendas if total_vendas > 0 else 0
        
        estatisticas = {
            'total_vendas': total_vendas,
            'faturamento': faturamento,
            'total_itens': total_itens,
            'ticket_medio': ticket_medio
        }
        
        return jsonify({
            'vendas': vendas,
            'estatisticas': estatisticas
        })
        
    except Exception as e:
        print(f"Erro na API vendas período: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# API para obter detalhes de uma venda específica
@app.route('/api/vendas/<int:venda_id>/detalhes')
@login_required
def api_venda_detalhes(venda_id):
    """API para obter detalhes completos de uma venda"""
    try:
        venda = obter_venda_por_id(venda_id)
        if not venda:
            return jsonify({'error': 'Venda não encontrada'}), 404
            
        return jsonify(venda)
        
    except Exception as e:
        print(f"Erro na API venda detalhes: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# APIs para exportação de vendas
@app.route('/api/vendas/exportar/<formato>')
@login_required
def api_exportar_vendas(formato):
    """API para exportar vendas em diferentes formatos"""
    try:
        data_inicio = request.args.get('inicio')
        data_fim = request.args.get('fim')
        
        if not data_inicio or not data_fim:
            return jsonify({'error': 'Parâmetros de data são obrigatórios'}), 400
        
        if formato not in ['excel', 'pdf']:
            return jsonify({'error': 'Formato não suportado'}), 400
        
        # Por enquanto, retornar um placeholder - implementar exportação real posteriormente
        return jsonify({
            'message': f'Exportação em {formato} será implementada em breve',
            'periodo': f'{data_inicio} a {data_fim}'
        })
        
    except Exception as e:
        print(f"Erro na API exportar vendas: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/vendas/<int:venda_id>')
@login_required
def visualizar_venda(venda_id):
    try:
        venda = obter_venda_por_id(venda_id)
        if not venda:
            flash('Venda não encontrada!', 'error')
            return redirect(url_for('vendas'))
        config_empresa = obter_configuracoes_empresa()
        return render_template('visualizar_venda.html', venda=venda, config_empresa=config_empresa)
    except Exception as e:
        flash(f'Erro ao carregar venda: {str(e)}', 'error')
        return redirect(url_for('vendas'))

@app.route('/api/venda/<int:venda_id>')
@login_required
def api_venda(venda_id):
    try:
        print(f"API: Buscando venda {venda_id}")
        venda = obter_venda_por_id(venda_id)
        if not venda:
            print(f"API: Venda {venda_id} não encontrada")
            return jsonify({'error': 'Venda não encontrada'}), 404
        
        print(f"API: Venda {venda_id} encontrada")
        
        # Converter para formato JSON serializable
        venda_json = {
            'id': venda['id'],
            'cliente_nome': venda.get('cliente_nome', 'Cliente Avulso'),
            'forma_pagamento': venda.get('forma_pagamento', 'dinheiro'),
            'total': float(venda.get('total', 0)),
            'desconto': float(venda.get('desconto', 0)),
            'valor_pago': float(venda.get('valor_pago', 0)),
            'troco': float(venda.get('troco', 0)),
            'created_at': venda['created_at'].isoformat() if hasattr(venda.get('created_at'), 'isoformat') else str(venda.get('created_at', '')),
            'itens': []
        }
        
        # Adicionar itens da venda
        for item in venda.get('itens', []):
            venda_json['itens'].append({
                'produto_nome': item.get('produto_nome', ''),
                'quantidade': int(item.get('quantidade', 0)),
                'preco_unitario': float(item.get('preco_unitario', 0))
            })
        
        print(f"API: Venda {venda_id} convertida para JSON com {len(venda_json['itens'])} itens")
        return jsonify(venda_json)
    except Exception as e:
        print(f"API: Erro ao buscar venda {venda_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/vendas/<int:venda_id>/recibo')
def recibo_venda(venda_id):
    """Gera recibo para impressão com informações completas da empresa"""
    try:
        from Minha_autopecas_web.logica_banco import obter_venda_por_id, obter_configuracoes_empresa
        
        venda = obter_venda_por_id(venda_id)
        if not venda:
            flash('Venda não encontrada', 'error')
            return redirect(url_for('vendas'))
        
        # Buscar configurações da empresa
        empresa = obter_configuracoes_empresa()
        
        return render_template('recibo_venda.html', venda=venda, empresa=empresa)
    
    except Exception as e:
        flash(f'Erro ao gerar recibo: {str(e)}', 'error')
        return redirect(url_for('vendas'))

@app.route('/api/configuracoes-empresa')
@login_required
def api_configuracoes_empresa():
    try:
        print("API: Buscando configurações da empresa")
        config = obter_configuracoes_empresa()
        print(f"API: Configurações carregadas: {config.get('nome_empresa', 'N/A')}")
        return jsonify(config)
    except Exception as e:
        print(f"API: Erro ao buscar configurações da empresa: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/vendas/registrar', methods=['POST'], endpoint='registrar_venda')
@login_required
def registrar_venda_route():
    try:
        cliente_id = request.form.get('cliente_id')
        if cliente_id:
            cliente_id = int(cliente_id)
        else:
            cliente_id = None
            
        forma_pagamento = request.form['forma_pagamento']
        desconto = float(request.form.get('desconto', 0))
        observacoes = request.form.get('observacoes')
        
        # Validação: Se não é venda a prazo, o caixa DEVE estar aberto
        if forma_pagamento != 'prazo' and not caixa_esta_aberto():
            # Se a requisição é AJAX, retorna JSON
            if request.headers.get('Content-Type') == 'application/json' or request.args.get('ajax') == '1':
                return jsonify({
                    'success': False,
                    'error': '❌ CAIXA FECHADO! O caixa deve estar aberto para registrar vendas à vista. Por favor, abra o caixa antes de continuar.',
                    'error_type': 'cash_drawer_closed'
                }), 400
            
            # Redirecionar para vendas com mensagem de erro
            flash('❌ CAIXA FECHADO! O caixa deve estar aberto para registrar vendas. Por favor, abra o caixa antes de continuar.', 'error')
            return redirect(url_for('vendas'))
        
        # Itens da venda (vem do JavaScript)
        itens_json = request.form.get('itens')
        if not itens_json:
            flash('Nenhum item foi adicionado à venda!', 'error')
            return redirect(url_for('vendas'))
            
        itens = json.loads(itens_json)
        
        if not itens:
            flash('Nenhum item foi adicionado à venda!', 'error')
            return redirect(url_for('vendas'))
            
        # Validar se todos os itens têm os campos necessários
        for i, item in enumerate(itens):
            if 'produto_id' not in item:
                flash(f'Item {i+1}: produto_id ausente', 'error')
                return redirect(url_for('vendas'))
            if 'quantidade' not in item:
                flash(f'Item {i+1}: quantidade ausente', 'error')
                return redirect(url_for('vendas'))
            if 'preco_unitario' not in item:
                flash(f'Item {i+1}: preco_unitario ausente', 'error')
                return redirect(url_for('vendas'))
        
        venda_id = registrar_venda(cliente_id, itens, forma_pagamento, desconto, observacoes, current_user.id)
        
        # Se a requisição é AJAX, retorna JSON com o ID da venda
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('ajax') == '1':
            return jsonify({
                'success': True,
                'venda_id': venda_id,
                'message': f'Venda #{venda_id} registrada com sucesso!'
            })
        
        # Verificar se deve imprimir o recibo
        imprimir_recibo = request.form.get('imprimir_recibo') == 'on'
        
        if imprimir_recibo:
            flash(f'Venda #{venda_id} registrada com sucesso!', 'success')
            # Redireciona para o recibo em uma nova aba
            return render_template('venda_sucesso.html', venda_id=venda_id, imprimir=True)
        else:
            flash(f'Venda #{venda_id} registrada com sucesso!', 'success')
        
    except Exception as e:
        # Se a requisição é AJAX, retorna erro em JSON
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('ajax') == '1':
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
            
        flash(f'Erro ao registrar venda: {str(e)}', 'error')
    
    return redirect(url_for('vendas'))

@app.route('/vendas/<int:venda_id>/deletar', methods=['POST'])
@login_required
def deletar_venda_route(venda_id):
    """
    Rota para deletar uma venda específica
    """
    try:
        # Verificar se o usuário tem permissão para vendas ou é admin
        if not verificar_permissao(current_user.id, 'vendas') and not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Você não tem permissão para deletar vendas.'
            }), 403
        
        # Verificar se a venda existe antes de tentar deletar
        venda = obter_venda_por_id(venda_id)
        if not venda:
            return jsonify({
                'success': False,
                'error': f'Venda #{venda_id} não encontrada.'
            }), 404
        
        # Executar a deleção
        resultado = deletar_venda(venda_id, restaurar_estoque=True)
        
        if resultado['success']:
            # Log da operação
            app.logger.info(f'Venda #{venda_id} deletada pelo usuário {current_user.username}')
            
            # Criar mensagem de sucesso detalhada
            msg_detalhes = []
            if resultado['itens_deletados'] > 0:
                msg_detalhes.append(f"{resultado['itens_deletados']} itens removidos")
            if resultado['estoque_restaurado']:
                produtos_restaurados = len(resultado['estoque_restaurado'])
                msg_detalhes.append(f"estoque de {produtos_restaurados} produtos restaurado")
            if resultado['movimentacoes_caixa_deletadas'] > 0:
                msg_detalhes.append(f"{resultado['movimentacoes_caixa_deletadas']} movimentações de caixa removidas")
            
            mensagem = f'Venda #{venda_id} deletada com sucesso'
            if msg_detalhes:
                mensagem += f' ({", ".join(msg_detalhes)})'
            
            return jsonify({
                'success': True,
                'message': mensagem,
                'detalhes': resultado
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('erro', 'Erro desconhecido ao deletar venda.')
            }), 500
            
    except Exception as e:
        app.logger.error(f'Erro ao deletar venda #{venda_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }), 500

# CONTAS A PAGAR
@app.route('/contas-a-pagar-hoje')
@required_permission('financeiro')
def contas_a_pagar_hoje():
    filtro = request.args.get('filtro', 'hoje')
    status = request.args.get('status', 'pendente')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    contas = listar_contas_pagar_por_periodo(filtro, data_inicio, data_fim, status)
    fornecedores = obter_fornecedores_para_select()
    hoje = hoje_br()
    
    # Calcular estatísticas
    total_contas = len(contas)
    total_valor = sum(conta['valor'] for conta in contas)
    valor_medio = total_valor / total_contas if total_contas > 0 else 0
    
    # Contar por status
    atrasadas = len([c for c in contas if c['dias_restantes'] < 0])
    vencendo_7_dias = len([c for c in contas if 0 <= c['dias_restantes'] <= 7])
    futuras = len([c for c in contas if c['dias_restantes'] > 7])
    
    estatisticas = {
        'total_contas': total_contas,
        'total_valor': total_valor,
        'valor_medio': valor_medio,
        'atrasadas': atrasadas,
        'vencendo_7_dias': vencendo_7_dias,
        'futuras': futuras
    }
    
    # Buscar configurações da empresa
    configuracoes_empresa = obter_configuracoes_empresa()
    
    return render_template('contas_a_pagar_hoje.html', 
                         contas=contas, 
                         fornecedores=fornecedores, 
                         hoje=hoje,
                         filtro_atual=filtro,
                         status_atual=status,
                         estatisticas=estatisticas,
                         configuracoes_empresa=configuracoes_empresa)

@app.route('/contas-pagar/adicionar', methods=['POST'])
@required_permission('financeiro')
def adicionar_conta_pagar_route():
    descricao = request.form['descricao']
    valor = float(request.form['valor'])
    data_vencimento = request.form['data_vencimento']
    categoria = request.form.get('categoria')
    observacoes = request.form.get('observacoes')
    fornecedor_id = request.form.get('fornecedor_id')
    
    # Converter fornecedor_id para None se estiver vazio
    if fornecedor_id and fornecedor_id.strip():
        fornecedor_id = int(fornecedor_id)
    else:
        fornecedor_id = None
    
    try:
        sucesso, mensagem = adicionar_conta_pagar(descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id)
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'warning')
    except Exception as e:
        flash(f'Erro ao adicionar conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_pagar_hoje'))

@app.route('/contas-pagar/pagar/<int:id>', methods=['POST'])
@required_permission('financeiro')
def pagar_conta_route(id):
    try:
        pagar_conta(id)
        flash('Conta marcada como paga!', 'success')
    except Exception as e:
        flash(f'Erro ao pagar conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_pagar_hoje'))

@app.route('/contas-pagar/duplicar/<int:id>', methods=['POST'])
@required_permission('financeiro')
def duplicar_conta_pagar_route(id):
    try:
        sucesso, mensagem = duplicar_conta_pagar(id)
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'warning')
    except Exception as e:
        flash(f'Erro ao duplicar conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_pagar_hoje'))

@app.route('/contas-pagar/excluir/<int:id>', methods=['POST'])
@required_permission('financeiro')
def excluir_conta_pagar_route(id):
    try:
        sucesso, mensagem = excluir_conta_pagar(id)
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'warning')
    except Exception as e:
        flash(f'Erro ao excluir conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_pagar_hoje'))

@app.route('/contas-pagar/obter/<int:id>', methods=['GET'])
@required_permission('financeiro')
def obter_conta_pagar_route(id):
    try:
        sucesso, resultado = obter_conta_pagar(id)
        if sucesso:
            return jsonify({'success': True, 'conta': resultado})
        else:
            return jsonify({'success': False, 'message': resultado})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/contas-pagar/editar/<int:id>', methods=['POST'])
@required_permission('financeiro')
def editar_conta_pagar_route(id):
    try:
        descricao = request.form.get('descricao')
        valor = float(request.form.get('valor'))
        data_vencimento = request.form.get('data_vencimento')
        categoria = request.form.get('categoria')
        observacoes = request.form.get('observacoes')
        fornecedor_id = request.form.get('fornecedor_id')
        
        if fornecedor_id and fornecedor_id.strip():
            fornecedor_id = int(fornecedor_id)
        else:
            fornecedor_id = None
        
        sucesso, mensagem = editar_conta_pagar(id, descricao, valor, data_vencimento, categoria, observacoes, fornecedor_id)
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'warning')
    except Exception as e:
        flash(f'Erro ao editar conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_pagar_hoje'))

# CONTAS A RECEBER
@app.route('/contas-a-receber-hoje')
@required_permission('financeiro')
def contas_a_receber_hoje():
    filtro = request.args.get('filtro', 'hoje')
    status = request.args.get('status', 'pendente')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    contas = listar_contas_receber_por_periodo(filtro, data_inicio, data_fim, status)
    clientes = listar_clientes()
    hoje = hoje_br()
    
    # Calcular estatísticas
    total_contas = len(contas)
    total_valor = sum(conta['valor'] for conta in contas)
    valor_medio = total_valor / total_contas if total_contas > 0 else 0
    
    # Contar por status
    atrasadas = len([c for c in contas if c['dias_restantes'] < 0])
    vencendo_7_dias = len([c for c in contas if 0 <= c['dias_restantes'] <= 7])
    futuras = len([c for c in contas if c['dias_restantes'] > 7])
    
    estatisticas = {
        'total_contas': total_contas,
        'total_valor': total_valor,
        'valor_medio': valor_medio,
        'atrasadas': atrasadas,
        'vencendo_7_dias': vencendo_7_dias,
        'futuras': futuras
    }
    
    # Buscar configurações da empresa
    configuracoes_empresa = obter_configuracoes_empresa()
    
    return render_template('contas_a_receber_hoje.html', 
                         contas=contas, 
                         clientes=clientes, 
                         hoje=hoje,
                         filtro_atual=filtro,
                         status_atual=status,
                         estatisticas=estatisticas,
                         configuracoes_empresa=configuracoes_empresa)

@app.route('/contas-receber/receber/<int:id>', methods=['POST'])
@required_permission('financeiro')
def receber_conta_route(id):
    try:
        receber_conta(id)
        flash('Conta marcada como recebida!', 'success')
    except Exception as e:
        flash(f'Erro ao receber conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_receber_hoje'))

@app.route('/contas-receber/adicionar', methods=['POST'])
@required_permission('financeiro')
def adicionar_conta_receber_route():
    try:
        descricao = request.form.get('descricao')
        valor = float(request.form.get('valor'))
        data_vencimento = request.form.get('data_vencimento')
        cliente_id = request.form.get('cliente_id') or None
        observacoes = request.form.get('observacoes')
        
        sucesso, mensagem = adicionar_conta_receber(descricao, valor, data_vencimento, cliente_id, observacoes)
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'warning')
    except Exception as e:
        flash(f'Erro ao adicionar conta a receber: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_receber_hoje'))

@app.route('/contas-receber/duplicar/<int:id>', methods=['POST'])
@required_permission('financeiro')
def duplicar_conta_receber_route(id):
    try:
        sucesso, mensagem = duplicar_conta_receber(id)
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'warning')
    except Exception as e:
        flash(f'Erro ao duplicar conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_receber_hoje'))

@app.route('/contas-receber/excluir/<int:id>', methods=['POST'])
@required_permission('financeiro')
def excluir_conta_receber_route(id):
    try:
        sucesso, mensagem = excluir_conta_receber(id)
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'warning')
    except Exception as e:
        flash(f'Erro ao excluir conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_receber_hoje'))

@app.route('/contas-receber/obter/<int:id>', methods=['GET'])
@required_permission('financeiro')
def obter_conta_receber_route(id):
    try:
        sucesso, resultado = obter_conta_receber(id)
        if sucesso:
            return jsonify({'success': True, 'conta': resultado})
        else:
            return jsonify({'success': False, 'message': resultado})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/contas-receber/editar/<int:id>', methods=['POST'])
@required_permission('financeiro')
def editar_conta_receber_route(id):
    try:
        descricao = request.form.get('descricao')
        valor = float(request.form.get('valor'))
        data_vencimento = request.form.get('data_vencimento')
        cliente_id = request.form.get('cliente_id')
        observacoes = request.form.get('observacoes')
        
        if cliente_id and cliente_id.strip():
            cliente_id = int(cliente_id)
        else:
            cliente_id = None
        
        sucesso, mensagem = editar_conta_receber(id, descricao, valor, data_vencimento, cliente_id, observacoes)
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'warning')
    except Exception as e:
        flash(f'Erro ao editar conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_receber_hoje'))

# ORÇAMENTOS
@app.route('/orcamentos')
@login_required
def orcamentos():
    orcamentos_lista = listar_orcamentos()
    produtos_data = listar_produtos(page=1, per_page=999999)
    produtos = produtos_data['produtos']
    clientes = listar_clientes()
    return render_template('orcamentos.html', 
                         orcamentos=orcamentos_lista, 
                         produtos=produtos, 
                         clientes=clientes)

@app.route('/orcamentos/criar', methods=['POST'], endpoint='criar_orcamento_route')
@login_required
def criar_orcamento_route():
    try:
        # Receber dados do formulário
        cliente_id = request.form.get('cliente_id') or None
        desconto = float(request.form.get('desconto', 0))
        observacoes = request.form.get('observacoes', '')
        
        # Processar itens do orçamento
        itens = []
        produtos_ids = request.form.getlist('produto_id[]')
        quantidades = request.form.getlist('quantidade[]')
        precos = request.form.getlist('preco[]')
        
        for i in range(len(produtos_ids)):
            if produtos_ids[i] and quantidades[i] and precos[i]:
                itens.append({
                    'produto_id': int(produtos_ids[i]),
                    'quantidade': int(quantidades[i]),
                    'preco_unitario': float(precos[i])
                })
        
        if not itens:
            flash('Adicione pelo menos um item ao orçamento', 'error')
            return redirect(url_for('orcamentos'))
        
        # Criar orçamento
        orcamento_id = criar_orcamento(
            itens=itens,
            cliente_id=int(cliente_id) if cliente_id else None,
            desconto=desconto,
            observacoes=observacoes,
            usuario_id=current_user.id
        )
        
        flash('Orçamento criado com sucesso!', 'success')
        return redirect(url_for('visualizar_orcamento', id=orcamento_id))
        
    except Exception as e:
        flash(f'Erro ao criar orçamento: {str(e)}', 'error')
        return redirect(url_for('orcamentos'))

@app.route('/orcamentos/<int:id>')
@login_required
def visualizar_orcamento(id):
    orcamento = obter_orcamento(id)
    if not orcamento:
        flash('Orçamento não encontrado', 'error')
        return redirect(url_for('orcamentos'))
    
    config_empresa = obter_configuracoes_empresa()
    return render_template('visualizar_orcamento.html', orcamento=orcamento, config_empresa=config_empresa)

@app.route('/orcamentos/<int:id>/editar')
@login_required
def editar_orcamento_route(id):
    orcamento = obter_orcamento(id)
    if not orcamento:
        flash('Orçamento não encontrado!', 'error')
        return redirect(url_for('orcamentos'))
    
    # Verificar se o orçamento pode ser editado
    if orcamento['status'].lower() != 'pendente':
        flash('Apenas orçamentos pendentes podem ser editados!', 'error')
        return redirect(url_for('visualizar_orcamento', id=id))
    
    # Obter dados necessários
    produtos_data = listar_produtos(page=1, per_page=999999)
    produtos = produtos_data['produtos']
    clientes = listar_clientes()
    
    return render_template('editar_orcamento.html', 
                         orcamento=orcamento, 
                         produtos=produtos, 
                         clientes=clientes)

@app.route('/orcamentos/<int:id>/atualizar', methods=['POST'], endpoint='atualizar_orcamento_route')
@login_required
def atualizar_orcamento_route(id):
    try:
        # Obter dados do formulário
        cliente_id = request.form.get('cliente_id')
        if cliente_id == '':
            cliente_id = None
        
        desconto = float(request.form.get('desconto', 0))
        observacoes = request.form.get('observacoes', '')
        
        # Obter itens do orçamento
        produtos_ids = request.form.getlist('produto_id[]')
        quantidades = request.form.getlist('quantidade[]')
        precos_unitarios = request.form.getlist('preco_unitario[]')
        
        if not produtos_ids:
            flash('Adicione pelo menos um produto ao orçamento!', 'error')
            return redirect(url_for('editar_orcamento_route', id=id))
        
        # Preparar itens
        itens = []
        for i in range(len(produtos_ids)):
            item = {
                'produto_id': int(produtos_ids[i]),
                'quantidade': int(quantidades[i]),
                'preco_unitario': float(precos_unitarios[i])
            }
            itens.append(item)
        
        # Atualizar orçamento
        sucesso = atualizar_orcamento(id, itens, cliente_id, desconto, observacoes)
        
        if sucesso:
            flash('Orçamento atualizado com sucesso!', 'success')
            return redirect(url_for('visualizar_orcamento', id=id))
        else:
            flash('Erro ao atualizar orçamento!', 'error')
            return redirect(url_for('editar_orcamento_route', id=id))
            
    except Exception as e:
        flash(f'Erro ao atualizar orçamento: {str(e)}', 'error')
        return redirect(url_for('editar_orcamento_route', id=id))

@app.route('/orcamentos/<int:id>/converter', methods=['POST'])
@login_required
def converter_orcamento_route(id):
    try:
        forma_pagamento = request.form.get('forma_pagamento')
        if not forma_pagamento:
            flash('Forma de pagamento é obrigatória', 'error')
            return redirect(url_for('visualizar_orcamento', id=id))
        
        venda_id = converter_orcamento_em_venda(id, forma_pagamento)
        flash('Orçamento convertido em venda com sucesso!', 'success')
        return redirect(url_for('vendas'))
        
    except Exception as e:
        flash(f'Erro ao converter orçamento: {str(e)}', 'error')
        return redirect(url_for('visualizar_orcamento', id=id))

@app.route('/orcamentos/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_orcamento_route(id):
    try:
        sucesso = excluir_orcamento(id)
        if sucesso:
            flash('Orçamento excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir orçamento!', 'error')
    except Exception as e:
        flash(f'Erro ao excluir orçamento: {str(e)}', 'error')
    
    return redirect(url_for('orcamentos'))

# RELATÓRIOS
@app.route('/relatorios')
@login_required
def relatorios():
    # Verificar se o usuário tem permissão para acessar relatórios
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('relatorios.html')

@app.route('/relatorios/vendas')
@login_required
def relatorio_vendas():
    # Verificar permissão
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obter parâmetros da URL
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    cliente_id = request.args.get('cliente_id')
    
    # Gerar relatório
    relatorio = gerar_relatorio_vendas(data_inicio, data_fim, cliente_id)
    
    # Buscar lista de clientes para o filtro
    clientes = listar_clientes()
    
    return render_template('relatorios/vendas.html', 
                         relatorio=relatorio, 
                         clientes=clientes,
                         data_inicio=data_inicio,
                         data_fim=data_fim,
                         cliente_id=cliente_id)

@app.route('/relatorios/produtos-mais-vendidos')
@login_required
def relatorio_produtos_mais_vendidos():
    # Verificar permissão
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obter parâmetros da URL
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    limite = int(request.args.get('limite', 10))
    
    # Gerar relatório
    relatorio = gerar_relatorio_produtos_mais_vendidos(data_inicio, data_fim, limite)
    
    return render_template('relatorios/produtos_mais_vendidos.html', 
                         relatorio=relatorio,
                         data_inicio=data_inicio,
                         data_fim=data_fim,
                         limite=limite)

@app.route('/relatorios/estoque')
@login_required
def relatorio_estoque():
    # Verificar permissão
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    # Gerar relatório
    relatorio = gerar_relatorio_estoque()
    
    # Obter configurações da empresa
    configuracoes_empresa = obter_configuracoes_empresa()
    
    return render_template('relatorios/estoque.html', 
                         relatorio=relatorio,
                         configuracoes_empresa=configuracoes_empresa)

@app.route('/relatorios/financeiro')
@login_required
def relatorio_financeiro():
    # Verificar permissão
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obter parâmetros da URL
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Gerar relatório
    relatorio = gerar_relatorio_financeiro(data_inicio, data_fim)
    
    return render_template('relatorios/financeiro.html', 
                         relatorio=relatorio,
                         data_inicio=data_inicio,
                         data_fim=data_fim)

# FUNÇÕES DE EXPORTAÇÃO PDF
def criar_cabecalho_empresa(doc, styles, config_empresa):
    """Cria cabeçalho padrão com informações da empresa"""
    from reportlab.platypus import Image
    story = []
    
    # Verificar se existe logo da empresa
    logo_path = None
    if config_empresa.get('logo_path'):
        # Logo personalizada
        logo_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', config_empresa['logo_path'].lstrip('/'))
        if os.path.exists(logo_full_path):
            logo_path = logo_full_path
    
    # Se não houver logo personalizada, tentar logo padrão
    if not logo_path:
        default_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'empresa', 'logo.png')
        if os.path.exists(default_logo):
            logo_path = default_logo
    
    # Se tiver logo, criar layout com logo e texto
    if logo_path:
        try:
            # Criar tabela com logo e informações
            logo_img = Image(logo_path, width=60, height=60)
            
            empresa_info = []
            empresa_info.append(Paragraph(config_empresa.get('nome_empresa', 'FG AUTO PEÇAS'), 
                                        ParagraphStyle('EmpresaTitle', parent=styles['Heading1'], 
                                                     fontSize=16, textColor=colors.HexColor('#1a237e'))))
            
            # Informações da empresa
            info_empresa = []
            if config_empresa.get('endereco'):
                info_empresa.append(config_empresa['endereco'])
            if config_empresa.get('cidade') and config_empresa.get('estado'):
                info_empresa.append(f"{config_empresa['cidade']} - {config_empresa['estado']}")
            if config_empresa.get('telefone'):
                info_empresa.append(f"Tel: {config_empresa['telefone']}")
            if config_empresa.get('email'):
                info_empresa.append(f"Email: {config_empresa['email']}")
            
            if info_empresa:
                empresa_info.append(Paragraph(' | '.join(info_empresa), 
                                            ParagraphStyle('EmpresaInfo', parent=styles['Normal'], 
                                                         fontSize=9, textColor=colors.HexColor('#546e7a'))))
            
            # Criar tabela com logo e informações
            header_data = [[logo_img, empresa_info]]
            header_table = Table(header_data, colWidths=[80, 450])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            story.append(header_table)
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            # Fallback para texto apenas
            story.extend(criar_cabecalho_texto_apenas(styles, config_empresa))
    else:
        # Sem logo, apenas texto
        story.extend(criar_cabecalho_texto_apenas(styles, config_empresa))
    
    # Linha separadora
    story.append(Spacer(1, 10))
    
    return story

def criar_cabecalho_texto_apenas(styles, config_empresa):
    """Cria cabeçalho apenas com texto quando não há logo"""
    story = []
    
    # Título da empresa
    title_style = ParagraphStyle(
        'EmpresaTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=5,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a237e')
    )
    
    empresa_style = ParagraphStyle(
        'EmpresaInfo',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#546e7a')
    )
    
    story.append(Paragraph(config_empresa.get('nome_empresa', 'FG AUTO PEÇAS'), title_style))
    
    # Informações da empresa
    info_empresa = []
    if config_empresa.get('endereco'):
        info_empresa.append(config_empresa['endereco'])
    if config_empresa.get('cidade') and config_empresa.get('estado'):
        info_empresa.append(f"{config_empresa['cidade']} - {config_empresa['estado']}")
    if config_empresa.get('cep'):
        info_empresa.append(f"CEP: {config_empresa['cep']}")
    if config_empresa.get('telefone'):
        info_empresa.append(f"Tel: {config_empresa['telefone']}")
    if config_empresa.get('email'):
        info_empresa.append(f"Email: {config_empresa['email']}")
    if config_empresa.get('cnpj'):
        info_empresa.append(f"CNPJ: {config_empresa['cnpj']}")
    
    if info_empresa:
        story.append(Paragraph(' | '.join(info_empresa), empresa_style))
    
    return story

def criar_rodape_empresa(doc, config_empresa):
    """Cria rodapé com informações da empresa"""
    rodape_texto = f"Relatório gerado pelo Sistema {config_empresa.get('nome_empresa', 'FG AUTO PEÇAS')} - {agora_br().strftime('%d/%m/%Y às %H:%M')}"
    return rodape_texto

def criar_pdf_vendas(relatorio, data_inicio=None, data_fim=None, cliente_selecionado=None):
    """Gera PDF do relatório de vendas com layout MODERNO"""
    from pdf_layout_moderno import (
        CoresPDF, criar_cabecalho_empresa_moderno, criar_cabecalho_moderno, criar_painel_kpis, 
        criar_tabela_moderna, criar_secao_titulo, criar_rodape_moderno,
        formatar_moeda
    )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=70, 
                           leftMargin=40, rightMargin=40)
    story = []
    config_empresa = obter_configuracoes_empresa()
    
    # CABEÇALHO DA EMPRESA (Logo e informações)
    story.extend(criar_cabecalho_empresa_moderno(config_empresa))
    
    # TÍTULO DO RELATÓRIO
    subtitulo = ""
    if data_inicio and data_fim:
        subtitulo = f"Período: {data_inicio} a {data_fim}"
    if cliente_selecionado:
        if subtitulo:
            subtitulo += f" | Cliente: {cliente_selecionado}"
        else:
            subtitulo = f"Cliente: {cliente_selecionado}"
    
    story.extend(criar_cabecalho_moderno("RELATÓRIO DE VENDAS", subtitulo=subtitulo))
    
    # PAINEL DE KPIs
    kpis = [
        {
            'titulo': 'Total de Vendas',
            'valor': str(relatorio.get('quantidade_vendas', 0)),
            'subtitulo': 'transações',
            'cor': CoresPDF.PRIMARIA
        },
        {
            'titulo': 'Valor Total',
            'valor': formatar_moeda(relatorio.get('total_geral', 0)),
            'subtitulo': 'faturamento',
            'cor': CoresPDF.SUCESSO
        },
        {
            'titulo': 'Ticket Médio',
            'valor': formatar_moeda(relatorio.get('ticket_medio', 0)),
            'subtitulo': 'por venda',
            'cor': CoresPDF.INFO
        }
    ]
    
    story.append(criar_painel_kpis(kpis))
    story.append(Spacer(1, 25))
    
    # VENDAS DETALHADAS - TODAS AS VENDAS
    if relatorio.get('vendas'):
        story.append(criar_secao_titulo(f"🛒 VENDAS DETALHADAS ({len(relatorio['vendas'])} vendas)"))
        story.append(Spacer(1, 10))
        
        # Dividir em páginas se necessário
        vendas = relatorio['vendas']
        vendas_por_pagina = 30
        
        for i in range(0, len(vendas), vendas_por_pagina):
            vendas_pagina = vendas[i:i + vendas_por_pagina]
            
            vendas_data = [['ID', 'Data', 'Cliente', 'Vendedor', 'Itens', 'Pagamento', 'Total']]
            
            for venda in vendas_pagina:
                vendas_data.append([
                    str(venda['id']),
                    str(venda['data_venda'])[:10],
                    str(venda['cliente'])[:18],
                    str(venda['vendedor'])[:14],
                    str(venda['quantidade_itens']),
                    str(venda['forma_pagamento'])[:10],
                    formatar_moeda(venda['total'])
                ])
            
            # Adicionar linha de total
            vendas_data.append([
                '', '', '', '', '', 'TOTAL:',
                formatar_moeda(sum(v['total'] for v in vendas_pagina))
            ])
            
            vendas_table = criar_tabela_moderna(
                vendas_data,
                [0.6*inch, 0.9*inch, 1.5*inch, 1.2*inch, 0.6*inch, 1*inch, 1*inch],
                destacar_total=True,
                cores_alternadas=True
            )
            story.append(vendas_table)
            
            if i + vendas_por_pagina < len(vendas):
                story.append(PageBreak())
                story.append(Spacer(1, 10))
    
    # Rodapé moderno
    def add_page_elements(canvas, doc):
        criar_rodape_moderno(canvas, doc, config_empresa, canvas.getPageNumber())
    
    doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
    buffer.seek(0)
    return buffer
    
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer

def criar_pdf_contas_a_receber(relatorio, data_inicio=None, data_fim=None, status=None):
    """Gera PDF do relatório de contas a receber com layout MODERNO"""
    from pdf_layout_moderno import (
        CoresPDF, criar_cabecalho_empresa_moderno, criar_cabecalho_moderno, criar_painel_kpis,
        criar_tabela_moderna, criar_secao_titulo, criar_rodape_moderno, formatar_moeda
    )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=70, 
                           leftMargin=40, rightMargin=40)
    story = []
    config_empresa = obter_configuracoes_empresa()
    
    # CABEÇALHO DA EMPRESA (Logo e informações)
    story.extend(criar_cabecalho_empresa_moderno(config_empresa))
    
    # TÍTULO DO RELATÓRIO
    subtitulo = ""
    if data_inicio and data_fim:
        subtitulo = f"Período: {data_inicio} a {data_fim}"
    if status:
        if subtitulo:
            subtitulo += f" | Status: {status.capitalize()}"
        else:
            subtitulo = f"Status: {status.capitalize()}"
    
    story.extend(criar_cabecalho_moderno("CONTAS A RECEBER", subtitulo=subtitulo))

    # PAINEL DE KPIs
    if relatorio.get('estatisticas'):
        estatisticas = relatorio['estatisticas']
        kpis = [
            {
                'titulo': 'Total de Contas',
                'valor': str(estatisticas.get('total_contas', 0)),
                'subtitulo': 'contas',
                'cor': CoresPDF.PRIMARIA
            },
            {
                'titulo': 'Valor Total',
                'valor': formatar_moeda(estatisticas.get('total_valor', 0)),
                'subtitulo': 'a receber',
                'cor': CoresPDF.SUCESSO
            },
            {
                'titulo': 'Valor Médio',
                'valor': formatar_moeda(estatisticas.get('valor_medio', 0)),
                'subtitulo': 'por conta',
                'cor': CoresPDF.INFO
            },
            {
                'titulo': 'Atrasadas',
                'valor': str(estatisticas.get('atrasadas', 0)),
                'subtitulo': 'contas',
                'cor': CoresPDF.ERRO
            }
        ]
        story.append(criar_painel_kpis(kpis))
        story.append(Spacer(1, 25))

    # CONTAS DETALHADAS
    if relatorio.get('contas'):
        story.append(criar_secao_titulo(f"📋 CONTAS DETALHADAS ({len(relatorio['contas'])} registros)"))
        story.append(Spacer(1, 10))
        
        contas_data = [['ID', 'Vencimento', 'Cliente', 'Descrição', 'Valor', 'Status']]
        
        for conta in relatorio['contas']:
            # Ícone de status
            status_icon = ''
            if conta['status'] == 'pago':
                status_icon = '✅ Pago'
            elif conta['status'] == 'pendente':
                status_icon = '⏳ Pendente'
            elif conta['status'] == 'atrasado':
                status_icon = '🔴 Atrasado'
            else:
                status_icon = conta['status']
            
            contas_data.append([
                str(conta['id']),
                str(conta['data_vencimento'])[:10],
                str(conta['cliente_nome'])[:25],
                str(conta['descricao'])[:30],
                formatar_moeda(conta['valor']),
                status_icon
            ])
        
        contas_table = criar_tabela_moderna(
            contas_data,
            [0.5*inch, 1*inch, 1.8*inch, 2.2*inch, 1*inch, 1*inch],
            cores_alternadas=True
        )
        story.append(contas_table)
    
    # RODAPÉ MODERNO
    def add_page_footer(canvas, doc):
        criar_rodape_moderno(canvas, doc, config_empresa, canvas.getPageNumber())
    
    doc.build(story, onFirstPage=add_page_footer, onLaterPages=add_page_footer)
    buffer.seek(0)
    return buffer

@app.route('/relatorios/contas-a-receber/pdf')
@login_required
def exportar_contas_a_receber_pdf():
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    filtro = request.args.get('filtro', 'todos')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    status = request.args.get('status', 'pendente')
    
    contas = listar_contas_receber_por_periodo(filtro, data_inicio, data_fim, status)
    estatisticas = {
        'total_contas': len(contas),
        'total_valor': sum(c['valor'] for c in contas),
        'valor_medio': sum(c['valor'] for c in contas) / len(contas) if contas else 0,
        'atrasadas': len([c for c in contas if c['dias_restantes'] < 0])
    }
    relatorio = {'contas': contas, 'estatisticas': estatisticas}
    
    pdf_buffer = criar_pdf_contas_a_receber(relatorio, data_inicio, data_fim, status)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_contas_a_receber.pdf'
    
    return response

def criar_pdf_contas_a_pagar(relatorio, data_inicio=None, data_fim=None, status=None):
    """Gera PDF do relatório de contas a pagar com layout MODERNO"""
    from pdf_layout_moderno import (
        CoresPDF, criar_cabecalho_empresa_moderno, criar_cabecalho_moderno, criar_painel_kpis,
        criar_tabela_moderna, criar_secao_titulo, criar_rodape_moderno, formatar_moeda
    )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=70, 
                           leftMargin=40, rightMargin=40)
    story = []
    config_empresa = obter_configuracoes_empresa()
    
    # CABEÇALHO DA EMPRESA (Logo e informações)
    story.extend(criar_cabecalho_empresa_moderno(config_empresa))
    
    # TÍTULO DO RELATÓRIO
    subtitulo = ""
    if data_inicio and data_fim:
        subtitulo = f"Período: {data_inicio} a {data_fim}"
    if status:
        if subtitulo:
            subtitulo += f" | Status: {status.capitalize()}"
        else:
            subtitulo = f"Status: {status.capitalize()}"
    
    story.extend(criar_cabecalho_moderno("CONTAS A PAGAR", subtitulo=subtitulo))

    # PAINEL DE KPIs
    if relatorio.get('estatisticas'):
        estatisticas = relatorio['estatisticas']
        kpis = [
            {
                'titulo': 'Total de Contas',
                'valor': str(estatisticas.get('total_contas', 0)),
                'subtitulo': 'contas',
                'cor': CoresPDF.PRIMARIA
            },
            {
                'titulo': 'Valor Total',
                'valor': formatar_moeda(estatisticas.get('total_valor', 0)),
                'subtitulo': 'a pagar',
                'cor': CoresPDF.AVISO
            },
            {
                'titulo': 'Valor Médio',
                'valor': formatar_moeda(estatisticas.get('valor_medio', 0)),
                'subtitulo': 'por conta',
                'cor': CoresPDF.INFO
            },
            {
                'titulo': 'Atrasadas',
                'valor': str(estatisticas.get('atrasadas', 0)),
                'subtitulo': 'contas',
                'cor': CoresPDF.ERRO
            }
        ]
        story.append(criar_painel_kpis(kpis))
        story.append(Spacer(1, 25))

    # CONTAS DETALHADAS
    if relatorio.get('contas'):
        story.append(criar_secao_titulo(f"📋 CONTAS DETALHADAS ({len(relatorio['contas'])} registros)"))
        story.append(Spacer(1, 10))
        
        contas_data = [['ID', 'Vencimento', 'Fornecedor', 'Descrição', 'Categoria', 'Valor', 'Status']]
        
        for conta in relatorio['contas']:
            # Ícone de status
            status_icon = ''
            if conta['status'] == 'pago':
                status_icon = '✅ Pago'
            elif conta['status'] == 'pendente':
                status_icon = '⏳ Pendente'
            elif conta['status'] == 'atrasado':
                status_icon = '🔴 Atrasado'
            else:
                status_icon = conta['status']
            
            contas_data.append([
                str(conta['id']),
                str(conta['data_vencimento'])[:10],
                str(conta['fornecedor_nome'])[:22],
                str(conta['descricao'])[:25],
                str(conta['categoria'])[:15],
                formatar_moeda(conta['valor']),
                status_icon
            ])
        
        contas_table = criar_tabela_moderna(
            contas_data,
            [0.5*inch, 0.9*inch, 1.5*inch, 1.8*inch, 0.9*inch, 0.9*inch, 0.9*inch],
            cores_alternadas=True
        )
        story.append(contas_table)
    
    # RODAPÉ MODERNO
    def add_page_footer(canvas, doc):
        criar_rodape_moderno(canvas, doc, config_empresa, canvas.getPageNumber())
    
    doc.build(story, onFirstPage=add_page_footer, onLaterPages=add_page_footer)
    buffer.seek(0)
    return buffer

@app.route('/relatorios/contas-a-pagar/pdf')
@login_required
def exportar_contas_a_pagar_pdf():
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    filtro = request.args.get('filtro', 'todos')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    status = request.args.get('status', 'pendente')
    
    contas = listar_contas_pagar_por_periodo(filtro, data_inicio, data_fim, status)
    estatisticas = {
        'total_contas': len(contas),
        'total_valor': sum(c['valor'] for c in contas),
        'valor_medio': sum(c['valor'] for c in contas) / len(contas) if contas else 0,
        'atrasadas': len([c for c in contas if c['dias_restantes'] < 0])
    }
    relatorio = {'contas': contas, 'estatisticas': estatisticas}
    
    pdf_buffer = criar_pdf_contas_a_pagar(relatorio, data_inicio, data_fim, status)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_contas_a_pagar.pdf'
    
    return response

def criar_pdf_produtos_mais_vendidos(relatorio, data_inicio=None, data_fim=None, limite=10):
    """Gera PDF do relatório de produtos mais vendidos com layout MODERNO"""
    from pdf_layout_moderno import (
        CoresPDF, criar_cabecalho_empresa_moderno, criar_cabecalho_moderno, criar_painel_kpis, 
        criar_tabela_moderna, criar_secao_titulo, criar_rodape_moderno,
        formatar_moeda
    )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=70, 
                           leftMargin=40, rightMargin=40)
    story = []
    config_empresa = obter_configuracoes_empresa()
    
    # CABEÇALHO DA EMPRESA (Logo e informações)
    story.extend(criar_cabecalho_empresa_moderno(config_empresa))
    
    # TÍTULO DO RELATÓRIO
    subtitulo = ""
    if data_inicio and data_fim:
        subtitulo = f"Período: {data_inicio} a {data_fim}"
    
    story.extend(criar_cabecalho_moderno(
        "PRODUTOS MAIS VENDIDOS",
        subtitulo=subtitulo
    ))
    
    # PAINEL DE KPIs - Mostrar top 3
    if relatorio.get('produtos') and len(relatorio['produtos']) >= 3:
        top_3 = relatorio['produtos'][:3]
        kpis = []
        medalhas = ['🥇', '🥈', '🥉']
        cores = [CoresPDF.SUCESSO, CoresPDF.INFO, CoresPDF.AVISO]
        
        for i, produto in enumerate(top_3):
            kpis.append({
                'titulo': f"{medalhas[i]} {i+1}º Lugar",
                'valor': str(produto['quantidade_vendida']) + ' un.',
                'subtitulo': str(produto['nome'])[:20],
                'cor': cores[i]
            })
        
        # Se houver valor total, adicionar
        if relatorio.get('total_vendido'):
            kpis.append({
                'titulo': 'Total Vendido',
                'valor': formatar_moeda(relatorio['total_vendido']),
                'subtitulo': f'{limite} produtos',
                'cor': CoresPDF.PRIMARIA
            })
        
        story.append(criar_painel_kpis(kpis[:4]))  # Máximo 4 KPIs
        story.append(Spacer(1, 25))
    
    # RANKING COMPLETO
    if relatorio.get('produtos'):
        story.append(criar_secao_titulo(f"📊 RANKING COMPLETO (Top {limite})"))
        story.append(Spacer(1, 10))
        
        produtos_data = [['🏆', 'Produto', 'Código', 'Qtd Vendida', 'Valor Total', '% Total']]
        
        # Calcular total para porcentagem
        total_quantidade = sum(p['quantidade_vendida'] for p in relatorio['produtos'])
        total_valor = sum(p['valor_total'] for p in relatorio['produtos'])
        
        for i, produto in enumerate(relatorio['produtos'], 1):
            # Ícones para top 3
            if i == 1:
                posicao = '🥇'
            elif i == 2:
                posicao = '🥈'
            elif i == 3:
                posicao = '🥉'
            else:
                posicao = f"{i}º"
            
            # Calcular porcentagem
            percent = (produto['valor_total'] / total_valor * 100) if total_valor > 0 else 0
            
            produtos_data.append([
                posicao,
                str(produto['nome'])[:28],
                str(produto['codigo'])[:12],
                str(produto['quantidade_vendida']),
                formatar_moeda(produto['valor_total']),
                f"{percent:.1f}%"
            ])
        
        # Linha de total
        produtos_data.append([
            '', 'TOTAL', '', str(total_quantidade), formatar_moeda(total_valor), '100%'
        ])
        
        produtos_table = criar_tabela_moderna(
            produtos_data,
            [0.7*inch, 2.3*inch, 1*inch, 1*inch, 1.2*inch, 0.8*inch],
            destacar_total=True,
            cores_alternadas=True
        )
        story.append(produtos_table)
    
    # Rodapé moderno
    def add_page_elements(canvas, doc):
        criar_rodape_moderno(canvas, doc, config_empresa, canvas.getPageNumber())
    
    doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
    buffer.seek(0)
    return buffer



def criar_pdf_estoque(relatorio):
    """Gera PDF do relatório de estoque com layout MODERNO e cards."""
    from pdf_layout_moderno import (
        CoresPDF, criar_cabecalho_empresa_moderno, criar_cabecalho_moderno, criar_painel_kpis, 
        criar_tabela_moderna, criar_secao_titulo, criar_rodape_moderno,
        formatar_moeda
    )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=70, 
                           leftMargin=40, rightMargin=40)
    story = []
    config_empresa = obter_configuracoes_empresa()

    # Verificar se há erro no relatório
    if relatorio.get('erro'):
        story.append(Paragraph(f"Erro ao gerar relatório: {relatorio['erro']}", 
                              ParagraphStyle('Normal', fontSize=12)))
        doc.build(story)
        buffer.seek(0)
        return buffer

    # CABEÇALHO DA EMPRESA (Logo e informações)
    story.extend(criar_cabecalho_empresa_moderno(config_empresa))
    
    # TÍTULO DO RELATÓRIO
    story.extend(criar_cabecalho_moderno("RELATÓRIO DE ESTOQUE"))

    # PAINEL DE KPIs COM CARDS
    resumo = relatorio.get('resumo', {})
    kpis = [
        {
            'titulo': 'Total de Produtos',
            'valor': str(resumo.get('total_produtos', 0)),
            'subtitulo': 'cadastrados',
            'cor': CoresPDF.PRIMARIA
        },
        {
            'titulo': 'Sem Estoque',
            'valor': str(resumo.get('produtos_sem_estoque', 0)),
            'subtitulo': 'produtos',
            'cor': CoresPDF.ERRO
        },
        {
            'titulo': 'Estoque Baixo',
            'valor': str(resumo.get('produtos_estoque_baixo', 0)),
            'subtitulo': 'produtos',
            'cor': CoresPDF.AVISO
        },
        {
            'titulo': 'Valor Total',
            'valor': formatar_moeda(resumo.get('valor_total_estoque', 0)),
            'subtitulo': 'em estoque',
            'cor': CoresPDF.SUCESSO
        }
    ]
    
    story.append(criar_painel_kpis(kpis))
    story.append(Spacer(1, 25))

    # ANÁLISE POR CATEGORIA
    if relatorio.get('categorias'):
        story.append(criar_secao_titulo("📊 ANÁLISE POR CATEGORIA"))
        story.append(Spacer(1, 10))
        
        categorias_data = [['Categoria', 'Qtd Produtos', 'Total Estoque', 'Valor Total']]
        
        for cat in relatorio['categorias']:
            categorias_data.append([
                str(cat.get('nome', 'Sem categoria'))[:30],
                str(cat.get('quantidade_produtos', 0)),
                str(cat.get('total_estoque', 0)) + ' un.',
                formatar_moeda(cat.get('valor_categoria', 0))
            ])
        
        categorias_table = criar_tabela_moderna(
            categorias_data,
            [2.5*inch, 1.5*inch, 1.5*inch, 2*inch],
            cores_alternadas=True
        )
        story.append(categorias_table)
        story.append(Spacer(1, 20))

    # PRODUTOS DETALHADOS - TODOS OS PRODUTOS
    if relatorio.get('produtos'):
        story.append(criar_secao_titulo(f"📦 PRODUTOS DETALHADOS ({len(relatorio['produtos'])} itens)"))
        story.append(Spacer(1, 10))
        
        # Dividir produtos em páginas se necessário
        produtos = relatorio['produtos']
        produtos_por_pagina = 35  # Máximo de produtos por página
        
        for i in range(0, len(produtos), produtos_por_pagina):
            produtos_pagina = produtos[i:i + produtos_por_pagina]
            
            produtos_data = [['Código', 'Produto', 'Qtd', 'Mín.', 'P. Venda', 'Val. Est.', 'Status']]
            
            for produto in produtos_pagina:
                status = produto.get('status', 'N/A')
                
                # Formatar status com cor
                if status == 'Sem Estoque':
                    status_fmt = '🔴 ' + status
                elif status == 'Estoque Baixo':
                    status_fmt = '🟡 ' + status
                else:
                    status_fmt = '🟢 OK'
                
                produtos_data.append([
                    str(produto.get('codigo', produto.get('codigo_barras', '-')))[:12],
                    str(produto.get('nome', ''))[:28],
                    str(produto.get('estoque', 0)),
                    str(produto.get('estoque_minimo', 1)),
                    formatar_moeda(produto.get('preco', 0)),
                    formatar_moeda(produto.get('valor_estoque', 0)),
                    status_fmt
                ])
            
            produtos_table = criar_tabela_moderna(
                produtos_data,
                [0.8*inch, 2*inch, 0.5*inch, 0.5*inch, 0.9*inch, 1*inch, 1.3*inch],
                cores_alternadas=True
            )
            story.append(produtos_table)
            
            # Adicionar quebra de página se houver mais produtos
            if i + produtos_por_pagina < len(produtos):
                story.append(PageBreak())
                story.append(Spacer(1, 10))

    # Rodapé personalizado
    def add_page_elements(canvas, doc):
        criar_rodape_moderno(canvas, doc, config_empresa, canvas.getPageNumber())
    
    doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
    buffer.seek(0)
    return buffer

# ROTAS DE EXPORTAÇÃO PDF
@app.route('/relatorios/vendas/pdf')
@login_required
def exportar_vendas_pdf():
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    cliente_id = request.args.get('cliente_id')
    
    relatorio = gerar_relatorio_vendas(data_inicio, data_fim, cliente_id)
    
    # Buscar nome do cliente se especificado
    cliente_nome = None
    if cliente_id:
        clientes = listar_clientes()
        for cliente in clientes:
            if str(cliente.id) == str(cliente_id):
                cliente_nome = cliente.nome
                break
    
    pdf_buffer = criar_pdf_vendas(relatorio, data_inicio, data_fim, cliente_nome)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_vendas.pdf'
    
    return response

@app.route('/relatorios/produtos-mais-vendidos/pdf')
@login_required
def exportar_produtos_mais_vendidos_pdf():
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    limite = int(request.args.get('limite', 10))
    
    relatorio = gerar_relatorio_produtos_mais_vendidos(data_inicio, data_fim, limite)
    pdf_buffer = criar_pdf_produtos_mais_vendidos(relatorio, data_inicio, data_fim, limite)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_produtos_mais_vendidos.pdf'
    
    return response

@app.route('/relatorios/estoque/pdf')
@login_required
def exportar_estoque_pdf():
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    relatorio = gerar_relatorio_estoque()
    pdf_buffer = criar_pdf_estoque(relatorio)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_estoque.pdf'
    
    return response

def criar_pdf_caixa(status_caixa, movimentacoes, resumo_vendas, data):
    """Gera PDF do relatório de caixa com layout MODERNO."""
    from pdf_layout_moderno import (
        CoresPDF, criar_cabecalho_empresa_moderno, criar_cabecalho_moderno, criar_painel_kpis, 
        criar_tabela_moderna, criar_secao_titulo, criar_rodape_moderno,
        criar_card_resumo, formatar_moeda
    )
    from datetime import datetime
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=70, 
                           leftMargin=40, rightMargin=40)
    story = []
    config_empresa = obter_configuracoes_empresa()

    # Formatar data
    data_formatada = datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
    
    # CABEÇALHO DA EMPRESA (Logo e informações)
    story.extend(criar_cabecalho_empresa_moderno(config_empresa))
    
    # TÍTULO DO RELATÓRIO
    story.extend(criar_cabecalho_moderno(
        f"RELATÓRIO DE CAIXA",
        subtitulo=f"Data: {data_formatada}"
    ))

    # PAINEL DE KPIs DO CAIXA
    if status_caixa:
        kpis = [
            {
                'titulo': 'Saldo Inicial',
                'valor': formatar_moeda(status_caixa['saldo_inicial']),
                'subtitulo': status_caixa['data_abertura'].strftime('%H:%M') if status_caixa['data_abertura'] else '-',
                'cor': CoresPDF.INFO
            },
            {
                'titulo': 'Entradas',
                'valor': formatar_moeda(status_caixa['total_entradas']),
                'subtitulo': f"{status_caixa['total_movimentacoes']} movimentações",
                'cor': CoresPDF.SUCESSO
            },
            {
                'titulo': 'Saídas',
                'valor': formatar_moeda(status_caixa['total_saidas']),
                'subtitulo': 'retiradas',
                'cor': CoresPDF.ERRO
            },
            {
                'titulo': 'Saldo Atual',
                'valor': formatar_moeda(status_caixa['saldo_atual']),
                'subtitulo': 'no caixa',
                'cor': CoresPDF.PRIMARIA
            }
        ]
        story.append(criar_painel_kpis(kpis))
        story.append(Spacer(1, 20))

    # VENDAS DO DIA
    if resumo_vendas and resumo_vendas.get('total_vendas', 0) > 0:
        itens = [
            ('Total de Vendas:', str(resumo_vendas.get('total_vendas', 0)) + ' vendas'),
            ('Valor das Vendas:', formatar_moeda(resumo_vendas.get('valor_vendas', 0))),
            ('Itens Vendidos:', str(resumo_vendas.get('itens_vendidos', 0)) + ' unidades')
        ]
        story.append(criar_card_resumo('💰 Vendas do Dia', itens, CoresPDF.SUCESSO))
        story.append(Spacer(1, 20))

    # MOVIMENTAÇÕES DETALHADAS
    if movimentacoes:
        story.append(criar_secao_titulo(f"📝 MOVIMENTAÇÕES ({len(movimentacoes)} registros)"))
        story.append(Spacer(1, 10))
        
        mov_data = [['Hora', 'Tipo', 'Categoria', 'Descrição', 'Valor', 'Usuário']]
        
        for mov in movimentacoes:
            hora = mov['data_movimentacao'].strftime('%H:%M') if mov['data_movimentacao'] else '-'
            tipo = '⬆️ Entrada' if mov['tipo'] == 'entrada' else '⬇️ Saída'
            valor = formatar_moeda(mov['valor'])
            if mov['tipo'] == 'saida':
                valor = f"-{valor}"
            else:
                valor = f"+{valor}"
            
            mov_data.append([
                hora,
                tipo,
                mov['categoria'][:12],
                mov['descricao'][:28],
                valor,
                mov['usuario_nome'][:14] if mov['usuario_nome'] else '-'
            ])
        
        mov_table = criar_tabela_moderna(
            mov_data,
            [0.7*inch, 1*inch, 1*inch, 2*inch, 0.9*inch, 1.2*inch],
            cores_alternadas=True
        )
        story.append(mov_table)
        story.append(Spacer(1, 20))

    # RESUMO FINANCEIRO FINAL
    if status_caixa:
        saldo_dia = status_caixa['total_entradas'] - status_caixa['total_saidas']
        itens = [
            ('Saldo Inicial:', formatar_moeda(status_caixa['saldo_inicial'])),
            ('(+) Total de Entradas:', formatar_moeda(status_caixa['total_entradas'])),
            ('(-) Total de Saídas:', formatar_moeda(status_caixa['total_saidas'])),
            ('(=) Saldo do Dia:', formatar_moeda(saldo_dia)),
            ('Saldo Atual:', formatar_moeda(status_caixa['saldo_atual']))
        ]
        story.append(criar_card_resumo('📊 Resumo Financeiro', itens, CoresPDF.PRIMARIA))

    # Rodapé moderno
    def add_page_elements(canvas, doc):
        criar_rodape_moderno(canvas, doc, config_empresa, canvas.getPageNumber())

    doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
    buffer.seek(0)
    return buffer

def criar_pdf_financeiro(relatorio, data_inicio=None, data_fim=None):
    """Gera PDF do relatório financeiro com layout MODERNO."""
    from pdf_layout_moderno import (
        CoresPDF, criar_cabecalho_empresa_moderno, criar_cabecalho_moderno, criar_painel_kpis, 
        criar_tabela_moderna, criar_secao_titulo, criar_rodape_moderno,
        criar_card_resumo, formatar_moeda, formatar_porcentagem
    )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=70, 
                           leftMargin=40, rightMargin=40)
    story = []
    config_empresa = obter_configuracoes_empresa()

    # CABEÇALHO DA EMPRESA (Logo e informações)
    story.extend(criar_cabecalho_empresa_moderno(config_empresa))
    
    # TÍTULO DO RELATÓRIO
    subtitulo = ""
    if data_inicio and data_fim:
        subtitulo = f"Período: {data_inicio} a {data_fim}"
    
    story.extend(criar_cabecalho_moderno("RELATÓRIO FINANCEIRO", subtitulo=subtitulo))

    # PAINEL DE KPIs FINANCEIROS
    resumo = relatorio.get('resumo', {})
    saldo_liquido = resumo.get('saldo_liquido', 0)
    cor_saldo = CoresPDF.SUCESSO if saldo_liquido >= 0 else CoresPDF.ERRO
    
    kpis = [
        {
            'titulo': 'Total Vendas',
            'valor': formatar_moeda(resumo.get('total_vendas', 0)),
            'subtitulo': 'faturamento',
            'cor': CoresPDF.PRIMARIA
        },
        {
            'titulo': 'Total Recebido',
            'valor': formatar_moeda(resumo.get('total_recebido', 0)),
            'subtitulo': 'recebimentos',
            'cor': CoresPDF.SUCESSO
        },
        {
            'titulo': 'Total Pago',
            'valor': formatar_moeda(resumo.get('total_pago', 0)),
            'subtitulo': 'pagamentos',
            'cor': CoresPDF.ERRO
        },
        {
            'titulo': 'Saldo Líquido',
            'valor': formatar_moeda(saldo_liquido),
            'subtitulo': 'resultado',
            'cor': cor_saldo
        }
    ]
    
    story.append(criar_painel_kpis(kpis))
    story.append(Spacer(1, 25))

    # CARD DE CONTAS A RECEBER E PAGAR
    row_cards = []
    
    # Card Contas a Receber
    itens_receber = [
        ('Total a Receber:', formatar_moeda(resumo.get('total_a_receber', 0)))
    ]
    card_receber = criar_card_resumo('📥 Contas a Receber', itens_receber, CoresPDF.INFO)
    row_cards.append(card_receber)
    
    # Card Contas a Pagar
    itens_pagar = [
        ('Total a Pagar:', formatar_moeda(resumo.get('total_a_pagar', 0)))
    ]
    card_pagar = criar_card_resumo('📤 Contas a Pagar', itens_pagar, CoresPDF.AVISO)
    row_cards.append(card_pagar)
    
    # Criar linha com os 2 cards
    cards_table = Table([row_cards], colWidths=[3.75*inch, 3.75*inch])
    cards_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(cards_table)
    story.append(Spacer(1, 20))

    # VENDAS POR FORMA DE PAGAMENTO
    if relatorio.get('vendas_forma_pagamento'):
        story.append(criar_secao_titulo("💳 VENDAS POR FORMA DE PAGAMENTO"))
        story.append(Spacer(1, 10))
        
        vendas_data = [['Forma de Pagamento', 'Quantidade', 'Valor Total', '% do Total']]
        
        total_vendas = sum(v['valor'] for v in relatorio['vendas_forma_pagamento'])
        
        for venda in relatorio['vendas_forma_pagamento']:
            percentual = (venda['valor'] / total_vendas * 100) if total_vendas > 0 else 0
            vendas_data.append([
                venda['forma_pagamento'],
                str(venda['quantidade']) + ' vendas',
                formatar_moeda(venda['valor']),
                formatar_porcentagem(percentual)
            ])
        
        # Linha de total
        vendas_data.append([
            'TOTAL',
            str(sum(v['quantidade'] for v in relatorio['vendas_forma_pagamento'])) + ' vendas',
            formatar_moeda(total_vendas),
            '100%'
        ])
        
        vendas_table = criar_tabela_moderna(
            vendas_data,
            [2.5*inch, 1.5*inch, 1.7*inch, 1.3*inch],
            destacar_total=True,
            cores_alternadas=True
        )
        story.append(vendas_table)

    # Rodapé moderno
    def add_page_elements(canvas, doc):
        criar_rodape_moderno(canvas, doc, config_empresa, canvas.getPageNumber())
    
    doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
    buffer.seek(0)
    return buffer

@app.route('/relatorios/financeiro/pdf')
@login_required
def exportar_financeiro_pdf():
    if not verificar_permissao(current_user.id, 'relatorios'):
        flash('Acesso negado. Você não tem permissão para acessar relatórios.', 'error')
        return redirect(url_for('dashboard'))
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    relatorio = gerar_relatorio_financeiro(data_inicio, data_fim)
    pdf_buffer = criar_pdf_financeiro(relatorio, data_inicio, data_fim)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_financeiro.pdf'
    
    return response

# API ENDPOINTS PARA AUTOCOMPLETE
@app.route('/api/marcas')
@login_required
def api_marcas():
    """Retorna todas as marcas cadastradas no sistema"""
    try:
        marcas = obter_marcas_cadastradas()
        return jsonify(marcas)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/categorias')
@login_required
def api_categorias():
    """Retorna todas as categorias cadastradas no sistema"""
    try:
        categorias = obter_categorias_cadastradas()
        return jsonify(categorias)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# TRATAMENTO DE ERROS
@app.errorhandler(404)
def not_found(error):
    return render_template('erros/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('erros/500.html'), 500

# CONTEXTO GLOBAL DO TEMPLATE
@app.context_processor
def inject_globals():
    return {
        'moment': datetime,
        'today': hoje_br()
    }

if __name__ == '__main__':
    # Inicializar o banco de dados (apenas cria tabelas se não existirem)
    # init_db()  # Comentado - tabelas já criadas no deploy
    # criar_usuario_admin()  # Comentado - usar script criar_admin.py
    # popular_dados_exemplo()  # Comentado para não popular dados de exemplo
    
    # Rodar a aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
