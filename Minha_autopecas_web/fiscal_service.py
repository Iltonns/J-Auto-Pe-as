import os
import hashlib
import requests
from datetime import datetime
from decimal import Decimal

from Minha_autopecas_web.logica_banco import (
    criar_rascunho_nfe_para_venda,
    obter_dados_venda_para_nfe,
    atualizar_dados_nfe,
    obter_nfe_por_venda,
    registrar_evento_nfe,
    atualizar_nfe_por_webhook,
)


def _apenas_digitos(valor):
    if not valor:
        return ''
    return ''.join(ch for ch in str(valor) if ch.isdigit())


def _to_float(valor, default=0.0):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return default


def _mapear_status_remoto(status_remoto):
    if not status_remoto:
        return 'processando'

    status = str(status_remoto).strip().lower()
    if status in ('autorizada', 'autorizado', 'approved', 'aprovada', 'success'):
        return 'autorizada'
    if status in ('rejeitada', 'rejeitado', 'rejected', 'error', 'erro'):
        return 'rejeitada'
    if status in ('cancelada', 'cancelado', 'canceled'):
        return 'cancelada'
    if status in ('rascunho', 'draft'):
        return 'rascunho'
    if status in ('enviada', 'sent'):
        return 'enviada'
    return 'processando'


def _serializar_nfe(nfe):
    if not isinstance(nfe, dict):
        return nfe

    serializado = {}
    for chave, valor in nfe.items():
        if isinstance(valor, datetime):
            serializado[chave] = valor.isoformat()
        elif isinstance(valor, Decimal):
            serializado[chave] = float(valor)
        else:
            serializado[chave] = valor
    return serializado


def validar_dados_fiscais(dados):
    erros = []

    venda = dados.get('venda', {})
    empresa = dados.get('empresa', {})
    itens = dados.get('itens', [])

    cnpj_emitente = _apenas_digitos(empresa.get('cnpj'))
    if len(cnpj_emitente) != 14:
        erros.append('CNPJ da empresa inválido ou não configurado.')

    if not empresa.get('ie'):
        erros.append('Inscrição Estadual da empresa não configurada.')

    if not empresa.get('estado'):
        erros.append('UF da empresa não configurada.')

    if not empresa.get('codigo_municipio_ibge'):
        erros.append('Código do município IBGE da empresa não configurado.')

    if not empresa.get('crt'):
        erros.append('CRT da empresa não configurado.')

    if not venda.get('cliente_id'):
        erros.append('Venda sem cliente vinculado. Para emitir NF-e, selecione um cliente cadastrado.')

    documento_cliente = _apenas_digitos(venda.get('cliente_cpf_cnpj'))
    if not documento_cliente:
        erros.append('Cliente sem CPF/CNPJ cadastrado.')

    if documento_cliente and len(documento_cliente) not in (11, 14):
        erros.append('CPF/CNPJ do cliente inválido.')

    if not venda.get('cliente_endereco'):
        erros.append('Endereço do cliente não informado.')

    if not itens:
        erros.append('Venda sem itens para emissão fiscal.')

    for idx, item in enumerate(itens, start=1):
        if not item.get('ncm'):
            erros.append(f'Item {idx} sem NCM cadastrado.')
        if not item.get('cfop'):
            erros.append(f'Item {idx} sem CFOP cadastrado.')
        if not item.get('unidade'):
            erros.append(f'Item {idx} sem unidade cadastrada.')

    return erros


def montar_payload_nfe(dados, numero_nfe, serie, ambiente):
    venda = dados['venda']
    empresa = dados['empresa']
    itens = dados['itens']

    payload_itens = []
    total_produtos = 0.0

    for item in itens:
        valor_total_item = _to_float(item.get('subtotal'))
        total_produtos += valor_total_item

        payload_itens.append({
            'venda_item_id': item.get('venda_item_id'),
            'produto_id': item.get('produto_id'),
            'descricao': item.get('produto_nome'),
            'ncm': item.get('ncm'),
            'cest': item.get('cest'),
            'cfop': item.get('cfop'),
            'unidade': item.get('unidade') or 'UN',
            'origem_mercadoria': item.get('origem_mercadoria') or '0',
            'csosn': item.get('csosn') or '102',
            'cst_icms': item.get('cst_icms'),
            'cst_pis': item.get('cst_pis') or '01',
            'cst_cofins': item.get('cst_cofins') or '01',
            'aliquota_icms': _to_float(item.get('aliquota_icms')),
            'aliquota_pis': _to_float(item.get('aliquota_pis')),
            'aliquota_cofins': _to_float(item.get('aliquota_cofins')),
            'quantidade': _to_float(item.get('quantidade')),
            'valor_unitario': _to_float(item.get('preco_unitario')),
            'valor_total': valor_total_item,
        })

    valor_desconto = _to_float(venda.get('desconto'))
    valor_total_nota = _to_float(venda.get('total'))

    payload = {
        'identificacao': {
            'numero': int(numero_nfe),
            'serie': int(serie),
            'modelo': '55',
            'ambiente': ambiente,
            'natureza_operacao': 'Venda de mercadoria',
            'data_emissao': datetime.utcnow().isoformat(),
        },
        'emitente': {
            'razao_social': empresa.get('nome_empresa'),
            'cnpj': _apenas_digitos(empresa.get('cnpj')),
            'ie': empresa.get('ie'),
            'crt': empresa.get('crt') or '1',
            'cnae': empresa.get('cnae'),
            'endereco': empresa.get('endereco'),
            'cidade': empresa.get('cidade'),
            'estado': empresa.get('estado'),
            'cep': _apenas_digitos(empresa.get('cep')),
            'codigo_municipio_ibge': empresa.get('codigo_municipio_ibge'),
            'telefone': _apenas_digitos(empresa.get('telefone')),
            'email': empresa.get('email'),
        },
        'destinatario': {
            'nome': venda.get('cliente_nome'),
            'tipo_pessoa': venda.get('cliente_tipo_pessoa') or ('JURIDICA' if len(_apenas_digitos(venda.get('cliente_cpf_cnpj'))) == 14 else 'FISICA'),
            'cpf_cnpj': _apenas_digitos(venda.get('cliente_cpf_cnpj')),
            'ie': venda.get('cliente_ie'),
            'indicador_ie': venda.get('cliente_indicador_ie') or '9',
            'endereco': venda.get('cliente_endereco') or 'NAO INFORMADO',
            'bairro': venda.get('cliente_bairro') or 'CENTRO',
            'numero': venda.get('cliente_numero') or 'S/N',
            'complemento': venda.get('cliente_complemento'),
            'cidade': venda.get('cliente_cidade') or empresa.get('cidade') or 'NAO INFORMADA',
            'estado': venda.get('cliente_estado') or empresa.get('estado'),
            'cep': _apenas_digitos(venda.get('cliente_cep') or empresa.get('cep') or '00000000'),
            'codigo_municipio_ibge': venda.get('cliente_codigo_municipio_ibge') or empresa.get('codigo_municipio_ibge'),
            'telefone': _apenas_digitos(venda.get('cliente_telefone')),
            'email': venda.get('cliente_email'),
        },
        'itens': payload_itens,
        'pagamento': {
            'forma_pagamento': venda.get('forma_pagamento'),
            'valor': valor_total_nota,
        },
        'totais': {
            'valor_produtos': round(total_produtos, 2),
            'valor_desconto': round(valor_desconto, 2),
            'valor_nota': round(valor_total_nota, 2),
        },
        'metadata': {
            'venda_id': venda.get('id'),
            'observacoes': venda.get('observacoes'),
        },
    }

    return payload


def _emitir_nfe_mock(venda_id, numero, serie, payload):
    base = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{venda_id}-{numero}-{serie}"
    hash_base = hashlib.sha1(base.encode('utf-8')).hexdigest().upper()
    chave_falsa = ('35' + ''.join(ch for ch in hash_base if ch.isdigit()) + '0' * 44)[:44]
    protocolo = datetime.utcnow().strftime('135%y%m%d%H%M%S')

    xml_mock = (
        f"<nfe><infNFe><ide><nNF>{numero}</nNF><serie>{serie}</serie></ide>"
        f"<total><vNF>{payload['totais']['valor_nota']}</vNF></total></infNFe></nfe>"
    )

    return {
        'sucesso': True,
        'status': 'autorizada',
        'chave_acesso': chave_falsa,
        'protocolo': protocolo,
        'motivo': 'Autorizada em ambiente de simulacao (mock).',
        'xml_autorizado': xml_mock,
        'danfe_url': None,
        'response_payload': {
            'provider': 'mock',
            'status': 'autorizada',
            'chave_acesso': chave_falsa,
            'protocolo': protocolo,
        }
    }


def _emitir_nfe_provider_http(payload):
    api_base_url = os.getenv('NFE_API_BASE_URL', '').strip().rstrip('/')
    api_token = os.getenv('NFE_API_TOKEN', '').strip()
    endpoint = os.getenv('NFE_EMISSAO_ENDPOINT', '/nfe').strip()
    timeout = int(os.getenv('NFE_TIMEOUT_SECONDS', '30') or 30)

    if not api_base_url or not api_token:
        return {
            'sucesso': False,
            'status': 'erro_configuracao',
            'motivo': 'NFE_API_BASE_URL e NFE_API_TOKEN precisam estar configurados.',
            'response_payload': {
                'erro': 'configuracao_incompleta'
            }
        }

    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint

    url = f"{api_base_url}{endpoint}"
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except Exception as e:
        return {
            'sucesso': False,
            'status': 'erro_envio',
            'motivo': f'Falha de comunicacao com provedor fiscal: {str(e)}',
            'response_payload': {'erro': str(e)}
        }

    try:
        data = response.json()
    except Exception:
        data = {'raw': response.text}

    status_local = _mapear_status_remoto(data.get('status') or data.get('situacao'))

    chave = data.get('chave_acesso') or data.get('chave') or data.get('access_key')
    protocolo = data.get('protocolo') or data.get('protocolo_autorizacao') or data.get('protocol')
    motivo = data.get('motivo') or data.get('mensagem') or data.get('message') or response.reason
    danfe_url = data.get('danfe_url') or data.get('url_danfe')
    xml_autorizado = data.get('xml_autorizado') or data.get('xml')

    sucesso = response.status_code in (200, 201, 202) and status_local in ('autorizada', 'processando')

    return {
        'sucesso': sucesso,
        'status': status_local,
        'chave_acesso': chave,
        'protocolo': protocolo,
        'motivo': motivo,
        'danfe_url': danfe_url,
        'xml_autorizado': xml_autorizado,
        'response_payload': data,
    }


def emitir_nfe_para_venda(venda_id, usuario_id):
    ambiente = os.getenv('NFE_AMBIENTE', 'homologacao').strip().lower() or 'homologacao'
    provider = os.getenv('NFE_PROVIDER', 'mock').strip().lower() or 'mock'

    serie_env = os.getenv('NFE_SERIE_PADRAO', '1').strip() or '1'
    try:
        serie = max(1, int(serie_env))
    except ValueError:
        serie = 1

    rascunho = criar_rascunho_nfe_para_venda(
        venda_id=venda_id,
        usuario_id=usuario_id,
        ambiente=ambiente,
        serie=serie,
    )

    if not rascunho.get('sucesso'):
        return {
            'sucesso': False,
            'status': 'erro_interno',
            'mensagem': rascunho.get('erro', 'Falha ao preparar rascunho fiscal.'),
        }

    nfe = rascunho['nfe']
    dados = obter_dados_venda_para_nfe(venda_id)

    if not dados.get('sucesso'):
        atualizar_dados_nfe(nfe['id'], status='rejeitada', motivo_status=dados.get('erro'))
        return {
            'sucesso': False,
            'status': 'rejeitada',
            'nfe': _serializar_nfe(obter_nfe_por_venda(venda_id)),
            'mensagem': dados.get('erro', 'Nao foi possivel carregar dados da venda para NF-e.'),
        }

    erros = validar_dados_fiscais(dados)
    if erros:
        motivo = ' | '.join(erros)
        atualizar_dados_nfe(nfe['id'], status='rejeitada', motivo_status=motivo)
        registrar_evento_nfe(nfe['id'], tipo_evento='validacao', status='rejeitada', justificativa=motivo, usuario_id=usuario_id)
        return {
            'sucesso': False,
            'status': 'rejeitada',
            'nfe': _serializar_nfe(obter_nfe_por_venda(venda_id)),
            'erros_validacao': erros,
            'mensagem': 'Falha de validacao fiscal. Corrija os dados e tente novamente.',
        }

    payload = montar_payload_nfe(dados, nfe.get('numero'), nfe.get('serie'), ambiente)

    atualizar_dados_nfe(
        nfe['id'],
        status='enviada',
        payload_json=payload,
        data_emissao=datetime.utcnow(),
        ambiente=ambiente,
    )

    if provider == 'mock':
        resposta = _emitir_nfe_mock(venda_id, nfe.get('numero'), nfe.get('serie'), payload)
    else:
        resposta = _emitir_nfe_provider_http(payload)

    status_final = resposta.get('status', 'processando')
    motivo = resposta.get('motivo')

    atualizar = {
        'status': status_final,
        'motivo_status': motivo,
        'response_json': resposta.get('response_payload') or {},
    }

    if resposta.get('chave_acesso'):
        atualizar['chave_acesso'] = resposta['chave_acesso']
    if resposta.get('protocolo'):
        atualizar['protocolo_autorizacao'] = resposta['protocolo']
    if resposta.get('danfe_url'):
        atualizar['danfe_url'] = resposta['danfe_url']
    if resposta.get('xml_autorizado'):
        atualizar['xml_autorizado'] = resposta['xml_autorizado']
    if status_final == 'autorizada':
        atualizar['data_autorizacao'] = datetime.utcnow()

    atualizar_dados_nfe(nfe['id'], **atualizar)

    registrar_evento_nfe(
        nfe['id'],
        tipo_evento='emissao',
        status=status_final,
        protocolo=resposta.get('protocolo'),
        justificativa=motivo,
        request_json=payload,
        response_json=resposta.get('response_payload'),
        usuario_id=usuario_id,
    )

    nfe_atualizada = obter_nfe_por_venda(venda_id)

    return {
        'sucesso': bool(resposta.get('sucesso')),
        'status': status_final,
        'nfe': _serializar_nfe(nfe_atualizada),
        'mensagem': motivo or 'Emissao fiscal processada.',
    }


def consultar_nfe_por_venda(venda_id):
    nfe = obter_nfe_por_venda(venda_id)
    if not nfe:
        return {'sucesso': False, 'mensagem': 'NF-e ainda não gerada para esta venda.'}

    return {
        'sucesso': True,
        'nfe': _serializar_nfe(nfe),
    }


def processar_webhook_nfe(payload, token=None):
    token_esperado = os.getenv('NFE_WEBHOOK_TOKEN', '').strip()
    if token_esperado and token != token_esperado:
        return {'sucesso': False, 'erro': 'Token de webhook inválido.', 'status_code': 401}

    if not isinstance(payload, dict):
        return {'sucesso': False, 'erro': 'Payload inválido.', 'status_code': 400}

    nfe_id = payload.get('nfe_id')
    venda_id = payload.get('venda_id')
    status = _mapear_status_remoto(payload.get('status') or payload.get('situacao'))

    try:
        resultado = atualizar_nfe_por_webhook(
            nfe_id=nfe_id,
            venda_id=venda_id,
            status=status,
            payload=payload,
        )
    except Exception as e:
        print(f"Erro ao atualizar NF-e por webhook: {e}")
        return {'sucesso': False, 'erro': 'Falha interna ao processar webhook fiscal.', 'status_code': 500}

    if not resultado.get('sucesso'):
        return {'sucesso': False, 'erro': resultado.get('erro'), 'status_code': 400}

    return {'sucesso': True, 'status_code': 200, 'nfe_id': resultado.get('nfe_id')}

