BEGIN;

-- =========================================================
-- 1) Tabela de planos SaaS
-- =========================================================
CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    price_monthly NUMERIC(10,2) NOT NULL DEFAULT 0,
    max_users INTEGER,
    max_products INTEGER,
    max_sales_month INTEGER,
    nfe_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    support_level TEXT NOT NULL DEFAULT 'standard',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_plans_slug
    ON plans (slug);

-- =========================================================
-- 2) Tabela de assinaturas por tenant
-- =========================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE RESTRICT,
    status TEXT NOT NULL DEFAULT 'active',
    current_period_start TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    current_period_end TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
    trial_ends_at TIMESTAMP,
    canceled_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_subscriptions_tenant_id
    ON subscriptions (tenant_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id
    ON subscriptions (plan_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_status
    ON subscriptions (status);

-- =========================================================
-- 3) Planos padrão
-- =========================================================
INSERT INTO plans (
    name, slug, price_monthly, max_users, max_products, max_sales_month,
    nfe_enabled, support_level, active, created_at, updated_at
)
VALUES
    ('START', 'start', 39.90, 2, 300, 300, FALSE, 'email', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('GESTAO', 'gestao', 69.90, 5, 1500, 1500, TRUE, 'prioritario', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('PRO', 'pro', 99.90, NULL, NULL, NULL, TRUE, 'dedicado', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (slug) DO UPDATE
SET
    name = EXCLUDED.name,
    price_monthly = EXCLUDED.price_monthly,
    max_users = EXCLUDED.max_users,
    max_products = EXCLUDED.max_products,
    max_sales_month = EXCLUDED.max_sales_month,
    nfe_enabled = EXCLUDED.nfe_enabled,
    support_level = EXCLUDED.support_level,
    active = EXCLUDED.active,
    updated_at = CURRENT_TIMESTAMP;

-- =========================================================
-- 4) Backfill de assinaturas para tenants existentes
-- =========================================================
INSERT INTO subscriptions (
    tenant_id, plan_id, status, current_period_start, current_period_end,
    trial_ends_at, canceled_at, created_at, updated_at
)
SELECT
    t.id,
    p.id,
    'active',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '30 days',
    NULL,
    NULL,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM tenants t
JOIN plans p
  ON p.slug = 'start'
LEFT JOIN subscriptions s
  ON s.tenant_id = t.id
WHERE s.id IS NULL;

COMMIT;
