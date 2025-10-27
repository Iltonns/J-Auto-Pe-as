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
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Importar funções do banco de dados
from Minha_autopecas_web.logica_banco import (
    init_db, criar_usuario_admin, verificar_usuario, buscar_usuario_por_id,
    buscar_usuario_por_email, atualizar_senha_usuario,
    criar_usuario, listar_usuarios, editar_usuario, deletar_usuario, verificar_permissao,
    listar_clientes, adicionar_cliente, editar_cliente, deletar_cliente,
    listar_produtos, buscar_produto, adicionar_produto, editar_produto, deletar_produto, obter_produto_por_id,
    deletar_todos_os_produtos, limpar_completamente_produtos,
    registrar_venda, listar_vendas, obter_vendas_do_dia, sincronizar_vendas_com_caixa, obter_venda_por_id, deletar_venda,
    obter_configuracoes_empresa, atualizar_configuracoes_empresa,
    listar_contas_pagar_hoje, adicionar_conta_pagar, pagar_conta,
    listar_contas_receber_hoje, receber_conta, adicionar_conta_receber,
    listar_contas_pagar_por_periodo, listar_contas_receber_por_periodo,
    obter_estatisticas_dashboard, produtos_estoque_baixo,
    criar_orcamento, listar_orcamentos, obter_orcamento, converter_orcamento_em_venda, atualizar_orcamento, excluir_orcamento,
    popular_dados_exemplo,
    # Novas funções do caixa
    abrir_caixa, fechar_caixa, registrar_movimentacao_caixa, obter_status_caixa,
    listar_movimentacoes_caixa, criar_lancamento_financeiro, listar_lancamentos_financeiros,
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
    limpar_sincronizacoes_incorretas
)

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_mude_em_producao'

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
    logout_user()
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

@app.route('/debug-vendas')
@login_required
def debug_vendas():
    """Rota para debugar dados de vendas"""
    from datetime import date
    hoje = date.today().strftime('%Y-%m-%d')
    
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

@app.route('/produtos')
@login_required
def produtos():
    """Exibe a página de gerenciamento de produtos"""
    try:
        produtos_lista = listar_produtos()
        fornecedores_lista = obter_fornecedores_para_select()
        return render_template('produtos.html', produtos=produtos_lista, fornecedores=fornecedores_lista)
    except Exception as e:
        flash(f'Erro ao carregar produtos: {str(e)}', 'error')
        return render_template('produtos.html', produtos=[], fornecedores=[])

@app.route('/produtos/buscar')
@login_required
def buscar_produto_route():
    """API para buscar produtos"""
    try:
        termo = request.args.get('termo', '').strip()
        if not termo:
            return jsonify([])
        
        produtos = buscar_produto(termo)
        return jsonify(produtos)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/produtos/buscar')
@login_required
def api_buscar_produtos():
    """API avançada para buscar produtos com filtros"""
    try:
        termo = request.args.get('q', '').strip().lower()
        categoria = request.args.get('categoria', '')
        
        produtos = listar_produtos()
        
        # Filtrar por categoria se especificada
        if categoria and categoria != 'todas':
            produtos = [p for p in produtos if p.get('categoria') == categoria]
        
        # Filtrar por termo de busca se especificado
        if termo:
            produtos_filtrados = []
            for produto in produtos:
                if (termo in produto['nome'].lower() or 
                    termo in str(produto['id']) or
                    (produto.get('codigo_barras') and termo in produto['codigo_barras'].lower()) or
                    (produto.get('codigo_fornecedor') and termo in produto['codigo_fornecedor'].lower()) or
                    (produto.get('categoria') and termo in produto['categoria'].lower()) or
                    (produto.get('descricao') and termo in produto['descricao'].lower())):
                    produtos_filtrados.append(produto)
            produtos = produtos_filtrados
        
        return jsonify(produtos[:50])  # Limitar a 50 resultados
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/produto/<termo>')
@login_required
def api_buscar_produto_unico(termo):
    """Busca um produto específico pelo termo"""
    try:
        produtos = listar_produtos()
        
        # Primeiro tenta encontrar por ID exato
        try:
            produto_id = int(termo)
            for produto in produtos:
                if produto['id'] == produto_id:
                    return jsonify(produto)
        except ValueError:
            pass
        
        # Depois busca por código de barras exato
        for produto in produtos:
            if produto.get('codigo_barras') and produto['codigo_barras'].lower() == termo.lower():
                return jsonify(produto)
        
        # Depois busca por código de fornecedor exato
        for produto in produtos:
            if produto.get('codigo_fornecedor') and produto['codigo_fornecedor'].lower() == termo.lower():
                return jsonify(produto)
        
        # Por último, busca por nome (primeiro que contenha o termo)
        termo_lower = termo.lower()
        for produto in produtos:
            if termo_lower in produto['nome'].lower():
                return jsonify(produto)
        
        return jsonify({'error': 'Produto não encontrado'})
    except Exception as e:
        return jsonify({'error': str(e)})

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
        
        # Campos numéricos
        estoque = safe_int(request.form.get('estoque', 0))
        estoque_minimo = safe_int(request.form.get('estoque_minimo', 5), 5)
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
            marca=marca if marca else None
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
        
        # Campos numéricos
        estoque = safe_int(request.form.get('estoque', 0))
        estoque_minimo = safe_int(request.form.get('estoque_minimo', 5), 5)
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
            marca=marca if marca else None
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
                estoque_minimo_padrao = int(request.form.get('estoque_minimo_padrao', 5))
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

# VENDAS
@app.route('/vendas')
@login_required
def vendas():
    from datetime import datetime
    clientes_lista = listar_clientes()
    # Buscar vendas do dia para exibir na lista
    vendas_dados = obter_vendas_do_dia()
    vendas_hoje = vendas_dados.get('vendas', [])
    produtos_lista = listar_produtos()
    usuarios_lista = listar_usuarios()
    
    # Calcular estatísticas
    total_vendas_hoje = sum(venda.get('total', 0) for venda in vendas_hoje)
    total_itens_vendidos = sum(venda.get('total_itens', 0) for venda in vendas_hoje)
    ticket_medio = total_vendas_hoje / len(vendas_hoje) if vendas_hoje else 0
    
    # Data de hoje para filtros
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    
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
    """Gera recibo para impressão"""
    try:
        from Minha_autopecas_web.logica_banco import obter_venda_por_id
        
        venda = obter_venda_por_id(venda_id)
        if not venda:
            flash('Venda não encontrada', 'error')
            return redirect(url_for('vendas'))
        
        return render_template('recibo_venda.html', venda=venda)
    
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
    hoje = date.today()
    
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
    
    return render_template('contas_a_pagar_hoje.html', 
                         contas=contas, 
                         fornecedores=fornecedores, 
                         hoje=hoje,
                         filtro_atual=filtro,
                         status_atual=status,
                         estatisticas=estatisticas)

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
    hoje = date.today()
    
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
    
    return render_template('contas_a_receber_hoje.html', 
                         contas=contas, 
                         clientes=clientes, 
                         hoje=hoje,
                         filtro_atual=filtro,
                         status_atual=status,
                         estatisticas=estatisticas)

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

# ORÇAMENTOS
@app.route('/orcamentos')
@login_required
def orcamentos():
    orcamentos_lista = listar_orcamentos()
    produtos = listar_produtos()
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
    produtos = listar_produtos()
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
    
    return render_template('relatorios/estoque.html', relatorio=relatorio)

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
    rodape_texto = f"Relatório gerado pelo Sistema {config_empresa.get('nome_empresa', 'FG AUTO PEÇAS')} - {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    return rodape_texto

def criar_pdf_vendas(relatorio, data_inicio=None, data_fim=None, cliente_selecionado=None):
    """Gera PDF do relatório de vendas"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    story = []
    
    # Obter configurações da empresa
    config_empresa = obter_configuracoes_empresa()
    
    # Cabeçalho da empresa
    story.extend(criar_cabecalho_empresa(doc, styles, config_empresa))
    
    # Configurar estilos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2962ff')
    )
    
    # Título do relatório
    story.append(Paragraph("RELATÓRIO DE VENDAS", title_style))
    
    # Período
    if data_inicio and data_fim:
        periodo = f"Período: {data_inicio} a {data_fim}"
        story.append(Paragraph(periodo, styles['Normal']))
        story.append(Spacer(1, 10))
    
    if cliente_selecionado:
        story.append(Paragraph(f"Cliente: {cliente_selecionado}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Resumo
    resumo_data = [
        ['Resumo', 'Valor'],
        ['Total de Vendas', str(relatorio['quantidade_vendas'])],
        ['Valor Total', f"R$ {relatorio['total_geral']:.2f}"],
        ['Ticket Médio', f"R$ {relatorio['ticket_medio']:.2f}"]
    ]
    
    resumo_table = Table(resumo_data, colWidths=[3*inch, 2*inch])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2962ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f7fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(resumo_table)
    story.append(Spacer(1, 20))
    
    # Vendas detalhadas
    if relatorio['vendas']:
        story.append(Paragraph("Vendas Detalhadas", styles['Heading3']))
        story.append(Spacer(1, 12))
        
        vendas_data = [['ID', 'Data', 'Cliente', 'Vendedor', 'Itens', 'Pagamento', 'Total']]
        
        for venda in relatorio['vendas']:
            vendas_data.append([
                str(venda['id']),
                str(venda['data_venda']),
                str(venda['cliente'])[:20],  # Limitar caracteres
                str(venda['vendedor'])[:15],
                str(venda['quantidade_itens']),
                str(venda['forma_pagamento'])[:10],
                f"R$ {venda['total']:.2f}"
            ])
        
        vendas_table = Table(vendas_data, colWidths=[0.7*inch, 1*inch, 1.5*inch, 1.2*inch, 0.8*inch, 1*inch, 1*inch])
        vendas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2962ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f7fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(vendas_table)
    
    # Adicionar rodapé
    def add_page_number(canvas, doc):
        canvas.saveState()
        rodape = criar_rodape_empresa(doc, config_empresa)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(50, 30, rodape)
        canvas.drawRightString(doc.pagesize[0] - 50, 30, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()
    
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer

def criar_pdf_produtos_mais_vendidos(relatorio, data_inicio=None, data_fim=None, limite=10):
    """Gera PDF do relatório de produtos mais vendidos"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    story = []
    
    # Obter configurações da empresa
    config_empresa = obter_configuracoes_empresa()
    
    # Cabeçalho da empresa
    story.extend(criar_cabecalho_empresa(doc, styles, config_empresa))
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2962ff')
    )
    
    story.append(Paragraph("RELATÓRIO DE PRODUTOS MAIS VENDIDOS", title_style))
    
    if data_inicio and data_fim:
        periodo = f"Período: {data_inicio} a {data_fim}"
        story.append(Paragraph(periodo, styles['Normal']))
        story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"Limitado aos {limite} produtos mais vendidos", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if relatorio['produtos']:
        produtos_data = [['Posição', 'Produto', 'Código', 'Quantidade Vendida', 'Valor Total']]
        
        for i, produto in enumerate(relatorio['produtos'], 1):
            produtos_data.append([
                str(i),
                str(produto['nome'])[:30],
                str(produto['codigo']),
                str(produto['quantidade_vendida']),
                f"R$ {produto['valor_total']:.2f}"
            ])
        
        produtos_table = Table(produtos_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1.5*inch, 1.5*inch])
        produtos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2962ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f7fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(produtos_table)
    
    # Adicionar rodapé
    def add_page_number(canvas, doc):
        canvas.saveState()
        rodape = criar_rodape_empresa(doc, config_empresa)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(50, 30, rodape)
        canvas.drawRightString(doc.pagesize[0] - 50, 30, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()
    
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer

def criar_pdf_estoque(relatorio):
    """Gera PDF do relatório de estoque"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    story = []
    
    # Obter configurações da empresa
    config_empresa = obter_configuracoes_empresa()
    
    # Cabeçalho da empresa
    story.extend(criar_cabecalho_empresa(doc, styles, config_empresa))
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2962ff')
    )
    
    story.append(Paragraph("RELATÓRIO DE ESTOQUE", title_style))
    story.append(Spacer(1, 20))
    
    # Verificar se há erro no relatório
    if relatorio.get('erro'):
        story.append(Paragraph(f"Erro ao gerar relatório: {relatorio['erro']}", styles['Normal']))
    else:
        # Resumo - usar dados do resumo se disponível, senão calcular
        resumo = relatorio.get('resumo', {})
        total_produtos = resumo.get('total_produtos', len(relatorio.get('produtos', [])))
        produtos_sem_estoque = resumo.get('produtos_sem_estoque', 0)
        produtos_estoque_baixo = resumo.get('produtos_estoque_baixo', 0)
        valor_total_estoque = resumo.get('valor_total_estoque', 0)
        
        # Se não temos dados do resumo, calcular a partir dos produtos
        if not resumo and relatorio.get('produtos'):
            valor_total_estoque = sum(produto.get('valor_estoque', produto.get('preco', 0) * produto.get('estoque', 0)) 
                                    for produto in relatorio['produtos'])
            produtos_sem_estoque = sum(1 for produto in relatorio['produtos'] 
                                     if produto.get('estoque', 0) <= 0)
            produtos_estoque_baixo = sum(1 for produto in relatorio['produtos'] 
                                       if produto.get('status') == 'Estoque Baixo')
        
        resumo_data = [
            ['Indicador', 'Valor'],
            ['Total de Produtos', str(total_produtos)],
            ['Produtos em Estoque', str(total_produtos - produtos_sem_estoque)],
            ['Produtos em Falta', str(produtos_sem_estoque)],
            ['Valor Total em Estoque', f"R$ {valor_total_estoque:.2f}"]
        ]
        
        resumo_table = Table(resumo_data, colWidths=[3*inch, 2*inch])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2962ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f7fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(resumo_table)
        story.append(Spacer(1, 30))
        
        # Produtos
        if relatorio.get('produtos'):
            story.append(Paragraph("Produtos Detalhados", styles['Heading3']))
            story.append(Spacer(1, 12))
            
            produtos_data = [['Código', 'Nome', 'Categoria', 'Estoque', 'Preço', 'Valor Total']]
            
            for produto in relatorio['produtos']:
                produtos_data.append([
                    str(produto.get('codigo', produto.get('codigo_barras', ''))),
                    str(produto.get('nome', ''))[:25],
                    str(produto.get('categoria', ''))[:15],
                    str(produto.get('estoque', 0)),
                    f"R$ {produto.get('preco', 0):.2f}",
                    f"R$ {produto.get('valor_estoque', produto.get('preco', 0) * produto.get('estoque', 0)):.2f}"
                ])
            
            produtos_table = Table(produtos_data, colWidths=[1*inch, 2*inch, 1.2*inch, 0.8*inch, 1*inch, 1.2*inch])
            produtos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2962ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f7fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            story.append(produtos_table)
    
    # Adicionar rodapé
    def add_page_number(canvas, doc):
        canvas.saveState()
        rodape = criar_rodape_empresa(doc, config_empresa)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(50, 30, rodape)
        canvas.drawRightString(doc.pagesize[0] - 50, 30, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()
    
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer

def criar_pdf_financeiro(relatorio, data_inicio=None, data_fim=None):
    """Gera PDF do relatório financeiro"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    story = []
    
    # Obter configurações da empresa
    config_empresa = obter_configuracoes_empresa()
    
    # Cabeçalho da empresa
    story.extend(criar_cabecalho_empresa(doc, styles, config_empresa))
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2962ff')
    )
    
    story.append(Paragraph("RELATÓRIO FINANCEIRO", title_style))
    
    if data_inicio and data_fim:
        periodo = f"Período: {data_inicio} a {data_fim}"
        story.append(Paragraph(periodo, styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Resumo - usar dados do resumo se disponível
    resumo = relatorio.get('resumo', {})
    
    # Verificar se há erro no relatório
    if relatorio.get('erro'):
        story.append(Paragraph(f"Erro ao gerar relatório: {relatorio['erro']}", styles['Normal']))
        story.append(Spacer(1, 20))
        # Gerar PDF vazio com erro
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    total_a_receber = resumo.get('total_a_receber', 0)
    total_a_pagar = resumo.get('total_a_pagar', 0)
    saldo_liquido = resumo.get('saldo_liquido', total_a_receber - total_a_pagar)
    
    # Se não temos dados do resumo, calcular a partir das contas
    if not resumo:
        if relatorio.get('contas_receber'):
            total_a_receber = sum(conta.get('valor', 0) for conta in relatorio['contas_receber'])
        if relatorio.get('contas_pagar'):
            total_a_pagar = sum(conta.get('valor', 0) for conta in relatorio['contas_pagar'])
        saldo_liquido = total_a_receber - total_a_pagar
    
    resumo_data = [
        ['Indicador', 'Valor'],
        ['Total a Receber', f"R$ {total_a_receber:.2f}"],
        ['Total a Pagar', f"R$ {total_a_pagar:.2f}"],
        ['Saldo Líquido', f"R$ {saldo_liquido:.2f}"]
    ]
    
    resumo_table = Table(resumo_data, colWidths=[3*inch, 2*inch])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2962ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f7fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(resumo_table)
    story.append(Spacer(1, 30))
    
    # Contas a Receber
    if relatorio.get('contas_receber'):
        story.append(Paragraph("Contas a Receber", styles['Heading3']))
        story.append(Spacer(1, 12))
        
        receber_data = [['Data Vencimento', 'Descrição', 'Cliente', 'Valor', 'Status']]
        
        for conta in relatorio['contas_receber']:
            data_venc = conta.get('data_vencimento', '')
            if isinstance(data_venc, str):
                data_venc_str = data_venc
            else:
                data_venc_str = data_venc.strftime('%d/%m/%Y') if data_venc else ''
            
            receber_data.append([
                data_venc_str,
                str(conta.get('descricao', ''))[:25],
                str(conta.get('cliente', ''))[:20],
                f"R$ {conta.get('valor', 0):.2f}",
                str(conta.get('status', ''))
            ])
        
        receber_table = Table(receber_data, colWidths=[1.2*inch, 2*inch, 1.5*inch, 1*inch, 1*inch])
        receber_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#d4edda')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(receber_table)
        story.append(Spacer(1, 20))
    
    # Contas a Pagar
    if relatorio.get('contas_pagar'):
        story.append(Paragraph("Contas a Pagar", styles['Heading3']))
        story.append(Spacer(1, 12))
        
        pagar_data = [['Data Vencimento', 'Descrição', 'Fornecedor', 'Valor', 'Status']]
        
        for conta in relatorio['contas_pagar']:
            data_venc = conta.get('data_vencimento', '')
            if isinstance(data_venc, str):
                data_venc_str = data_venc
            else:
                data_venc_str = data_venc.strftime('%d/%m/%Y') if data_venc else ''
            
            pagar_data.append([
                data_venc_str,
                str(conta.get('descricao', ''))[:25],
                str(conta.get('fornecedor', ''))[:20],
                f"R$ {conta.get('valor', 0):.2f}",
                str(conta.get('status', ''))
            ])
        
        pagar_table = Table(pagar_data, colWidths=[1.2*inch, 2*inch, 1.5*inch, 1*inch, 1*inch])
        pagar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8d7da')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(pagar_table)
    
    # Adicionar rodapé
    def add_page_number(canvas, doc):
        canvas.saveState()
        rodape = criar_rodape_empresa(doc, config_empresa)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(50, 30, rodape)
        canvas.drawRightString(doc.pagesize[0] - 50, 30, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()
    
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
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
        'today': date.today()
    }

if __name__ == '__main__':
    # Inicializar o banco de dados
    init_db()
    criar_usuario_admin()
    popular_dados_exemplo()
    
    # Rodar a aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
