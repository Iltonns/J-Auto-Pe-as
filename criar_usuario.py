#!/usr/bin/env python
"""Script para criar usuario com tenant_id no banco Neon/PostgreSQL."""
import getpass
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERRO: DATABASE_URL nao configurada no arquivo .env")
    sys.exit(1)

try:
    import psycopg2
    from werkzeug.security import generate_password_hash
except ImportError as exc:
    print(f"ERRO de importacao: {exc}")
    sys.exit(1)


def obter_tenant_id(cursor, tenant_slug):
    """Resolve tenant_id pelo slug; fallback para primeiro tenant cadastrado."""
    cursor.execute("SELECT id, slug, nome FROM tenants WHERE slug = %s ORDER BY id LIMIT 1", (tenant_slug,))
    row = cursor.fetchone()
    if row:
        return int(row[0]), row[1], row[2]

    cursor.execute("SELECT id, slug, nome FROM tenants ORDER BY id LIMIT 1")
    row = cursor.fetchone()
    if row:
        return int(row[0]), row[1], row[2]

    return None, None, None


def main():
    print("=" * 60)
    print("CRIAR NOVO USUARIO - ERP AUTO PECAS")
    print("=" * 60)

    tenant_slug = input("Slug do tenant [erp-auto-pecas]: ").strip() or "erp-auto-pecas"

    username = input("Nome de usuario: ").strip()
    if not username:
        print("ERRO: nome de usuario nao pode estar vazio")
        sys.exit(1)

    password = getpass.getpass("Senha: ").strip()
    if not password:
        print("ERRO: senha nao pode estar vazia")
        sys.exit(1)

    nome_completo = input("Nome completo: ").strip()
    if not nome_completo:
        print("ERRO: nome completo nao pode estar vazio")
        sys.exit(1)

    email = input("Email: ").strip()
    if not email:
        print("ERRO: email nao pode estar vazio")
        sys.exit(1)

    print("\n--- PERMISSOES (S/N) ---")
    permissoes = {
        "permissao_vendas": input("Permitir VENDAS? (S/n): ").lower() != "n",
        "permissao_estoque": input("Permitir ESTOQUE? (S/n): ").lower() != "n",
        "permissao_clientes": input("Permitir CLIENTES? (S/n): ").lower() != "n",
        "permissao_financeiro": input("Permitir FINANCEIRO? (S/n): ").lower() != "n",
        "permissao_caixa": input("Permitir CAIXA? (S/n): ").lower() != "n",
        "permissao_relatorios": input("Permitir RELATORIOS? (S/n): ").lower() != "n",
        "permissao_admin": input("Permitir ADMIN? (S/n): ").lower() != "n",
    }

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        tenant_id, tenant_slug_resolvido, tenant_nome = obter_tenant_id(cursor, tenant_slug)
        if tenant_id is None:
            print("ERRO: nenhum tenant encontrado na tabela tenants.")
            conn.close()
            sys.exit(1)

        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE username = %s AND tenant_id = %s",
            (username, tenant_id),
        )
        if cursor.fetchone()[0] > 0:
            print(f"ERRO: usuario '{username}' ja existe no tenant '{tenant_slug_resolvido}'.")
            conn.close()
            sys.exit(1)

        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE email = %s AND tenant_id = %s",
            (email, tenant_id),
        )
        if cursor.fetchone()[0] > 0:
            print(f"ERRO: email '{email}' ja existe no tenant '{tenant_slug_resolvido}'.")
            conn.close()
            sys.exit(1)

        password_hash = generate_password_hash(password)
        cursor.execute(
            """
            INSERT INTO usuarios (
                username, password_hash, nome_completo, email,
                permissao_vendas, permissao_estoque, permissao_clientes,
                permissao_financeiro, permissao_caixa, permissao_relatorios, permissao_admin,
                ativo, tenant_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s)
            """,
            (
                username,
                password_hash,
                nome_completo,
                email,
                permissoes["permissao_vendas"],
                permissoes["permissao_estoque"],
                permissoes["permissao_clientes"],
                permissoes["permissao_financeiro"],
                permissoes["permissao_caixa"],
                permissoes["permissao_relatorios"],
                permissoes["permissao_admin"],
                tenant_id,
            ),
        )
        conn.commit()

        print("\n" + "=" * 60)
        print("USUARIO CRIADO COM SUCESSO")
        print("=" * 60)
        print(f"Tenant: {tenant_nome} ({tenant_slug_resolvido}) [id={tenant_id}]")
        print(f"Usuario: {username}")
        print(f"Email: {email}")
        print(f"Nome: {nome_completo}")
        print("=" * 60)
    except Exception as exc:
        conn.rollback()
        print(f"ERRO ao criar usuario: {exc}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
