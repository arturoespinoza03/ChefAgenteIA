# Continuar Chef-IA en Visual Studio Code

## Abrir y comprobar

Abre esta carpeta completa desde Visual Studio Code: Archivo → Abrir carpeta → Chef-IA. Requiere Python 3.10 o posterior; la ejecución del proyecto usa únicamente su biblioteca estándar. No hace falta instalar paquetes para consultar los datos o ejecutar las pruebas.

En Terminal → Nueva terminal:

```sh
python3 -m unittest discover -s tests -v
python3 src/query_data.py kaggle-search chicken
python3 src/query_data.py kaggle-recipe Ground_Beef_Soup
python3 src/query_data.py ingredient tomato
```

También están disponibles tareas en Terminal → Ejecutar tarea. Si el editor ofrece elegir intérprete, selecciona Python 3.10 o posterior. Si `python3` no existe en tu equipo, instala Python desde su distribución oficial antes de ejecutar las tareas.

## Qué funciona realmente

- Consulta local sin red de 719 recetas Kaggle, 10.892 pasos y 2.893 referencias a imágenes, con los archivos de imagen incluidos.
- Catálogo adicional TheMealDB: 25 recetas y 202 entradas de ingredientes.
- Pruebas de consultas, integridad, lectura, exportación y correspondencia de datos.
- Importación remota ya ejecutada en Supabase y recuentos comprobados. Consulta relacionada verificada: Ground Beef Soup, nueve pasos.
- Definición aprobada del agente y Skill propia escrita.

No existe todavía una aplicación web, backend conversacional o agente ejecutable. No se afirma que el archivo Skill se cargue automáticamente. El catálogo Kaggle no permite buscar por todos los ingredientes: solo tiene nombres y pasos, más la extracción inicial de tres recetas.

## Estado de las decisiones y siguiente paso

El usuario pide trabajar **uno a uno y preguntar antes de ejecutar cada siguiente fase**.

1. Agente principal Chef Personal: definición aprobada y guardada en `docs/AGENTE.md` y `agent/INSTRUCCIONES.md`.
2. Skill `planificar-menu-con-evidencia`: aprobada y creada en `skills/planificar-menu-con-evidencia/SKILL.md`. Su validador de formato externo no se ejecutó por falta de PyYAML; la ejecución del proyecto no depende de ese validador.
3. MCP: propuesta presentada, **todavía no aprobada ni configurada**. Se propone el MCP oficial de Supabase, limitado al proyecto y solo lectura, con `list_tables` y `execute_sql`. Solicitar aprobación antes de conectarlo. No asumir que una sesión de navegador equivale a conexión MCP.
4. Definir backend, frontend y flujo completo: pendiente de propuesta y aprobación.
5. Matriz de errores y acciones que necesitan autorización: pendiente de propuesta y aprobación. Las instrucciones actuales ya prohíben cambios y compras sin autorización.

La petición de trasladar el proyecto no aprueba las fases pendientes ni habilita nuevas conexiones.

## Supabase

Proyecto: `uochnxgzsdslcgsznqso`.

Panel: https://supabase.com/dashboard/project/uochnxgzsdslcgsznqso

Endpoint: https://uochnxgzsdslcgsznqso.supabase.co

Las seis tablas tienen RLS activa. El acceso de `anon` y `authenticated` fue revocado; el navegador autenticado pudo importar con el SQL Editor. Un futuro frontend no podrá leerlas simplemente con la URL pública. Diseñar acceso de backend o políticas apropiadas después de aprobar la arquitectura; no desactivar RLS por comodidad.

No se exportaron sesiones, contraseñas, tokens o claves privadas. Una conexión nueva requiere autenticación autorizada. Las imágenes están locales; a Supabase solo se subieron las referencias. Subirlas a Storage es una tarea pendiente, no necesaria para la consulta local.

**No vuelvas a ejecutar `supabase/01_import.sql` en el proyecto ya importado.** Es una migración inicial, no idempotente, y fallará si existen sus tablas. Usa `02_verify.sql` para comprobar recuentos sin cambiar datos.

## Estructura y fuentes

- `data/`: SQLite, originales, imágenes, manifiestos y extracción de ingredientes.
- `src/`: consultas, importadores y exportador PostgreSQL.
- `tests/`: batería local.
- `evidence/`: resultados locales y evidencias reales de Supabase.
- `docs/`: alcance, calidad, agente y contexto del hackathon.
- `agent/`: instrucciones aprobadas.
- `skills/`: Skill propia.
- `supabase/`: migración, CSV, consultas y destino.
- `.vscode/`: tareas y recomendación de extensión Python.

No hay datos de precios: se retiraron por decisión del usuario. Precios de supermercados solo bajo petición, mediante una integración futura comprobada, sin asumir API pública de Mercadona o Carrefour.

Los datos y las licencias están documentados en `docs/DATOS.md` y `docs/KAGGLE.md`. Kaggle declara CC0; TheMealDB tiene condiciones propias. No imponer una licencia única a todo el contenido.
