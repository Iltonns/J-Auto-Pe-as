from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


class CoresPDF:
    PRIMARIA = colors.HexColor("#1F4E79")
    SUCESSO = colors.HexColor("#2E7D32")
    AVISO = colors.HexColor("#EF6C00")
    INFO = colors.HexColor("#1565C0")
    ERRO = colors.HexColor("#C62828")
    TEXTO = colors.HexColor("#202124")
    CINZA_CLARO = colors.HexColor("#F3F4F6")
    CINZA_MEDIO = colors.HexColor("#D1D5DB")


def _safe_text(value, default="-"):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def formatar_moeda(valor):
    try:
        numero = float(valor or 0)
    except (TypeError, ValueError):
        numero = 0.0

    bruto = f"{numero:,.2f}"
    # Convert to pt-BR style: 1,234.56 -> 1.234,56
    bruto = bruto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {bruto}"


def formatar_porcentagem(valor):
    try:
        numero = float(valor or 0)
    except (TypeError, ValueError):
        numero = 0.0
    return f"{numero:.1f}%"


def criar_cabecalho_empresa_moderno(config_empresa):
    nome_empresa = _safe_text((config_empresa or {}).get("nome_empresa"), "Empresa")
    cnpj = _safe_text((config_empresa or {}).get("cnpj"), "")
    cidade = _safe_text((config_empresa or {}).get("cidade"), "")
    estado = _safe_text((config_empresa or {}).get("estado"), "")
    telefone = _safe_text((config_empresa or {}).get("telefone"), "")
    email = _safe_text((config_empresa or {}).get("email"), "")

    style_nome = ParagraphStyle(
        "pdf_empresa_nome",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=CoresPDF.PRIMARIA,
        alignment=TA_LEFT,
    )
    style_info = ParagraphStyle(
        "pdf_empresa_info",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=CoresPDF.TEXTO,
        alignment=TA_LEFT,
    )

    info_linhas = []
    if cnpj:
        info_linhas.append(f"CNPJ: {cnpj}")
    localidade = " - ".join([p for p in [cidade, estado] if p and p != "-"])
    if localidade:
        info_linhas.append(localidade)
    if telefone and telefone != "-":
        info_linhas.append(f"Tel: {telefone}")
    if email and email != "-":
        info_linhas.append(f"Email: {email}")

    story = [Paragraph(nome_empresa, style_nome)]
    if info_linhas:
        story.append(Paragraph(" | ".join(info_linhas), style_info))
    story.append(Spacer(1, 10))
    return story


def criar_cabecalho_moderno(titulo, subtitulo=""):
    style_titulo = ParagraphStyle(
        "pdf_titulo",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=CoresPDF.TEXTO,
        alignment=TA_LEFT,
    )
    style_subtitulo = ParagraphStyle(
        "pdf_subtitulo",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4B5563"),
        alignment=TA_LEFT,
    )

    story = [Paragraph(_safe_text(titulo, "Relatorio"), style_titulo)]
    if subtitulo:
        story.append(Paragraph(_safe_text(subtitulo, ""), style_subtitulo))
    story.append(Spacer(1, 10))
    return story


def _kpi_card(kpi):
    titulo = _safe_text((kpi or {}).get("titulo"), "")
    valor = _safe_text((kpi or {}).get("valor"), "0")
    subtitulo = _safe_text((kpi or {}).get("subtitulo"), "")
    cor = (kpi or {}).get("cor") or CoresPDF.PRIMARIA

    style_titulo = ParagraphStyle(
        "kpi_titulo",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#374151"),
    )
    style_valor = ParagraphStyle(
        "kpi_valor",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=cor,
    )
    style_subtitulo = ParagraphStyle(
        "kpi_subtitulo",
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#6B7280"),
    )

    conteudo = [
        [Paragraph(titulo, style_titulo)],
        [Paragraph(valor, style_valor)],
        [Paragraph(subtitulo, style_subtitulo)],
    ]
    tabela = Table(conteudo, colWidths=[1.6 * inch])
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CoresPDF.CINZA_CLARO),
                ("BOX", (0, 0), (-1, -1), 0.5, CoresPDF.CINZA_MEDIO),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tabela


def criar_painel_kpis(kpis):
    lista = [k for k in (kpis or []) if isinstance(k, dict)]
    if not lista:
        return Spacer(1, 1)

    cards = [_kpi_card(kpi) for kpi in lista]
    tabela = Table([cards], colWidths=[None] * len(cards))
    tabela.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return tabela


def criar_tabela_moderna(data, colWidths, destacar_total=False, cores_alternadas=True):
    tabela = Table(data or [[]], colWidths=colWidths, repeatRows=1)

    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), CoresPDF.PRIMARIA),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, CoresPDF.CINZA_MEDIO),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
    ]

    row_count = len(data or [])
    if cores_alternadas and row_count > 2:
        for idx in range(1, row_count):
            if idx % 2 == 0:
                estilos.append(("BACKGROUND", (0, idx), (-1, idx), CoresPDF.CINZA_CLARO))

    if destacar_total and row_count >= 2:
        last = row_count - 1
        estilos.extend(
            [
                ("BACKGROUND", (0, last), (-1, last), colors.HexColor("#E5E7EB")),
                ("FONTNAME", (0, last), (-1, last), "Helvetica-Bold"),
            ]
        )

    tabela.setStyle(TableStyle(estilos))
    return tabela


def criar_secao_titulo(titulo):
    style = ParagraphStyle(
        "pdf_secao_titulo",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=CoresPDF.PRIMARIA,
        alignment=TA_LEFT,
    )
    return Paragraph(_safe_text(titulo, "Secao"), style)


def criar_card_resumo(titulo, itens, cor):
    style_titulo = ParagraphStyle(
        "card_resumo_titulo",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=cor or CoresPDF.PRIMARIA,
        alignment=TA_LEFT,
    )
    style_linha = ParagraphStyle(
        "card_resumo_linha",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=CoresPDF.TEXTO,
        alignment=TA_LEFT,
    )

    linhas = [[Paragraph(_safe_text(titulo, "Resumo"), style_titulo)]]
    for item in itens or []:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        chave, valor = item
        linhas.append([Paragraph(f"{_safe_text(chave, '')} {_safe_text(valor, '')}", style_linha)])

    tabela = Table(linhas, colWidths=[3.5 * inch])
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CoresPDF.CINZA_CLARO),
                ("BOX", (0, 0), (-1, -1), 0.6, CoresPDF.CINZA_MEDIO),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tabela


def criar_rodape_moderno(canvas, doc, config_empresa, pagina_atual):
    canvas.saveState()
    largura, _ = doc.pagesize
    y = 32
    canvas.setStrokeColor(CoresPDF.CINZA_MEDIO)
    canvas.setLineWidth(0.5)
    canvas.line(40, y + 10, largura - 40, y + 10)

    nome_empresa = _safe_text((config_empresa or {}).get("nome_empresa"), "Empresa")
    gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#4B5563"))
    canvas.drawString(40, y, f"{nome_empresa} | Gerado em {gerado_em}")
    canvas.drawRightString(largura - 40, y, f"Pagina {pagina_atual}")
    canvas.restoreState()
