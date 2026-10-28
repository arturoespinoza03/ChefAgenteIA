SELECT 'chef_kaggle_recipes' AS tabla, count(*) AS filas, 719 AS esperado FROM public.chef_kaggle_recipes UNION ALL
SELECT 'chef_kaggle_steps' AS tabla, count(*) AS filas, 10892 AS esperado FROM public.chef_kaggle_steps UNION ALL
SELECT 'chef_kaggle_images' AS tabla, count(*) AS filas, 2893 AS esperado FROM public.chef_kaggle_images UNION ALL
SELECT 'chef_themealdb_recipes' AS tabla, count(*) AS filas, 25 AS esperado FROM public.chef_themealdb_recipes UNION ALL
SELECT 'chef_themealdb_ingredients' AS tabla, count(*) AS filas, 202 AS esperado FROM public.chef_themealdb_ingredients UNION ALL
SELECT 'chef_curated_ingredients' AS tabla, count(*) AS filas, 34 AS esperado FROM public.chef_curated_ingredients;
SELECT r.id,r.name,s.position,s.instruction FROM public.chef_kaggle_recipes r JOIN public.chef_kaggle_steps s ON s.recipe_id=r.id WHERE r.id='Ground_Beef_Soup' ORDER BY s.position;
