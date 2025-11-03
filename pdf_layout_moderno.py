"""
Módulo para criar layouts modernos e profissionais para PDFs
Sistema de Autopeças - Layout Moderno com Cards
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas as pdf_canvas


# Paleta de cores moderna
class CoresPDF:
    """Paleta de cores moderna para o sistema"""
    # Cores primárias
    PRIMARIA = colors.HexColor('#1a237e')  # Azul escuro
    PRIMARIA_CLARA = colors.HexColor('#3949ab')
    PRIMARIA_ESCURA = colors.HexColor('#000051')
    
    # Cores de destaque
    SUCESSO = colors.HexColor('#2e7d32')  # Verde
    SUCESSO_CLARO = colors.HexColor('#4caf50')
    SUCESSO_BG = colors.HexColor('#e8f5e9')
    
    AVISO = colors.HexColor('#f57c00')  # Laranja
    AVISO_CLARO = colors.HexColor('#ff9800')
    AVISO_BG = colors.HexColor('#fff3e0')
    
    ERRO = colors.HexColor('#c62828')  # Vermelho
    ERRO_CLARO = colors.HexColor('#e53935')
    ERRO_BG = colors.HexColor('#ffebee')
    
    INFO = colors.HexColor('#0277bd')  # Azul claro
    INFO_CLARO = colors.HexColor('#03a9f4')
    INFO_BG = colors.HexColor('#e1f5fe')
    
    # Cores neutras
    CINZA_ESCURO = colors.HexColor('#37474f')
    CINZA_MEDIO = colors.HexColor('#546e7a')
    CINZA_CLARO = colors.HexColor('#eceff1')
    CINZA_BG = colors.HexColor('#f5f7fa')
    
    BRANCO = colors.white
    TEXTO = colors.HexColor('#212121')
    TEXTO_SECUNDARIO = colors.HexColor('#757575')


def criar_card_kpi(titulo, valor, subtitulo="", cor=CoresPDF.PRIMARIA, largura=2*inch):
    """
    Cria um card estilo KPI moderno
    """
    data = [
        [Paragraph(f'<font size=10 color="#757575"><b>{titulo}</b></font>', 
                   ParagraphStyle('center', alignment=TA_CENTER))],
        [Paragraph(f'<font size=18 color="{cor.hexval()}"><b>{valor}</b></font>', 
                   ParagraphStyle('center', alignment=TA_CENTER))],
    ]
    
    if subtitulo:
        data.append([Paragraph(f'<font size=8 color="#9e9e9e">{subtitulo}</font>', 
                              ParagraphStyle('center', alignment=TA_CENTER))])
    
    card_table = Table(data, colWidths=[largura])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CoresPDF.BRANCO),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('BOX', (0, 0), (-1, -1), 2, cor),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    
    return card_table


def criar_painel_kpis(kpis_list):
    """
    Cria um painel com múltiplos KPIs em linha
    kpis_list: lista de dicionários com {titulo, valor, subtitulo, cor}
    """
    cards = []
    for kpi in kpis_list:
        card = criar_card_kpi(
            kpi.get('titulo', ''),
            kpi.get('valor', ''),
            kpi.get('subtitulo', ''),
            kpi.get('cor', CoresPDF.PRIMARIA),
            largura=1.8*inch
        )
        cards.append(card)
    
    # Criar tabela com os cards lado a lado
    painel_data = [cards]
    largura_card = 7.5 / len(cards)  # Distribuir igualmente
    
    painel_table = Table(painel_data, colWidths=[largura_card*inch] * len(cards))
    painel_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    return painel_table


def criar_cabecalho_empresa_moderno(config_empresa):
    """
    Cria cabeçalho completo da empresa com logo e informações
    """
    import os
    from reportlab.platypus import Image
    
    elementos = []
    
    # Tentar carregar logo
    logo_path = None
    if config_empresa.get('logo_path'):
        logo_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', config_empresa['logo_path'].lstrip('/'))
        if os.path.exists(logo_full_path):
            logo_path = logo_full_path
    
    # Logo padrão
    if not logo_path:
        default_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'empresa', 'logo.png')
        if os.path.exists(default_logo):
            logo_path = default_logo
    
    # Estilo para nome da empresa
    nome_style = ParagraphStyle(
        'NomeEmpresa',
        fontSize=18,
        textColor=CoresPDF.PRIMARIA,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        leading=22,
        spaceAfter=5
    )
    
    # Estilo para informações
    info_style = ParagraphStyle(
        'InfoEmpresa',
        fontSize=8,
        textColor=CoresPDF.TEXTO_SECUNDARIO,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=10
    )
    
    if logo_path:
        try:
            # Criar logo
            logo_img = Image(logo_path, width=70, height=70)
            
            # Criar informações da empresa
            info_empresa = []
            info_empresa.append(Paragraph(
                f'<b>{config_empresa.get("nome_empresa", "FG AUTO PEÇAS")}</b>',
                nome_style
            ))
            
            # Linha 1: CNPJ e Telefone
            linha1 = []
            if config_empresa.get('cnpj'):
                linha1.append(f"<b>CNPJ:</b> {config_empresa['cnpj']}")
            if config_empresa.get('telefone'):
                linha1.append(f"<b>Tel:</b> {config_empresa['telefone']}")
            
            if linha1:
                info_empresa.append(Paragraph(' | '.join(linha1), info_style))
            
            # Linha 2: Endereço completo
            linha2 = []
            if config_empresa.get('endereco'):
                linha2.append(config_empresa['endereco'])
            if config_empresa.get('cidade') and config_empresa.get('estado'):
                linha2.append(f"{config_empresa['cidade']}/{config_empresa['estado']}")
            if config_empresa.get('cep'):
                linha2.append(f"CEP: {config_empresa['cep']}")
            
            if linha2:
                info_empresa.append(Paragraph(' - '.join(linha2), info_style))
            
            # Linha 3: Email e Site
            linha3 = []
            if config_empresa.get('email'):
                linha3.append(f"<b>Email:</b> {config_empresa['email']}")
            if config_empresa.get('site'):
                linha3.append(f"<b>Site:</b> {config_empresa['site']}")
            
            if linha3:
                info_empresa.append(Paragraph(' | '.join(linha3), info_style))
            
            # Criar tabela com logo e informações
            header_data = [[logo_img, info_empresa]]
            header_table = Table(header_data, colWidths=[90, 6.6*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elementos.append(header_table)
            
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            # Fallback: cabeçalho sem logo
            elementos.extend(_criar_cabecalho_sem_logo(config_empresa, nome_style, info_style))
    else:
        # Sem logo
        elementos.extend(_criar_cabecalho_sem_logo(config_empresa, nome_style, info_style))
    
    # Linha separadora decorativa
    linha_sep = Table([['']], colWidths=[7.5*inch])
    linha_sep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CoresPDF.PRIMARIA),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elementos.append(linha_sep)
    elementos.append(Spacer(1, 15))
    
    return elementos


def _criar_cabecalho_sem_logo(config_empresa, nome_style, info_style):
    """Cria cabeçalho sem logo (fallback)"""
    elementos = []
    
    # Centralizar quando não há logo
    nome_style.alignment = TA_CENTER
    info_style.alignment = TA_CENTER
    
    elementos.append(Paragraph(
        f'<b>{config_empresa.get("nome_empresa", "FG AUTO PEÇAS")}</b>',
        nome_style
    ))
    
    # Todas as informações em linhas centralizadas
    info_linhas = []
    
    if config_empresa.get('cnpj'):
        info_linhas.append(f"CNPJ: {config_empresa['cnpj']}")
    
    endereco_parts = []
    if config_empresa.get('endereco'):
        endereco_parts.append(config_empresa['endereco'])
    if config_empresa.get('cidade') and config_empresa.get('estado'):
        endereco_parts.append(f"{config_empresa['cidade']}/{config_empresa['estado']}")
    if config_empresa.get('cep'):
        endereco_parts.append(f"CEP: {config_empresa['cep']}")
    
    if endereco_parts:
        info_linhas.append(' - '.join(endereco_parts))
    
    contato_parts = []
    if config_empresa.get('telefone'):
        contato_parts.append(f"Tel: {config_empresa['telefone']}")
    if config_empresa.get('email'):
        contato_parts.append(f"Email: {config_empresa['email']}")
    
    if contato_parts:
        info_linhas.append(' | '.join(contato_parts))
    
    for linha in info_linhas:
        elementos.append(Paragraph(linha, info_style))
    
    elementos.append(Spacer(1, 5))
    
    return elementos


def criar_cabecalho_moderno(titulo, subtitulo="", data_geracao=None):
    """
    Cria um cabeçalho moderno com gradiente visual (apenas título do relatório)
    """
    from datetime import datetime
    
    if not data_geracao:
        data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
    
    # Estilo para o título
    titulo_style = ParagraphStyle(
        'TituloModerno',
        fontSize=22,
        textColor=CoresPDF.PRIMARIA,
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=26
    )
    
    # Estilo para o subtítulo
    subtitulo_style = ParagraphStyle(
        'SubtituloModerno',
        fontSize=11,
        textColor=CoresPDF.TEXTO_SECUNDARIO,
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=14
    )
    
    elementos = []
    
    # Título
    elementos.append(Paragraph(titulo, titulo_style))
    
    # Subtítulo se fornecido
    if subtitulo:
        elementos.append(Paragraph(subtitulo, subtitulo_style))
    
    # Data de geração
    data_style = ParagraphStyle(
        'DataGeracao',
        fontSize=8,
        textColor=CoresPDF.TEXTO_SECUNDARIO,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    elementos.append(Paragraph(f'Gerado em: {data_geracao}', data_style))
    elementos.append(Spacer(1, 18))
    
    return elementos


def criar_tabela_moderna(dados, colunas_larguras, destacar_total=False, cores_alternadas=True):
    """
    Cria uma tabela com layout moderno
    """
    tabela = Table(dados, colWidths=colunas_larguras)
    
    estilo_base = [
        # Cabeçalho com gradiente
        ('BACKGROUND', (0, 0), (-1, 0), CoresPDF.PRIMARIA),
        ('TEXTCOLOR', (0, 0), (-1, 0), CoresPDF.BRANCO),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Corpo da tabela
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        
        # Bordas sutis
        ('GRID', (0, 0), (-1, -1), 0.5, CoresPDF.CINZA_CLARO),
        ('BOX', (0, 0), (-1, -1), 1.5, CoresPDF.PRIMARIA),
    ]
    
    # Cores alternadas nas linhas
    if cores_alternadas and len(dados) > 1:
        for i in range(1, len(dados)):
            if i % 2 == 0:
                estilo_base.append(('BACKGROUND', (0, i), (-1, i), CoresPDF.CINZA_BG))
            else:
                estilo_base.append(('BACKGROUND', (0, i), (-1, i), CoresPDF.BRANCO))
    
    # Destacar linha de total
    if destacar_total and len(dados) > 1:
        estilo_base.extend([
            ('BACKGROUND', (0, -1), (-1, -1), CoresPDF.PRIMARIA_CLARA),
            ('TEXTCOLOR', (0, -1), (-1, -1), CoresPDF.BRANCO),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
        ])
    
    tabela.setStyle(TableStyle(estilo_base))
    return tabela


def criar_secao_titulo(titulo, icone=""):
    """
    Cria um título de seção moderno
    """
    if icone:
        titulo_texto = f"{icone} {titulo}"
    else:
        titulo_texto = titulo
    
    titulo_style = ParagraphStyle(
        'SecaoTitulo',
        fontSize=14,
        textColor=CoresPDF.PRIMARIA,
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderPadding=8,
        backColor=CoresPDF.CINZA_BG,
        leftIndent=10,
        leading=18
    )
    
    return Paragraph(titulo_texto, titulo_style)


def criar_card_resumo(titulo, itens, cor_borda=CoresPDF.PRIMARIA):
    """
    Cria um card de resumo com informações em lista
    itens: lista de tuplas (label, valor)
    """
    # Título do card
    dados = [[Paragraph(f'<font size=12 color="{CoresPDF.PRIMARIA.hexval()}"><b>{titulo}</b></font>',
                       ParagraphStyle('center', alignment=TA_CENTER))]]
    
    # Adicionar itens
    for label, valor in itens:
        dados.append([
            Paragraph(f'<font size=9>{label}</font>', 
                     ParagraphStyle('left', alignment=TA_LEFT)),
            Paragraph(f'<font size=9><b>{valor}</b></font>', 
                     ParagraphStyle('right', alignment=TA_RIGHT))
        ])
    
    card_table = Table(dados, colWidths=[3.5*inch, 1.5*inch])
    card_table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), CoresPDF.CINZA_BG),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Corpo
        ('BACKGROUND', (0, 1), (-1, -1), CoresPDF.BRANCO),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        
        # Linhas separadoras sutis
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, CoresPDF.CINZA_CLARO),
        
        # Borda do card
        ('BOX', (0, 0), (-1, -1), 2, cor_borda),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    
    return card_table


def criar_rodape_moderno(canvas, doc, config_empresa, numero_pagina):
    """
    Cria um rodapé moderno para o PDF
    """
    canvas.saveState()
    
    # Linha decorativa
    canvas.setStrokeColor(CoresPDF.PRIMARIA)
    canvas.setLineWidth(2)
    canvas.line(50, 50, doc.pagesize[0] - 50, 50)
    
    # Informações da empresa (esquerda)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(CoresPDF.TEXTO_SECUNDARIO)
    
    info_empresa = config_empresa.get('nome_empresa', 'FG AUTO PEÇAS')
    if config_empresa.get('telefone'):
        info_empresa += f" | Tel: {config_empresa['telefone']}"
    if config_empresa.get('email'):
        info_empresa += f" | {config_empresa['email']}"
    
    canvas.drawString(50, 35, info_empresa)
    
    # Número da página (direita)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(CoresPDF.PRIMARIA)
    canvas.drawRightString(doc.pagesize[0] - 50, 35, f"Página {numero_pagina}")
    
    canvas.restoreState()


def criar_badge_status(texto, tipo='info'):
    """
    Cria um badge de status colorido
    tipos: 'sucesso', 'aviso', 'erro', 'info'
    """
    cores_badge = {
        'sucesso': (CoresPDF.SUCESSO_BG, CoresPDF.SUCESSO),
        'aviso': (CoresPDF.AVISO_BG, CoresPDF.AVISO),
        'erro': (CoresPDF.ERRO_BG, CoresPDF.ERRO),
        'info': (CoresPDF.INFO_BG, CoresPDF.INFO),
    }
    
    cor_fundo, cor_texto = cores_badge.get(tipo, cores_badge['info'])
    
    badge_style = ParagraphStyle(
        'Badge',
        fontSize=8,
        textColor=cor_texto,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        backColor=cor_fundo,
        borderWidth=1,
        borderColor=cor_texto,
        borderPadding=4,
        borderRadius=3,
    )
    
    return Paragraph(texto, badge_style)


def formatar_moeda(valor):
    """
    Formata valor para moeda brasileira
    """
    try:
        return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"


def formatar_porcentagem(valor):
    """
    Formata valor para porcentagem
    """
    try:
        return f"{float(valor):.1f}%"
    except:
        return "0.0%"
