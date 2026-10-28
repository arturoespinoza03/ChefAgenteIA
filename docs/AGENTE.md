# Diseño del agente principal: Chef Personal

Aprobado por el usuario el 28 de octubre de 2026. Estado: definición documentada; implementación pendiente.

## Objetivo y usuario

Ayudar a personas a elegir recetas y organizar menús con los datos de Supabase, explicando qué información está disponible y qué falta.

Entradas: ingredientes disponibles, preferencias, exclusiones, comensales y número de comidas. Solo se solicitan los datos pertinentes a la petición.

Resultado: recetas seleccionadas, instrucciones y propuesta de menú con procedencia. La consulta de precios en internet se activa únicamente bajo petición. No se inventan cantidades, raciones, tiempos, información nutricional ni precios ausentes.

Las instrucciones aprobadas se conservan en `agent/INSTRUCCIONES.md`.

## Decisiones y tareas

| Situación | Decisión |
|---|---|
| Falta una preferencia imprescindible | Pedir una aclaración breve. |
| Búsqueda por nombre | Buscar en el catálogo y recuperar detalles. |
| Aprovechar ingredientes | Consultar ingredientes estructurados o extracciones documentadas y declarar su cobertura limitada. |
| Solicitud de menú | Seleccionar recetas, justificar la combinación y señalar restricciones pendientes de verificar. |
| Comensales indicados pero raciones originales ausentes | Explicar que no se pueden ajustar cantidades con fiabilidad. |
| No hay resultados compatibles | Explicar el motivo y proponer relajar una preferencia, sin ignorar exclusiones. |
| Solicitud de precios | Activar búsqueda externa; pedir ubicación o supermercado cuando sea necesario. |
| Fallo de herramienta | Informar del fallo sin simular resultados ni afirmar que la consulta se realizó. |

## Demostración inicial propuesta

«Propón tres cenas variadas y muéstrame las instrucciones de la que elija».

La planificación por tiempo exacto, cantidades o presupuesto queda condicionada a disponer de los datos necesarios. Los pasos de preparación no se interpretan como una ficha completa de ingredientes ni como verificación de restricciones.

## Estado de los siguientes pasos

Skill propia, servidor MCP y herramientas reales, arquitectura de backend y frontend, flujo completo y matriz de errores y autorizaciones: pendientes de propuesta y aprobación por separado. La aprobación de este diseño no autoriza su implementación automática ni cambios en Supabase.
