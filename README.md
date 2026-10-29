# Chef — asistente de recetas

Proyecto educativo de sistema agéntico aplicado a planificación culinaria. Alcance actualizado: consulta y selección de recetas, instrucciones y apoyo para identificar ingredientes. La interfaz web local consulta un backend de solo lectura que accede a Supabase bajo demanda. Las recetas se traducen automáticamente al español en el propio equipo al abrirlas, usando Argos Translate. El agente conversacional y el ejecutable `.exe` siguen pendientes.

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

## Aplicación web local

La interfaz web local usa HTML, CSS y JavaScript; el backend consulta ambos catálogos en Supabase bajo demanda, sin descargar el catálogo completo. Busca por nombre e ingredientes disponibles en español e inglés. Las recetas se traducen localmente al abrirlas; el texto no se envía a servicios de traducción externos. Instala las dependencias del backend y descarga una vez el modelo de traducción inglés-español:

```sh
python -m pip install -r requirements-backend.txt
python src/install_translation_model.py
```

Configura `SUPABASE_PUBLISHABLE_KEY` en `.env` con la clave pública del proyecto. El modelo se descarga desde el índice oficial de Argos durante la instalación inicial; después la traducción funciona sin conexión y no necesita claves de traducción.

El modelo ocupa aproximadamente 88 MB. En Windows, si `pip` falla al extraer dependencias por la longitud de la ruta del Python de Microsoft Store, usa un entorno virtual en una ruta corta:

```powershell
python -m venv C:\venvs\chef-ia
C:\venvs\chef-ia\Scripts\python.exe -m pip install -r requirements-backend.txt
C:\venvs\chef-ia\Scripts\python.exe src\install_translation_model.py
C:\venvs\chef-ia\Scripts\python.exe src\api.py
```

Inicia el servidor:

```sh
python src/api.py
```

Se abrirá el navegador en `http://127.0.0.1:8765`. El backend solo escucha en la interfaz local; no lo expongas directamente a Internet.

La antigua interfaz PySide6 sigue disponible con `python src/desktop.py`. La web es la interfaz recomendada.

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
