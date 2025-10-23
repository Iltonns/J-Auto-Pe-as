# SISTEMA DE AUTOPEÇAS - FAMÍLIA
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, date
import json
import os

# Importar funções do banco de dados
from Minha_autopecas_web.logica_banco import (
    init_db, criar_usuario_admin, verificar_usuario, buscar_usuario_por_id,
    listar_clientes, adicionar_cliente, editar_cliente, deletar_cliente,
    listar_produtos, buscar_produto, adicionar_produto, editar_produto, deletar_produto,
    registrar_venda, listar_vendas,
    listar_contas_pagar_hoje, listar_contas_pagar_em_atraso, adicionar_conta_pagar, pagar_conta,
    listar_contas_receber_hoje, listar_contas_receber_em_atraso, receber_conta,
    obter_estatisticas_dashboard, produtos_estoque_baixo
)

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_mude_em_producao'

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
    if user_data:
        return User(user_data)
    return None

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
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

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

# CLIENTES
@app.route('/clientes')
@login_required
def clientes():
    clientes_lista = listar_clientes()
    return render_template('clientes.html', clientes=clientes_lista)

@app.route('/clientes/adicionar', methods=['POST'])
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

@app.route('/clientes/editar/<int:id>', methods=['POST'])
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

@app.route('/clientes/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_cliente_route(id):
    try:
        deletar_cliente(id)
        flash('Cliente excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir cliente: {str(e)}', 'error')
    
    return redirect(url_for('clientes'))

# PRODUTOS
@app.route('/produtos')
@login_required
def produtos():
    produtos_lista = listar_produtos()
    return render_template('produtos.html', produtos=produtos_lista)

@app.route('/produtos/buscar')
@login_required
def buscar_produto_route():
    termo = request.args.get('termo', '')
    produtos = buscar_produto(termo)
    return jsonify(produtos)

@app.route('/produtos/adicionar', methods=['POST'])
@login_required
def adicionar_produto_route():
    nome = request.form['nome']
    preco = float(request.form['preco'])
    estoque = int(request.form.get('estoque', 0))
    estoque_minimo = int(request.form.get('estoque_minimo', 5))
    codigo_barras = request.form.get('codigo_barras')
    descricao = request.form.get('descricao')
    categoria = request.form.get('categoria')
    
    try:
        adicionar_produto(nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria)
        flash('Produto adicionado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar produto: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

@app.route('/produtos/editar/<int:id>', methods=['POST'])
@login_required
def editar_produto_route(id):
    nome = request.form['nome']
    preco = float(request.form['preco'])
    estoque = int(request.form['estoque'])
    estoque_minimo = int(request.form.get('estoque_minimo', 5))
    codigo_barras = request.form.get('codigo_barras')
    descricao = request.form.get('descricao')
    categoria = request.form.get('categoria')
    
    try:
        editar_produto(id, nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria)
        flash('Produto editado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao editar produto: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

@app.route('/produtos/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_produto_route(id):
    try:
        deletar_produto(id)
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir produto: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

# VENDAS
@app.route('/vendas')
@login_required
def vendas():
    clientes_lista = listar_clientes()
    vendas_lista = listar_vendas()
    return render_template('vendas.html', clientes=clientes_lista, vendas=vendas_lista)

@app.route('/vendas/registrar', methods=['POST'])
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
        
        venda_id = registrar_venda(cliente_id, itens, forma_pagamento, desconto, observacoes, current_user.id)
        flash(f'Venda #{venda_id} registrada com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao registrar venda: {str(e)}', 'error')
    
    return redirect(url_for('vendas'))

# CONTAS A PAGAR
@app.route('/contas-a-pagar-hoje')
@login_required
def contas_a_pagar_hoje():
    contas = listar_contas_pagar_hoje()
    hoje = date.today()
    return render_template('contas_a_pagar_hoje.html', contas=contas, hoje=hoje)

@app.route('/pagamentos-em-atraso')
@login_required
def pagamentos_em_atraso():
    contas = listar_contas_pagar_em_atraso()
    return render_template('pagamentos_em_atraso.html', contas=contas)

@app.route('/contas-pagar/adicionar', methods=['POST'])
@login_required
def adicionar_conta_pagar_route():
    descricao = request.form['descricao']
    valor = float(request.form['valor'])
    data_vencimento = request.form['data_vencimento']
    categoria = request.form.get('categoria')
    observacoes = request.form.get('observacoes')
    
    try:
        adicionar_conta_pagar(descricao, valor, data_vencimento, categoria, observacoes)
        flash('Conta a pagar adicionada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_pagar_hoje'))

@app.route('/contas-pagar/pagar/<int:id>', methods=['POST'])
@login_required
def pagar_conta_route(id):
    try:
        pagar_conta(id)
        flash('Conta marcada como paga!', 'success')
    except Exception as e:
        flash(f'Erro ao pagar conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_pagar_hoje'))

# CONTAS A RECEBER
@app.route('/contas-a-receber-hoje')
@login_required
def contas_a_receber_hoje():
    contas = listar_contas_receber_hoje()
    hoje = date.today()
    return render_template('contas_a_receber_hoje.html', contas=contas, hoje=hoje)

@app.route('/recebimentos-em-atraso')
@login_required
def recebimentos_em_atraso():
    contas = listar_contas_receber_em_atraso()
    return render_template('recebimentos_em_atraso.html', contas=contas)

@app.route('/contas-receber/receber/<int:id>', methods=['POST'])
@login_required
def receber_conta_route(id):
    try:
        receber_conta(id)
        flash('Conta marcada como recebida!', 'success')
    except Exception as e:
        flash(f'Erro ao receber conta: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('contas_a_receber_hoje'))

# RELATÓRIOS
@app.route('/relatorios')
@login_required
def relatorios():
    return render_template('relatorios.html')

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
    
    # Rodar a aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
