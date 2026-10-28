# Chef — asistente de recetas

Proyecto educativo de sistema agéntico aplicado a planificación culinaria. Alcance actualizado: consulta y selección de recetas, instrucciones y apoyo para identificar ingredientes. La capa de datos funciona; agente, Skills, MCP e interfaz quedan por implementar.

## Alcance

- Catálogo Kaggle: 719 recetas, 10.892 pasos y 2.893 referencias a imágenes.
- Catálogo complementario TheMealDB: 25 recetas y 202 entradas de ingredientes.
- Extracción asistida por IA de 34 menciones de ingredientes en tres recetas, con referencia al paso original; pendiente de validación por el equipo.
- Sin precios almacenados, cruce económico ni garantía de presupuesto.
- Precios de supermercados: consulta opcional en internet únicamente cuando el usuario la solicite. No hay conectores de Mercadona o Carrefour implementados.

## Ejecutar

Requiere Python 3.10 o posterior. Desde esta carpeta:

```sh
python3 src/query_data.py kaggle-search chicken
python3 src/query_data.py kaggle-recipe Ground_Beef_Soup
python3 src/query_data.py ingredient tomato
python3 src/query_data.py recipe 53151
python3 -m unittest discover -s tests -v
```

Reconstrucción local, sin red:

```sh
python3 src/import_kaggle.py
python3 src/import_data.py --offline
```

`python3 src/import_data.py` actualiza únicamente TheMealDB mediante su API pública. Las reconstrucciones sustituyen las bases generadas; editar las fuentes, no las bases manualmente.

## Documentación

- [Alcance y precios bajo petición](docs/ALCANCE.md).
- [Fuentes y calidad](docs/DATOS.md).
- [Detalle Kaggle](docs/KAGGLE.md).
- `evidence/tests.txt`: pruebas actuales.
- `data/curated/recipe_ingredients.json`: extracción inicial trazable.

## Fuentes y condiciones

[Food Recipes dataset, de samsatp/sathianpong](https://www.kaggle.com/datasets/sathianpong/foodrecipe): licencia declarada en Kaggle CC0: Public Domain. Metadatos preservados en `evidence/kaggle_metadata.json`; procedencia editorial original no acreditada en esos metadatos.

[TheMealDB](https://www.themealdb.com/): [condiciones propias](https://themealdb.com/terms_of_use.php), sin atribuir licencia abierta general. Consultar los límites antes de redistribuir contenido de terceros.

Las imágenes locales ocupan aproximadamente 180 MB. No se incluyen claves API privadas. No se han fusionado ni deduplicado los catálogos entre fuentes. Las recetas no tienen verificación exhaustiva de cantidades, raciones, tiempos ni alérgenos.

## Supabase

Paquete de migración preparado en [supabase/](supabase/README.md), con SQL PostgreSQL, CSV y consultas de verificación. Importación completada y verificada en el proyecto `uochnxgzsdslcgsznqso`: seis tablas con los recuentos esperados, RLS activa y consulta relacionada comprobada. Las imágenes binarias permanecen locales.

## Agente principal

Diseño aprobado de **Chef Personal** en [docs/AGENTE.md](docs/AGENTE.md) e instrucciones en [agent/INSTRUCCIONES.md](agent/INSTRUCCIONES.md). Se ha documentado la definición; el agente ejecutable y sus herramientas todavía no están implementados.

## Skill propia

[Planificar menú con evidencia](skills/planificar-menu-con-evidencia/SKILL.md): procedimiento aprobado para seleccionar recetas consultadas, justificar un menú y señalar datos ausentes. Archivo creado; su integración y ejecución por el agente quedan pendientes.

## Continuar en Visual Studio Code

Empieza por [CONTINUAR_EN_VSCODE.md](CONTINUAR_EN_VSCODE.md): ejecución local, estado real, Supabase, aprobaciones y tareas pendientes. El contexto y los requisitos del hackathon están en [docs/CONTEXTO_HACKATHON.md](docs/CONTEXTO_HACKATHON.md).
