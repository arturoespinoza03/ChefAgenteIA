# Fuentes, estructura y calidad de datos

Alcance actualizado el 28 de octubre de 2026: recetas sin precios almacenados. Open Prices y su cruce se han retirado por decisión del usuario.

## Kaggle

[Food Recipes dataset](https://www.kaggle.com/datasets/sathianpong/foodrecipe), publicado por samsatp/sathianpong. Licencia declarada CC0: Public Domain, verificada en la API pública de Kaggle. La versión de catálogo consultada es 3, actualizada el 31/08/2021; no acredita por sí sola la versión exacta del archivo local. Metadatos, hashes y límites de procedencia están documentados en [KAGGLE.md](KAGGLE.md).

Importación: `data/raw/kaggle/` → `data/kaggle.sqlite`. Tablas `recipes`, `steps` e `images`.

- 719 recetas, 10.892 pasos y 2.893 referencias a imágenes.
- Cuatro recetas sin pasos y cuatro sin imágenes referenciadas.
- Ninguna referencia a imagen inexistente; 28 archivos de imagen sin asociación.
- No incluye ingredientes estructurados, raciones o cantidades utilizables para el conjunto.

## TheMealDB

Fuente: [API pública](https://www.themealdb.com/api.php), endpoint `https://www.themealdb.com/api/json/v1/1/search.php?s=`. Acceso público de prueba `1` para desarrollo educativo, sin credenciales privadas. [Condiciones propias](https://themealdb.com/terms_of_use.php), sin atribuir una licencia abierta general ni permisos sobre contenido de terceros. No se descargan sus imágenes o vídeos.

Importación: `data/raw/themealdb.json` → `data/recipes.sqlite`.

- `recipes`: identificador, nombre, categoría, área, instrucciones y enlaces de procedencia.
- `recipe_ingredients`: receta, posición, ingrediente, clave normalizada y medida original.
- Muestra: 25 recetas y 202 entradas de ingredientes; no es catálogo completo ni muestra aleatoria.
- Se retiran espacios exteriores y se normalizan claves con `casefold`; se conserva la medida textual, sin conversiones inventadas.
- No permite certificar alérgenos, raciones ni tiempos estructurados.

## Extracción inicial

`data/curated/recipe_ingredients.json` conserva 34 menciones en tres recetas Kaggle, con paso y fragmento original. Es extracción manual asistida por IA, pendiente de validación por el equipo; no es cobertura completa ni ficha certificada. Cantidades y unidades permanecen nulas cuando no constan. No contiene vínculos a precios.

## Consultas y pruebas

`src/query_data.py` permite búsqueda Kaggle por nombre, detalle de receta Kaggle, búsqueda TheMealDB por ingrediente y detalle de receta TheMealDB. Consultas parametrizadas, de solo lectura y con cierre de conexiones.

Las reconstrucciones se ejecutan sin red desde los originales. Se conserva la evidencia de pruebas actual en `evidence/tests.txt`. Los catálogos permanecen separados y no se suman como recetas únicas deduplicadas.

## Errores y límites

Instrucciones incompletas, referencias a vídeos ausentes, unidades heterogéneas y ausencia de cantidades pueden limitar las recomendaciones. No se traducen ni validan automáticamente todas las recetas. Las etiquetas y menciones de ingredientes no certifican dietas o ausencia de alérgenos. La cobertura del catálogo y la de extracción estructurada deben mostrarse por separado.

La consulta opcional de precios en supermercados requiere una implementación posterior; véase [ALCANCE.md](ALCANCE.md).
