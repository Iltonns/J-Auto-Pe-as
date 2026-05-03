BEGIN;

-- =========================================================
-- Etapa 5: suporte a superadmin global para painel de tenants
-- =========================================================
ALTER TABLE public.usuarios
    ADD COLUMN IF NOT EXISTS is_superadmin BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_usuarios_is_superadmin
    ON public.usuarios (is_superadmin);

-- Bootstrap: promove o admin do tenant padrão como superadmin global
DO $$
DECLARE
    v_tenant_id INTEGER;
BEGIN
    BEGIN
        SELECT id
          INTO v_tenant_id
          FROM public.tenants
         WHERE slug = 'erp-auto-pecas'
         ORDER BY id
         LIMIT 1;
    EXCEPTION WHEN undefined_table THEN
        v_tenant_id := NULL;
    END;

    IF v_tenant_id IS NOT NULL THEN
        UPDATE public.usuarios
           SET is_superadmin = TRUE
         WHERE id = (
            SELECT id
              FROM public.usuarios
             WHERE tenant_id = v_tenant_id
               AND username = 'admin'
             ORDER BY id
             LIMIT 1
         );
    END IF;
END
$$;

COMMIT;
