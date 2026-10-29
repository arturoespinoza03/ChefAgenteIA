# Instrucciones para continuar Chef-IA

Leer primero `CONTINUAR_EN_VSCODE.md`, `docs/ALCANCE.md` y `docs/AGENTE.md`.

- Trabajar por fases y solicitar aprobación del usuario antes de ejecutar la siguiente fase. No convertir una aprobación anterior en autorización para despliegues ni cambios remotos de datos o permisos.
- El usuario aprobó el agente, la Skill y la arquitectura de la aplicación. Se añadió `.vscode/mcp.json` para Supabase MCP, limitado al proyecto y en modo de solo lectura. El usuario confirmó que VS Code lo muestra conectado; esta sesión no expone herramientas Supabase MCP, por lo que aquí no se ha ejecutado una consulta remota.
- La web `src/web/` usa un backend local de solo lectura con `SUPABASE_PUBLISHABLE_KEY`; la conexión a los dos catálogos está probada. `service_role` no se usa. Las búsquedas en español traducen localmente términos culinarios conocidos; LibreTranslate en `.env` es opcional para términos no reconocidos y para traducir recetas cuando se solicita desde la interfaz. No afirmar que esa traducción externa funciona sin probar un endpoint configurado. No desplegar el backend ni modificar datos o políticas RLS sin aprobación explícita.
- Preservar los datos reales, los originales y su trazabilidad. No inventar ingredientes completos, cantidades, raciones, tiempos, precios o aptitud para alergias.
- No reintroducir Open Prices. Las consultas futuras de precios en internet se hacen únicamente bajo petición.
- Supabase ya está importado. No ejecutar de nuevo la migración inicial ni modificar permisos sin autorización. No guardar secretos en archivos versionados o en respuestas.
- Mantener separados diseño documentado, código funcional y validación remota. No presentar el proyecto como aplicación completa o MCP conectado.
- Seguir la documentación de pruebas para cambios funcionales. La consulta local y los tests no requieren paquetes externos.
