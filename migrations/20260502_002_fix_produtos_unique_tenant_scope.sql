BEGIN;

-- =========================================================
-- Correção multi-tenant de unicidade em produtos
-- Objetivo: remover unicidade global de codigo_barras e
-- aplicar unicidade por tenant (tenant_id + codigo_barras).
-- =========================================================

-- 1) Remove constraint/indice global legado de codigo_barras
ALTER TABLE public.produtos
    DROP CONSTRAINT IF EXISTS produtos_codigo_barras_key;

DROP INDEX IF EXISTS public.produtos_codigo_barras_key;

-- 2) Cria unicidade por tenant para codigo_barras
-- Observacao: como codigo_barras permite NULL, usamos indice parcial
-- para preservar comportamento de multiplos NULLs sem conflito.
CREATE UNIQUE INDEX IF NOT EXISTS uq_produtos_tenant_codigo_barras
    ON public.produtos (tenant_id, codigo_barras)
    WHERE codigo_barras IS NOT NULL;

COMMIT;
