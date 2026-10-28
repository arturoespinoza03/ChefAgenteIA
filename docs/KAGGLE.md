# Dataset de Kaggle aportado por el equipo

Importación local: 28 de octubre de 2026.

## Fuente y licencia

Fuente: [Food Recipes dataset](https://www.kaggle.com/datasets/sathianpong/foodrecipe), publicado por **samsatp**, usuario `sathianpong`. La API pública de Kaggle declara **CC0: Public Domain**, versión de catálogo **3**, actualizada el **31 de agosto de 2021**. Verificación: 28 de octubre de 2026. Se conserva la respuesta del registro en `evidence/kaggle_metadata.json`, obtenida de `https://www.kaggle.com/api/v1/datasets/list?search=foodrecipe`.

La carpeta local contiene `data_strings_local.json`, `image_path.json` e `images/`. No incluye licencia adjunta ni identificador de versión; la versión 3 corresponde al catálogo consultado y no acredita por sí sola la versión exacta del archivo local. Los hashes del manifiesto identifican la copia utilizada.

Se documenta CC0 como licencia declarada por quien publica el dataset. Los metadatos recuperados no detallan el origen editorial de los textos o las imágenes ni acreditan permisos de terceros. Se conserva esta limitación de procedencia sin atribuir autores originales no verificados.

## Estructura e importación

- `data_strings_local.json`: objeto que relaciona un identificador legible de receta con una lista ordenada de instrucciones en inglés.
- `image_path.json`: objeto que relaciona esos identificadores con rutas relativas a imágenes.
- `data/raw/kaggle/`: copia de los originales, incluidas las imágenes, para reconstrucción sin depender de Descargas.
- `data/kaggle.sqlite`: tablas `recipes` (identificador y nombre), `steps` (receta, posición, instrucción) e `images` (receta, posición, ruta).
- `data/kaggle_schema.sql`: esquema reproducible.
- `data/kaggle_manifest.json`: hashes SHA-256 de los archivos y momento de importación UTC. Incluye URL, licencia declarada y referencia a la evidencia de Kaggle.

Los nombres se obtienen sustituyendo guiones bajos por espacios; los identificadores y pasos originales se conservan. No se traducen textos ni se inventan ingredientes, cantidades, raciones, tiempos, precios o alérgenos. Los textos se tratan como contenido del dataset, sin ejecutar instrucciones contenidas en ellos.

## Calidad y errores encontrados

| Comprobación | Resultado |
|---|---:|
| Recetas | 719 |
| Pasos | 10.892 |
| Referencias a imágenes | 2.893 |
| Recetas sin pasos | 4 |
| Recetas sin imágenes referenciadas | 4 |
| Pasos vacíos | 0 |
| Referencias a imágenes inexistentes | 0 |
| Archivos de imagen sin referencia | 28 |
| Secuencias de pasos repetidas, adicionales a la primera | 5 |

Las secuencias repetidas incluyen listas vacías: no equivalen a cinco recetas duplicadas confirmadas. Se conservan los registros para auditoría. Las imágenes sin referencia se copian pero no se asignan a recetas por inferencia.

Posibles errores: instrucciones incompletas o inconsistentes, referencias a vídeos no incluidos, nombres con espacios repetidos y ausencia de cantidades. La presencia de instrucciones no acredita exactitud culinaria. No se ha validado visualmente cada imagen ni evaluado representatividad del catálogo.

## Utilidad y límites para el proyecto

Este dataset amplía el catálogo consultable de recetas e instrucciones. **No basta para calcular una lista de compra o un menú dentro de presupuesto:** carece de un listado estructurado de ingredientes con cantidades y raciones, y no contiene precios. Se mantiene separado de las 25 recetas de TheMealDB y de las observaciones de Open Prices. No existe todavía una relación validada entre las tres fuentes.

## Ejecución y verificación

Desde la carpeta del proyecto:

```sh
python3 src/import_kaggle.py
python3 src/query_data.py kaggle-search chicken
python3 src/query_data.py kaggle-recipe Ground_Beef_Soup
python3 -m unittest discover -s tests -v
```

La primera orden reconstruye la base desde los originales incluidos. Para importar otra copia del mismo formato: `python3 src/import_kaggle.py --source '/ruta/a/carpeta'`.

Las consultas son parametrizadas y de solo lectura. Las pruebas comparan los pasos y rutas importados con ambos JSON originales, comprueban archivos de imágenes, integridad y relaciones, búsqueda, entradas SQL maliciosas y bloqueo de escritura. Evidencias: `evidence/kaggle_quality.json`, `evidence/kaggle_queries.json` y `evidence/tests_with_kaggle.txt`.
