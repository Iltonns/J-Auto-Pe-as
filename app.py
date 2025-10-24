# SISTEMA DE AUTOPEÇAS - FAMÍLIA
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, date
import json
import os
from functools import wraps

# Importar funções do banco de dados
from Minha_autopecas_web.logica_banco import (
    init_db, criar_usuario_admin, verificar_usuario, buscar_usuario_por_id,
    buscar_usuario_por_email, atualizar_senha_usuario,
    criar_usuario, listar_usuarios, editar_usuario, deletar_usuario, verificar_permissao,
    listar_clientes, adicionar_cliente, editar_cliente, deletar_cliente,
    listar_produtos, buscar_produto, adicionar_produto, editar_produto, deletar_produto,
    registrar_venda, listar_vendas, obter_vendas_do_dia, sincronizar_vendas_com_caixa,
    listar_contas_pagar_hoje, listar_contas_pagar_em_atraso, adicionar_conta_pagar, pagar_conta,
    listar_contas_receber_hoje, listar_contas_receber_em_atraso, receber_conta,
    obter_estatisticas_dashboard, produtos_estoque_baixo,
    criar_orcamento, listar_orcamentos, obter_orcamento, converter_orcamento_em_venda,
    popular_dados_exemplo,
    # Novas funções do caixa
    abrir_caixa, fechar_caixa, registrar_movimentacao_caixa, obter_status_caixa,
    listar_movimentacoes_caixa, criar_lancamento_financeiro, listar_lancamentos_financeiros,
    # Função de importação XML
    importar_produtos_de_xml
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

# ROTAS DE CRIAÇÃO DE USUÁRIO
@app.route('/criar-usuario', methods=['POST'])
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
            'admin': request.form.get('permissao_admin') == 'on'
        }
        
        # Se logado, usar o ID do usuário atual como created_by
        created_by = current_user.id if current_user.is_authenticated else None
        
        success, message = criar_usuario(username, password, nome_completo, email, permissoes, created_by)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        flash(f'Erro ao criar usuário: {str(e)}', 'error')
    
    return redirect(url_for('login'))

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
            'admin': request.form.get('permissao_admin') == 'on'
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

@app.route('/api/produtos/buscar')
@login_required
def api_buscar_produtos():
    termo = request.args.get('q', '').strip().lower()
    produtos = listar_produtos()
    
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

@app.route('/api/produto/<termo>')
@login_required
def api_buscar_produto_unico(termo):
    """Busca um produto específico pelo termo"""
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

@app.route('/produtos/adicionar', methods=['POST'], endpoint='adicionar_produto')
@login_required
def adicionar_produto_route():
    nome = request.form['nome']
    codigo_barras = request.form.get('codigo_barras')
    codigo_fornecedor = request.form.get('codigo_fornecedor')
    descricao = request.form.get('descricao')
    categoria = request.form.get('categoria')
    
    # Validação segura para campos numéricos
    try:
        estoque = int(request.form.get('estoque', 0))
    except (ValueError, TypeError):
        estoque = 0
    
    try:
        estoque_minimo_value = request.form.get('estoque_minimo', '5').strip()
        if estoque_minimo_value == '':
            estoque_minimo = 5
        else:
            estoque_minimo = int(estoque_minimo_value)
    except (ValueError, TypeError):
        estoque_minimo = 5
    
    # O novo sistema sempre usa custo + margem
    try:
        preco_custo = float(request.form.get('preco_custo', 0))
    except (ValueError, TypeError):
        preco_custo = 0.0
        
    try:
        margem_lucro = float(request.form.get('margem_lucro', 0))
    except (ValueError, TypeError):
        margem_lucro = 0.0
    
    # O preço já vem calculado do frontend, mas vamos recalcular para garantir
    if preco_custo > 0 and margem_lucro >= 0:
        preco = preco_custo + (preco_custo * margem_lucro / 100)
    else:
        try:
            preco = float(request.form.get('preco', 0))
        except (ValueError, TypeError):
            preco = 0.0
    
    try:
        adicionar_produto(nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
                         codigo_fornecedor, preco_custo, margem_lucro)
        flash('Produto adicionado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar produto: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

@app.route('/produtos/editar/<int:id>', methods=['POST'], endpoint='atualizar_produto')
@login_required
def editar_produto_route(id):
    nome = request.form['nome']
    codigo_barras = request.form.get('codigo_barras')
    codigo_fornecedor = request.form.get('codigo_fornecedor')
    descricao = request.form.get('descricao')
    categoria = request.form.get('categoria')
    
    # Validação segura para campos numéricos
    try:
        estoque = int(request.form.get('estoque', 0))
    except (ValueError, TypeError):
        estoque = 0
    
    try:
        estoque_minimo_value = request.form.get('estoque_minimo', '5').strip()
        if estoque_minimo_value == '':
            estoque_minimo = 5
        else:
            estoque_minimo = int(estoque_minimo_value)
    except (ValueError, TypeError):
        estoque_minimo = 5
    
    # O novo sistema sempre usa custo + margem
    try:
        preco_custo = float(request.form.get('preco_custo', 0))
    except (ValueError, TypeError):
        preco_custo = 0.0
        
    try:
        margem_lucro = float(request.form.get('margem_lucro', 0))
    except (ValueError, TypeError):
        margem_lucro = 0.0
    
    # O preço já vem calculado do frontend, mas vamos recalcular para garantir
    if preco_custo > 0 and margem_lucro >= 0:
        preco = preco_custo + (preco_custo * margem_lucro / 100)
    else:
        try:
            preco = float(request.form.get('preco', 0))
        except (ValueError, TypeError):
            preco = 0.0
    
    try:
        editar_produto(id, nome, preco, estoque, estoque_minimo, codigo_barras, descricao, categoria,
                      codigo_fornecedor, preco_custo, margem_lucro)
        flash('Produto editado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao editar produto: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

@app.route('/produtos/deletar/<int:id>', methods=['POST'], endpoint='excluir_produto')
@login_required
def deletar_produto_route(id):
    try:
        deletar_produto(id)
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir produto: {str(e)}', 'error')
    
    return redirect(url_for('produtos'))

@app.route('/produtos/importar-xml', methods=['POST'], endpoint='importar_produtos_xml')
@login_required
def importar_produtos_xml_route():
    """Rota para importar produtos via arquivo XML de NFe"""
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
                # Ler conteúdo do arquivo
                conteudo_xml = arquivo.read().decode('utf-8')
                
                # Processar XML
                resultado = importar_produtos_de_xml(conteudo_xml)
                
                if resultado['sucesso']:
                    # Montar mensagem de sucesso
                    mensagem_partes = []
                    
                    if resultado['produtos_importados']:
                        mensagem_partes.append(f"{len(resultado['produtos_importados'])} produtos importados")
                    
                    if resultado['produtos_atualizados']:
                        mensagem_partes.append(f"{len(resultado['produtos_atualizados'])} produtos atualizados")
                    
                    if mensagem_partes:
                        flash(f"Importação concluída! {', '.join(mensagem_partes)}.", 'success')
                    else:
                        flash('Nenhum produto foi processado.', 'warning')
                    
                    # Mostrar erros se houver
                    if resultado['erros']:
                        for erro in resultado['erros'][:5]:  # Mostrar apenas os 5 primeiros erros
                            flash(f"Aviso: {erro}", 'warning')
                        
                        if len(resultado['erros']) > 5:
                            flash(f"... e mais {len(resultado['erros']) - 5} avisos.", 'warning')
                
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
    clientes_lista = listar_clientes()
    vendas_lista = listar_vendas()
    produtos_lista = listar_produtos()
    return render_template('vendas.html', clientes=clientes_lista, vendas=vendas_lista, produtos=produtos_lista)

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
        flash(f'Venda #{venda_id} registrada com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao registrar venda: {str(e)}', 'error')
    
    return redirect(url_for('vendas'))

# CONTAS A PAGAR
@app.route('/contas-a-pagar-hoje')
@required_permission('financeiro')
def contas_a_pagar_hoje():
    contas = listar_contas_pagar_hoje()
    hoje = date.today()
    return render_template('contas_a_pagar_hoje.html', contas=contas, hoje=hoje)

@app.route('/pagamentos-em-atraso')
@required_permission('financeiro')
def pagamentos_em_atraso():
    contas = listar_contas_pagar_em_atraso()
    return render_template('pagamentos_em_atraso.html', contas=contas)

@app.route('/contas-pagar/adicionar', methods=['POST'])
@required_permission('financeiro')
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
    contas = listar_contas_receber_hoje()
    hoje = date.today()
    return render_template('contas_a_receber_hoje.html', contas=contas, hoje=hoje)

@app.route('/recebimentos-em-atraso')
@required_permission('financeiro')
def recebimentos_em_atraso():
    contas = listar_contas_receber_em_atraso()
    return render_template('recebimentos_em_atraso.html', contas=contas)

@app.route('/contas-receber/receber/<int:id>', methods=['POST'])
@required_permission('financeiro')
def receber_conta_route(id):
    try:
        receber_conta(id)
        flash('Conta marcada como recebida!', 'success')
    except Exception as e:
        flash(f'Erro ao receber conta: {str(e)}', 'error')
    
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
    
    return render_template('visualizar_orcamento.html', orcamento=orcamento)

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
    popular_dados_exemplo()
    
    # Rodar a aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
