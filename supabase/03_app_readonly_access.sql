-- Optional initial setup only; review current policies before running.
-- The public catalog read access has already been verified remotely.
-- This grants unauthenticated project clients read access to these catalog tables.
-- Do not apply if any listed table is expected to contain private information.
BEGIN;

DO $$
DECLARE
    target_table text;
    app_tables text[] := ARRAY[
        'chef_kaggle_recipes',
        'chef_kaggle_steps',
        'chef_kaggle_images',
        'chef_themealdb_recipes',
        'chef_themealdb_ingredients'
    ];
BEGIN
    FOREACH target_table IN ARRAY app_tables LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = target_table
              AND c.relkind = 'r'
              AND c.relrowsecurity
        ) THEN
            RAISE EXCEPTION
                'Expected public.% to exist with row-level security enabled',
                target_table;
        END IF;

        IF has_table_privilege('anon', format('public.%I', target_table), 'INSERT')
            OR has_table_privilege('anon', format('public.%I', target_table), 'UPDATE')
            OR has_table_privilege('anon', format('public.%I', target_table), 'DELETE')
            OR has_table_privilege('anon', format('public.%I', target_table), 'TRUNCATE')
            OR has_table_privilege('anon', format('public.%I', target_table), 'REFERENCES')
            OR has_table_privilege('anon', format('public.%I', target_table), 'TRIGGER')
            OR has_table_privilege('authenticated', format('public.%I', target_table), 'INSERT')
            OR has_table_privilege('authenticated', format('public.%I', target_table), 'UPDATE')
            OR has_table_privilege('authenticated', format('public.%I', target_table), 'DELETE')
            OR has_table_privilege('authenticated', format('public.%I', target_table), 'TRUNCATE')
            OR has_table_privilege('authenticated', format('public.%I', target_table), 'REFERENCES')
            OR has_table_privilege('authenticated', format('public.%I', target_table), 'TRIGGER')
        THEN
            RAISE EXCEPTION
                'Unexpected write privileges on public.%; review grants before applying',
                target_table;
        END IF;

        IF EXISTS (
            SELECT 1
            FROM pg_policies AS policies
            WHERE policies.schemaname = 'public'
              AND policies.tablename = target_table
              AND policies.policyname = 'chef_app_anon_read'
        ) THEN
            RAISE EXCEPTION
                'Policy chef_app_anon_read already exists on public.%; review before applying',
                target_table;
        END IF;
    END LOOP;
END
$$;

GRANT SELECT ON TABLE
    public.chef_kaggle_recipes,
    public.chef_kaggle_steps,
    public.chef_kaggle_images,
    public.chef_themealdb_recipes,
    public.chef_themealdb_ingredients
TO anon;

CREATE POLICY chef_app_anon_read ON public.chef_kaggle_recipes
    FOR SELECT TO anon USING (true);
CREATE POLICY chef_app_anon_read ON public.chef_kaggle_steps
    FOR SELECT TO anon USING (true);
CREATE POLICY chef_app_anon_read ON public.chef_kaggle_images
    FOR SELECT TO anon USING (true);
CREATE POLICY chef_app_anon_read ON public.chef_themealdb_recipes
    FOR SELECT TO anon USING (true);
CREATE POLICY chef_app_anon_read ON public.chef_themealdb_ingredients
    FOR SELECT TO anon USING (true);

COMMIT;
