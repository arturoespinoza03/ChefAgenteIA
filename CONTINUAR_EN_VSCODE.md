# Continuar Chef-IA en Visual Studio Code

## Abrir y comprobar

Abre esta carpeta completa desde Visual Studio Code: Archivo → Abrir carpeta → Chef-IA. Requiere Python 3.10 o posterior. Las consultas locales y pruebas de datos existentes usan la biblioteca estándar.

En Terminal → Nueva terminal:

```sh
python3 -m unittest discover -s tests -v
python3 src/query_data.py kaggle-search chicken
python3 src/query_data.py kaggle-recipe Ground_Beef_Soup
python3 src/query_data.py ingredient tomato
```

También están disponibles tareas en Terminal → Ejecutar tarea. Si el editor ofrece elegir intérprete, selecciona Python 3.10 o posterior. Si `python3` no existe en tu equipo, instala Python desde su distribución oficial antes de ejecutar las tareas.

## Aplicación web local

Instala el backend y prepara la configuración local:

```powershell
python -m pip install -r requirements-backend.txt
Copy-Item .env.example .env
python src/install_translation_model.py
```

En `.env`, configura `SUPABASE_PUBLISHABLE_KEY`. El comando `install_translation_model.py` descarga e instala el modelo inglés-español de Argos una sola vez. Después, al abrir una receta, se traduce automáticamente en el equipo; los textos de recetas no se envían a un servicio de traducción externo.

El modelo ocupa aproximadamente 88 MB. Si Windows informa de una ruta demasiado larga al instalar las dependencias, crea un entorno virtual fuera de la carpeta profunda del proyecto, por ejemplo `C:\venvs\chef-ia`, e instala y ejecuta la aplicación usando `C:\venvs\chef-ia\Scripts\python.exe`.

Ejecuta `python src/api.py` o la tarea `Chef-IA: iniciar web local`; se abrirá `http://127.0.0.1:8765` en el navegador. El backend solo escucha en `127.0.0.1`. La antigua ventana PySide6 puede abrirse con `python src/desktop.py`.

## Qué funciona realmente

- Consulta local sin red de 719 recetas Kaggle, 10.892 pasos y 2.893 referencias a imágenes, con los archivos de imagen incluidos.
- Catálogo adicional TheMealDB: 25 recetas y 202 entradas de ingredientes.
- Pruebas de consultas, integridad, lectura, exportación y correspondencia de datos.
- Interfaz HTML/CSS/JavaScript abierta en el navegador; busca en ambos catálogos sin selector visible y traduce automáticamente las recetas al español en el equipo con el modelo local Argos.
- Importación remota ya ejecutada en Supabase y recuentos comprobados. Consulta relacionada verificada: Ground Beef Soup, nueve pasos.
- Definición aprobada del agente y Skill propia escrita.

No existe todavía una aplicación web ni un agente conversacional ejecutable. No se afirma que el archivo Skill se cargue automáticamente. El catálogo Kaggle no permite buscar por todos los ingredientes: solo tiene nombres y pasos, más la extracción inicial de tres recetas.

## Estado de las decisiones y siguiente paso

El usuario pide trabajar **uno a uno y preguntar antes de ejecutar cada siguiente fase**.

1. Agente principal Chef Personal: definición aprobada y guardada en `docs/AGENTE.md` y `agent/INSTRUCCIONES.md`.
2. Skill `planificar-menu-con-evidencia`: aprobada y creada en `skills/planificar-menu-con-evidencia/SKILL.md`. Su validador de formato externo no se ejecutó por falta de PyYAML; la ejecución del proyecto no depende de ese validador.
3. MCP: aprobado. `.vscode/mcp.json` configura el MCP oficial de Supabase para el proyecto `uochnxgzsdslcgsznqso`, con `read_only=true` y solo las funciones de base de datos y documentación. El usuario confirmó que VS Code muestra el servidor conectado. Esta sesión no expone herramientas Supabase MCP, así que no se ha ejecutado aquí una consulta remota. El MCP es para desarrollo; el `.exe` consultará Supabase mediante acceso de aplicación seguro, no mediante la sesión MCP de VS Code.
4. Interfaz web `src/web/` y backend local: la web consulta en tiempo real ambos catálogos Supabase a través de `src/api.py`. Los términos habituales de búsqueda en español se traducen localmente; las recetas se traducen automáticamente al abrirlas con el modelo Argos inglés-español. La instalación inicial del modelo requiere conexión a Internet; las traducciones posteriores son locales.
5. Matriz de errores y acciones que necesitan autorización: pendiente de propuesta y aprobación. Las instrucciones actuales ya prohíben cambios y compras sin autorización.

La petición de trasladar el proyecto no aprueba las fases pendientes ni habilita nuevas conexiones.

## Supabase

Proyecto: `uochnxgzsdslcgsznqso`.

Panel: https://supabase.com/dashboard/project/uochnxgzsdslcgsznqso

Endpoint: https://uochnxgzsdslcgsznqso.supabase.co

Las seis tablas tienen RLS activa. El usuario proporcionó la clave pública, que se configuró solo en el `.env` local, ignorado por Git. La API REST devolvió filas de prueba de las cinco tablas de catálogo y el backend completó búsquedas y detalles en ambos catálogos. Esto confirma lectura pública para esos datos; no confirma que se ejecutara exactamente `03_app_readonly_access.sql` ni que no existan permisos de escritura.

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
