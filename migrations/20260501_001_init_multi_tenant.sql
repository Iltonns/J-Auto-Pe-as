BEGIN;

-- =========================================================
-- 1) Tabela de tenants (base multi-tenant)
-- =========================================================
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    slug TEXT NOT NULL,
    nome TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_tenants_slug
    ON tenants (slug);

-- Tenant padrão obrigatório
INSERT INTO tenants (slug, nome, status)
VALUES ('erp-auto-pecas', 'ERP Auto Peças', 'active')
ON CONFLICT (slug) DO UPDATE
SET nome = EXCLUDED.nome,
    status = EXCLUDED.status;

-- =========================================================
-- 2) Adicionar tenant_id (NULLABLE) nas tabelas operacionais
-- =========================================================
ALTER TABLE usuarios                 ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE clientes                 ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE fornecedores             ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE produtos                 ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE vendas                   ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE itens_venda              ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE orcamentos               ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE itens_orcamento          ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE movimentacoes            ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE contas_pagar             ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE contas_receber           ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE caixa_sessoes            ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE caixa_movimentacoes      ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE lancamentos_financeiros  ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE configuracoes_empresa    ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE fiscal_nfe_numeracao     ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE fiscal_nfe               ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE fiscal_nfe_itens         ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE fiscal_nfe_eventos       ADD COLUMN IF NOT EXISTS tenant_id INTEGER;

-- =========================================================
-- 3) Backfill do tenant_id existente + default de compatibilidade
-- =========================================================
DO $$
DECLARE
    v_tenant_id INTEGER;
    v_table TEXT;
BEGIN
    SELECT id
      INTO v_tenant_id
      FROM tenants
     WHERE slug = 'erp-auto-pecas'
     ORDER BY id
     LIMIT 1;

    IF v_tenant_id IS NULL THEN
        RAISE EXCEPTION 'Tenant padrão erp-auto-pecas não encontrado.';
    END IF;

    -- Tabelas "pai" / independentes
    UPDATE usuarios                SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE clientes                SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE fornecedores            SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE produtos                SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE vendas                  SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE orcamentos              SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE movimentacoes           SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE contas_pagar            SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE contas_receber          SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE caixa_sessoes           SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE caixa_movimentacoes     SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE lancamentos_financeiros SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE configuracoes_empresa   SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE fiscal_nfe_numeracao    SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;

    -- Tabelas filhas (herdar tenant de pai quando possível)
    UPDATE itens_venda iv
       SET tenant_id = v.tenant_id
      FROM vendas v
     WHERE iv.tenant_id IS NULL
       AND iv.venda_id = v.id
       AND v.tenant_id IS NOT NULL;

    UPDATE itens_orcamento io
       SET tenant_id = o.tenant_id
      FROM orcamentos o
     WHERE io.tenant_id IS NULL
       AND io.orcamento_id = o.id
       AND o.tenant_id IS NOT NULL;

    UPDATE fiscal_nfe fn
       SET tenant_id = v.tenant_id
      FROM vendas v
     WHERE fn.tenant_id IS NULL
       AND fn.venda_id = v.id
       AND v.tenant_id IS NOT NULL;

    UPDATE fiscal_nfe_itens fi
       SET tenant_id = fn.tenant_id
      FROM fiscal_nfe fn
     WHERE fi.tenant_id IS NULL
       AND fi.nfe_id = fn.id
       AND fn.tenant_id IS NOT NULL;

    UPDATE fiscal_nfe_eventos fe
       SET tenant_id = fn.tenant_id
      FROM fiscal_nfe fn
     WHERE fe.tenant_id IS NULL
       AND fe.nfe_id = fn.id
       AND fn.tenant_id IS NOT NULL;

    -- Fallback (qualquer sobra)
    UPDATE itens_venda        SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE itens_orcamento    SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE fiscal_nfe         SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE fiscal_nfe_itens   SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;
    UPDATE fiscal_nfe_eventos SET tenant_id = v_tenant_id WHERE tenant_id IS NULL;

    -- Compatibilidade com app atual (que ainda não envia tenant_id):
    -- define DEFAULT tenant_id = tenant padrão
    FOREACH v_table IN ARRAY ARRAY[
        'usuarios','clientes','fornecedores','produtos','vendas','itens_venda',
        'orcamentos','itens_orcamento','movimentacoes','contas_pagar',
        'contas_receber','caixa_sessoes','caixa_movimentacoes',
        'lancamentos_financeiros','configuracoes_empresa','fiscal_nfe_numeracao',
        'fiscal_nfe','fiscal_nfe_itens','fiscal_nfe_eventos'
    ]
    LOOP
        IF to_regclass(v_table) IS NOT NULL THEN
            EXECUTE format(
                'ALTER TABLE %I ALTER COLUMN tenant_id SET DEFAULT %s',
                v_table, v_tenant_id
            );
        END IF;
    END LOOP;
END
$$;

-- =========================================================
-- 4) Índices por tenant_id
-- =========================================================
DO $$
DECLARE
    v_table TEXT;
BEGIN
    FOREACH v_table IN ARRAY ARRAY[
        'usuarios','clientes','fornecedores','produtos','vendas','itens_venda',
        'orcamentos','itens_orcamento','movimentacoes','contas_pagar',
        'contas_receber','caixa_sessoes','caixa_movimentacoes',
        'lancamentos_financeiros','configuracoes_empresa','fiscal_nfe_numeracao',
        'fiscal_nfe','fiscal_nfe_itens','fiscal_nfe_eventos'
    ]
    LOOP
        IF to_regclass(v_table) IS NOT NULL THEN
            EXECUTE format(
                'CREATE INDEX IF NOT EXISTS %I ON %I (tenant_id)',
                'idx_' || v_table || '_tenant_id',
                v_table
            );
        END IF;
    END LOOP;
END
$$;

-- =========================================================
-- 5) Foreign keys para tenants(id) (NOT VALID por segurança de lock/scan)
-- =========================================================
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT *
          FROM (VALUES
            ('usuarios',                'fk_usuarios_tenant_id'),
            ('clientes',                'fk_clientes_tenant_id'),
            ('fornecedores',            'fk_fornecedores_tenant_id'),
            ('produtos',                'fk_produtos_tenant_id'),
            ('vendas',                  'fk_vendas_tenant_id'),
            ('itens_venda',             'fk_itens_venda_tenant_id'),
            ('orcamentos',              'fk_orcamentos_tenant_id'),
            ('itens_orcamento',         'fk_itens_orcamento_tenant_id'),
            ('movimentacoes',           'fk_movimentacoes_tenant_id'),
            ('contas_pagar',            'fk_contas_pagar_tenant_id'),
            ('contas_receber',          'fk_contas_receber_tenant_id'),
            ('caixa_sessoes',           'fk_caixa_sessoes_tenant_id'),
            ('caixa_movimentacoes',     'fk_caixa_movimentacoes_tenant_id'),
            ('lancamentos_financeiros', 'fk_lanc_fin_tenant_id'),
            ('configuracoes_empresa',   'fk_config_empresa_tenant_id'),
            ('fiscal_nfe_numeracao',    'fk_fiscal_num_tenant_id'),
            ('fiscal_nfe',              'fk_fiscal_nfe_tenant_id'),
            ('fiscal_nfe_itens',        'fk_fiscal_nfe_itens_tenant_id'),
            ('fiscal_nfe_eventos',      'fk_fiscal_nfe_eventos_tenant_id')
          ) AS t(table_name, constraint_name)
    LOOP
        IF to_regclass(r.table_name) IS NOT NULL THEN
            IF NOT EXISTS (
                SELECT 1
                  FROM pg_constraint c
                 WHERE c.conname = r.constraint_name
                   AND c.conrelid = to_regclass(r.table_name)
            ) THEN
                EXECUTE format(
                    'ALTER TABLE %I ADD CONSTRAINT %I
                     FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                     ON UPDATE RESTRICT ON DELETE RESTRICT
                     NOT VALID',
                    r.table_name, r.constraint_name
                );
            END IF;
        END IF;
    END LOOP;
END
$$;

COMMIT;
