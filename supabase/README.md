# Importación a Supabase

Importación ejecutada y verificada el 28/10/2026 en el proyecto `uochnxgzsdslcgsznqso`. Los seis recuentos coinciden. Consulta relacionada verificada: Ground Beef Soup, 9 pasos. Evidencias en `evidence/supabase_counts.txt`, `evidence/supabase_counts.png` y `evidence/supabase_query.txt`. RLS verificada activa en las seis tablas.

## Contenido

- `01_import.sql`: crea seis tablas con prefijo `chef_`, relaciones e índices e importa todos los registros en una transacción. No incluye precios. Si alguna tabla ya existe, falla sin sustituirla ni borrar datos.
- `02_verify.sql`: consulta los recuentos esperados y los pasos de una receta.
- CSV por tabla: alternativa para inspección o importación, después de crear el esquema; no importarlos además del SQL porque duplicarían filas. Los campos vacíos en CSV no distinguen NULL de cadena vacía; el SQL sí conserva la diferencia.
- `manifest.json`: recuentos y SHA-256 del SQL.

## Subida

Seleccionar el proyecto correcto en Supabase. En SQL Editor ejecutar el contenido de `01_import.sql` y después `02_verify.sql`. Para conexión PostgreSQL administrativa puede ejecutarse el mismo archivo con un cliente compatible. No guardar contraseñas o claves en el repositorio.

Tablas: 719 recetas Kaggle, 10.892 pasos, 2.893 referencias a imágenes; 25 recetas TheMealDB, 202 entradas de ingredientes; 34 menciones de ingredientes extraídas y pendientes de validación del equipo. Los catálogos mantienen identificadores y tablas separados.

RLS activada en las seis tablas. La clave pública ya pudo leer cada una de las cinco tablas de catálogo que necesita la app; el acceso real de lectura anónima está comprobado. No se verificaron aquí permisos de escritura ni cambios exactos de políticas.

Las imágenes binarias no están en PostgreSQL: se conservan rutas relativas. Para mostrarlas desde una web alojada fuera de este equipo será necesario subir los archivos a Storage y relacionar sus rutas con las del bucket. No se crea un bucket público automáticamente.

## Reconstrucción y comprobación local

```sh
python3 src/export_supabase.py
python3 -m unittest discover -s tests -v
```

La prueba de exportación importa los INSERT en una base SQLite temporal, adaptando las instrucciones exclusivas de PostgreSQL, y compara todas las filas con los CSV y las relaciones. **No verifica sintaxis PostgreSQL, permisos Supabase ni disponibilidad remota.** La importación y consulta remotas se verificaron adicionalmente en SQL Editor; las imágenes binarias siguen locales.

Fuentes y licencias: `docs/DATOS.md` y `docs/KAGGLE.md`.

## Proyecto de destino

Proyecto indicado por el usuario: `uochnxgzsdslcgsznqso`. URL pública: https://uochnxgzsdslcgsznqso.supabase.co . Esta URL identifica el destino, pero no autoriza ni autentica una importación. Estado: importación remota completada y recuentos verificados mediante SQL Editor.

## Acceso de lectura para la aplicación

`03_app_readonly_access.sql` contiene el SQL propuesto para permitir lectura pública de cinco tablas de catálogo. No se confirmó que ese archivo exacto se ejecutara; no lo vuelvas a ejecutar a ciegas. Se probó la clave pública contra la API REST y una fila fue devuelta desde cada una de las cinco tablas, incluidos pasos e ingredientes.

El backend de la app usa `SUPABASE_PUBLISHABLE_KEY`; no requiere `service_role`. La lectura anónima implica que cualquiera con la clave pública puede leer estas tablas según RLS. No se probaron operaciones de escritura.
